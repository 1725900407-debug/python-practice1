# Python 小步练习室

面向「PS- National Holiday HW.zip」10 道 Python 作业的中文互动学习网站。

已实现 7 个知识专题和 100 道练习：30 短题、20 修错、20 单知识点编程、20 综合迁移（每类作业两题）、10 作业对应题。完整对应关系见 [覆盖报告](docs/coverage.md)，附件原要求与平台约定的区别见 [范围与限制](docs/requirements.md)。

## 启动

需要 Python 3、curl、sha256sum。首次准备会以正常 TLS 下载固定版本 Pyodide 到忽略目录 `web/vendor`，并核对仓库记录的 SHA-256；不需要 pip/npm 依赖。

```bash
bash setup.sh
python3 server.py --port 8000
```

通过可访问本机 8000 端口的浏览器打开网站。开发服务默认绑定 `0.0.0.0`；若只需本机访问，可加 `--host 127.0.0.1`。不要直接以 file:// 打开 HTML。云环境界面是否提供端口转发由平台决定；仓库不自动创建公开预览地址。

## 实现

- 浏览器 Web Worker 中的真实 CPython/Pyodide 执行；强制停止后可重新运行。学习者代码不在静态服务器上执行。
- AST 与实际执行联合检查函数、循环、extend/sort/del；检查输入次数、分支边界与金额格式。
- 支持作业要求的 turtle 指令，SVG 展示图形；不是完整桌面 Tk turtle。
- 学习/英文模拟作业两种模式，逐层提示、答案查看记录、同知识点新题要求。
- 真实错题诊断、草稿保存、错题本、站内证据计数、次日与三日复测；手机适配。
- 数据保存在当前浏览器 localStorage，可导入/导出；没有账户或跨设备自动同步。

## 核验

```bash
python3 -m unittest discover -s tests -v
```

当前参考程序已在本机 Python 和 Chromium/Pyodide 上实际执行。70 道编程题共 140 组运行用例，20 份故障样例应失败。30 道短题逐项核对答案与概念说明。核验报告在 `web/verification.json`，内容变更需要重新核验，不能沿用旧证据。

可选浏览器回归（需要开发验证用的 Playwright 和 Chromium，应用本身不依赖它们；先启动服务）：

```bash
python3 tests/browser_runtime.py
python3 tests/browser_ui.py
python3 tools/verify.py
```

AST 判题覆盖常见初学者写法；任意 Python 的语义不能被完整自动证明。复杂间接操作需人工核对。本系统用于练习反馈，不保证考试成绩，也不作为防作弊考试系统。
