# RainyXscientist

RainyXscientist is a new project for end-to-end AI-assisted research execution.
It provides a practical command-line research copilot that can plan tasks, call tools, run multi-step workflows, and keep long-term session memory for iterative scientific work.

## What RainyXscientist does

- Multi-agent workflow for planning, research, coding, analysis, and writing.
- CLI and TUI interfaces for interactive local work.
- MCP tool integration for extending external capabilities.
- Multi-channel architecture (for example Telegram, Slack, Feishu, WeChat, Discord, QQ).
- Persistent thread/session state to continue research over time.

## Complete tutorial: download → configure → launch

Follow these steps once on a clean machine. **PyPI package name:** `Rxscientist` · **CLI commands:** `rxsci` / `Rxscientist`.

### Step 1 — Prerequisites

| Requirement | Notes |
|-------------|--------|
| **Python** | **3.11+** (see `requires-python` in `pyproject.toml`). |
| **Installer** | `pip` (bundled with Python) or **`uv`** ([docs.astral.sh/uv](https://docs.astral.sh/uv/)). |
| **Network** | Needed to install packages and call LLM / search APIs. |
| **API key** | Default stack uses **Anthropic** (`ANTHROPIC_API_KEY`). Other providers need their own keys (see Step 3). |

Check Python: `python --version` or `py -3.12 --version` on Windows.

### Step 2 — Install the package (choose one path)

**A — PyPI (simplest once a release exists)**

```bash
pip install Rxscientist
```

Or with uv:

```bash
uv tool install Rxscientist
```

If PyPI returns *package not found*, use B–D until maintainers publish.

**B — Install directly from Git** (always up to date with `main`)

```bash
uv tool install "git+https://github.com/Ar1haraNaN7mI/RainyXscientist.git"
```

Pin a branch/tag if needed:

```bash
uv tool install "git+https://github.com/Ar1haraNaN7mI/RainyXscientist.git@main"
```

**C — Clone and run in a dev environment**

```bash
git clone https://github.com/Ar1haraNaN7mI/RainyXscientist.git
cd RainyXscientist
uv sync
uv run rxsci
```

After `uv sync`, activate `.venv` if you prefer and run `rxsci` from that environment.

**D — Offline / air-gapped: wheel from GitHub Releases**

1. Open [Releases](https://github.com/Ar1haraNaN7mI/RainyXscientist/releases) and download **`Rxscientist-*-py3-none-any.whl`** (source `.tar.gz` is optional).
2. Install with the Python you plan to use:

```bash
pip install /path/to/Rxscientist-*-py3-none-any.whl
```

Replace the filename with the asset you downloaded.

### Step 3 — Configure API keys and defaults

Configuration **priority** (highest first): **CLI flags** → **environment variables** → **`config.yaml`** → **built-in defaults**.

**Recommended first-time setup — interactive wizard**

```bash
rxsci onboard
```

This walks you through API keys and basic options (you can skip validation flags if needed).

**Environment variables**

Set at least the key for your provider. Defaults in code target **Anthropic** unless you change `provider` / `model` in config.

| Provider (examples) | Typical variable |
|---------------------|------------------|
| Anthropic (Claude) | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Google Gemini | `GOOGLE_API_KEY` |
| Others | See `Rainscientist/config/settings.py` mappings (`*_API_KEY`) |

On Windows (PowerShell, current session):

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-api03-..."
```

**Config file**

User-wide YAML (created on first save):

- **Windows:** `%USERPROFILE%\.config\Rxscientist\config.yaml`
- **Linux / macOS:** `$XDG_CONFIG_HOME/Rxscientist/config.yaml` or `~/.config/Rxscientist/config.yaml`

Inspect or edit keys with:

```bash
rxsci config
```

**`.env` files** (loaded automatically when present)

Layers are merged; later layers override earlier ones for the same variable name:

1. `.env` next to the repo’s **`pyproject.toml`** (so keys work even if your shell is not in the project folder).
2. `.env` under the Rxscientist config directory (same folder as `config.yaml`).
3. `.env` discovered from the **current working directory** (highest priority).

Example **repo** `.env` at the clone root:

```env
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Step 4 — Launch

Start the interactive UI (default may be TUI or CLI depending on config):

```bash
rxsci
```

Help and subcommands:

```bash
rxsci --help
```

If `rxsci` is not on `PATH`, call the module entry (same CLI):

```bash
python -m Rxscientist --help
```

On Windows, `rxsci.exe` usually lives under your Python or virtualenv **`Scripts`** directory — add that folder to **PATH** if the command is not found.

### Step 5 — Verify and next steps

- Send a short prompt; if you see credential errors, re-check Step 3 (wizard, env, YAML, `.env`).
- Explore **`rxsci config`**, **`/help`** inside the UI (when available), and optional **MCP** tooling for external integrations.

#### 中文简明步骤

1. **安装 Python 3.11+**，建议使用 **pip** 或 **uv**。  
2. **安装包**：优先 `pip install Rxscientist`；若 PyPI 暂无包，使用上文 **B/C/D**（Git / 克隆 / Release  wheel）。  
3. **配置密钥**：运行 **`rxsci onboard`**，或设置环境变量（如 **`ANTHROPIC_API_KEY`**），或编辑 **`%USERPROFILE%\.config\Rxscientist\config.yaml`**（Windows），或在项目根 / 配置目录放置 **`.env`**。  
4. **启动**：执行 **`rxsci`**；若无命令，使用 **`python -m Rxscientist`**，并把 Python 的 **`Scripts`** 加入 **PATH**。  

---

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

Each successful push to `main` publishes **wheel / sdist** to **PyPI** and attaches the same builds to [GitHub Releases](https://github.com/Ar1haraNaN7mI/RainyXscientist/releases) (tag `v0.0.<run_id>.<run_attempt>`). There is **no standalone `.exe`** in those assets (they are Python packages).

1. Open the latest Release and download **`Rxscientist-*-py3-none-any.whl`** (and optionally the `.tar.gz` source distribution).
2. Install with pip (use the same Python where you want `rxsci`):

```bash
pip install "C:\path\to\Rxscientist-*-py3-none-any.whl"
rxsci
```

Replace the path and filename with the asset you actually downloaded (version is in the file name).

### Publishing to PyPI (maintainers)

**`.github/workflows/build.yml`** runs on every **push to `main`**: after the QA job passes, the **build-and-release** job sets a unique PyPI version **`0.0.<run_id>.<run_attempt>`** (injected into `pyproject.toml` in CI only; the repository keeps a **`0.0.0` placeholder**), runs **`uv build`**, publishes **`dist/*`** to PyPI, then creates a [GitHub Release](https://github.com/Ar1haraNaN7mI/RainyXscientist/releases) tagged **`v0.0.<run_id>.<run_attempt>`** with the same artifacts. **No manual version bumps or tag pushes** are required for the default flow.

One-time **GitHub secret** (required for CI uploads): create a **PyPI API token** at [pypi.org → Account settings → API tokens](https://pypi.org/manage/account/) with **Entire account** or project-scoped upload rights for **`Rxscientist`**. In this GitHub repository → **Settings** → **Secrets and variables** → **Actions** → add **`PYPITOKENKEY`** with the token value (matches `.github/workflows/build.yml`). The workflow uses **`__token__`** as the PyPI user name for API tokens.

Project name on PyPI must be **`Rxscientist`**; change `[project] name` in `pyproject.toml` if the name is taken on first publish.

**Optional:** you can also configure [PyPI trusted publishing (OIDC)](https://docs.pypi.org/trusted-publishers/) for the same service account and switch the workflow to OIDC later if you prefer not to store a long-lived token.

Manual upload (same token locally, different version in `pyproject.toml` for each upload if not using CI):

```bash
uv build
uv publish --token <pypi-api-token>
```

Use a token with **Entire account** or **Project-scoped** upload scope from PyPI account settings (do not commit tokens).

---

## 中文：下载与启动说明（Windows）

更系统的「下载 → 配置 → 启动」全流程见前文 **Complete tutorial: download → configure → launch**（含中英文摘要）；本节补充 Windows 常见问题与路径。

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
py -3.12 -m pip install .\Rxscientist-*-py3-none-any.whl
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
3. **GitHub 仓库秘密变量（CI 发 PyPI 必配）**  
   - 在 [PyPI 账户](https://pypi.org/manage/account/) 创建 **API token**（整站或仅 **`Rxscientist`** 项目上传权限）。  
   - 在 GitHub 本仓库：**Settings → Secrets and variables → Actions**，新增 **`PYPITOKENKEY`**，值为该 token（与工作流中名称一致）。  
4. **发版（默认全自动化）**：向 **`main` 分支推送** 且通过 QA 后，**`build.yml`** 用 **`PYPITOKENKEY`** 在 CI 中写入唯一版本号 **`0.0.<run_id>.<run_attempt>`**，**`uv build`** 并上传 PyPI，再创建带同名 **`v0.0.…` 标签** 的 GitHub Release。仓库中 **`version` 为占位 `0.0.0`**，无需为发版手改版本号或打标签。  
5. **本地用同一 token 上传（备用）**：切勿把 token 写进仓库。本地发版前在 `pyproject.toml` 中设好 **不与其他已上传版本冲突** 的 `version`：

```bash
uv build
uv publish --token <粘贴token>
```

PyPI 禁止重复上传同一版本；CI 已用 `run_id` 与 `run_attempt` 保证每次推送唯一。

---

## Why this project

RXscientist focuses on turning fragmented prompts into a repeatable research loop:
question intake, task decomposition, evidence collection, implementation, review, and refinement.
The goal is to make one local agent runtime usable for both exploratory research and engineering-heavy scientific tasks.

## Project status

This repository is being positioned as the new RXscientist project.
Documentation and examples are intentionally being simplified and refreshed.
