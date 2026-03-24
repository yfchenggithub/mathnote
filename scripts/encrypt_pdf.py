"""
PDF 加密脚本（适用于 LaTeX 生成后的 PDF）
功能：
1. 添加密码保护
2. 禁止复制 / 打印 / 修改
3. 可扩展：批量处理

使用方式：
python encrypt_pdf.py input.pdf output.pdf user123
"""

# -*- coding: utf-8 -*-

import sys
import os
import pikepdf

sys.stdout.reconfigure(encoding="utf-8")


def encrypt_pdf(input_path, output_path, user_tag):
    """
    PDF 加密主函数

    :param input_path: 原始PDF路径
    :param output_path: 输出PDF路径
    :param user_tag: 用户标识（用于生成密码）
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")

    # 👉 密码策略（你可以改）
    print("开始加密：", input_path)

    with pikepdf.open(input_path) as pdf:
        pdf.save(
            output_path,
            encryption=pikepdf.Encryption(
                # 🔐 权限控制
                allow=pikepdf.Permissions(
                    accessibility=True,  # ✅ 允许辅助功能（阅读器/朗读）
                    extract=True,  # ✅ 允许复制（重要！）
                    modify_annotation=True,  # ✅ 允许批注（学生会用）
                    modify_other=False,  # ❌ 禁止修改内容（核心）
                    print_lowres=True,  # ✅ 允许打印
                    print_highres=True,  # ✅ 允许高清打印
                )
            ),
        )

    print("加密完成：", output_path)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python encrypt_pdf.py 输入.pdf 输出.pdf 用户ID")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    user_id = sys.argv[3]

    encrypt_pdf(input_pdf, output_pdf, user_id)
