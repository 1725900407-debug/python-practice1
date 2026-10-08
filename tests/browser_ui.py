"""User-facing workflows in a real browser. Server must run on port 8000."""
import json
import hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
qs={q['id']:q for q in json.loads((ROOT/'web/content.json').read_text())['questions']}
checks=[]
def check(name, condition=True):
    assert condition,name
    checks.append(name)
KEY='python-little-steps-v1'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=b.new_page(viewport={'width':1440,'height':1000});page.set_default_timeout(30000)
    errors=[];page.on('pageerror',lambda e: errors.append(str(e)))
    page.goto('http://127.0.0.1:8000/');page.locator('h1').wait_for()
    check('home renders and has no runtime exception',not errors)
    def go(id):
        page.goto('http://127.0.0.1:8000/#question/'+id)
        page.locator('#code' if qs[id]['kind']!='short' else '#submit-choice').wait_for()
    def saved(): return page.evaluate('(key)=>JSON.parse(localStorage.getItem(key))',KEY)
    def submit(id):
        before=len(saved().get('records',{}).get(id,{}).get('attempts',[]))
        page.locator('#code').fill(qs[id]['solution'])
        if qs[id].get('dual'): page.locator('#code-alt').fill(qs[id]['solutionAlt'])
        page.locator('#submit-code').click()
        page.wait_for_function('([key,id,n])=>JSON.parse(localStorage.getItem(key)).records[id].attempts.length>n',arg=[KEY,id,before],timeout=90000)
        check(id+' real browser grade', '所有自动测试通过' in page.locator('#result').inner_text())
    go('P01');page.locator('#code').fill('print(input()+2)');page.locator('#submit-code').click()
    page.locator('#result h3').wait_for(timeout=90000)
    check('type feedback', '类型错误' in page.locator('#result').inner_text())
    page.reload();page.locator('#code').wait_for();check('draft restoration',page.locator('#code').input_value()=='print(input()+2)')
    submit('P01');check('unassisted attempt recorded',saved()['records']['P01']['attempts'][-1]['independent'])
    check('two delayed reviews queued',len([r for r in saved()['reviews'] if r['qid']=='P01'])==2)
    page.goto('http://127.0.0.1:8000/#wrongbook');page.locator('h1').wait_for()
    page.locator('.attempt').first.wait_for()
    check('wrongbook contains actual failed code','print(input()+2)' in page.locator('#app').text_content())
    go('P04');page.locator('#mode-exam').click()
    check('exam hides hints before submission',page.locator('#show-hint').count()==0)
    check('exam hides Chinese prompt',page.locator('.chinese').count()==0)
    submit('P04');check('exam reveals help after submission',page.locator('#show-hint').count()==1)
    page.locator('#mode-learn').click();go('P02')
    page.locator('#show-hint').click();first=page.locator('#help-content').inner_text()
    check('hint level1 only',qs['P02']['hints'][0] in first and qs['P02']['hints'][1] not in first)
    page.locator('#show-hint').click();check('hint level2',qs['P02']['hints'][1] in page.locator('#help-content').inner_text())
    page.locator('#show-solution').click();submit('P02')
    check('solution exposure prevents independent credit',not saved()['records']['P02']['attempts'][-1]['independent'])
    page.reload();page.locator('#code').wait_for();check('assistance persists after reload',saved()['records']['P02']['seenSolution'])
    check('new-topic challenge gate persists',bool(saved()['pendingTopics'].get('input')))
    go('H03');submit('H03')
    check('new independent variant clears answer gate',not saved()['pendingTopics'].get('input'))
    go('P03');page.locator('#code').fill('import time\ntime.sleep(60)');page.locator('#run-code').click()
    page.wait_for_timeout(300);page.locator('#stop-code').click()
    page.locator('#result').get_by_text('运行已结束',exact=False).wait_for()
    check('Stop terminates worker during blocking Python','运行已停止' in page.locator('#result').inner_text())
    page.locator('#code').fill('print("worker restarted")');page.locator('#run-code').click()
    page.locator('#result .output').wait_for(timeout=90000)
    check('worker restarts','worker restarted' in page.locator('#result').inner_text())
    go('H09');submit('H09');check('ten SVG polygons',page.locator('#drawing-target polygon').count()==10)
    go('H10');submit('H10');check('both loops verified','逐项测试 · 2 / 2' in page.locator('#result').inner_text())
    # Make both review stages overdue; first review must defer the third-day stage.
    page.evaluate('''key=>{const s=JSON.parse(localStorage.getItem(key)); for(const r of s.reviews) if(r.qid==='P01') {r.at=Date.now()-1000;r.done=null;} localStorage.setItem(key,JSON.stringify(s));}''',KEY)
    page.reload();go('P01');check('delayed review starts blank',page.locator('#code').input_value()=='')
    submit('P01');rs=[r for r in saved()['reviews'] if r['qid']=='P01']
    check('overdue stages are not completed together',bool(next(r for r in rs if r['stage']==1)['done']) and not next(r for r in rs if r['stage']==3)['done'])
    check('third-day review postponed after late day1',next(r for r in rs if r['stage']==3)['at']>page.evaluate('Date.now()')+86400000)
    page.goto('http://127.0.0.1:8000/#coverage');page.locator('.coverage-card').first.wait_for()
    check('10 original mappings and20 transfer links',page.locator('.coverage-card').count()==10 and page.locator('.coverage-card a[href*="question/T"]').count()==20)
    page.goto('http://127.0.0.1:8000/#practice');page.locator('#kind-filter').select_option('homework')
    check('100-item filtering',page.locator('.question-row').count()==10)
    page.goto('http://127.0.0.1:8000/#diagnostic');page.locator('#start-diagnostic').click()
    for i,id in enumerate(['S01','S08','S12','S17','S23','S28']):
        chosen=(qs[id]['solution']+1)%3 if i==0 else qs[id]['solution']
        page.locator(f'input[name="diagnostic-choice"][value="{chosen}"]').check()
        page.locator('#diagnostic-next').click()
    check('diagnostic records actual5/6 and wrong topic',saved()['diagnostic']['correct']==5 and saved()['diagnostic']['weak']==['input'])
    page.set_viewport_size({'width':375,'height':812});go('H10')
    check('375px question no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    page.goto('http://127.0.0.1:8000/#home');page.locator('h1').wait_for()
    check('375px home no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    check('no uncaught JS exception',not errors)
    (ROOT/'.local').mkdir(exist_ok=True)
    hashes={name:hashlib.sha256((ROOT/'web'/name).read_bytes()).hexdigest() for name in ['index.html','styles.css','app.js','worker.js']}
    (ROOT/'.local/browser-ui.json').write_text(json.dumps({'passed':True,'checks':checks,'count':len(checks),'assetHashes':hashes},ensure_ascii=False,indent=2))
    print(json.dumps({'passed':True,'checks':len(checks)},ensure_ascii=False),flush=True)
    b.close()
