<div align="center">

# repos-management

Tooling for managing course repositories in **HOAHRB-Courses**.

[English](README.md) | [中文](README.zh-CN.md)

</div>

---

## What this repo does

This repository has two responsibilities:

- Core course automation:
  - Convert `readme.toml` ⇄ `README.md`
  - Provide the reusable GitHub Actions workflow used by course repositories
  - Generate worktree metadata
- Manual maintenance tools:
  - Fetch a temporary course-repository list
  - Trigger workflows or run the retained scripts in `scripts/`

`repos_list.txt` is a local, temporary input. It is ignored by Git and is never
committed, uploaded, or shared between workflow runs.

The preferred way to use this repo is:

```bash
python3 -m repos_management --help
```

---

## Requirements

- Python **3.11+**
- Optional (recommended): [GitHub CLI](https://cli.github.com/) (`gh`)

---

## Quickstart

### 1) Convert TOML → README

```bash
python3 -m repos_management rdme toml2md --input path/to/readme.toml --overwrite
```

### 2) Convert README → TOML

```bash
python3 -m repos_management rdme md2toml --input path/to/README.md --overwrite
```

### 3) Fetch a temporary repository list and trigger workflows

```bash
python3 -m repos_management repos fetch
python3 -m repos_management workflow trigger --delay 2
```

Dry-run:

```bash
python3 -m repos_management workflow trigger --dry-run
```

---

## Authentication

### `workflow trigger`

- Uses `GITHUB_TOKEN` if set.
- Otherwise falls back to `gh auth token`.

The token must be able to dispatch workflows (typical scopes: `repo`, `workflow`).

### `repos fetch`

- Uses `PERSONAL_ACCESS_TOKEN` from env or `.env`.
- You can also pass `--token` explicitly.

Typical scopes: `read:org`, `repo`.

---

## CLI reference

### `rdme toml2md`

Convert `readme.toml` → `README.md`.

```bash
python3 -m repos_management rdme toml2md --input <file-or-dir> [--output <file>] [--overwrite]
```

- If `--input` is a directory, it scans `**/readme.toml` and writes `README.md` next to each file.

### `rdme md2toml`

Convert `README.md` → `readme.toml`.

```bash
python3 -m repos_management rdme md2toml --input <file-or-dir> [--output <file>] [--overwrite] [--verbose]
```

- If `--input` is a directory, it scans `**/README.md` and writes `readme.toml` next to each file.

### `workflow trigger`

Trigger each course repo workflow file (default: `trigger-workflow.yml`) via `workflow_dispatch`.

```bash
python3 -m repos_management workflow trigger \
  --org HOAHRB-Courses \
  --repos-file repos_list.txt \
  --workflow-file trigger-workflow.yml \
  --ref main \
  --delay 2
```

### `repos fetch`

Fetch repositories under an org and write `repos_list.txt`.

```bash
python3 -m repos_management repos fetch --org HOAHRB-Courses
```

---

## Lecturers TOML schema (breaking change)

Only the **new** lecturers schema is supported:

```toml
[lecturers]

[[lecturers.intro]]
content = "..."  # optional
# author is optional
# author = { name = "", link = "", date = "" }

[[lecturers.items]]
name = "郑宜峰"

[[lecturers.items.reviews]]
content = "挺好的老师，交流时感觉很亲切。"
# author is optional
# author = { name = "xxx", link = "xxx", date = "xxx" }

[[lecturers.summary]]
content = "..."  # optional
```

Legacy TOML `[[lecturers]]` / `[[lecturers.reviews]]` is **not supported** and will raise an error.

---

## How course repositories CI works (high-level)

A typical course repository contains:

- `.github/workflows/trigger-workflow.yml`

This workflow calls the reusable workflow in this repo:

```yaml
uses: HOAHRB/repos-management/.github/workflows/reusable_worktree_generate.yml@main
```

To update all course repositories after `repos-management` changes are merged to `main`, run:

```bash
python3 -m repos_management workflow trigger
```

---

## Grade source contract

Course repositories own grade composition in `readme.toml`; there is no central
grade-summary file. `jwts` may add one automatic item in a `基本信息` section:

```toml
[[sections.items]]
source = "grades_summary"
content = "【成绩构成】: 作业 40% | 考试 60%"
```

The same form is used under `[[courses.sections.items]]` in multi-project
repositories. TOML → README emits a separate
`<!-- TOML-BADGES: source="grades_summary" -->` group. README → TOML rebuilds
only manual `basic_info` badges and preserves the existing source-marked item;
editing automatic badges in README cannot replace the item written by `jwts`.

## Manual maintenance scripts

Some power tools remain in `./scripts/` (use with care):

### GitHub Operations
- `add_workflow.sh` - 为课程仓库添加/更新 workflow 文件（通过 PR）
- `add_licenses.py` - 批量添加 LICENSE 文件（通过 PR）
- `add_secrets.sh` - 批量添加 GitHub secrets
- `approve_pr.sh` - 批量审核通过 PR
- `close_pr.sh` - 批量关闭 PR
- `batch_trigger_workflows.sh` - 批量触发工作流

### File Operations
- `delete_dir.sh` - 删除仓库中的目录
- `batch_delete.sh` - 批量删除多仓库中的目录

### Conversion Scripts
- `convert_toml_to_readme.py` - Convert TOML to README
- `readme_to_toml.py` - Convert README to TOML

### Other
- `generate_worktree_info.py` - Generate worktree info JSON
- `rdme_autogen.py` - Used by course repositories CI to orchestrate conversion
- `pull_or_clone.py` - Pull or clone repositories
- `fetch_repos.py` - Fetch repositories list

The scripts retain their existing arguments and behavior. List-consuming scripts
expect a workspace-local `repos_list.txt` generated with `repos fetch`.
