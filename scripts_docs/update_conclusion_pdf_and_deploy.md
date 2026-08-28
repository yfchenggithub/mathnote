# 二级结论 LaTeX 更新后：生成 PDF 并发布到服务器

本文记录这样一个固定场景：本地已经修改某个二级结论目录中的 LaTeX 文件，现在需要重新生成该结论的 PDF，并更新服务器上的 PDF、索引和相关静态资源。

下面以 `I058_cauchy_schwarz_2d` 为例。其他结论只需把命令中的 `I058` 换成相应 ID。

## 最短答案

如果服务器密码已经配置好，进入项目根目录后执行这一条即可：

```powershell
Set-Location D:\mathnote
python -B .\scripts\incremental_publish.py I058
```

`incremental_publish.py` 会再次编译 PDF，因此不是必须先单独运行 `build_conclusion_pdfs.py`。

## 推荐操作顺序

### 1. 进入项目根目录

```powershell
Set-Location D:\mathnote
```

发布脚本会改写项目数据文件，并在本地后端仓库中提交指定文件。开始前建议确认两个工作区没有需要另行保留的同路径修改：

```powershell
git status --short
git -C D:\mathnode_backend status --short
```

### 2. 预演 PDF 构建，确认 ID 和输出文件名

这一步不写入任何文件：

```powershell
python -B .\scripts\build_conclusion_pdfs.py I058 --dry-run
```

预期会看到：

```text
I058: 07_inequality/I058_cauchy_schwarz_2d -> I058_cauchy_schwarz_2d.pdf
```

### 3. 可选：先在本地生成 PDF 并检查

如果想在正式发布前打开 PDF 人工检查，使用下面的安全写法：

```powershell
python -B .\scripts\build_conclusion_pdfs.py I058 --overwrite --map-json .\.tmp\I058_conclusion_pdf_map.preview.json
Start-Process .\build\conclusion_pdfs\I058_cauchy_schwarz_2d.pdf
```

生成的 PDF 位于：

```text
D:\mathnote\build\conclusion_pdfs\I058_cauchy_schwarz_2d.pdf
```

这里把 `--map-json` 指向 `.tmp`，是为了避免单条预览构建把正式的 `build\conclusion_pdf_map.json` 改写成只包含 `I058` 的映射。

### 4. 如未配置密码，在当前 PowerShell 会话中安全输入

发布脚本从环境变量 `MATHNOTE_REMOTE_PASSWORD` 读取 SSH 和 sudo 密码。若 Windows 用户或系统环境变量中已经配置过，可跳过本步骤。

```powershell
$securePassword = Read-Host "服务器 SSH/sudo 密码" -AsSecureString
$env:MATHNOTE_REMOTE_PASSWORD = [System.Net.NetworkCredential]::new("", $securePassword).Password
```

不要把真实密码直接写进本文、脚本、Git 提交或命令历史。

### 5. 正式发布并更新服务器

```powershell
python -B .\scripts\incremental_publish.py I058
```

默认情况下，这条命令会依次完成：

1. 根据 `07_inequality\I058_cauchy_schwarz_2d` 重新生成搜索数据、详情数据和公式资源。
2. 重新编译 `build\conclusion_pdfs\I058_cauchy_schwarz_2d.pdf`，并覆盖旧 PDF。
3. 合并 `canonical_content_v2.json`、`backend_search_index.json` 和完整的 `conclusion_pdf_map.json`。
4. 将数据文件和 PDF 同步到 `D:\mathnode_backend\app\data`。
5. 在 `D:\mathnode_backend` 中提交并推送本次后端文件。
6. 上传当前结论的公式和 TikZ 静态资源。
7. 让服务器在 `/root/math_search_backend` 中执行 `git pull --ff-only`。
8. 重启 `math-search.service`，并显示服务状态。
9. 写入发布报告 `reports\incremental_publish_report.json`。

静态图片处理顺序为：先由 `scripts/render_tikz_assets.mjs` 将正文引用的
`assets/tikz/<ID>_*.tex` 渲染为 `public/static/tikz/<ID>/*.png` 对应的
`image_block`，再由 `scripts/render_math_assets.mjs` 处理公式图片。TikZ
资源会和公式资源一起上传，但分别保存在服务器的 `/static/tikz/<ID>/`
与 `/static/formulas/<ID>/`。任何 TikZ 编译失败都会在数据合并、资源上传
和服务重启之前终止发布，避免服务器出现“部分图片已更新、部分仍是源路径”
的状态。

临时工作区清理前，两类 PNG 还会分别备份到本地
`public/static/tikz/<ID>/` 和 `public/static/formulas/<ID>/`，便于复核和复用。

## 发布后检查

### 检查本地 PDF

```powershell
Get-Item .\build\conclusion_pdfs\I058_cauchy_schwarz_2d.pdf |
    Select-Object FullName, Length, LastWriteTime
```

### 查看发布报告中的关键结果

```powershell
$report = Get-Content -Raw .\reports\incremental_publish_report.json | ConvertFrom-Json
$report.outputs.pdf_delta
$report.outputs.backend_git
$report.outputs.remote
```

应重点确认：

- `pdf_delta` 中存在 `I058`，文件名为 `I058_cauchy_schwarz_2d.pdf`。
- `backend_git.pushed` 为 `true`，或者在文件内容未变化时明确显示跳过。
- `remote.skipped` 为 `false`，且 `restart` 为 `true`。

也可以检查本地后端仓库最近一次提交：

```powershell
git -C D:\mathnode_backend log -1 --oneline
```

## 常见补救命令

### 后端已经推送，但服务器拉取或重启失败

直接重新执行服务器端的拉取与重启：

```powershell
python -B .\scripts\remote_pull_restart.py
```

只拉取、不重启：

```powershell
python -B .\scripts\remote_pull_restart.py --pull-only
```

只重启、不拉取：

```powershell
python -B .\scripts\remote_pull_restart.py --restart-only
```

先预览远程命令、不连接服务器：

```powershell
python -B .\scripts\remote_pull_restart.py --dry-run
```

### 不执行 SSH 上传、服务器拉取或服务重启

```powershell
python -B .\scripts\incremental_publish.py I058 --no-deploy
```

注意：`--no-deploy` 仍会同步、提交并推送本地后端仓库。若只想在本机完成处理，不提交或推送两个 Git 仓库，使用：

```powershell
python -B .\scripts\incremental_publish.py I058 --no-deploy --skip-backend-git-publish --skip-project-git-publish
```

### 本地后端仓库需要先拉取最新版本

```powershell
python -B .\scripts\incremental_publish.py I058 --pull-backend-repo
```

## 可选：保存 LaTeX 源文件修改到 mathnote 仓库

服务器上的 PDF 由后端仓库发布；`incremental_publish.py` 不会替你提交 `I058` 目录中的 LaTeX 源文件。需要备份源文件修改时，另行执行：

```powershell
git add -- .\07_inequality\I058_cauchy_schwarz_2d
git commit -m "Update I058 Cauchy-Schwarz 2D conclusion"
git push origin main
```

提交前先用 `git status --short` 检查范围，避免带入无关文件。

## 一页命令清单

```powershell
Set-Location D:\mathnote

# 可选：预演和本地检查
python -B .\scripts\build_conclusion_pdfs.py I058 --dry-run
python -B .\scripts\build_conclusion_pdfs.py I058 --overwrite --map-json .\.tmp\I058_conclusion_pdf_map.preview.json
Start-Process .\build\conclusion_pdfs\I058_cauchy_schwarz_2d.pdf

# 未配置服务器密码时才需要
$securePassword = Read-Host "服务器 SSH/sudo 密码" -AsSecureString
$env:MATHNOTE_REMOTE_PASSWORD = [System.Net.NetworkCredential]::new("", $securePassword).Password

# 正式发布：会重新生成 PDF，并完成后端推送、服务器拉取和服务重启
python -B .\scripts\incremental_publish.py I058

# 查看结果
$report = Get-Content -Raw .\reports\incremental_publish_report.json | ConvertFrom-Json
$report.outputs.pdf_delta
$report.outputs.backend_git
$report.outputs.remote
```
