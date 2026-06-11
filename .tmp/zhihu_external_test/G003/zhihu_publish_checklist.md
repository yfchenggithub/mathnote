# 知乎发布检查清单：G003

1. 打开 `preview.html` 检查封面、标题、正文和公式顺序。
2. 确认 `assets_manifest.json` 中 `missing_asset_count` 为 0。
3. 运行不带 `--package-only` 的脚本，让 Chrome 打开知乎写文章页。
4. 登录知乎后检查标题、封面、正文、公式图片和小程序码。
5. 确认无误后人工点击发布。

生成文件：

- 封面：`D:\mathnote\.tmp\zhihu_external_test\G003\cover.png`
- 正文 blocks：`D:\mathnote\.tmp\zhihu_external_test\G003\article_blocks.json`
- 预览：`D:\mathnote\.tmp\zhihu_external_test\G003\preview.html`
- 资源清单：`D:\mathnote\.tmp\zhihu_external_test\G003\assets_manifest.json`
