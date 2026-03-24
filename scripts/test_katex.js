const katex = require("katex");

try {
  const html = katex.renderToString("c = \\sqrt{a^2 + b^2}", {
    throwOnError: true,
  });
  console.log("✅ KaTeX 安装成功！生成的 HTML 片段如下：");
  console.log(html);
} catch (err) {
  console.error("❌ KaTeX 运行失败：", err);
}
