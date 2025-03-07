import base64
import json
import os
import hashlib
import hmac
import logging
import requests
from datetime import datetime
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.DEBUG)  # 显示详细调试信息
# 配置日志
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 服务常量配置
SERVICE_CONFIG = {
    "method": "POST",
    "service": "cv",
    "region": "cn-north-1",
    "host": "visual.volcengineapi.com",
    "endpoint": "https://visual.volcengineapi.com",
    "action": "CVProcess",
    "version": "2022-08-31"
}

class VolcBookGenerator:
    """火山引擎绘本生成器"""

    def __init__(self, output_dir="output"):
        # 初始化配置
        self.access_key = "AKLTNWU1ZGQyNDZkZTkwNDhjN2FhNDhhZDY0ZmQ3YzcxYmM"
        self.secret_key = "TUdNMU9UTXpOR0ZtWXpZME5EQTRPV0k1Tm1JeFpqRmhaVGt3TkdWaFl6WQ=="
        self.output_dir = Path(output_dir)
        self._validate_credentials()
        self._init_workspace()

        # 页面计数器
        self.page_count = 0

    def _validate_credentials(self):
        """验证凭证有效性"""
        if not self.access_key or not self.secret_key:
            raise ValueError("请设置VOLC_AK和VOLC_SK环境变量")

    def _init_workspace(self):
        """初始化工作目录"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"工作目录已初始化：{self.output_dir.absolute()}")

    @staticmethod
    def sign(key, msg):
        """HMAC签名工具"""
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def _get_signature_key(self, date_stamp):
        """生成签名密钥链"""
        secret_key = f"{self.secret_key}".encode()
        k_date = self.sign(secret_key, date_stamp)
        k_region = self.sign(k_date, SERVICE_CONFIG["region"])
        k_service = self.sign(k_region, SERVICE_CONFIG["service"])
        return self.sign(k_service, 'request')

    def _generate_headers(self, body: str):
        """生成请求头（包含签名）"""
        t = datetime.utcnow()
        current_date = t.strftime('%Y%m%dT%H%M%SZ')
        datestamp = t.strftime('%Y%m%d')

        # 规范请求要素
        canonical_querystring = f"Action={SERVICE_CONFIG['action']}&Version={SERVICE_CONFIG['version']}"
        payload_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()

        # 构造规范请求
        canonical_request = '\n'.join([
            SERVICE_CONFIG["method"],
            "/",
            canonical_querystring,
            f'content-type:application/json\nhost:{SERVICE_CONFIG["host"]}\n'
            f'x-content-sha256:{payload_hash}\nx-date:{current_date}\n',
            'content-type;host;x-content-sha256;x-date',
            payload_hash
        ])

        # 生成签名
        credential_scope = f"{datestamp}/{SERVICE_CONFIG['region']}/{SERVICE_CONFIG['service']}/request"
        string_to_sign = '\n'.join([
            'HMAC-SHA256',
            current_date,
            credential_scope,
            hashlib.sha256(canonical_request.encode()).hexdigest()
        ])

        signing_key = self._get_signature_key(datestamp)
        signature = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()

        return {
            'X-Date': current_date,
            'Authorization': f'HMAC-SHA256 Credential={self.access_key}/{credential_scope}, '
                             f'SignedHeaders=content-type;host;x-content-sha256;x-date, '
                             f'Signature={signature}',
            'X-Content-Sha256': payload_hash,
            'Content-Type': 'application/json'
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=10, max=30))
    def generate_page(self, prompt: str, page_num: int = None, **params):
        """生成绘本页面"""
        try:
            # 构造请求体
            request_body = {
                "req_key": "high_aes_general_v21_L",
                "prompt": prompt,
                "width": 1024,
                "height": 768,
                **params
            }

            # 发送生成请求
            response = requests.post(
                SERVICE_CONFIG["endpoint"],
                params={
                    "Action": SERVICE_CONFIG["action"],
                    "Version": SERVICE_CONFIG["version"]
                },
                headers=self._generate_headers(json.dumps(request_body)),
                json=request_body,
                timeout=(20, 40)  # 连接超时10秒，读取超时30秒
            )
            response.raise_for_status()

            # 处理响应数据
            result = response.json()

            # 调试日志：打印原始响应
            logger.debug(f"API原始响应：{json.dumps(result, ensure_ascii=False)}")
            # 修改状态码判断条件
            if not isinstance(result, dict) or result.get("code") != 10000:
                logger.error(f"生成失败：{result.get('message', '未知错误')}")
                return None

            data = result.get("data", {})
            binary_data = data.get("binary_data_base64", [])
            image_urls = data.get("image_urls", [])

            # 优先处理base64数据
            if binary_data:
                image_content = base64.b64decode(binary_data[0])
                if page_num is None:
                    self.page_count += 1
                    page_num = self.page_count
                filename = f"page_{page_num:03d}.png"
                save_path = self.output_dir / filename
                with open(save_path, "wb") as f:
                    f.write(image_content)
                logger.info(f"Base64图片保存成功：{save_path}")
                return save_path
            elif image_urls:
                image_url = image_urls[0]
                if page_num is None:
                    self.page_count += 1
                    page_num = self.page_count
                return self._save_image(image_url, page_num)
            else:
                logger.error("响应中未包含有效图片数据")
                return None

        except Exception as e:
            logger.error(f"生成过程中出现错误：{str(e)}")
            return None


    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=10, max=30))
    def _save_image(self, image_url: str, page_num: int):
        """下载并保存图片"""
        try:
            response = requests.get(image_url, timeout=15)
            response.raise_for_status()

            filename = f"page_{page_num:03d}.png"
            save_path = self.output_dir / filename

            with open(save_path, "wb") as f:
                f.write(response.content)

            logger.info(f"页面保存成功：{save_path}")
            return save_path

        except Exception as e:
            logger.error(f"图片下载失败：{str(e)}")
            raise

# 使用示例
if __name__ == "__main__":
    # 初始化生成器
    book_gen = VolcBookGenerator(output_dir="my_storybook")

    # 生成绘本页面
    pages = [
        {"prompt": "卡通风格，森林中的小木屋，烟囱冒着炊烟，文字：\"童话小屋\" 位置：顶部中央，大小：72px，颜色：#8B4513"},
        {"prompt": "水彩风格，湖边钓鱼的熊先生，文字：\"宁静午后\" 位置：右下角，颜色：#2F4F4F"},
        {"prompt": "科幻风格，太空站里的机器人，文字：\"地球历 3023\" 位置：左下角，大小：48px"}
    ]

    for idx, page_config in enumerate(pages, 1):
        result = book_gen.generate_page(page_num=idx, **page_config)
        if not result:
            logger.error(f"第{idx}页生成失败，跳过后续操作")
            break
