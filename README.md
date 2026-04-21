# RXscientist

RXscientist is a new project for end-to-end AI-assisted research execution.
It provides a practical command-line research copilot that can plan tasks, call tools, run multi-step workflows, and keep long-term session memory for iterative scientific work.

## What RXscientist does

- Multi-agent workflow for planning, research, coding, analysis, and writing.
- CLI and TUI interfaces for interactive local work.
- MCP tool integration for extending external capabilities.
- Multi-channel architecture (for example Telegram, Slack, Feishu, WeChat, Discord, QQ).
- Persistent thread/session state to continue research over time.

## Quick start (install then run)

Start the CLI with **`rxsci`** after installing the **`Rxscientist`** Python package (see `pyproject.toml` — PyPI name is **`Rxscientist`**, CLI commands are **`rxsci`** / **`Rxscientist`**).

### Option A — From PyPI

After a release is published to PyPI:

```bash
pip install Rxscientist
rxsci
```

```bash
uv tool install Rxscientist
rxsci
```

If install fails with *package not found*, maintainers may not have uploaded yet — use Options B–D.

### Option B — Install from Git (recommended if PyPI is empty)

```bash
uv tool install "git+https://github.com/Ar1haraNaN7mI/RainyXscientist.git"
rxsci
```

To pin a branch or tag:

```bash
uv tool install "git+https://github.com/Ar1haraNaN7mI/RainyXscientist.git@main"
```

### Option C — Clone repository and run in a project environment

```bash
git clone https://github.com/Ar1haraNaN7mI/RainyXscientist.git
cd RainyXscientist
uv sync
uv run rxsci
```

After `uv sync`, you can also activate the virtualenv (`.venv`) and run `rxsci` directly.

### Option D — Install from GitHub Release wheel (offline-friendly)

Each push to `main` publishes **wheel / sdist** assets under [Releases](https://github.com/Ar1haraNaN7mI/RainyXscientist/releases). There is **no standalone `.exe`** in those assets (they are Python packages).

1. Open the latest Release and download **`Rxscientist-*-py3-none-any.whl`** (and optionally the `.tar.gz` source distribution).
2. Install with pip (use the same Python where you want `rxsci`):

```bash
pip install "C:\path\to\Rxscientist-0.0.8-py3-none-any.whl"
rxsci
```

Replace the path and version string with the file you actually downloaded.

### Publishing to PyPI (maintainers)

This repo includes **`.github/workflows/publish-pypi.yml`**. One-time setup:

1. Create accounts on [pypi.org](https://pypi.org) (and optionally [test.pypi.org](https://test.pypi.org) for trials).
2. Confirm the project name **`Rxscientist`** is available on PyPI (change `[project] name` in `pyproject.toml` if it is taken).
3. On PyPI → **Publishing** → **Add a new pending publisher** → choose **GitHub** → organization/user **`Ar1haraNaN7mI`**, repository **`RainyXscientist`**, workflow **`publish-pypi.yml`**, PyPI project **`Rxscientist`** (must match `pyproject.toml`).
4. Bump **`version`** in `pyproject.toml`, commit, create and push an annotated tag **`vX.Y.Z`** matching that version (example: version `0.0.9` → tag **`v0.0.9`**). The workflow runs `uv build` and uploads **`dist/*`** to PyPI.

Manual upload (API token):

```bash
uv build
uv publish --token <pypi-api-token>
```

Use a token with **Entire account** or **Project-scoped** upload scope from PyPI account settings (do not commit tokens).

---

## 中文：下载与启动说明（Windows）

### PyPI 安装（推荐，在维护者已上传之后）

```powershell
pip install Rxscientist
rxsci
```

### 为什么有时会提示找不到包？

- **尚未上传到 PyPI**：会提示 *was not found in the package registry*，请先使用下面的 **Git / Release / 源码** 方式。
- **包名**：PyPI 上的分发名为 **`Rxscientist`**（区分大小写以索引为准）；安装后终端命令仍为 **`rxsci`**。

### 本项目有没有官方 `.exe`？

- **GitHub Actions 当前只构建并上传 `.whl` / `.tar.gz`**，**不提供一键绿色版 `.exe`**。
- 启动方式是安装 Python 包后使用控制台命令 **`rxsci`**（安装脚本会在 Python 的 `Scripts` 目录生成 `rxsci.exe`）。

### Windows 推荐流程

**1）已安装 Python 3.11+ 与 uv**

在 PowerShell 或 CMD 中：

```powershell
uv tool install "git+https://github.com/Ar1haraNaN7mI/RainyXscientist.git"
rxsci
```

若提示找不到 `rxsci`，请将 uv 安装的 **tools 目录**加入 `PATH`，或使用 Python 模块方式：

```powershell
python -m Rxscientist
```

（与控制台脚本 `rxsci` 等价，均调用同一 CLI 入口。）

**2）下载 Release 里的 wheel 再安装**

1. 打开：<https://github.com/Ar1haraNaN7mI/RainyXscientist/releases>
2. 在最新 Release 的 **Assets** 中下载 **`Rxscientist-*-py3-none-any.whl`**
3. 在下载目录执行（版本号按文件名修改）：

```powershell
py -3.12 -m pip install .\Rxscientist-0.0.8-py3-none-any.whl
rxsci
```

若仍找不到命令，直接使用模块入口：

```powershell
py -3.12 -m Rxscientist --help
```

安装成功后，`rxsci` 一般位于：

`%LOCALAPPDATA%\Programs\Python\Python3xx\Scripts\rxsci.exe`

或当前虚拟环境的：

`.venv\Scripts\rxsci.exe`

把对应 **`Scripts` 目录** 加入系统 **PATH**，即可在任意目录运行 `rxsci`。

**3）克隆源码开发/本地运行**

```powershell
git clone https://github.com/Ar1haraNaN7mI/RainyXscientist.git
cd RainyXscientist
uv sync
uv run rxsci
```

### 自行打包成独立 `.exe`（可选）

仓库未内置官方单文件 exe。若需要分发无 Python 环境的机器，可自行使用 **PyInstaller** 等对入口 **`Rainscientist.cli:main`**（包名 **`rxsci`**）打包；需在本地解决依赖与体积问题，此处不展开。

### 维护者：如何把项目上传到 PyPI？

1. **账号**：在 [pypi.org](https://pypi.org) 注册并完成邮箱验证。
2. **项目名**：打开 <https://pypi.org/project/Rxscientist/> ，若已被占用需在 `pyproject.toml` 里修改 **`[project] name`**（例如换成唯一名称）。
3. **可信发布（推荐，无需把 token 放进仓库）**  
   - PyPI：**Account settings → Publishing → Add pending publisher**  
   - 选择 GitHub：**Owner** `Ar1haraNaN7mI`，**Repository** `RainyXscientist`，**Workflow** `publish-pypi.yml`，**PyPI project name** `Rxscientist`（须与 `pyproject.toml` 一致）。  
   - 详见官方说明：<https://docs.pypi.org/trusted-publishers/>
4. **发版**：在 `pyproject.toml` 里提高 **`version`**，提交后打标签 **`v` + 语义化版本号**（例如版本 `0.0.9` → 标签 **`v0.0.9`**），推送标签将触发 **`.github/workflows/publish-pypi.yml`**，自动 **`uv build`** 并上传到 PyPI。  
   也可在 GitHub **Actions → Publish PyPI → Run workflow** 手动运行（同样需要已配置可信发布）。
5. **本地用令牌上传（备用）**：在 PyPI 账户设置里创建 **API token**，切勿提交到 Git：

```bash
uv build
uv publish --token <粘贴token>
```

同一版本号不能重复上传；每次发布前务必 **递增 `version`**。

---

## Why this project

RXscientist focuses on turning fragmented prompts into a repeatable research loop:
question intake, task decomposition, evidence collection, implementation, review, and refinement.
The goal is to make one local agent runtime usable for both exploratory research and engineering-heavy scientific tasks.

## Project status

This repository is being positioned as the new RXscientist project.
Documentation and examples are intentionally being simplified and refreshed.
