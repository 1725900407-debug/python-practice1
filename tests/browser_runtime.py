"""Actual Chromium + WebAssembly Python integration. Requires local server on 8000."""
import json
import hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=r'''
async () => {
  const origin=location.origin;
  const workerSource = `
    importScripts('${origin}/vendor/pyodide.js');
    (async()=>{
      const py=await loadPyodide({indexURL:'${origin}/vendor/'});
      py.runPython(await (await fetch('${origin}/engine.py')).text());
      self.postMessage({ready:true});
      onmessage=({data})=>{
        py.globals.set('_payload', JSON.stringify(data));
        const result=py.runPython('json.dumps(handle(json.loads(_payload)))');
        self.postMessage(JSON.parse(result));
      };
    })().catch(e=>self.postMessage({loadError:String(e)}));`;
  const worker=new Worker(URL.createObjectURL(new Blob([workerSource],{type:'application/javascript'})));
  function next() { return new Promise((resolve,reject)=> {worker.onmessage=e=>resolve(e.data); worker.onerror=e=>reject(Error(e.message));}); }
  const loaded=await next();
  if(!loaded.ready) throw Error(JSON.stringify(loaded));
  const content=await (await fetch('/content.json')).json();
  const results=[];
  for(const q of content.questions.filter(q=>q.kind!=='short')) {
    const resultP=next();
    worker.postMessage({action:'grade',code:q.solution,codeAlt:q.solutionAlt||'',question:q});
    const result=await resultP;
    results.push({id:q.id,passed:result.passed,caseCount:result.cases?.length,issues:result.issues,manual:result.manual});
  }
  const infiniteP=next();
  worker.postMessage({action:'run',code:'while True:\n    pass'});
  const infinite=await infiniteP;
  worker.terminate();
  return {results,infinite,loaded};
}
'''
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=b.new_page()
    page.set_default_timeout(90000)
    page.goto('http://127.0.0.1:8000/content.json')
    result=page.evaluate(SCRIPT)
    result['contentSha256']=hashlib.sha256((ROOT/'web/content.json').read_bytes()).hexdigest()
    result['engineSha256']=hashlib.sha256((ROOT/'web/engine.py').read_bytes()).hexdigest()
    failures=[x for x in result['results'] if not x['passed']]
    print(json.dumps(dict(exercises=len(result['results']),cases=sum(x['caseCount'] or 0 for x in result['results']),failures=failures,infinite=result['infinite']['error']),ensure_ascii=False),flush=True)
    (ROOT/'.local').mkdir(exist_ok=True)
    (ROOT/'.local/browser-runtime.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    assert not failures, failures
    assert result['infinite']['error']['type']=='LimitError'
    b.close()
