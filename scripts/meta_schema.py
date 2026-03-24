# -*- coding: utf-8 -*-
"""
========================================
文件名: meta_schema.py
作用:   定义 meta.json 的标准结构（唯一数据模板）
版本:   v3.0（结构化渲染 + 搜索引擎 + 推荐系统 + 性能控制）
========================================

【设计目标】
1. 支持极致搜索（拼音 / OCR / 公式匹配）
2. 支持小程序高性能渲染（分块 + 懒加载）
3. 支持动态演示（GeoGebra / 参数化）
4. 支持推荐系统（用户行为 + 关联图谱）
5. 支持未来扩展（知识图谱 / 多版本内容）

========================================
字段分类说明：
- 核心标识：唯一性、归属、版本
- 基础信息：标题、章节、难度等
- 搜索增强：拼音、关键词、权重控制
- OCR识别：拍照搜题、公式匹配
- 内容展示：结构化渲染（核心升级）
- 高级能力：推导、参数化、知识图谱
- 资产与分享：图片、动画、分享配置
- 运营与统计：标签、行为数据、推荐
========================================
"""

META_SCHEMA = {
    # ==================== 1. 核心标识 ====================
    "id": "",  # [必须] 全局唯一 ID（用于跳转 / 推荐 / 关联）
    "module": "",  # [必须] 模块名（如 "inequality"）
    "version": 3,  # [必须] Schema版本（用于兼容控制）
    # ==================== 2. 基础信息 ====================
    "title": "",  # [必须] 标题（展示 + 搜索核心）
    "chapter": "",  # [推荐] 章节（教材体系）
    "section": "",  # [推荐] 小节
    "difficulty": 0,  # [推荐] 难度 0-5
    "examFrequency": 0,  # [推荐] 考频 0-5
    "examScore": 0,  # [推荐] 分值
    "hotScore": 0,  # [推荐] 热度（可由行为数据计算）
    # ==================== 3. 搜索增强 ====================
    "pinyin": "",  # [推荐] 全拼
    "pinyinAbbr": "",  # [推荐] 首字母
    "keywords": [],  # [推荐] 关键词（搜索入口）
    "synonyms": [],  # [推荐] 同义词（语义扩展）
    "searchBoost": [],  # [可选] 强制提升词（权重加成）
    "searchMeta": {  # ⭐ [新增] 搜索权重控制（精排核心）
        "titleWeight": 10,
        "keywordWeight": 8,
        "synonymWeight": 6,
        "ocrWeight": 9,
        "formulaWeight": 7,
    },
    # ==================== 4. OCR / 拍照搜题 ====================
    "ocrKeywords": [],  # [可选] OCR关键词（文本匹配）
    "latexPatterns": [],  # [可选] LaTeX模板匹配
    "formulaTokens": [  # ⭐ [新增] 结构化公式token（轻量匹配核心）
        # 示例: "a+b", "\\sqrt{ab}", ">=0"
    ],
    # ==================== 5. 内容展示（核心升级） ====================
    "formulaRaw": "",  # [推荐] 原始LaTeX
    "previewLaTeX": "",  # [推荐] 卡片预览公式
    "summary": "",  # [推荐] 简短摘要（搜索结果页）
    "preview": "",  # [可选] 富文本预览
    # ==================== 6. 高级能力 ====================
    "derivationSteps": [  # [可选] 推导步骤（结构化）
        {"stepTitle": "", "content": "", "latex": ""}
    ],
    "relatedFormulas": [],  # [可选] 强语义关联（推荐用）
    "paramConfig": {  # [可选] 动态参数演示
        "type": "",  # geogebra / desmos / custom
        "params": {},
    },
    "contentBlocks": [  # ⭐⭐⭐ [核心新增] 结构化内容块
        {
            "type": "statement",  # [必须] statement / proof / example / trap / summary
            "title": "",  # [可选] 小标题
            "content": "",  # [推荐] HTML / Markdown
            "latex": "",  # [可选] 原始LaTeX
            "order": 0,  # [必须] 排序
            "foldable": True,  # [推荐] 是否默认折叠（性能关键）
        }
    ],
    "demoType": "",  # [可选] interactive / static / animation
    "graph": {  # ⭐ [新增] 知识图谱结构
        "prerequisites": [],  # 前置知识
        "extensions": [],  # 延伸知识
        "similar": [],  # 相似结论
    },
    "variants": {  # ⭐ [新增] 多版本内容
        "simple": "",  # 小白版
        "exam": "",  # 考试版
        "advanced": "",  # 提升版
    },
    # ==================== 7. 资产与分享 ====================
    "assets": {
        "svg": "",  # [可选] SVG（推荐）
        "webp": "",  # [可选] WebP（兼容）
        "thumbnail": "",  # [可选] 缩略图
        "animated": "",  # [可选] 动图（GIF/MP4）
    },
    "renderConfig": {  # ⭐ [新增] 渲染控制（性能核心）
        "renderMode": "svg",  # svg / webp / html
        "lazyLoad": True,  # 懒加载
        "priority": "normal",  # high / normal / low
    },
    "geogebraId": "",  # [可选] GeoGebra ID
    "relatedIds": [],  # [可选] 向后兼容
    "shareConfig": {"title": "", "imageUrl": "", "shareDesc": ""},
    # ==================== 8. 运营与统计 ====================
    "tags": [],  # [可选] 标签
    "abilityTags": [],  # [可选] 能力标签
    "knowledgeNode": "",  # [可选] 知识树节点
    "useScene": [],  # [可选] 使用场景
    "coreIdea": "",  # [可选] 核心思想
    "remarks": "",  # [可选] 注意事项
    "stats": {  # ⭐ [新增] 用户行为数据（推荐核心）
        "viewCount": 0,
        "likeCount": 0,
        "saveCount": 0,
        "errorCount": 0,
    },
    "isPro": 0,  # [推荐] 是否付费
    "formulas": [],  # [可选] 扩展公式（备用）
}
