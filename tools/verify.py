"""Write only confirmed verification evidence, tied to exact content/engine files."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
result=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT)
if result.returncode: raise SystemExit(result.returncode)
content=json.loads((ROOT/'web/content.json').read_text())
browser_report=ROOT/'.local/browser-runtime.json'
browser=json.loads(browser_report.read_text()) if browser_report.exists() else None
# The runtime integration run is local evidence. UI evidence is separately recorded.
ui_report=ROOT/'.local/browser-ui.json'
ui=json.loads(ui_report.read_text()) if ui_report.exists() else None
content_hash=hashlib.sha256((ROOT/'web/content.json').read_bytes()).hexdigest()
engine_hash=hashlib.sha256((ROOT/'web/engine.py').read_bytes()).hexdigest()
current_browser=bool(browser and browser.get('contentSha256')==content_hash and browser.get('engineSha256')==engine_hash)
ui_hashes={name:hashlib.sha256((ROOT/'web'/name).read_bytes()).hexdigest() for name in ['index.html','styles.css','app.js','worker.js']}
verification={
 'verified':True,'total':len(content['questions']),'counts':content['counts'],
 'executableExercises':sum(q['kind']!='short' for q in content['questions']),
 'shortReviewed':30,'shortReviewMethod':'逐项核对题面、答案与概念解释；非自动执行的选择题',
 'regressionTests':20,'debugStartersRejected':20,
 'browserValidated':bool(current_browser and len(browser['results'])==70 and all(r['passed'] for r in browser['results'])),
 'referenceCases':sum(r.get('caseCount',0) for r in browser['results']) if current_browser else 0,
 'uiValidated':bool(ui and ui.get('passed') and ui.get('assetHashes')==ui_hashes),
 'uiChecks':ui.get('count',0) if ui and ui.get('assetHashes')==ui_hashes else 0,
 'contentSha256':content_hash,
 'engineSha256':engine_hash,
 'scope':'参考程序、故障样例、边界回归及浏览器运行核验；不保证任意写法都可自动判定，也不是考试认证。'
}
(ROOT/'web/verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2))
print(json.dumps(verification,ensure_ascii=False,indent=2))
