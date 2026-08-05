<div align="center">

# repos-management

用于管理 **HOAHRB-Courses** 组织下课程仓库的工具集。

[中文](README.zh-CN.md) | [English](README.md)

</div>

---

## 本仓库做什么

本仓库有两类职责：

- 核心课程自动化：
  - `readme.toml` ⇄ `README.md` 双向转换
  - 为课程仓库提供 reusable GitHub Actions workflow
  - 生成 worktree 元数据
- 人工维护工具：
  - 获取临时课程仓库名单
  - 触发工作流，或运行 `scripts/` 中保留的脚本

`repos_list.txt` 是本地临时输入，已被 Git 忽略，不会提交、上传，也不会在不同 workflow run 之间共享。

推荐使用方式：

```bash
python3 -m repos_management --help
```

---

## 环境要求

- Python **3.11+**
- 可选（推荐）：[GitHub CLI](https://cli.github.com/)（`gh`）

---

## 快速开始

### 1) TOML → README

```bash
python3 -m repos_management rdme toml2md --input path/to/readme.toml --overwrite
```

### 2) README → TOML

```bash
python3 -m repos_management rdme md2toml --input path/to/README.md --overwrite
```

### 3) 获取临时名单并批量触发 workflow

```bash
python3 -m repos_management repos fetch
python3 -m repos_management workflow trigger --delay 2
```

只预览不执行：

```bash
python3 -m repos_management workflow trigger --dry-run
```

---

## 认证（Token）

### `workflow trigger`

- 优先使用环境变量 `GITHUB_TOKEN`
- 若未设置，则尝试使用 `gh auth token`

token 需要能够 dispatch workflow（常见 scope：`repo`, `workflow`）。

### `repos fetch`

- 默认读取环境变量/`.env` 中的 `PERSONAL_ACCESS_TOKEN`
- 也可通过 `--token` 显式传入

常见 scope：`read:org`, `repo`。

---

## CLI 参考

### `rdme toml2md`

将 `readme.toml` 转换为 `README.md`。

```bash
python3 -m repos_management rdme toml2md --input <文件或目录> [--output <文件>] [--overwrite]
```

- 若 `--input` 是目录，会扫描 `**/readme.toml`，并在同目录生成 `README.md`

### `rdme md2toml`

将 `README.md` 转换为 `readme.toml`。

```bash
python3 -m repos_management rdme md2toml --input <文件或目录> [--output <文件>] [--overwrite] [--verbose]
```

- 若 `--input` 是目录，会扫描 `**/README.md`，并在同目录生成 `readme.toml`

### `workflow trigger`

对每个课程仓库的 workflow（默认：`trigger-workflow.yml`）发起 `workflow_dispatch`：

```bash
python3 -m repos_management workflow trigger \
  --org HOAHRB-Courses \
  --repos-file repos_list.txt \
  --workflow-file trigger-workflow.yml \
  --ref main \
  --delay 2
```

### `repos fetch`

拉取组织下仓库列表并写入 `repos_list.txt`。

```bash
python3 -m repos_management repos fetch --org HOAHRB-Courses
```

---

## lecturers TOML 结构（破坏性变更）

仅支持 **新版** lecturers 结构：

```toml
[lecturers]

[[lecturers.intro]]
content = "..."  # 可选
# author 可选
# author = { name = "", link = "", date = "" }

[[lecturers.items]]
name = "郑宜峰"

[[lecturers.items.reviews]]
content = "挺好的老师，交流时感觉很亲切。"
# author 可选
# author = { name = "xxx", link = "xxx", date = "xxx" }

[[lecturers.summary]]
content = "..."  # 可选
```

旧版 `[[lecturers]]` / `[[lecturers.reviews]]` **不再支持**，会直接报错。

---

## 课程仓库 CI 工作方式（概览）

典型课程仓库包含：

- `.github/workflows/trigger-workflow.yml`

它会调用本仓库的 reusable workflow：

```yaml
uses: HOAHRB/repos-management/.github/workflows/reusable_worktree_generate.yml@main
```

当 `repos-management` 的改动合并到 `main` 后，如需让所有课程仓库更新，可运行：

```bash
python3 -m repos_management workflow trigger
```

---

## 成绩构成的来源标记

成绩构成由课程仓库的 `readme.toml` 负责维护，不再使用中央成绩汇总文件。`jwts` 可以在“基本信息”节中写入一条自动项：

```toml
[[sections.items]]
source = "grades_summary"
content = "【成绩构成】: 作业 40% | 考试 60%"
```

multi-project 仓库使用同样的形式，只是路径为 `[[courses.sections.items]]`。TOML → README 会单独生成
`<!-- TOML-BADGES: source="grades_summary" -->` 分组；README → TOML 只重建人工 `basic_info` 徽章，并保留原有的自动项。因此，直接编辑 README 中的自动徽章不会覆盖 `jwts` 写入的内容。

## 人工维护脚本

部分"强力工具"仍保留在 `./scripts/` 下（谨慎使用）：

### GitHub 操作
- `add_workflow.sh` - 为课程仓库添加/更新 workflow 文件（通过 PR）
- `add_licenses.py` - 批量添加 LICENSE 文件（通过 PR）
- `add_secrets.sh` - 批量添加 GitHub secrets
- `approve_pr.sh` - 批量审核通过 PR
- `close_pr.sh` - 批量关闭 PR
- `batch_trigger_workflows.sh` - 批量触发工作流

### 文件操作
- `delete_dir.sh` - 删除仓库中的目录
- `batch_delete.sh` - 批量删除多仓库中的目录

### 转换脚本
- `convert_toml_to_readme.py` - TOML 转 README
- `readme_to_toml.py` - README 转 TOML

### 其他
- `generate_worktree_info.py` - 生成 worktree 信息
- `rdme_autogen.py` - 课程仓库 CI 中用于编排转换流程
- `pull_or_clone.py` - Pull 或 clone 仓库
- `fetch_repos.py` - 获取仓库列表

这些脚本的参数和行为保持不变。依赖名单的脚本会读取工作目录中的 `repos_list.txt`；先用 `repos fetch` 生成即可。
