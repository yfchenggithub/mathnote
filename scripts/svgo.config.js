/**
 * ========================================
 * SVGO CONFIG — LaTeX SVG 工业级 Preset
 * ----------------------------------------
 * 适用于：
 *   dvisvgm / LaTeX 数学公式 SVG
 *
 * 设计目标：
 *   ✅ 几何 0 失真
 *   ✅ 保留所有 transform / path 精度
 *   ✅ 支持无限缩放（小程序 / WebView）
 *   ✅ 最大化压缩（安全范围内）
 *
 * ⚠️ 严格禁止：
 *   - 改写 path 数据
 *   - 合并路径
 *   - 删除 viewBox
 * ========================================
 */

module.exports = {
  multipass: true,

  // ❗关键：不能低于 3（建议 3~4）
  floatPrecision: 3,

  plugins: [
    /**
     * ================================
     * ✅ 安全清理（不会影响几何）
     * ================================
     */

    "removeDoctype",
    "removeXMLProcInst",
    "removeComments",
    "removeMetadata",
    "removeEditorsNSData",
    "cleanupAttrs",
    "minifyStyles",
    "convertStyleToAttrs",
    "cleanupIds", // ⚠️ 安全（不影响 dvisvgm）

    /**
     * ================================
     * ✅ 结构优化（安全）
     * ================================
     */

    "removeEmptyAttrs",
    "removeEmptyText",
    "removeEmptyContainers",
    "removeHiddenElems",

    /**
     * ================================
     * ⚠️ 半安全（已限制行为）
     * ================================
     */

    {
      name: "collapseGroups",
      active: false, // ❗禁止（dvisvgm 强依赖 group 层级）
    },

    {
      name: "convertTransform",
      active: false, // ❗禁止（会破坏矩阵精度）
    },

    {
      name: "mergePaths",
      active: false, // ❗禁止（会破坏字符结构）
    },

    {
      name: "convertPathData",
      active: false, // ❗禁止（最危险）
    },

    /**
     * ================================
     * 🚨 绝对禁止（核心保护）
     * ================================
     */

    {
      name: "removeViewBox",
      active: false, // ❗必须保留（缩放核心）
    },

    {
      name: "removeUnknownsAndDefaults",
      active: false, // ❗可能误删关键属性
    },

    {
      name: "removeUselessStrokeAndFill",
      active: false, // ❗LaTeX glyph 依赖 fill
    },

    {
      name: "cleanupNumericValues",
      active: false, // ❗避免精度损失（由 floatPrecision 控制）
    },

    /**
     * ================================
     * 🧠 dvisvgm 专项优化
     * ================================
     */

    {
      name: "removeUnusedNS",
      active: true,
    },

    {
      name: "sortAttrs",
      active: true,
    },

    {
      name: "removeDimensions",
      active: false, // ❗保留 width/height（小程序兼容更稳）
    },
  ],
};
