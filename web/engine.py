"""Python execution, AST checks and an SVG-compatible turtle command adapter.
Runs inside a disposable browser worker. Not a high-stakes anti-cheating grader.
"""
import ast
import builtins
import contextlib
import io
import json
import math
import re
import sys
import types

class LimitError(Exception):
    pass

class Drawing:
    def __init__(self):
        self.x = self.y = self.heading = 0.0
        self.down = True
        self.line = '#285e54'
        self.fill = '#9be7cf'
        self.filling = None
        self.segments = []
        self.shapes = []
        self.events = []
    def event(self, name, args):
        self.events.append({'name': name, 'args': list(args), 'down': self.down})
    def move(self, x, y, name, args):
        self.event(name, args)
        if self.down:
            self.segments.append({'a': [self.x, self.y], 'b': [x, y], 'color': self.line})
            if self.filling is not None:
                self.filling.append([x, y])
        self.x, self.y = x, y
    def forward(self, d):
        a = math.radians(self.heading)
        self.move(self.x + d * math.cos(a), self.y + d * math.sin(a), 'forward', [d])
    def backward(self, d):
        a = math.radians(self.heading)
        self.move(self.x - d * math.cos(a), self.y - d * math.sin(a), 'backward', [d])
    def left(self, a):
        self.event('left', [a]); self.heading += a
    def right(self, a):
        self.event('right', [a]); self.heading -= a
    def penup(self):
        self.down = False; self.event('penup', [])
    def pendown(self):
        self.down = True; self.event('pendown', [])
    def setpos(self, x, y=None):
        if y is None:
            x, y = x
        self.move(float(x), float(y), 'setpos', [x, y])
    def pencolor(self, c=None):
        if c is None: return self.line
        self.line = c; self.event('pencolor', [c])
    def fillcolor(self, c=None):
        if c is None: return self.fill
        self.fill = c; self.event('fillcolor', [c])
    def begin_fill(self):
        self.event('begin_fill', []); self.filling = [[self.x, self.y]]
    def end_fill(self):
        self.event('end_fill', [])
        if self.filling is None: raise ValueError('begin_fill() must precede end_fill()')
        self.shapes.append({'points': self.filling, 'fill': self.fill, 'color': self.line})
        self.filling = None
    def setheading(self, a):
        self.heading = a; self.event('setheading', [a])
    def done(self): pass
    def speed(self, *_): pass
    def hideturtle(self): pass
    def module(self):
        mod = types.ModuleType('turtle')
        for name in ['forward','backward','left','right','penup','pendown','setpos','pencolor','fillcolor','begin_fill','end_fill','setheading','done','speed','hideturtle']:
            setattr(mod, name, getattr(self, name))
        mod.fd = mod.forward; mod.bk = mod.backward; mod.lt = mod.left; mod.rt = mod.right
        mod.goto = mod.setpos; mod.up = mod.penup; mod.down = mod.pendown
        # One turtle supported; extra instances intentionally share the same drawing.
        mod.Turtle = lambda: self
        return mod
    def data(self):
        return {'segments': self.segments, 'shapes': self.shapes, 'events': self.events}

class Audit(ast.NodeTransformer):
    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Attribute) and node.func.attr in ('append','extend','sort'):
            return ast.copy_location(ast.Call(func=ast.Name(id='__audit_method', ctx=ast.Load()),
                args=[node.func.value, ast.Constant(node.func.attr), *node.args], keywords=node.keywords), node)
        return node
    def visit_Delete(self, node):
        self.generic_visit(node)
        before, after = [], []
        for target in node.targets:
            if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                before.append(ast.copy_location(ast.Expr(ast.Call(ast.Name('__audit_delete_before', ast.Load()), [ast.Name(target.value.id,ast.Load())], [])), node))
                after.append(ast.copy_location(ast.Expr(ast.Call(ast.Name('__audit_delete_after', ast.Load()), [ast.Name(target.value.id,ast.Load())], [])), node))
        return before + [node] + after

def execute(code, inputs=None):
    tree = ast.parse(code, filename='<learner>')
    drawing = Drawing()
    old_turtle = sys.modules.get('turtle')
    sys.modules['turtle'] = drawing.module()
    output, transcript, operations, calls, lines = io.StringIO(), [], [], [], set()
    values = iter(inputs or [])
    used = []
    deletion = {}
    def input_fn(prompt=''):
        try: value = next(values)
        except StopIteration: raise EOFError('输入已用完：请在输入框每行填写一个 input() 的回答。')
        used.append(str(value)); transcript.append({'prompt': str(prompt), 'value': str(value)})
        return str(value)
    def method(obj, name, *args, **kwargs):
        variables=[key for key,value in sys._getframe(1).f_locals.items() if value is obj]
        before = list(obj) if isinstance(obj, list) else None
        result = getattr(obj, name)(*args, **kwargs)
        if isinstance(obj, list):
            operations.append({'name': name, 'before': before, 'after': list(obj), 'object': id(obj), 'variables':variables})
        return result
    def del_before(obj):
        if isinstance(obj,list): deletion[id(obj)] = list(obj)
    def del_after(obj):
        if isinstance(obj,list): operations.append({'name':'del','before':deletion.get(id(obj),[]),'after':list(obj),'object':id(obj),'variables':[key for key,value in sys._getframe(1).f_locals.items() if value is obj]})
    count = 0
    def trace(frame, event, arg):
        nonlocal count
        if frame.f_code.co_filename == '<learner>' and event == 'line':
            lines.add(frame.f_lineno); count += 1
            if count > 50000: raise LimitError('超过执行步数限制。检查 while 的条件与更新，或停止运行。')
        return trace
    def profile(frame, event, arg):
        if frame.f_code.co_filename == '<learner>' and event in ('call','return'):
            parent = frame.f_back.f_code.co_name if frame.f_back else ''
            calls.append({'name':frame.f_code.co_name,'parent':parent,'event':event,'type':type(arg).__name__,'value':arg if isinstance(arg,(int,float,bool,str,type(None))) else None})
    env = {'__name__':'__main__', '__builtins__':dict(vars(builtins)), '__audit_method':method, '__audit_delete_before':del_before, '__audit_delete_after':del_after}
    env['__builtins__']['input'] = input_fn
    error = None
    try:
        sys.settrace(trace); sys.setprofile(profile)
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            exec(compile(ast.fix_missing_locations(Audit().visit(ast.parse(code))), '<learner>', 'exec'), env)
    except BaseException as exc:
        error = {'type':type(exc).__name__, 'message':str(exc)}
    finally:
        sys.settrace(None); sys.setprofile(None)
        if old_turtle is None: sys.modules.pop('turtle',None)
        else: sys.modules['turtle'] = old_turtle
    return {'stdout':output.getvalue(), 'input':transcript, 'used':len(used), 'operations':operations, 'calls':calls, 'lines':list(lines), 'drawing':drawing.data(), 'error':error, 'tree':tree}

def category(error):
    name = error['type']
    if name in ('SyntaxError','IndentationError','TabError'): return '语法错误'
    if name in ('TypeError','ValueError'): return '类型错误'
    if name == 'LimitError': return '执行超限'
    if name == 'EOFError': return '输入次数错误'
    return '运行错误'

def dependencies(tree):
    """Conservative data/control dependence for ordinary beginner solutions.
    A proof for arbitrary Python is not claimed; unresolved indirect calls are
    exposed to the UI for human review rather than approved silently.
    """
    parents={child:parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    names=lambda node: {x.id for x in ast.walk(node) if isinstance(x,ast.Name) and isinstance(x.ctx,ast.Load)}
    graph={}; sinks=set()
    for n in ast.walk(tree):
        if isinstance(n,(ast.Assign,ast.AnnAssign,ast.AugAssign)):
            targets=n.targets if isinstance(n,ast.Assign) else [n.target]
            for t in targets:
                for x in ast.walk(t):
                    if isinstance(x,ast.Name): graph.setdefault(x.id,set()).update(names(n.value))
        if isinstance(n,ast.FunctionDef):
            graph.setdefault(n.name,set()).update(names(n))
        output=isinstance(n,ast.Call) and ((isinstance(n.func,ast.Name) and n.func.id=='print') or (isinstance(n.func,ast.Attribute) and n.func.attr in ('forward','backward','setpos','begin_fill','end_fill')))
        mutation=isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('append','extend','sort')
        if mutation:
            base={x.id for x in ast.walk(n.func.value) if isinstance(x,ast.Name)}
            for x in base: graph.setdefault(x,set()).update(names(n))
            ancestor=parents.get(n)
            while ancestor:
                if isinstance(ancestor,(ast.If,ast.While)):
                    for x in base: graph[x].update(names(ancestor.test))
                ancestor=parents.get(ancestor)
        if output:
            sinks.update(names(n))
            if isinstance(n,ast.Delete):
                sinks.update(x.id for x in ast.walk(n) if isinstance(x,ast.Name))
            ancestor=parents.get(n)
            while ancestor:
                if isinstance(ancestor,(ast.If,ast.While)): sinks.update(names(ancestor.test))
                if isinstance(ancestor,ast.For): sinks.update(names(ancestor.iter))
                if isinstance(ancestor,ast.FunctionDef): sinks.add(ancestor.name)
                ancestor=parents.get(ancestor)
    relevant=set(sinks)
    while True:
        new=relevant | set().union(*(graph.get(x,set()) for x in relevant))
        if new==relevant: break
        relevant=new
    return relevant

def structure(tree, run, required):
    issues, manual = [], []
    nodes = list(ast.walk(tree))
    executed = set(run['lines'])
    returns = [x for x in run['calls'] if x['event']=='return' and x['name']!='<module>']
    relevant=dependencies(tree)
    definitions={n.name:n for n in nodes if isinstance(n,ast.FunctionDef)}
    participating={x['name'] for x in returns if x['name'] in relevant}
    if 'function' in required and not returns:
        issues.append('要求定义并实际调用函数，不能只写顶层语句。')
    elif 'function' in required and not participating:
        issues.append('检测到函数调用，但函数未参与结果、判断或绘图；不能用无关函数代替题目要求。')
    if 'numeric_return' in required and not any(x['name'] in participating and x['type'] in ('int','float') for x in returns):
        issues.append('计算函数必须通过 return 返回数值；print 输出不能代替返回值。')
    if 'nested' in required and not any(x['event']=='call' and x['parent'] not in ('<module>','') for x in run['calls']):
        issues.append('要求一个实际执行的函数调用另一个函数。')
    elif 'nested' in required and not any(x['event']=='call' and x['parent'] in participating and x['name'] in relevant for x in run['calls']):
        issues.append('嵌套函数调用必须参与题目的计算。')
    if 'parameter' in required and not any(isinstance(n,ast.FunctionDef) and n.args.args and any(c['name']==n.name for c in returns) for n in nodes):
        issues.append('要求实际调用接收参数的函数。')
    if 'bool' in required and not any(x['type']=='bool' and x['name'] in participating for x in returns):
        issues.append('检查函数必须实际返回 True 或 False。')
    for kind, cls in [('for',ast.For),('while',ast.While)]:
        if kind in required:
            loops = [n for n in nodes if isinstance(n,cls) and any(b.lineno in executed for b in n.body)]
            if not loops: issues.append(f'要求使用实际执行的 {kind} 循环完成任务。')
            elif not any(any(isinstance(x,(ast.Call,ast.Assign,ast.AugAssign)) for b in n.body for x in ast.walk(b)) for n in loops):
                issues.append(f'{kind} 循环体没有参与计算、输出或绘图。')
            else:
                useful=False
                uncertain=False
                for loop in loops:
                    for b in loop.body:
                        for x in ast.walk(b):
                            if isinstance(x,(ast.Assign,ast.AugAssign,ast.AnnAssign)):
                                targets=x.targets if isinstance(x,ast.Assign) else [x.target]
                                if any(isinstance(t,ast.Name) and t.id in relevant for t in targets): useful=True
                            if isinstance(x,ast.Call):
                                if isinstance(x.func,ast.Name) and x.func.id in relevant:
                                    # print inside a loop produces the task's rows.
                                    if x.func.id=='print' and all(isinstance(a,ast.Constant) and a.value in ('',None) for a in x.args): continue
                                    useful=True
                                elif isinstance(x.func,ast.Attribute):
                                    base={n.id for n in ast.walk(x.func.value) if isinstance(n,ast.Name)}
                                    if base & relevant: useful=True
                                    else: uncertain=True
                if not useful:
                    if uncertain: manual.append(f'{kind} 已执行，但无法可靠确认其用于任务；需要人工核对。')
                    else: issues.append(f'{kind} 循环未参与输出、累积计算或绘图。')
    for name in ('extend','sort','del','append'):
        if name in required:
            ops = [x for x in run['operations'] if x['name']==name]
            if not ops: issues.append(f'要求实际对列表执行 {name}。')
            elif not any(set(x.get('variables',[])) & relevant for x in ops):
                issues.append(f'{name} 操作发生在未参与结果的列表上。请对解决本题的列表使用该操作。')
            elif name=='sort':
                if not any(x['after']==sorted(x['before']) for x in ops): issues.append('sort() 没有产生排序结果。')
            elif not any(x['before']!=x['after'] for x in ops): issues.append(f'{name} 必须实际改变列表。')
    if 'elif' in required and not any(isinstance(n,ast.If) and n.orelse and isinstance(n.orelse[0],ast.If) for n in nodes):
        issues.append('题目要求使用 if / elif 分档。')
    return issues, manual

def numbers(s):
    return [float(x) for x in re.findall(r'(?<![A-Za-z])[-+]?(?:\d+\.\d+|\d+)',s)]

def near(a,b): return abs(a-b) < 0.006

def drawing_check(run, ns, perimeter=180):
    d=run['drawing']; shapes=d['shapes']
    if len(shapes)!=len(ns): return False, f'应有 {len(ns)} 个填充图形，实际 {len(shapes)} 个。'
    boxes=[]
    for shape,n in zip(shapes,ns):
        pts=shape['points']
        if len(pts)!=n+1: return False, f'{n} 边形应画 {n} 条边。'
        if math.dist(pts[0],pts[-1])>0.01: return False, '多边形没有闭合，检查 360 / n 的转角。'
        if any(abs(math.dist(a,b)-perimeter/n)>0.01 for a,b in zip(pts,pts[1:])): return False, f'边长应为 {perimeter} / n。'
        # Check external turns, independent of initial heading and turning direction.
        angles=[math.atan2(b[1]-a[1],b[0]-a[0]) for a,b in zip(pts,pts[1:])]
        for a,b in zip(angles,angles[1:]):
            delta=abs((b-a+math.pi)%(2*math.pi)-math.pi)
            if abs(delta-2*math.pi/n)>0.001: return False, '每次转向应为 360 / n。'
        boxes.append((min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)))
    for i,a in enumerate(boxes):
        for b in boxes[i+1:]:
            if min(a[2],b[2])-max(a[0],b[0])>0.01 and min(a[3],b[3])-max(a[1],b[1])>0.01:
                return False, '图形的包围框重叠，请增大间距。斜向交错布局需人工核对。'
    moves=[e for e in d['events'] if e['name']=='setpos']
    if len(moves)<len(ns) or any(e['down'] for e in moves): return False, '每个图形前要 setpos；移动时必须先 penup。'
    if len(d['segments'])!=sum(ns): return False, '检测到额外连线或缺失边。'
    if not all(any(e['name']==k for e in d['events']) for k in ['pencolor','fillcolor']): return False, '需要设置线条与填充颜色。'
    return True,''

def check_case(q, case, run):
    out=run['stdout'].strip(); rule=q.get('validator','exact')
    expected=case.get('expected','')
    if rule=='exact':
        if out==str(expected).strip(): return True,'',''
        if out.split()==str(expected).split(): return False,'格式错误','计算内容接近，但行、空格或格式未符合题目。'
        return False,case.get('category','逻辑错误'),'实际输出与期望不同。'
    if rule=='money':
        vals=numbers(out)
        ok=bool(vals) and near(vals[-1],expected)
        if ok and not re.search(r'\$\s*'+re.escape(f'{expected:.2f}')+r'(?!\d)',out): return False,'格式错误','金额要带 $ 并保留两位小数（练习平台约定，原题示例格式）。'
        return ok,'逻辑错误','检查价格、优惠条件以及折后金额。'
    if rule=='quantity':
        n=int(case['inputs'][0]); rate=n+4 if n<=5 else 10
        cost=20*n*(1-rate/100)
        if not numbers(out) or not near(numbers(out)[-1],cost): return False,'边界错误','检查 1～5 件的 5%～9% 与超过 5 件的 10%。'
        perc=re.findall(r'(\d+(?:\.\d+)?)\s*%',out)
        if (n<=5 and (len(perc)!=1 or float(perc[0])!=rate)) or (n>5 and perc): return False,'格式错误','1～5 件显示折扣百分比；超过 5 件只显示折后总额。'
        return bool(re.search(r'\$\s*'+re.escape(f'{cost:.2f}')+r'(?!\d)',out)),'格式错误','金额需要 $ 和两位小数。'
    if rule=='deduct':
        if case['inputs'][0]=='n': return ('Bye Bye' in out and run['used']==1),'逻辑错误','n 分支应输出 Bye Bye，不再读入数字。'
        return (numbers(out) and near(numbers(out)[-1],expected) and run['used']==4),'逻辑错误','y 分支应读三个数并计算 100 减去三数之和。'
    if rule=='table':
        vals=numbers(out)
        ok=len(vals)==3 and all(near(a,b) for a,b in zip(vals,expected))
        if not ok: return False,'边界错误','检查 200、500、1000 的分档顺序和折扣金额。'
        if len(out.splitlines())<2 or not all(x in out.lower() for x in ('purchase','discount','total')): return False,'格式错误','需要表头 Purchase Amount、Discount、Total，以及一行对应金额。'
        if len(re.findall(r'\$\s*\d+\.\d{2}(?!\d)',out))!=3: return False,'格式错误','三列金额都要带 $ 和两位小数。'
        return True,'',''
    if rule=='hours':
        return bool(re.search(r'Total Hours:\s*'+str(expected)+r'\.',out)),'格式错误','按附件代码输出 Total Hours:，结果用 :.0f，句末为句点。'
    if rule=='convert':
        if case.get('invalid'): return ('invalid' in out.lower()),'逻辑错误','无效单位应输出包含 invalid 的说明。'
        ok=bool(numbers(out)) and near(numbers(out)[-1],expected)
        if not ok: return False,'逻辑错误','核对 1.60934 的乘除方向。'
        if case['unit'] not in out.lower() or not re.search(re.escape(f'{expected:.2f}'),out): return False,'格式错误','输出转换后的单位，并保留两位小数。'
        return True,'',''
    if rule=='movies':
        ops=run['operations']
        valid=False
        for ext in [x for x in ops if x['name']=='extend' and len(x['before'])==3 and len(x['after'])==6]:
            sorts=[x for x in ops if x['object']==ext['object'] and x['name']=='sort' and len(x['after'])==6]
            dels=[x for x in ops if x['object']==ext['object'] and x['name']=='del' and len(x['before'])==6 and len(x['after'])==5]
            if sorts and dels and ops.index(ext)<ops.index(sorts[0])<ops.index(dels[0]):
                last=dels[0]['after']
                valid=all(isinstance(x,str) for x in last) and last==sorted(last) and repr(last) in out
                if valid: break
        return valid,'未满足指定写法','同一列表须从 3 个电影用 extend 加到 6 个，再 sort，再 del 删除 1 个并打印结果。'
    if rule=='days':
        good=[]; valid=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        for value in case['inputs']:
            if value in valid and value not in good: good.append(value)
        vals=numbers(out)
        if run['used']!=7: return False,'边界错误','固定读取 7 次输入，重复或错误输入也占一次。'
        if not vals or vals[-1]!=len(good): return False,'逻辑错误','结尾应报告成功加入的不重复星期数量。'
        if good and repr(good) not in out: return False,'逻辑错误','成功添加后需要显示列表；结尾列表应保留输入顺序。'
        valid_attempts=[v for v in case['inputs'] if v in valid]
        if len(valid_attempts)!=len(set(valid_attempts)) and not re.search(r'already|duplicate',out,re.I): return False,'逻辑错误','遇到已成功加入的重复星期需要说明 already / duplicate。'
        if any(v not in valid for v in case['inputs']) and not re.search(r'not a day|invalid',out,re.I): return False,'逻辑错误','无效星期需要说明 not a day / invalid。'
        if any(c['type']=='bool' and c['value'] is True for c in run['calls'] if c['event']=='return') is False and good: return False,'未满足指定写法','添加动作应使用返回 True 的检查函数。'
        # Verify add operations never admit invalid/duplicate entries.
        adds=[x for x in run['operations'] if x['name']=='append']
        if any(len(x['after'])!=len(set(x['after'])) or any(v not in valid for v in x['after']) for x in adds): return False,'逻辑错误','列表中出现了重复或无效星期。'
        boolean_names={c['name'] for c in run['calls'] if c['event']=='return' and c['type']=='bool'}
        cond_names=set()
        for node in ast.walk(run['tree']):
            if isinstance(node,ast.If) and any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr=='append' for child in node.body for x in ast.walk(child)):
                cond_names.update(x.id for x in ast.walk(node.test) if isinstance(x,ast.Name))
        for node in ast.walk(run['tree']):
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in cond_names for t in node.targets):
                cond_names.update(x.id for x in ast.walk(node.value) if isinstance(x,ast.Name))
        if good and not (boolean_names & cond_names): return False,'未满足指定写法','加入列表的分支需要使用检查函数返回的布尔值，而不是调用后忽略。'
        return True,'',''
    if rule=='polygons':
        ok,msg=drawing_check(run,case.get('ns',list(range(3,13))),case.get('perimeter',180))
        return ok,'逻辑错误',msg
    return False,'需要人工核对','没有可用的自动判题规则。'

def grade(code, q, code_alt=''):
    if q.get('kind')=='short': raise ValueError('Short questions use explicit choice keys, not program grading.')
    if q.get('dual'):
        first=dict(q,dual=False,required=['for']); second=dict(q,dual=False,required=['while'])
        a=grade(code,first); b=grade(code_alt,second)
        return {'passed':a['passed'] and b['passed'],'cases':a['cases']+b['cases'],'issues':a['issues']+b['issues'],'manual':a['manual']+b['manual'],'stdout':'FOR:\n'+a['stdout']+'\nWHILE:\n'+b['stdout'],'drawing':a['drawing']}
    try: ast.parse(code,filename='<learner>')
    except (SyntaxError,IndentationError) as exc:
        return {'passed':False,'cases':[],'issues':[{'category':'语法错误','message':f'第 {exc.lineno} 行：{exc.msg}'}],'manual':[],'stdout':'','drawing':None}
    results=[]; issues=[]; manual=[]; first=None; all_runs=[]
    for i,case in enumerate(q.get('cases',[])):
        run=execute(code,case.get('inputs',[]))
        all_runs.append(run)
        if first is None: first=run
        if run['error']:
            ok=False; cat=category(run['error']); msg=run['error']['message']
        else:
            ok,cat,msg=check_case(q,case,run)
        results.append({'name':case.get('label',f'测试 {i+1}'),'passed':bool(ok),'category':cat if not ok else '', 'message':msg if not ok else '', 'actual':run['stdout'], 'expected':case.get('expected'), 'inputs':case.get('inputs',[])})
        if not ok and not any(x['category']==cat and x['message']==msg for x in issues): issues.append({'category':cat,'message':msg})
    if first:
        errs,notes=structure(first['tree'],first,q.get('required',[]))
        # A branch-only first test can omit a function. Combine dynamic activity across cases.
        if errs and len(q.get('cases',[]))>1:
            combined=dict(first)
            runs=all_runs[1:]
            for field in ('calls','lines','operations'):
                combined[field]=first[field]+[item for r in runs for item in r[field]]
            errs,notes=structure(first['tree'],combined,q.get('required',[]))
        issues.extend({'category':'未满足指定写法','message':e} for e in errs)
        manual=notes
        names={c['name'] for r in all_runs for c in r['calls'] if c['event']=='call'}
        for name in q.get('requiredNames',[]):
            if name not in names: issues.append({'category':'未满足指定写法','message':f'附件代码指定 {name}，需要定义并实际调用它。'})
        if q.get('validator')=='days':
            bool_values={c['value'] for r in all_runs for c in r['calls'] if c['event']=='return' and c['type']=='bool'}
            if not {True,False}.issubset(bool_values): issues.append({'category':'未满足指定写法','message':'星期检查函数需要在有效和重复/无效输入时分别返回 True 与 False。'})
    else: issues.append({'category':'需要人工核对','message':'本题没有可执行的测试。'})
    return {'passed':bool(results) and all(x['passed'] for x in results) and not issues,'cases':results,'issues':issues,'manual':manual,'stdout':first['stdout'] if first else '', 'drawing':first['drawing'] if first else None}

def handle(payload):
    try:
        if payload['action']=='grade': return grade(payload['code'],payload['question'],payload.get('codeAlt',''))
        run=execute(payload['code'],payload.get('inputs',[]))
        run.pop('tree',None)
        return run
    except BaseException as exc:
        return {'passed':False,'issues':[{'category':category({'type':type(exc).__name__}),'message':str(exc)}],'error':{'type':type(exc).__name__,'message':str(exc)}}
