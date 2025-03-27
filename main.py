# main.py
import re
import json
import logging
import os
from pathlib import Path
from fpdf import FPDF, XPos, YPos  # 导入新参数类型

from generators.text_generator import generate_story
from generators.image_generator import VolcBookGenerator

# 添加中文字体配置
FONT_PATH = "/Library/Fonts/SourceHanSerifSC-Regular.otf"  # 思源宋体路径

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_pdf(book_dir, pages):
    """生成绘本PDF（使用思源宋体显示中文）"""
    pdf = FPDF()

    # 强制使用UTF-8编码
    pdf.core_fonts_encoding = 'utf-8'

    # 加载中文字体
    try:
        pdf.add_font('SourceHan', '', FONT_PATH, uni=True)
        pdf.add_font('SourceHan', 'B', FONT_PATH, uni=True)  # 加载粗体
        logger.info("成功加载思源宋体")
    except Exception as e:
        logger.error(f"字体加载失败：{e}")
        return

    # 读取元数据
    with open(book_dir / "metadata.json", encoding="utf-8") as f:
        metadata = json.load(f)

    # 使用主题作为标题
    title = metadata["params"]["theme"]

    # 获取原始内容文本
    raw_content = metadata["raw_data"]["choices"][0]["message"]["content"]

    # 添加封面
    pdf.add_page()
    pdf.set_font('SourceHan', 'B', 28)

    # 计算标题垂直位置，使其居中
    pdf.cell(
        200,
        40,
        text=title,
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
        align='C'
    )

    # 添加绘本风格信息
    pdf.set_font('SourceHan', '', 14)
    style_info = f"风格：{metadata['params']['style']} | 页数：{metadata['params']['page_count']}"
    pdf.cell(
        200,
        20,
        text=style_info,
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
        align='C'
    )

    # 添加封面图片(使用第一页图片)
    cover_image = str(book_dir / "page_001.png")
    if os.path.exists(cover_image):
        pdf.image(cover_image, x=30, y=80, w=150)

    # 为每页内容创建图文对照布局
    for page_num in range(1, len(pages)+1):
        # 添加图片页
        pdf.add_page()
        image_path = str(book_dir / f"page_{page_num:03d}.png")
        pdf.image(image_path, x=10, y=10, w=190)  # 插入图片

        # 添加页码
        pdf.set_font('SourceHan', '', 10)
        pdf.set_text_color(150, 150, 150)
        pdf.text(190, 286, f"{page_num}/{len(pages)}")

        # 重置文本颜色
        pdf.set_text_color(0, 0, 0)

    # 添加完整故事内容页
    pdf.add_page()
    pdf.set_font('SourceHan', 'B', 16)
    pdf.cell(
        200,
        20,
        text="故事全文",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
        align='C'
    )

    # 设置正文字体
    pdf.set_font('SourceHan', '', 12)

    # 添加格式化后的内容
    y_position = 40
    line_height = 8

    for i, page_content in enumerate(pages):
        # 添加页标题
        pdf.set_font('SourceHan', 'B', 14)
        page_title = f"第{i+1}页"
        pdf.set_xy(10, y_position)
        pdf.cell(190, 10, page_title, ln=1)
        y_position += 10

        # 重设字体
        pdf.set_font('SourceHan', '', 12)

        # 移除[...]格式的标记，让内容更易读
        clean_content = re.sub(r'\[(.*?)\]', r'\1', page_content)

        # 分段显示内容
        pdf.set_xy(15, y_position)
        pdf.multi_cell(180, line_height, clean_content)

        # 更新位置，添加段间距
        y_position = pdf.get_y() + 10

        # 检查是否需要新页
        if y_position > 270:
            pdf.add_page()
            y_position = 15

    # 保存PDF
    pdf.output(str(book_dir / "book.pdf"))
    logger.info(f"PDF生成成功：{book_dir / 'book.pdf'}")
    return str(book_dir / "book.pdf")

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
    # elements = [item.strip("[]") for item in page_text.split() if item.startswith("[")]
    elements = re.findall(r'\[(.*?)\]', page_text)

    # 构建提示词（排除JSON部分）<button class="citation-flag" data-index="2">
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

    # 解析分页内容（核心修改）<button class="citation-flag" data-index="1">
    raw_content = story["raw_data"]["choices"][0]["message"]["content"]
    pages = [p.strip() for p in raw_content.split("【PAGE】")[1:] if p.strip()]
    pages = pages[:params["page_count"]]  # 确保页数匹配

    # 生成每页内容
    for page_num, page_text in enumerate(pages, 1):
        logger.info(f"正在生成第{page_num}页...")

        # 构建图片提示词
        prompt = build_image_prompt(page_text, story["visual_tags"])

        # 提取对话内容
        dialogue = extract_dialogue(page_text)
        text_info = {
            "text": dialogue,
            "position": "bottom-center",
            "color": "#FFFFFF"
        } if dialogue else None

        # 生成带文字的图片
        result = image_gen.generate_page(
            prompt=prompt,
            page_num=page_num,
            text_info=text_info
        )

        if not result:
            logger.warning(f"第{page_num}页生成失败，跳过...")
            continue
    # 打印解析后的分页内容
    for i, page in enumerate(pages):
        print("--------")
        print(f"Page {i+1}: {page[:50]}...")
        print("--------")
    create_pdf(book_dir, pages)
if __name__ == "__main__":
    #
    # from PIL import Image
    # test_img = Image.new('RGB', (1024, 768), color=(0, 0, 128))
    # test_img.save("test_bg.png")
    # image_gen = VolcBookGenerator()
    # image_gen.add_text_overlay("test_bg.png", {
    #     "text": "测试文字叠加",
    #     "position": "bottom-center",
    #     "color": "#FFFFFF"
    # })


    # 生成参数配置
    book_params = {
        # "theme": "校园生活",
        # "theme": "公园散步",
        "theme": "飞流直下三千尺",
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


    #
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