# test_user_input.py
import os

from generators.image_generator import VolcImageGenerator
from generators.text_generator import generate_story
from utils.input_handler import split_story


def test_custom_input():
    test_cases = [
        {"theme": "月球农场", "style": "水彩", "pages": 4},
        {"theme": "恐龙学校", "style": "未知风格", "pages": 3}
    ]

    generator = VolcImageGenerator()

    for case in test_cases:
        print(f"\n测试案例: {case}")
        story = generate_story(case)
        page = split_story(story, 1)[0]
        img_path = generator.generate_async(page, case["style"])
        assert os.path.exists(img_path), "生成失败"
        print(f"✅ 测试通过: {img_path}")
