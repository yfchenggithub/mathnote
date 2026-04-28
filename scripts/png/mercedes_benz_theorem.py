from matplotlib import font_manager
import matplotlib.pyplot as plt
import numpy as np

# ================= 配置区域 =================
# 画面比例（宽, 高），常用示例： (16, 9), (9, 16), (3, 4), (1, 1)
TARGET_RATIO = (3, 4)
# 画布基础尺寸（单位：英寸）
BASE_SIZE = 10
# 预览渲染 DPI（屏幕显示）
FIGURE_DPI = 140
# 导出高清 DPI（文件输出，建议 >= 300）
EXPORT_DPI = 400

# 字号层级（阅读舒适）
TITLE_FONT_SIZE = 42
SUBTITLE_FONT_SIZE = 30
FORMULA_FONT_SIZE = 30
POINT_LABEL_FONT_SIZE = 26
AREA_LABEL_FONT_SIZE = 32

# 向量箭头参数（在 P->A/P->B/P->C 末端绘制箭头）
VECTOR_ARROW_HEAD_LEN = 0.8
VECTOR_ARROW_INSET = 0.12
VECTOR_ARROW_SCALE = 16

# 中文字体回退链：按顺序尝试，找到即用
PREFERRED_FONTS = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "PingFang SC",
    "Heiti SC",
    "Arial Unicode MS",
    "DejaVu Sans",
]

# 极简浅色块配色（接近参考图风格）
# 顺序对应：S_A, S_B, S_C
AREA_COLORS = ("#F8F2EA", "#EFF8EE", "#EEF4FA")
CANVAS_BG = "#FFFFFF"

TITLE_TEXT = "奔驰定理"
SUBTITLE_TEXT = "向量选择题直接出答案"
# ==========================================


def configure_font_fallback():
    """配置中文字体回退，避免乱码并兼容不同系统。"""
    available_fonts = {font.name for font in font_manager.fontManager.ttflist}
    fallback_chain = [name for name in PREFERRED_FONTS if name in available_fonts]
    if not fallback_chain:
        fallback_chain = ["DejaVu Sans"]
    elif "DejaVu Sans" not in fallback_chain:
        fallback_chain.append("DejaVu Sans")

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = fallback_chain
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["mathtext.fontset"] = "stix"
    plt.rcParams["mathtext.default"] = "it"
    return fallback_chain[0]


def draw_mercedes_theorem(ratio=(1, 1)):
    selected_font = configure_font_fallback()

    # 1. 定义三角形顶点和内部点 P
    A = np.array([3.0, 8.0])
    B = np.array([0.0, 1.0])
    C = np.array([7.0, 2.0])
    P = np.array([3.5, 3.5])

    # 2. 创建画布并设置比例
    w_ratio, h_ratio = ratio
    fig_width = BASE_SIZE if w_ratio >= h_ratio else BASE_SIZE * (w_ratio / h_ratio)
    fig_height = BASE_SIZE if h_ratio >= w_ratio else BASE_SIZE * (h_ratio / w_ratio)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=FIGURE_DPI)
    fig.patch.set_facecolor(CANVAS_BG)
    ax.set_facecolor(CANVAS_BG)

    # 3. 计算坐标轴范围并适配目标比例
    all_points = np.array([A, B, C, P])
    x_min, y_min = np.min(all_points, axis=0) - 1.5
    x_max, y_max = np.max(all_points, axis=0) + 1.5

    current_w = x_max - x_min
    current_h = y_max - y_min
    target_aspect = w_ratio / h_ratio
    current_aspect = current_w / current_h

    if current_aspect > target_aspect:
        desired_h = current_w / target_aspect
        diff = desired_h - current_h
        y_min -= diff / 2
        y_max += diff / 2
    else:
        desired_w = current_h * target_aspect
        diff = desired_w - current_w
        x_min -= diff / 2
        x_max += diff / 2

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect("equal")
    ax.axis("off")

    # 4. 绘制三个子三角形区域：S_A, S_B, S_C（浅色、低饱和）
    poly_a = plt.Polygon([P, B, C], facecolor=AREA_COLORS[0], alpha=0.92, zorder=2)
    poly_b = plt.Polygon([P, A, C], facecolor=AREA_COLORS[1], alpha=0.92, zorder=2)
    poly_c = plt.Polygon([P, A, B], facecolor=AREA_COLORS[2], alpha=0.92, zorder=2)
    ax.add_patch(poly_a)
    ax.add_patch(poly_b)
    ax.add_patch(poly_c)

    # 5. 绘制三条向量方向线：黑色虚线 + 末端箭头（P -> A/B/C）
    for start, end in ((P, A), (P, B), (P, C)):
        x_coords = [start[0], end[0]]
        y_coords = [start[1], end[1]]
        ax.plot(
            x_coords,
            y_coords,
            color="black",
            linestyle=(0, (4, 4)),
            linewidth=2.0,
            solid_capstyle="round",
            zorder=6,
        )

        # 在靠近端点处叠加箭头头部，强调 P -> A/B/C 的方向含义
        direction = end - start
        norm = np.linalg.norm(direction)
        if norm > 1e-8:
            unit = direction / norm
            head_len = min(VECTOR_ARROW_HEAD_LEN, norm * 0.35)
            end_inset = min(VECTOR_ARROW_INSET, norm * 0.08)
            arrow_head = end - unit * end_inset
            arrow_tail = arrow_head - unit * head_len
            ax.annotate(
                "",
                xy=arrow_head,
                xytext=arrow_tail,
                arrowprops=dict(
                    arrowstyle="-|>",
                    color="black",
                    lw=1.8,
                    mutation_scale=VECTOR_ARROW_SCALE,
                    shrinkA=0,
                    shrinkB=0,
                ),
                zorder=7,
            )

    # 6. 绘制三角形外框（纯黑）
    triangle_outline = plt.Polygon(
        [A, B, C], fill=False, edgecolor="black", linewidth=2.6, zorder=10
    )
    ax.add_patch(triangle_outline)

    # 标出点 P
    ax.scatter([P[0]], [P[1]], s=36, color="black", zorder=9)

    # 7. 顶点与面积符号标注（数学体、无底框）
    point_style = {
        "fontsize": POINT_LABEL_FONT_SIZE,
        "fontweight": "semibold",
        "color": "black",
    }
    ax.text(A[0], A[1] + 0.45, r"$A$", ha="center", va="center", **point_style)
    ax.text(B[0] - 0.48, B[1] - 0.55, r"$B$", ha="center", va="center", **point_style)
    ax.text(C[0] + 0.48, C[1] - 0.48, r"$C$", ha="center", va="center", **point_style)
    ax.text(P[0] - 0.18, P[1] + 0.15, r"$P$", ha="right", va="center", **point_style)

    center_a = (P + B + C) / 3
    center_b = (P + A + C) / 3
    center_c = (P + A + B) / 3
    ax.text(
        center_a[0],
        center_a[1],
        "$S_A$",
        ha="center",
        fontsize=AREA_LABEL_FONT_SIZE,
        color="black",
        fontweight="semibold",
    )
    ax.text(
        center_b[0],
        center_b[1],
        "$S_B$",
        ha="center",
        fontsize=AREA_LABEL_FONT_SIZE,
        color="black",
        fontweight="semibold",
    )
    ax.text(
        center_c[0],
        center_c[1],
        "$S_C$",
        ha="center",
        fontsize=AREA_LABEL_FONT_SIZE,
        color="black",
        fontweight="semibold",
    )

    # 8. 标题、副标题与公式（纯文本黑色，简洁大方）
    plt.text(
        0.5,
        0.965,
        TITLE_TEXT,
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=TITLE_FONT_SIZE,
        fontweight="black",
        color="black",
    )
    plt.text(
        0.5,
        0.885,
        SUBTITLE_TEXT,
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=SUBTITLE_FONT_SIZE,
        fontweight="bold",
        color="black",
    )

    formula = r"$S_A \cdot \vec{PA} + S_B \cdot \vec{PB} + S_C \cdot \vec{PC} = \vec{0}$"
    plt.text(
        0.5,
        0.05,
        formula,
        transform=ax.transAxes,
        ha="center",
        fontsize=FORMULA_FONT_SIZE,
        color="black",
    )

    # 9. 导出高清图片
    ratio_str = f"{ratio[0]}x{ratio[1]}"
    output_file = f"benz_theorem_{ratio_str}_{EXPORT_DPI}dpi.png"
    plt.tight_layout(pad=0.6)
    plt.savefig(
        output_file,
        dpi=EXPORT_DPI,
        bbox_inches="tight",
        pad_inches=0.12,
        facecolor=fig.get_facecolor(),
    )
    print(f"图片已生成：{output_file}（字体：{selected_font}）")
    plt.show()


if __name__ == "__main__":
    draw_mercedes_theorem(TARGET_RATIO)
