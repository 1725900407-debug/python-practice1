"""Human-authored content. Reference programs are fixture-tested, never generated at runtime."""
from pathlib import Path
import json
import textwrap
ROOT=Path(__file__).resolve().parents[1]
questions=[]
def code(s): return textwrap.dedent(s).strip()+'\n'
def add(id,title,topic,kind,en,zh,solution,cases=None,required=None,validator='exact',source='专项练习',starter='',**kw):
    questions.append(dict(id=id,title=title,topic=topic,kind=kind,en=en,zh=zh,solution=code(solution) if kind!='short' else solution,cases=cases or [],required=required or [],validator=validator,source=source,starter=code(starter) if starter else '',hints=kw.pop('hints',['先分清输入、处理和输出，再写出步骤。','检查数据类型、分支边界或循环更新；用一个小输入手动追踪。']),**kw))
def case(inputs,expected,label=None,**kw): return dict(inputs=list(map(str,inputs)),expected=expected,label=label or ' / '.join(map(str,inputs)) or '无输入',**kw)

# 10 homework-aligned tasks. Sample layout contracts are explicitly separated from teacher text.
add('H01','The Lab Depot','condition','homework',
    'Item price is $22.50. Read the number of items and the company name. Apply a 10% discount only if the name is "The Lab Depot"; otherwise print the total without a discount.',
    '每件 $22.50。读入购买数量、公司名称。只有名称恰好为 The Lab Depot 时减去总价的 10%，否则不打折。练习输出约定：金额带 $，保留两位小数；输入提示文字不参与判题。',
    '''n = int(input("Number of items: "))
name = input("Company name: ")
total = n * 22.50
if name == "The Lab Depot":
    total = total - total * 0.10
    print(f"Discounted total: ${total:.2f}")
else:
    print(f"Total cost: ${total:.2f}")''',
    [case([10,'The Lab Depot'],202.5),case([1,'The Lab Depot'],20.25),case([4,'Other'],90),case([4,'the lab depot'],90)],validator='money',source='附件第 1 题',hw=1)
add('H02','Quantity discount','condition','homework',
    'Each item costs $20.00. For 1–5 items, discounts are 5%, 6%, 7%, 8%, 9%. Above 5 items, the discount is 10%. Display the discount percentage only for 1–5 items, and display the discounted total in both branches.',
    '每件 $20。1～5 件分别优惠 5%、6%、7%、8%、9%；超过 5 件优惠 10%。前一个分支显示百分比，后一个分支只显示折后金额。金额按示例保留两位小数。没有额外增加负数或零输入判错条件。',
    '''n = int(input("Number of items: "))
if n <= 5:
    rate = n + 4
    total = n * 20 * (1 - rate / 100)
    print(f"Discounted total ({rate}% off): ${total:.2f}")
else:
    total = n * 20 * 0.9
    print(f"Total cost less discount: ${total:.2f}")''',
    [case([n],20*n*(1-(n+4 if n<=5 else 10)/100)) for n in [1,2,3,4,5,6,12]],validator='quantity',source='附件第 2 题',hw=2)
add('H03','Deduct from 100','input','homework',
    'Ask "Shall we begin y/n?" If the user does not want to begin, display "Bye Bye". Otherwise read 3 numbers and display 100 minus their sum.',
    '读 y/n。n 时输出 Bye Bye，不再读数字；y 时读入 3 个数，输出 100 减去三数之和。附件没有规定其他输入的处理；测试仅覆盖 y 与 n。',
    '''begin = input("Shall we begin y/n? ")
if begin == "y":
    a = float(input("Number 1: "))
    b = float(input("Number 2: "))
    c = float(input("Number 3: "))
    print(f"The three numbers deducted from 100 is {100-a-b-c:g}")
else:
    print("Bye Bye")''',
    [case(['n'],''),case(['y',10,20,30],40),case(['y',1.5,2.25,3],93.25)],validator='deduct',source='附件第 3 题',hw=3)
amounts=[0,199.99,200,200.01,499.99,500,500.01,999.99,1000,1000.01]
add('H04','Tiered discount table','format','homework',
    'Use if-elif: purchase >=1000 gets 20%, >=500 gets 10%, >=200 gets 5%, below 200 gets no discount. Display Purchase Amount, Discount, Total as a table.',
    '用 if / elif 分档：≥1000 为 20%，≥500 为 10%，≥200 为 5%，低于 200 不优惠。三列分别是原价、折扣金额、折后金额。按图片示例显示表头、$ 和两位小数；列间空格可不同。',
    '''amount = float(input("Purchase amount: "))
if amount >= 1000:
    rate = 0.20
elif amount >= 500:
    rate = 0.10
elif amount >= 200:
    rate = 0.05
else:
    rate = 0
saving = amount * rate
print("Purchase Amount    Discount    Total")
print(f"${amount:.2f}    ${saving:.2f}    ${amount-saving:.2f}")''',
    [case([a],[a,a*(.2 if a>=1000 else .1 if a>=500 else .05 if a>=200 else 0),a*(.8 if a>=1000 else .9 if a>=500 else .95 if a>=200 else 1)],f'金额 {a}') for a in amounts],required=['elif'],validator='table',source='附件第 4 题',hw=4)
add('H05','Calling one function from another','function','homework',
    'Create class_hours.py following the supplied code: each class has 10 × 1.5 tutorial hours and 7 × 1 lecture hours. hours_classes() returns the hours per class. total_hours(num_classes) calls it and returns the total. Read the class count and print Total Hours using .0f.',
    '按附件代码建立 hours_classes() 和 total_hours(num_classes)，每门课 10×1.5+7 小时。第二个函数调用第一个。读课程数，输出 Total Hours: {结果:.0f}.。附件把被调用函数先定义作为建议；Python 实际要求是调用发生时名称已定义，不要求两条 def 固定先后。',
    '''def hours_classes():
    return 10 * 1.5 + 7

def total_hours(num_classes):
    return hours_classes() * num_classes

number_of_classes = int(input("How many classes are there? "))
print(f"Total Hours: {total_hours(number_of_classes):.0f}.")''',
    [case([n],n*22) for n in [1,3,0]],required=['function','parameter','nested'],validator='hours',source='附件第 5 题',hw=5,filename='class_hours.py')
add('H06','Miles ↔ kilometres','function','homework',
    'Read a distance and its unit. Call the appropriate function. miles = kilometres / 1.60934; kilometers = miles * 1.60934. If the unit is neither kilometers nor miles, display an invalid-unit message.',
    '输入距离和单位，按单位调用不同转换函数。miles=kilometres/1.60934；kilometers=miles×1.60934。图片提示和示例用 Kilometers、Miles（大写首字母），正文用小写。原题没有严格规定大小写接受策略：本练习明确使用这两个示例词，不额外测试小写或英式拼写；无效单位用 Feet 测试。输出按示例保留两位小数及转换后的单位。',
    '''def to_miles(km):
    return km / 1.60934

def to_kilometers(miles):
    return miles * 1.60934

distance = float(input("Distance: "))
unit = input("Unit (Kilometers or Miles): ")
if unit == "Kilometers":
    print(f"Converted distance: {to_miles(distance):.2f} miles")
elif unit == "Miles":
    print(f"Converted distance: {to_kilometers(distance):.2f} kilometers")
else:
    print("This unit is invalid")''',
    [case([100,'Miles'],160.934,unit='kilometers'),case([1.60934,'Kilometers'],1,unit='miles'),case([0,'Miles'],0,unit='kilometers'),case([10,'Feet'],'',invalid=True)],required=['function','parameter'],validator='convert',source='附件第 6 题',hw=6)
add('H07','A movie list','list','homework',
    'Create a list of three movies you like. Add three more using extend(), sort the list, delete one movie using del, and print the list. Save as movies.py.',
    '创建包含 3 个喜欢的电影的列表。用 extend() 再加入 3 个，用 sort() 原地排序，再用 del 删除 1 个，打印检查结果。电影名和删除哪部可自行选择，判题不限定为示例答案。',
    '''movies = ["Up", "Coco", "Dune"]
movies.extend(["Soul", "Arrival", "Jaws"])
movies.sort()
del movies[2]
print(movies)''',
    [case([],None)],required=['extend','sort','del'],validator='movies',source='附件第 7 题',hw=7,filename='movies.py')
DAYS=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
add('H08','Seven attempts, not seven successes','list','homework',
    'Create days_of_week.py. A function checks that a day is valid and not already entered, tells the user about duplicates or invalid days, and returns True/False. Give exactly 7 attempts, add accepted days, show the list and report how many were correct.',
    '恰好问 7 次。函数检查是否为有效星期、是否重复；重复或无效时说明原因，返回 True/False。仅 True 时加入列表并显示。结尾报告答对数量。图片明确将 wednesday 判错，所以不自动转小写或放宽大小写。重复和无效输入也占一次机会。',
    '''def check_day(day, entered):
    valid = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if day in entered:
        print("Already entered")
        return False
    if day not in valid:
        print("Not a day of the week")
        return False
    return True

entered = []
for attempt in range(7):
    day = input("Enter a day of the week: ")
    if check_day(day, entered):
        entered.append(day)
        print(entered)
print(f"You have correctly entered {len(entered)} day(s) of the week.")''',
    [case(DAYS,7,'7 个有效星期'),case(['Monday','Monday','wednesday','March','Tuesday','Tomorrow','Thursday'],3,'重复、大小写与无效输入'),case(['x']*7,0,'7 次全错'),case(['Sunday']*7,1,'7 次重复')],required=['function','parameter','bool'],validator='days',source='附件第 8 题',hw=8,filename='days_of_week.py')
POLYGON='''import turtle as t

def polygon(n):
    t.begin_fill()
    for side in range(n):
        t.forward(180 / n)
        t.left(360 / n)
    t.end_fill()

t.pencolor("#285e54")
t.fillcolor("#b6efde")
for n in range(3, 13):
    t.penup()
    t.setpos(((n-3) % 5) * 120 - 260, ((n-3) // 5) * 140 - 100)
    t.pendown()
    polygon(n)
t.done()'''
add('H09','Separate polygons','turtle','homework',
    'Create separate_polygons.py. Use a polygon function taking the number of sides. Turn by 360/n and use side length 180/n. Loop over 3 to 12 sides, move using setpos, penup/pendown, and set line and fill colors so the polygons do not overlap.',
    '用带边数参数的函数绘制多边形，边长 180/n，转角 360/n。循环覆盖 3～12；每个图形前抬笔、setpos、落笔；设置线条和填充颜色。本平台采用 begin_fill/end_fill 验证填充。附件写了“如下图”，但上传图片没有示例图，不限定具体配色或布局。',
    POLYGON,[case([],None,ns=list(range(3,13)))],required=['function','parameter','for'],validator='polygons',source='附件第 9 题',hw=9,filename='separate_polygons.py')
times='\n'.join(f'{n} times 9 is {n*9}' for n in range(10,0,-1))
add('H10','Two ways to count down','loop','homework',
    'Write two separate programs: one using for, another using while. Print 10 times 9 is 90 down to 1 times 9 is 9, one line per product.',
    '分别提交两份程序：一份用 for，一份用 while。从 10 到 1 输出乘 9 的结果，恰好 10 行，首末行和句式须与附件一致。',
    '''for n in range(10, 0, -1):
    print(f"{n} times 9 is {n*9}")''',
    [case([],times)],source='附件第 10 题',hw=10,dual=True,solutionAlt=code('''n = 10
while n >= 1:
    print(f"{n} times 9 is {n*9}")
    n -= 1'''))

# 30 short questions: 4/5 options are unnecessary; three clear alternatives, one key.
SHORTS=[
('input','input() 的返回类型','What type does input() return?','输入 12 后，input() 返回的类型是什么？',['str','int','float'],0,'input() 返回字符串 "12"，数值运算前按需求转换。'),
('input','整数和浮点转换','What does int("2.5") do?','int("2.5") 会怎样？',['返回 2','返回 2.5','抛出 ValueError'],2,'带小数点的字符串不能直接 int()；使用 float()。'),
('input','表达式优先级','Predict 100 - (10 + 20 + 30).','100 - (10 + 20 + 30) 的值是什么？',['40','100','60'],0,'先算括号内的和，再从 100 减去。'),
('input','变量与引号','What is printed?','name = "Ada"\nprint("name", name)',['name Ada','Ada Ada','name name'],0,'引号内是字面字符串，无引号的 name 读取变量。'),
('input','数字还是文字','Predict the output.','a = input() # 输入 3\nprint(a * 2)',['6','33','TypeError'],1,'字符串乘整数会重复；int(a)*2 才是数值乘法。'),
('format','f-string 中的花括号','Predict the output.','n = 4\nprint(f"${n*2:.2f}")',['$8.00','$n*2','8'],0,'f 启用表达式插入，{} 求值，$ 是普通字符，:.2f 保留两位小数。'),
('format','缺失 f 前缀','Predict the output.','n = 7\nprint("{n}")',['7','{n}','SyntaxError'],1,'没有 f，花括号不会插入变量。'),
('format','零位小数不截断','Predict the output.','print(f"{2.8:.0f}")',['2','3','2.8'],1,'格式化到零位小数会舍入；int(2.8) 才是向零截断。'),
('format','百分号的作用','Predict the output.','rate = 10\nprint(f"{rate}%")',['10%','0.1','1000'],0,'% 在这个字符串中是普通字符，不会除以 100。'),
('format','折扣金额与折后金额','What are the saving and total?','原价 80，折扣 25%。折扣金额和折后金额分别是？',['20 和 60','25 和 55','60 和 20'],0,'折扣金额=80×0.25=20，折后金额=80−20=60。'),
('condition','赋值与比较','Which expression tests equality?','比较 name 是否等于 "The Lab Depot" 应使用？',['name = "The Lab Depot"','name == "The Lab Depot"','name := "The Lab Depot"'],1,'= 赋值，== 比较；if 需要条件表达式。'),
('condition','分档边界','Which rate applies to exactly 500?','附件金额折扣题，恰好 500 对应什么折扣率？',['5%','10%','20%'],1,'500 满足 >=500，但不满足 >=1000。'),
('condition','分支顺序','Predict this code for amount=1200.','if amount >= 200: rate=5\nelif amount >= 1000: rate=20\namount 为 1200 时 rate 是？',['20','5','两个分支都执行'],1,'if 首个真分支结束分档链。高门槛应放在前面。'),
('condition','严格字符串比较','Does this name match?','"The Lab Depot" == "the lab depot" 是？',['True','False','SyntaxError'],1,'字符串比较区分大小写，不自动加宽容规则。'),
('function','return 与 print','What is returned?','def f():\n    print(3)\nx = f()\nx 的值是什么？',['3','None','"3"'],1,'print 输出但不返回该值。没有 return 时返回 None。'),
('function','形参和实参','Identify the parameter.','def cost(n): return n*20\ncost(4)\n形参是？',['n','4','cost'],0,'n 是定义时的形参，4 是调用时传入的实参。'),
('function','函数定义先后','Will this run?','def outer(): return inner()\ndef inner(): return 3\nprint(outer())',['输出 3','NameError','outer 必须写在 inner 后'],0,'实际调用 outer 时 inner 已定义，因此可以运行。'),
('function','调用发生太早','What happens?','def outer(): return inner()\nprint(outer())\ndef inner(): return 3',['输出 3','NameError','输出 None'],1,'调用 outer 时 inner 的 def 尚未执行，名称未定义。'),
('function','局部变量','What happens?','def f():\n    local = 2\nf()\nprint(local)',['2','None','NameError'],2,'函数内的局部变量不能直接在顶层使用。'),
('function','布尔返回','What does the function return?','def valid(n): return n >= 5\nvalid(5)',['True','5','False'],0,'比较表达式返回 bool，>= 包含边界 5。'),
('list','索引从零开始','What is items[1]?','items = ["A", "B", "C"]\nitems[1] 是？',['A','B','C'],1,'索引 0 是 A，索引 1 是 B。'),
('list','append 和 extend','What is the list length?','a = [1]\na.append([2,3])\nlen(a) 是？',['2','3','1'],0,'append 把整个列表作为一个元素添加。extend 才会逐个添加。'),
('list','sort 的返回值','What does sort() return?','a = [3,1]\nx = a.sort()\nx 是？',['[1,3]','None','[3,1]'],1,'sort 原地改变 a，返回 None。'),
('list','按索引删除','Predict the list.','a = ["C","A","B"]\na.sort()\ndel a[1]\nprint(a)',['["A","C"]','["A","B"]','["B","C"]'],0,'排序为 A,B,C，del a[1] 删除 B。'),
('loop','range 终点不包含','What values occur?','list(range(3,7)) 是？',['[3,4,5,6]','[3,4,5,6,7]','[4,5,6,7]'],0,'起点包含，终点 7 不包含。'),
('loop','负步长','How do you count from 10 to 1?','哪句 range 依次产生 10 到 1？',['range(10,1,-1)','range(10,0,-1)','range(1,10,-1)'],1,'负步长时终点同样不包含，需用 0 才包括 1。'),
('loop','固定尝试与成功次数','When does the homework stop?','星期题前 3 次都错，已经用了几次机会？',['0 次','3 次','直到成功才计次数'],1,'附件规定 7 次尝试，每个输入都占一次。'),
('loop','累加器与计数器','What are total and count?','total=0; count=0\nfor n in [2,5]:\n    total += n\n    count += 1',['total=7,count=2','total=2,count=7','total=7,count=7'],0,'累加器加数值，计数器加发生次数。'),
('turtle','多边形的转角','What is the external angle?','画 6 边形，每边后转向角应是多少？',['120°','60°','30°'],1,'turtle 转外角 360/6=60，不是内角 120。'),
('turtle','移动时的笔状态','Which order avoids a connecting line?','从一个图形移动到另一个图形，应使用？',['setpos → penup → pendown','penup → setpos → pendown','pendown → setpos'],1,'先抬笔，移动不绘线，到达后落笔。'),
]
for i,(topic,title,en,zh,choices,key,explain) in enumerate(SHORTS,1):
    add(f'S{i:02}',title,topic,'short',en,zh,key,choices=choices,explanation=explain,source='专项短练习')

# 20 debugging exercises; defects differ in type, boundary, state, organization and formatting.
DEBUG=[
('input','先转换再计算','Read an integer and print twice its value.','读取整数，输出其两倍。','n=input()\nprint(n*2)','n=int(input())\nprint(n*2)',[case([3],'6'),case([12],'24')],[]),
('input','小数输入不能直接 int','Read a decimal price and add 2.5.','读入浮点价格，加 2.5，保留两位小数。','price=int(input())\nprint(f"{price+2.5:.2f}")','price=float(input())\nprint(f"{price+2.5:.2f}")',[case([1.2],'3.70')],[]),
('input','括号里的三数和','Read three numbers and print 100 minus their sum.','读三数，输出 100 减去三数之和。','a=float(input())\nb=float(input())\nc=float(input())\nprint(100-a+b+c)','a=float(input())\nb=float(input())\nc=float(input())\nprint(100-(a+b+c))',[case([10,20,30],'40.0')],[]),
('format','遗漏 f','Insert the variable in the sentence.','读整数数量，输出 Items: 数量。','n=int(input())\nprint("Items: {n}")','n=int(input())\nprint(f"Items: {n}")',[case([4],'Items: 4')],[]),
('format','价格小数位','Print a price with a dollar sign and two decimals.','读价格，带 $ 输出两位小数。','x=float(input())\nprint(f"${x:.0f}")','x=float(input())\nprint(f"${x:.2f}")',[case([3.75],'$3.75'),case([5],'$5.00')],[]),
('condition','赋值写进了 if','Print yes only for exact input y; otherwise print no.','恰好 y 输出 yes，其他输入输出 no。','a=input()\nif a = "y":\n    print("yes")\nelse:\n    print("no")','a=input()\nif a == "y":\n    print("yes")\nelse:\n    print("no")',[case(['y'],'yes'),case(['n'],'no')],[]),
('condition','最高档先判断','Output 20 for >=1000, 10 for >=500, else 0.','输出折扣率整数：≥1000 为 20，≥500 为 10，否则为 0。','a=float(input())\nif a>=500:\n    print(10)\nelif a>=1000:\n    print(20)\nelse:\n    print(0)','a=float(input())\nif a>=1000:\n    print(20)\nelif a>=500:\n    print(10)\nelse:\n    print(0)',[case([1000],'20'),case([500],'10'),case([499.99],'0')],['elif']),
('condition','漏掉边界','Print eligible for ages >=18, otherwise wait.','年龄至少 18 输出 eligible，否则 wait。','age=int(input())\nif age>18:\n    print("eligible")\nelse:\n    print("wait")','age=int(input())\nif age>=18:\n    print("eligible")\nelse:\n    print("wait")',[case([18],'eligible'),case([17],'wait')],[]),
('function','把 print 当 return','A function must return triple its parameter; print its result.','函数返回参数的三倍，顶层打印结果。','def triple(n):\n    print(n*3)\nx=int(input())\nprint(triple(x))','def triple(n):\n    return n*3\nx=int(input())\nprint(triple(x))',[case([4],'12')],['function','parameter']),
('function','调用时名称还不存在','Repair execution order without removing either function.','保留两个函数，把顶层调用移到名称都已定义之后。','def outer():\n    return inner()+1\nprint(outer())\ndef inner():\n    return 4','def outer():\n    return inner()+1\ndef inner():\n    return 4\nprint(outer())',[case([],'5')],['function','nested']),
('function','局部结果返回出去','Return the local total and print it outside the function.','在函数内求和，通过 return 把结果传回顶层。','def add(a,b):\n    total=a+b\nadd(2,3)\nprint(total)','def add(a,b):\n    total=a+b\n    return total\nprint(add(2,3))',[case([],'5')],['function','parameter']),
('function','布尔值不是字符串','Function returns bool; add only accepted days.','函数必须返回 bool；本练习仅接受 Monday，其他输入打印 False。','def valid(day):\n    return "False"\nday=input()\nif valid(day):\n    print(True)\nelse:\n    print(False)','def valid(day):\n    return day=="Monday"\nday=input()\nif valid(day):\n    print(True)\nelse:\n    print(False)',[case(['x'],'False'),case(['Monday'],'True')],['function','bool']),
('list','把列表变成 None','Sort the list in place and print it.','对 [3,1,2] 原地排序并打印列表。','a=[3,1,2]\na=a.sort()\nprint(a)','a=[3,1,2]\na.sort()\nprint(a)',[case([],'[1, 2, 3]')],['sort']),
('list','三个元素不是一个列表','Use extend to add B and C separately.','a=["A"]，用 extend 逐个加入 B、C 后打印。','a=["A"]\na.append(["B","C"])\nprint(a)','a=["A"]\na.extend(["B","C"])\nprint(a)',[case([],"['A', 'B', 'C']")],['extend']),
('list','索引选错位置','Delete the second item using del.','用 del 删除 [10,20,30] 的第二个元素。','a=[10,20,30]\ndel a[2]\nprint(a)','a=[10,20,30]\ndel a[1]\nprint(a)',[case([],'[10, 30]')],['del']),
('list','去重方向写反','Read three names and append only new names.','读 3 个名字，只 append 尚未出现的，最后打印列表。','a=[]\nfor i in range(3):\n    name=input()\n    if name in a:\n        a.append(name)\nprint(a)','a=[]\nfor i in range(3):\n    name=input()\n    if name not in a:\n        a.append(name)\nprint(a)',[case(['A','B','A'],"['A', 'B']")],['append','for']),
('loop','倒序少了末项','Use for to print 3,2,1 on separate lines.','用 for 分行输出 3、2、1。','for n in range(3,1,-1):\n    print(n)','for n in range(3,0,-1):\n    print(n)',[case([],'3\n2\n1')],['for']),
('loop','while 变量不更新','Use while to print 1,2,3 on separate lines.','用 while 输出 1、2、3；修复循环更新。','n=1\nwhile n<=3:\n    print(n)','n=1\nwhile n<=3:\n    print(n)\n    n+=1',[case([],'1\n2\n3')],['while']),
('loop','累加器不能每轮清零','Read three integers and print their sum using for.','用 for 读 3 个整数，最后输出和。','for i in range(3):\n    total=0\n    total+=int(input())\nprint(total)','total=0\nfor i in range(3):\n    total+=int(input())\nprint(total)',[case([2,3,4],'9')],['for']),
('turtle','外角与内角混淆','Draw one filled square, side length 45, at a chosen pen-up position.','画一个填充正方形，边长 45，抬笔 setpos 定位；设置两种颜色。','import turtle as t\nt.pencolor("green")\nt.fillcolor("cyan")\nt.penup()\nt.setpos(0,0)\nt.pendown()\nt.begin_fill()\nfor i in range(4):\n    t.forward(45)\n    t.left(180/4)\nt.end_fill()','import turtle as t\nt.pencolor("green")\nt.fillcolor("cyan")\nt.penup()\nt.setpos(0,0)\nt.pendown()\nt.begin_fill()\nfor i in range(4):\n    t.forward(45)\n    t.left(360/4)\nt.end_fill()',[case([],None,ns=[4])],['for'])
]
for i,(topic,title,en,zh,broken,solution,cases,required) in enumerate(DEBUG,1):
    add(f'D{i:02}',title,topic,'debug',en,zh,solution,cases,required,validator='polygons' if topic=='turtle' else 'exact',starter=broken,source='专项找错练习')

# 20 independently written single-concept exercises.
SINGLES=[
('input','剩余预算','Read budget and expense as floats; print their difference to 2 decimals.','读预算、支出两个浮点数；输出余额，两位小数。','budget=float(input())\nexpense=float(input())\nprint(f"{budget-expense:.2f}")',[case([100,21.25],'78.75'),case([12,13],'-1.00')],[]),
('input','整数商和余数','Read a nonnegative integer; pack items into boxes of 6. Print full boxes and leftovers separated by one space.','输入非负整数数量，每盒 6 个。输出完整盒数与剩余数，中间一个空格。','n=int(input())\nprint(n//6,n%6)',[case([14],'2 2'),case([12],'2 0')],[]),
('format','折扣率转百分数','Read a rate such as 0.125 and print it as a percentage to one decimal.','输入小数形式的折扣率，如 0.125，输出 12.5%。','rate=float(input())\nprint(f"{rate*100:.1f}%")',[case([.125],'12.5%'),case([.2],'20.0%')],[]),
('format','简洁收据','Read unit price and integer quantity. Print Price Qty Total then a row like $2.50 3 $7.50.','读单价、整数数量。第一行 Price Qty Total；第二行带 $ 的单价、数量和总价，金额两位小数，用一个空格分列。','p=float(input())\nn=int(input())\nprint("Price Qty Total")\nprint(f"${p:.2f} {n} ${p*n:.2f}")',[case([2.5,3],'Price Qty Total\n$2.50 3 $7.50')],[]),
('condition','半开温度区间','Print safe only when 18 <= temperature < 25; otherwise alert.','温度满足 18≤t<25 时 safe，否则 alert。','t=float(input())\nif 18<=t<25:\n    print("safe")\nelse:\n    print("alert")',[case([18],'safe'),case([24.99],'safe'),case([25],'alert'),case([17.99],'alert')],[]),
('condition','分类字符串','Read a category. adult costs 12, student costs 8; anything else prints invalid. Case-sensitive.','读类别，adult 输出 12，student 输出 8，其他输出 invalid。区分大小写。','category=input()\nif category=="adult":\n    print(12)\nelif category=="student":\n    print(8)\nelse:\n    print("invalid")',[case(['adult'],'12'),case(['student'],'8'),case(['Adult'],'invalid')],['elif']),
('function','函数返回价格','Write a function with a quantity parameter returning quantity * 7.5. Read quantity and print 2 decimals.','带数量形参的函数返回数量×7.5；读整数数量，顶层输出两位小数。','def cost(n):\n    return n*7.5\nn=int(input())\nprint(f"{cost(n):.2f}")',[case([3],'22.50'),case([0],'0.00')],['function','parameter']),
('function','区间判断返回 bool','Write a function returning True only for 0 <= score <= 100. Read a score and print the bool.','函数接收成绩，仅 0≤成绩≤100 返回 True，否则 False。读成绩并打印布尔结果。','def valid(score):\n    return 0<=score<=100\nprint(valid(float(input())))',[case([0],'True'),case([100],'True'),case([-1],'False')],['function','parameter','bool']),
('function','复用计算函数','Use one function returning 4.5 and another calling it to compute total hours for an input number of sessions. Print 1 decimal.','一个函数返回每次 4.5 小时，另一个带次数参数并调用它计算总小时。读次数，输出一位小数。','def one():\n    return 4.5\ndef total(n):\n    return one()*n\nprint(f"{total(int(input())):.1f}")',[case([3],'13.5')],['function','nested','parameter']),
('list','列表索引与长度','Create [4,8,12,16]. Print its first item, last item and length, separated by spaces.','创建 [4,8,12,16]，输出首项、末项、长度，用空格分隔。','a=[4,8,12,16]\nprint(a[0],a[len(a)-1],len(a))',[case([],'4 16 4')],[]),
('list','先扩展再排序','Create [8,2], extend it with [5,1], sort in place, print it.','创建 [8,2]，extend 加入 [5,1]，sort 原地排序并打印。','a=[8,2]\na.extend([5,1])\na.sort()\nprint(a)',[case([],'[1, 2, 5, 8]')],['extend','sort']),
('list','删除最后一项','Read three names into a list using append, use del to remove the last one, print the list.','使用 append 读入三个名字到列表，再用 del 删除最后一项并打印。','a=[]\nfor i in range(3):\n    a.append(input())\ndel a[2]\nprint(a)',[case(['A','B','C'],"['A', 'B']")],['append','del','for']),
('loop','步长筛选','Use for and range to print the positive multiples of 3 below 13, one per line.','用 for 和 range 输出小于 13 的正数 3 的倍数，每行一个。','for n in range(3,13,3):\n    print(n)',[case([],'3\n6\n9\n12')],['for']),
('loop','求和循环','Read a positive integer n and use for to sum 1 through n; print the sum.','读正整数 n，用 for 计算 1 到 n 的总和并输出。','n=int(input())\ntotal=0\nfor value in range(1,n+1):\n    total+=value\nprint(total)',[case([1],'1'),case([5],'15')],['for']),
('loop','while 累乘','Read a positive integer n and use while to compute 1*2*...*n; print the result.','读正整数 n，用 while 求 1×2×…×n 并打印。','n=int(input())\nvalue=1\nproduct=1\nwhile value<=n:\n    product*=value\n    value+=1\nprint(product)',[case([1],'1'),case([4],'24')],['while']),
('loop','计数不累加','Read five integers and use for to count values >=10. Print the count.','用 for 读五个整数，计数其中 ≥10 的数量，最后打印计数。','count=0\nfor i in range(5):\n    n=int(input())\n    if n>=10:\n        count+=1\nprint(count)',[case([9,10,11,0,20],'3')],['for']),
('turtle','参数化五边形','Use a parameterized function to draw one filled pentagon, side 180/n, angle 360/n, after pen-up setpos. Set colors.','写带边数参数的函数，画一个填充五边形，边长 180/n、转角 360/n，抬笔 setpos 定位并设置颜色。',POLYGON.replace('range(3, 13)','[5]'),[case([],None,ns=[5])],['function','parameter','for']),
('turtle','顺时针三角形','Use right turns to draw one filled triangle of side 60, at a pen-up position. Set line/fill colors.','使用 right 画一个填充三角形，边长 60，抬笔 setpos 定位，设置线条和填充颜色。',POLYGON.replace('range(3, 13)','[3]').replace('t.left(360 / n)','t.right(360 / n)'),[case([],None,ns=[3])],['for']),
('turtle','反向前进','Use backward and left to draw one filled square of side 45 after a pen-up setpos. Set colors.','使用 backward 和 left 画一个填充正方形，边长 45，抬笔 setpos 定位并设置颜色。',POLYGON.replace('range(3, 13)','[4]').replace('t.forward(180 / n)','t.backward(180 / n)'),[case([],None,ns=[4])],['for']),
('list','去重计数函数','Function reads three names, appends only new names, returns the count. Print count.','函数读三个名字，只 append 新名字，返回去重数量；顶层打印返回值。','def count_names():\n    seen=[]\n    for i in range(3):\n        name=input()\n        if name not in seen:\n            seen.append(name)\n    return len(seen)\nprint(count_names())',[case(['A','A','B'],'2'),case(['A','B','C'],'3')],['function','append','for']),
]
for i,(topic,title,en,zh,solution,cases,required) in enumerate(SINGLES,1):
    add(f'P{i:02}',title,topic,'program',en,zh,solution,cases,required,validator='polygons' if topic=='turtle' else 'exact',source='单知识点独立编程')

# Two substantive transfers for every homework type. They change organization,
# input/branch rules, output contract, algorithm or loop direction, not merely numbers.
def transfer(i,j,title,topic,en,zh,solution,cases,required=None,validator='exact',**kw):
    add(f'T{i:02}{j}',title,topic,'transfer',en,zh,solution,cases,required,validator,source=f'第 {i} 类综合迁移（额外拓展）',hw=i,**kw)
transfer(1,1,'会员优惠封装成函数','function','Read integer quantity and membership (member/guest). Function returns cost at $22.50 each with 10% off for member only. Print two decimals, no dollar sign.','数量与身份 member/guest 决定优惠。把计算放入带参数、返回数值的函数；每件 22.50，member 优惠 10%；只输出两位小数，不带 $。',
'''def cost(n, status):
    total=n*22.5
    if status=="member":
        return total*0.9
    return total
n=int(input())
status=input()
print(f"{cost(n,status):.2f}")''',[case([2,'member'],'40.50'),case([2,'guest'],'45.00')],['function','parameter'])
transfer(1,2,'双条件资格与节省额','condition','Read quantity and company. A 10% discount needs exact The Lab Depot AND quantity >=3. Print saving then total, two decimals separated by one space.','同时满足公司名恰好为 The Lab Depot 且数量 ≥3 才优惠 10%。按顺序输出节省额、折后额，两位小数、一个空格。每件 22.50。',
'''n=int(input())
name=input()
original=n*22.5
if name=="The Lab Depot" and n>=3:
    saving=original*0.1
else:
    saving=0
print(f"{saving:.2f} {original-saving:.2f}")''',[case([2,'The Lab Depot'],'0.00 45.00'),case([3,'The Lab Depot'],'6.75 60.75'),case([4,'Other'],'0.00 90.00')])
transfer(2,1,'次数固定的批量订单','loop','Process exactly three quantities using for. Same $20 and 1–5/6+ discounts as homework. Print each total to 2 decimals, then the sum on a final line.','用 for 连续处理 3 个订单数量。单价与原数量折扣相同，每个订单输出两位小数折后额，末行输出三个订单总和；不输出百分号。',
'''grand=0
for i in range(3):
    n=int(input())
    rate=n+4 if n<=5 else 10
    total=n*20*(1-rate/100)
    grand+=total
    print(f"{total:.2f}")
print(f"{grand:.2f}")''',[case([1,5,6],'19.00\n91.00\n108.00\n218.00')],['for'])
transfer(2,2,'固定立减与百分比选择','function','Function accepts quantity and offer. Each item is $20. flat subtracts $5 from the whole order; percent takes 10% off. Unknown offer returns original total. Read quantity and offer; print 2 decimals.','函数按 offer 选择不同优惠：flat 总价立减 5；percent 总价打九折；其他保持原价。单价 20，读数量与 offer，打印两位小数。输入数量为正整数。',
'''def bill(n,offer):
    total=n*20
    if offer=="flat":
        return total-5
    if offer=="percent":
        return total*0.9
    return total
n=int(input())
offer=input()
print(f"{bill(n,offer):.2f}")''',[case([1,'flat'],'15.00'),case([5,'percent'],'90.00'),case([6,'none'],'120.00')],['function','parameter'])
transfer(3,1,'剩余预算的收集循环','loop','Read y/n. n prints Bye Bye. y reads a budget then exactly four expenses using while; print the remaining budget to 2 decimals.','y 时读预算，再用 while 恰好读 4 笔支出，输出余额两位小数；n 只输出 Bye Bye，不读其他值。',
'''begin=input()
if begin=="n":
    print("Bye Bye")
else:
    budget=float(input())
    total=0
    count=0
    while count<4:
        total+=float(input())
        count+=1
    print(f"{budget-total:.2f}")''',[case(['n'],'Bye Bye'),case(['y',80,10,12.5,5,2.5],'50.00')],['while'])
transfer(3,2,'只在正确口令后调用','function','Read run/stop. stop prints Stopped. run calls a function that reads 3 decimal scores and returns their mean. Print the mean to 1 decimal.','读 run/stop。stop 输出 Stopped；run 调用函数读入三项浮点成绩并返回平均值，顶层打印一位小数。',
'''def mean():
    a=float(input())
    b=float(input())
    c=float(input())
    return (a+b+c)/3
choice=input()
if choice=="run":
    print(f"{mean():.1f}")
else:
    print("Stopped")''',[case(['stop'],'Stopped'),case(['run',70,80,90],'80.0')],['function'])
transfer(4,1,'边界随参数传入','function','Function accepts purchase amount and threshold. Below threshold rate is 0; at threshold or above rate is 15%. Return saving. Read amount then threshold; print saving and remaining cost to 2 decimals.','函数接收金额与门槛参数。低于门槛不优惠，达到门槛优惠 15%，函数返回节省额。读金额、门槛，输出节省额和折后额，两位小数、一个空格。',
'''def saving(amount,threshold):
    if amount>=threshold:
        return amount*0.15
    return 0
amount=float(input())
threshold=float(input())
s=saving(amount,threshold)
print(f"{s:.2f} {amount-s:.2f}")''',[case([299.99,300],'0.00 299.99'),case([300,300],'45.00 255.00')],['function','parameter'])
transfer(4,2,'由低至高的 elif 区间','condition','Use if/elif starting with low ranges: score <50 -> retry, <80 -> pass, otherwise distinction. Read a score and print the word.','用从低到高的 if / elif：分数 <50 为 retry，<80 为 pass，否则 distinction。读成绩并输出相应词。',
'''score=float(input())
if score<50:
    print("retry")
elif score<80:
    print("pass")
else:
    print("distinction")''',[case([49.99],'retry'),case([50],'pass'),case([79.99],'pass'),case([80],'distinction')],['elif'])
transfer(5,1,'函数顺序交换仍可用','function','Define total before per_class. per_class takes tutorial and lecture counts, using 1.5 and 1 hour each. total calls per_class and multiplies by class count. Read three integer counts; print 1 decimal.','先定义 total，再定义 per_class；前者调用后者。per_class 接收辅导和讲座次数，用 1.5 和 1 小时计算；total 再乘课程数。按顺序读三项：辅导次数、讲座次数、课程数；输出一位小数。',
'''def total(tutorials,lectures,classes):
    return per_class(tutorials,lectures)*classes
def per_class(tutorials,lectures):
    return tutorials*1.5+lectures
n=int(input())
m=int(input())
c=int(input())
print(f"{total(n,m,c):.1f}")''',[case([3,2,4],'26.0')],['function','nested','parameter'])
transfer(5,2,'函数加循环累计课程','function','hours(t,l) returns 1.5*t+l. A second function calls hours for exactly two courses using for and returns their sum. Read tutorial then lecture counts for each course; print .0f.','hours(t,l) 返回 1.5*t+l；第二个函数用 for 处理两门课并调用 hours，返回总和。每门按顺序输入辅导、讲座次数；顶层用 :.0f 输出。',
'''def hours(t,l):
    return 1.5*t+l
def combined():
    total=0
    for course in range(2):
        t=int(input())
        l=int(input())
        total+=hours(t,l)
    return total
print(f"{combined():.0f}")''',[case([1,1,2,2],'8'),case([3,2,4,1],'14')],['function','nested','for'])
transfer(6,1,'显式短单位转换','function','Use functions to convert cm to m (divide by 100) and m to cm (multiply by 100). Read value and exact cm/m; print value to 2 decimals then target unit. Other units print invalid.','用函数处理 cm↔m，读数值和严格小写单位 cm/m。输出两位小数和目标单位，中间一个空格；其他单位 invalid，不自动转换大小写。',
'''def to_m(x): return x/100
def to_cm(x): return x*100
x=float(input())
unit=input()
if unit=="cm":
    print(f"{to_m(x):.2f} m")
elif unit=="m":
    print(f"{to_cm(x):.2f} cm")
else:
    print("invalid")''',[case([150,'cm'],'1.50 m'),case([2,'m'],'200.00 cm'),case([2,'CM'],'invalid')],['function','parameter'])
transfer(6,2,'转换方向由数值菜单选择','function','Read menu choice first: 1 means miles to kilometers, 2 means reverse. Only for valid choices read distance. Use two functions and print converted value to 3 decimals. Other choices print invalid.','先输入菜单 1/2。1 英里转千米，2 反向；只有选择有效才继续读距离。使用两个转换函数和系数 1.60934，输出三位小数。其他菜单输入输出 invalid。',
'''def km(x): return x*1.60934
def miles(x): return x/1.60934
choice=input()
if choice=="1":
    x=float(input())
    print(f"{km(x):.3f}")
elif choice=="2":
    x=float(input())
    print(f"{miles(x):.3f}")
else:
    print("invalid")''',[case(['1',1],'1.609'),case(['2',1.60934],'1.000'),case(['3'],'invalid')],['function','parameter'])
transfer(7,1,'先删再扩展的名单','list','Create [Zoe,Ada,Max]. Delete the first name, extend with [Ben,Lia], sort in place, print list and length on separate lines.','创建 ["Zoe","Ada","Max"]；先 del 删除首项，再 extend 加入 Ben、Lia，sort 排序；分两行输出列表、长度。操作顺序与原题不同。',
'''a=["Zoe","Ada","Max"]
del a[0]
a.extend(["Ben","Lia"])
a.sort()
print(a)
print(len(a))''',[case([],"['Ada', 'Ben', 'Lia', 'Max']\n4")],['del','extend','sort'])
transfer(7,2,'循环收集不重复电影','list','Read four movie names, append only new names, sort them in place. If more than two remain, delete the last item using del. Print the list.','读 4 个电影名，只 append 新名字，sort 原地排序。如果数量 >2，用 del 删最后一项。打印列表；含重复输入。',
'''movies=[]
for i in range(4):
    title=input()
    if title not in movies:
        movies.append(title)
movies.sort()
if len(movies)>2:
    del movies[len(movies)-1]
print(movies)''',[case(['Z','A','Z','M'],"['A', 'M']"),case(['D','C','B','A'],"['A', 'B', 'C']")],['append','sort','del','for'])
transfer(8,1,'达到成功数才结束的拓展','loop','Explicit extension: ask until 3 unique valid colors red/green/blue are accepted. Use while and a bool function. Duplicates/invalid entries do not increase success count. Print accepted list and total attempts.','额外拓展：直到收集到 3 个不重复有效颜色 red/green/blue 才结束，区别于原题固定 7 次。用 while 和 bool 函数；打印有效颜色列表，再打印总尝试次数，各占一行。',
'''def valid(color,seen):
    return color in ["red","green","blue"] and color not in seen
seen=[]
attempts=0
while len(seen)<3:
    color=input()
    attempts+=1
    if valid(color,seen):
        seen.append(color)
print(seen)
print(attempts)''',[case(['red','red','pink','green','blue'],"['red', 'green', 'blue']\n5")],['function','bool','parameter','while','append'])
transfer(8,2,'按失败原因分别计数','list','Make exactly five attempts for unique valid codes A/B/C, case-sensitive. Bool function validates a code. Print accepted count, duplicate count, invalid count separated by spaces.','恰好 5 次输入有效代码 A/B/C，区分大小写。bool 函数验证有效且未重复。分别计数成功、重复、无效，最后按该顺序输出三个整数，用空格分隔。',
'''def valid(value,seen):
    return value in ["A","B","C"] and value not in seen
seen=[]
duplicate=0
invalid=0
for i in range(5):
    value=input()
    if valid(value,seen):
        seen.append(value)
    elif value in seen:
        duplicate+=1
    else:
        invalid+=1
print(len(seen),duplicate,invalid)''',[case(['A','A','x','B','a'],'2 1 2'),case(['A','B','C','C','B'],'3 2 0')],['function','bool','for','append'])
transfer(9,1,'只画偶数边形','turtle','Use a parameterized polygon function, side 180/n, angle 360/n. Use range with step 2 to draw 4,6,8,10,12 sides, clockwise, separated with pen-up setpos and colors.','带参数的多边形函数，边长 180/n，转角 360/n。range 步长 2，顺时针画 4、6、8、10、12 边形；抬笔 setpos 分离，设置颜色与填充。',
POLYGON.replace('range(3, 13)','range(4, 13, 2)').replace('t.left(360 / n)','t.right(360 / n)').replace('((n-3) % 5) * 120 - 260, ((n-3) // 5) * 140 - 100','(n-4)*70-280, 0'),[case([],None,ns=[4,6,8,10,12])],['function','parameter','for'],validator='polygons')
transfer(9,2,'用户选择图形，while 重复布局','turtle','Read a side count n (3..8). A parameterized polygon function uses side 180/n and angle 360/n. Use while to draw three copies on different positions. Set colors, fill, pen-up movement.','读边数 n（输入限定 3～8）。带参数函数用 180/n 与 360/n；用 while 在不同位置画 3 个副本。设置线条与填充颜色，移动时抬笔。',
'''import turtle as t
def polygon(n):
    t.begin_fill()
    for i in range(n):
        t.forward(180/n)
        t.left(360/n)
    t.end_fill()
n=int(input())
t.pencolor("navy")
t.fillcolor("lightblue")
i=0
while i<3:
    t.penup()
    t.setpos(i*140-180,0)
    t.pendown()
    polygon(n)
    i+=1''',[case([3],None,ns=[3,3,3]),case([8],None,ns=[8,8,8])],['function','parameter','while'],validator='polygons')
transfer(10,1,'用户输入乘数与上下限','loop','Read multiplier, high and low (high >= low). Use for to print a descending table, inclusive, in the form 5 x 4 = 20.','按顺序读乘数、上界、下界（上界≥下界）。用 for 输出包含两端的倒序乘法表，格式如 5 x 4 = 20。',
'''multiplier=int(input())
high=int(input())
low=int(input())
for n in range(high,low-1,-1):
    print(f"{n} x {multiplier} = {n*multiplier}")''',[case([4,5,3],'5 x 4 = 20\n4 x 4 = 16\n3 x 4 = 12'),case([2,1,1],'1 x 2 = 2')],['for'])
transfer(10,2,'倒序隔项与累加','loop','Use while to print products of 9,7,5,3,1 times 6, one per line. Then print their sum on the last line.','用 while 从 9 倒序每次减 2，分行打印每项乘 6 的结果，最后一行输出所有结果之和。既有步长也有累加。',
'''n=9
total=0
while n>=1:
    value=n*6
    print(value)
    total+=value
    n-=2
print(total)''',[case([],'54\n42\n30\n18\n6\n150')],['while'])

LESSONS=[
('input','01','输入与表达式','从文字到数字',
['字符串是文字，如 "12"；整数是 12；浮点数是 12.5。变量为值命名，带引号的变量名只是文字。','input() 总返回字符串。购买数量通常用 int(input())；金额与距离通常用 float(input())。int("2.5") 会报错。','括号改变运算顺序。折扣率 10% 在计算中写 0.10；原价−折扣金额=折后金额。引号包住字符串；if/def/循环末尾要冒号，代码块要缩进。'],
'n = int(input("数量："))\nprice = 22.50\noriginal = n * price\nsaving = original * 0.10\nprint(original - saving)', ['S01','D01','P01','T031'],[1,2,3]),
('format','02','输出格式','让结果清楚、准确',
['f-string 前缀 f 让花括号中的表达式求值并插入；引号定义字符串范围。$ 和 % 在字符串中是普通字符。','{value:.2f} 用定点格式显示两位小数；{value:.0f} 显示零位小数并舍入，不等于直接截断。二进制浮点与恰好一半的舍入需注意；例如 2.5 的 :.0f 是 2。','print("Price Qty Total") 可作表头，下一行按同样顺序分列。折扣金额不是折后金额；列标签要表达正确数值。'],
'amount = 345.67\nsaving = amount * 0.05\nprint("Purchase Amount  Discount  Total")\nprint(f"${amount:.2f}  ${saving:.2f}  ${amount-saving:.2f}")',['S08','D05','P04','T041'],[1,2,4,5,6]),
('condition','03','条件判断','把边界写进逻辑',
['= 把值赋给变量，== 比较是否相等。字符串相等区分大小写；原题未要求宽容处理时，不擅自 lower()。','if / elif / else 依次判断，只执行第一个真分支。金额分档用 >=1000、>=500、>=200 的高到低顺序；也可写明低到高的互斥区间。','> 与 >= 的差别在边界，< 与 <= 同理。不同分支可输出不同内容。原题没有指定的负数、零或非法数字输入，不能偷偷变成原题测试；拓展题会明确写输入范围。'],
'amount = float(input())\nif amount >= 1000:\n    rate = 0.20\nelif amount >= 500:\n    rate = 0.10\nelse:\n    rate = 0\nprint(rate)',['S12','D07','P05','T042'],[1,2,3,4,6,8]),
('function','04','函数与执行顺序','定义一次，调用多次',
['def 定义函数，函数名(实参) 才调用它。定义中的变量是形参，调用时给出的值是实参；函数内部变量通常是局部变量。','return 把结果交给调用者并结束函数；print 只产生输出。没有 return 时返回 None。检查函数可返回 True 或 False。','函数可调用另一个函数。被调用函数可以在调用者的 def 后定义，关键是实际调用发生时名称已经定义。附件第 5 题的定义顺序建议不能作为 Python 的普遍规则。','通过用户输入选择不同函数；数字参数与返回值可参与后续计算。'],
'def total(n):\n    return per_class() * n\n\ndef per_class():\n    return 10 * 1.5 + 7\n\nprint(total(3))',['S17','D10','P09','T051'],[5,6,8,9]),
('list','05','列表与去重','有顺序的一组值',
['列表用 [] 创建。索引从 0 开始；len(items) 返回长度，末项索引为 len(items)−1。','append(x) 添加一个元素；extend([a,b]) 添加多个元素。sort() 原地排序且返回 None，不要写 items = items.sort()。del items[i] 按索引删除。','in / not in 用来判断成员。用 not in 再 append 可防止重复。列表可与函数、循环、计数结合；固定尝试次数和成功加入数量须分开记录。'],
'movies = ["Up", "Coco", "Dune"]\nmovies.extend(["Soul", "Arrival", "Jaws"])\nmovies.sort()\ndel movies[2]\nprint(movies)',['S22','D14','P12','T071'],[7,8]),
('loop','06','for 与 while','追踪开始、条件和更新',
['range(start,stop,step) 包含起点、不包含终点。倒序 10～1 用 range(10,0,-1)，step 必须与方向一致。','while 需要初始值、继续条件、更新。例如 n=10，while n>=1，循环末尾 n-=1。忘记更新会死循环，网站可以停止工作线程。','累加器从 0 开始加数值；计数器按事件次数加 1。乘积从 1 开始。固定 7 次机会不同于收集 7 个有效答案。','同一任务可用 for 和 while 实现；附件第 10 题必须分别练习这两种写法。'],
'n = 3\nwhile n >= 1:\n    print(f"{n} times 9 is {n*9}")\n    n -= 1',['S26','D18','P14','T102'],[2,3,8,9,10]),
('turtle','07','turtle 综合绘图','从指令到几何',
['forward/backward 前进或后退，left/right 改变朝向。setpos(x,y) 改变位置；先 penup 再移动，到达后 pendown，避免连线。','pencolor 设置线色，fillcolor 设置填色；begin_fill 开始记录，end_fill 结束并填充。','多边形函数接收边数 n，外转角 360/n；本次作业指定边长 180/n。range(3,13) 覆盖 3～12。图形位置需要留出间距。','本网站在真实 Python 中运行这些指令，通过 SVG 兼容层展示，不使用桌面 Tk GUI。支持本课列出的指令；动画、鼠标事件、多只独立 turtle 和完整标准库 turtle API 不支持。'],
'import turtle as t\nt.penup()\nt.setpos(0,0)\nt.pendown()\nt.pencolor("navy")\nt.fillcolor("lightblue")\nt.begin_fill()\nfor side in range(3):\n    t.forward(180/3)\n    t.left(360/3)\nt.end_fill()',['S29','D20','P17','T091'],[9]),
]
lessons=[]
for topic,num,title,subtitle,paragraphs,example,path,hws in LESSONS:
    lessons.append(dict(id=topic,num=num,title=title,subtitle=subtitle,paragraphs=paragraphs,example=example,path=path,homeworks=hws,completion=example.replace('180/3','____').replace('int(input("数量："))','____').replace(':.2f','____',1) if topic in ('turtle','input','format') else example.replace('>= 1000','____').replace('per_class() * n','____').replace('movies.extend','____').replace('n -= 1','____')))

mapping=[]
for i in range(1,11):
    h=next(q for q in questions if q['id']==f'H{i:02}')
    topics=[l['id'] for l in lessons if i in l['homeworks']]
    relevant=[q['id'] for q in questions if q['kind'] in ['short','debug','program'] and q['topic'] in topics]
    mapping.append(dict(number=i,title=h['title'],source=h['source'],lessons=topics,specials=relevant,transfers=[f'T{i:02}1',f'T{i:02}2'],homework=h['id'],notes=h['zh']))
assert len(questions)==100
assert len({q['id'] for q in questions})==100
counts={k:sum(q['kind']==k for q in questions) for k in ['short','debug','program','transfer','homework']}
content=dict(questions=questions,lessons=lessons,mapping=mapping,counts=counts,version='2026-10-08-v1',sourceFile='PS- National Holiday HW.zip',verified=False,sourceNotes=['压缩包中 10 张作业图片已逐张阅读，另有 file name.jpg 命名示例。','第 9 题引用的图例未包含在上传图片中；按文字要求验证，不假定布局与配色。','第 6 题正文和示例单位大小写不同；练习显式采用示例 Kilometers/Miles，不擅自判错未指定输入。','file name.jpg 示例为 z1234444_01_the_lab_depot.py。未提供你的学号，不生成或假定学号。','学习与拓展题的精确输出约定会写在题面；原题输入提示文本、未规定负数/零、大小写扩展不作为隐藏判错条件。'])
(ROOT/'web/content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Authored {len(questions)} exercises: {counts}. Verification status is recorded separately by the test run.')
# Explicit return-value requirements: these exercises ask for numeric returns.
for q in questions:
    if q['id'] in ['H05','H06','D09','D11','P07','P09','P20','T011','T022','T032','T041','T051','T052','T061','T062']:
        q['required'].append('numeric_return')
(ROOT/'web/content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2),encoding='utf-8')
next(q for q in questions if q['id']=='H05')['requiredNames']=['hours_classes','total_hours']
(ROOT/'web/content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2),encoding='utf-8')
english_contracts={
'H01':'Platform output convention based on the example: show the final amount with a dollar sign and exactly two decimal places. Prompt wording is not graded.',
'H02':'Platform output convention: include a dollar sign and exactly two decimals for the total. For 1–5 items include the discount followed by %; above 5 do not include a percentage. Inputs tested are positive integer quantities.',
'H04':'Use the headers Purchase Amount, Discount, Total, then a new line with those three amounts in that order, each with $ and two decimals. Alignment spaces may vary.',
'H05':'The supplied function names hours_classes and total_hours must be used. Print the exact sentence Total Hours: <rounded integer>. (with a period). Defining the called function first is a suggestion; the actual requirement is that names exist when called.',
'H06':'Platform convention: accept exact units Kilometers and Miles from the example. The source prose and example differ in capitalization, so lowercase inputs are not hidden tests. Print the converted value with two decimals and the target unit miles/kilometers. Invalid-unit messages must contain invalid.',
'H08':'Use the capitalized English names Monday through Sunday. The screenshot rejects wednesday. Print the accepted list and finish with the accepted count. Explain duplicates using already or duplicate; explain invalid days using invalid or not a day. These keyword conventions make free-form messages machine-checkable.',
'H09':'For this browser exercise use begin_fill/end_fill for each polygon. The image refers to an output diagram, but the diagram is absent; colors and layout are your choice. The checker conservatively requires non-overlapping bounding boxes.'
}
for q in questions:
    if q['id'] in english_contracts: q['en']+=' '+english_contracts[q['id']]
(ROOT/'web/content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2),encoding='utf-8')
