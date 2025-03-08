# main.py
import json
import logging
import os
from pathlib import Path
from fpdf import FPDF, XPos, YPos  # 导入新参数类型

from generators.text_generator import generate_story
from generators.image_generator import VolcBookGenerator


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_pdf(book_dir):
    """生成绘本PDF（使用系统默认字体）"""
    pdf = FPDF()

    # 移除所有字体加载逻辑，直接使用系统默认配置
    pdf.core_fonts_encoding = 'utf-8'

    # 读取元数据
    with open(book_dir / "metadata.json", encoding="utf-8") as f:
        metadata = json.load(f)

    # 解析分页内容（核心修复）<button class="citation-flag" data-index="1">
    pages = []
    content = metadata["raw_data"]["choices"][0]["message"]["content"]
    for part in content.split("【PAGE"):
        if not part.strip():
            continue
        page_num = part[0]
        page_content = part.split("】", 1)[-1].strip()
        pages.append(page_content)

    # 添加封面
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 24)
    pdf.cell(
        200,
        30,
        text=metadata["params"]["theme"],
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
        align='C'
    )
    # 添加内容页
    for page_num in range(1, metadata["params"]["page_count"]+1):
        # 图片页
        pdf.add_page()
        image_path = str(book_dir / f"page_{page_num:03d}.png")
        pdf.image(image_path, x=10, y=30, w=190)

        # 文字页
        pdf.add_page()
        pdf.set_font('Helvetica', '', 12)
        text_content = pages[page_num-1]  # 修正内容获取方式

        # 处理中文显示（核心修复）<button class="citation-flag" data-index="2">
        try:
            pdf.multi_cell(0, 10, txt=text_content.encode('latin1').decode('utf8', errors='ignore'))
        except:
            pdf.multi_cell(0, 10, txt=text_content.encode('utf8').decode('latin1', errors='ignore'))

    # 保存PDF
    pdf_path = book_dir / "book.pdf"
    pdf.output(str(pdf_path))
    logger.info(f"PDF生成成功：{pdf_path}")

def extract_dialogue(page_text):
    """从文本中提取对话内容"""
    # 使用正则表达式 r"「(.*?)」" 匹配中文对话标记
    # 「 和 」 是中文对话的典型符号（类似「你好」这样的格式）
    # .*? 是非贪婪匹配，确保匹配到最近的结束符号
    # re.findall 返回所有匹配结果的列表
    # return " ".join(matches) 将多个对话合并为一个字符串
    import re
    matches = re.findall(r"「(.*?)」", page_text)
    return " ".join(matches) if matches else None
    # 在生成图片时添加文字信息


def build_image_prompt(page_text, visual_tags):
    """根据文本内容和可视化标签构建图片生成提示词"""
    # 提取可视化元素
    elements = [item.strip("[]") for item in page_text.split() if item.startswith("[")]

    # 构建提示词
    prompt = f"{visual_tags.get('style', '卡通')}风格，"
    prompt += "，".join(elements)
    prompt += f"，主色调：{','.join(visual_tags.get('colors', []))}"

    # 添加文字标注（如果需要）
    # prompt += "，文字：\"示例文字\" 位置：顶部中央，大小：72px，颜色：#8B4513"
    return prompt

def generate_book(params):
    """生成完整绘本"""
    # 生成故事文本
    story = generate_story(params)
    if not story:
        logger.error("故事生成失败，终止绘本生成")
        return

    # 初始化图片生成器
    image_gen = VolcBookGenerator(output_dir=f"books/{params['theme']}")

    # 创建目录结构
    book_dir = Path(f"books/{params['theme']}")
    book_dir.mkdir(parents=True, exist_ok=True)

    # 保存元数据
    with open(book_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "params": params,
            "visual_tags": story["visual_tags"],
            "raw_data": story["raw_data"]
        }, f, ensure_ascii=False, indent=2)

    # 生成每页内容
    for page_num, page_text in enumerate(story["pages"], 1):
        logger.info(f"正在生成第{page_num}页...")

        # 构建图片生成提示词
        prompt = build_image_prompt(page_text, story["visual_tags"])
        dialogue = extract_dialogue(page_text)
        text_info = {
            "text": dialogue,
            "position": "bottom-left",  # 可扩展更多位置参数
            "color": "#2F4F4F"
        } if dialogue else None
        # 生成图片
        result = image_gen.generate_page(
            prompt=prompt,
            page_num=page_num,
            text_info=text_info  # 新增参数传递
        )

        if not result:
            logger.warning(f"第{page_num}页图片生成失败，跳过...")
            continue

    create_pdf(book_dir)
if __name__ == "__main__":
    # 生成参数配置
    book_params = {
        "theme": "海洋星球大冒险",
        "style": "水彩",
        "page_count": 3
    }
    # 执行生成
    generate_book(book_params)

    # # 创建测试图片
    # from PIL import Image
    # test_img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    # test_img.save("test_image.png")
    # image_gen = VolcBookGenerator()

    # 测试文字叠加
    # image_gen.add_text_overlay("test_image.png", {
    #     "text": "这是一段测试文少时诵诗书所所所所所所所所字\n换行测试",
    #     "color": "#FF0000"
    # })



    # from PIL import Image
    # test_img = Image.new('RGB', (1024, 768), color=(0, 0, 0))  # 黑色背景
    # test_img.save("test_bg.jpg")
    #
    # image_gen.add_text_overlay("test_bg.jpg", {
    #     "text": "这是一段特别长的测试文字，用于验证自动换行功能是否正常。"
    #             "我们添加更多内容来测试换行效果，包括中英文混合、长单词处理等。"
    #             "AutomaticWordWrappingTestExample",
    #     "color": "#FF0000"
    # })