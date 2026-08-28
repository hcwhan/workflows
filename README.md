# workflows

通用 GitHub Actions 工作流集合。

## Workflows

| 文件 | 说明 | 触发 |
|------|------|------|
| `build-robust-windows.yml` | 在 Windows 上编译 [bigattichouse/robust](https://github.com/bigattichouse/robust) 的 `taguchi.dll` / `taguchi.exe` | 手动 |

## 使用 build-robust-windows

1. GitHub → **Actions** → **Build robust (Windows)** → **Run workflow**
2. 或命令行：

```bash
gh workflow run build-robust-windows.yml
gh run watch
```

3. 完成后在 Run 页面下载 **Artifacts** → `robust-windows-build`
4. 解压到本地 `llama-optimize/robust/build/`：

```
build/taguchi.dll
build/bin/taguchi.exe
```

## 本地触发与监听（可选）

```bash
python scripts/trigger_build_robust.py
```
