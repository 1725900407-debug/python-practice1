let runtime;
async function initialize() {
  if (!runtime) runtime = (async () => {
    importScripts('./vendor/pyodide.js');
    const py = await loadPyodide({indexURL:new URL('./vendor/',self.location.href).href});
    const response = await fetch('./engine.py');
    if (!response.ok) throw new Error('Python 判题引擎加载失败');
    py.runPython(await response.text());
    return py;
  })();
  return runtime;
}
self.onmessage = async ({data}) => {
  try {
    const py = await initialize();
    if (data.action === 'init') {self.postMessage({id:data.id,ready:true});return;}
    py.globals.set('_request_json', JSON.stringify(data.payload));
    const result = py.runPython('json.dumps(handle(json.loads(_request_json)), ensure_ascii=False)');
    self.postMessage({id:data.id,result:JSON.parse(result)});
  } catch (error) {self.postMessage({id:data.id,error:String(error.message || error)});}
};
