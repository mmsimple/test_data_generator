"""
Markdown Schema 解析器
使用 AI API 将 Markdown 数据库表结构文档转换为 YAML 配置
"""

import openai
import yaml
from typing import Optional
from pathlib import Path
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import logging

from .prompts import SCHEMA_PARSER_SYSTEM_PROMPT, build_user_prompt

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SchemaParseError(Exception):
    """Schema 解析错误"""

    pass


class SchemaValidationError(Exception):
    """Schema 验证错误"""

    pass


class SchemaParser:
    """Markdown Schema 解析器"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        api_base: Optional[str] = None,
        timeout: int = 120,
        max_retries: int = 3,
        verbose: bool = False,
    ):
        """
        初始化解析器

        Args:
            api_key: OpenAI API 密钥
            model: 使用的模型名称
            api_base: API base URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            verbose: 是否显示详细输出
        """
        import os

        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API 密钥未设置。请设置 OPENAI_API_KEY 环境变量或通过 --api-key 参数提供。"
            )

        self.model = model
        self.api_base = api_base
        self.timeout = timeout
        self.max_retries = max_retries
        self.verbose = verbose

        # 初始化 OpenAI 客户端
        self.client = openai.OpenAI(
            api_key=self.api_key, base_url=self.api_base, timeout=self.timeout
        )

        self.system_prompt = SCHEMA_PARSER_SYSTEM_PROMPT

        if self.verbose:
            logger.info(
                f"✓ 初始化解析器: model={model}, timeout={timeout}s, max_retries={max_retries}"
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (openai.APITimeoutError, openai.APIConnectionError, RuntimeError)
        ),
        reraise=True,
    )
    def _call_ai_api(self, markdown_content: str) -> str:
        """
        调用 AI API（带重试）

        Args:
            markdown_content: Markdown 文档内容

        Returns:
            YAML 配置字符串
        """
        user_prompt = build_user_prompt(markdown_content)

        if self.verbose:
            logger.info("\n🤖 发送请求到 AI API...")
            logger.info(f"   Model: {self.model}")
            logger.info(f"   Content length: {len(markdown_content)} 字符")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,  # 低温度确保确定性输出
                max_tokens=4000,  # 足够大的输出空间
                response_format={"type": "text"},  # 文本格式输出
            )

            yaml_content = response.choices[0].message.content.strip()

            # 清理可能的 markdown 代码块标记
            if yaml_content.startswith("```yaml"):
                yaml_content = yaml_content[7:]
            if yaml_content.startswith("```"):
                yaml_content = yaml_content[3:]
            if yaml_content.endswith("```"):
                yaml_content = yaml_content[:-3]
            yaml_content = yaml_content.strip()

            if self.verbose:
                usage = response.usage
                logger.info(f"✓ API 调用成功")
                logger.info(f"   Prompt tokens: {usage.prompt_tokens}")
                logger.info(f"   Completion tokens: {usage.completion_tokens}")
                logger.info(f"   Total tokens: {usage.total_tokens}")
                logger.info(f"   Output length: {len(yaml_content)} 字符")

            return yaml_content

        except openai.RateLimitError as e:
            logger.warning(f"⚠ API 速率限制: {e}")
            raise RuntimeError(f"Rate limit exceeded: {e}")

        except openai.APITimeoutError as e:
            logger.warning(f"⚠ API 超时: {e}")
            raise

        except openai.APIConnectionError as e:
            logger.warning(f"⚠ API 连接错误: {e}")
            raise

        except openai.APIError as e:
            logger.error(f"❌ API 错误: {e}")
            raise SchemaParseError(f"API 调用失败: {e}")

    def parse_markdown_to_yaml(self, markdown_file: str) -> str:
        """
        将 Markdown 文件解析为 YAML 配置

        Args:
            markdown_file: Markdown 文件路径

        Returns:
            YAML 配置字符串

        Raises:
            FileNotFoundError: 文件不存在
            SchemaParseError: 解析失败
            SchemaValidationError: YAML 验证失败
        """
        # 读取 Markdown 文件
        path = Path(markdown_file)
        if not path.exists():
            raise FileNotFoundError(f"Markdown 文件不存在: {markdown_file}")

        markdown_content = path.read_text(encoding="utf-8")

        if self.verbose:
            logger.info(f"✓ 读取文件: {markdown_file} ({len(markdown_content)} 字符)")

        # 调用 AI API
        yaml_content = self._call_ai_api(markdown_content)

        # 验证 YAML
        self._validate_yaml(yaml_content)

        return yaml_content

    def _validate_yaml(self, yaml_content: str) -> None:
        """
        验证生成的 YAML 配置

        Args:
            yaml_content: YAML 内容字符串

        Raises:
            SchemaValidationError: 验证失败
        """
        try:
            # 解析 YAML
            config = yaml.safe_load(yaml_content)

            # 基本结构验证
            if not isinstance(config, dict):
                raise SchemaValidationError("输出不是有效的字典")

            if "version" not in config:
                raise SchemaValidationError("缺少必需字段: version")

            # 验证 fields 或 tables 存在
            has_fields = "fields" in config and config["fields"]
            has_tables = "tables" in config and config["tables"]

            if not has_fields and not has_tables:
                raise SchemaValidationError("必须包含 fields 或 tables")

            # 验证字段配置
            if has_fields:
                for field_name, field_config in config["fields"].items():
                    if "type" not in field_config:
                        raise SchemaValidationError(f"字段 {field_name} 缺少 type")

            if has_tables:
                for table_name, table_config in config["tables"].items():
                    if "fields" not in table_config or not table_config["fields"]:
                        raise SchemaValidationError(f"表 {table_name} 缺少 fields")

                    for field_name, field_config in table_config["fields"].items():
                        if "type" not in field_config:
                            raise SchemaValidationError(
                                f"表 {table_name} 的字段 {field_name} 缺少 type"
                            )

            if self.verbose:
                logger.info("✓ YAML 配置验证通过")

        except yaml.YAMLError as e:
            raise SchemaValidationError(f"YAML 解析失败: {e}")

    def parse_markdown_to_dict(self, markdown_file: str) -> dict:
        """
        将 Markdown 文件解析为配置字典

        Args:
            markdown_file: Markdown 文件路径

        Returns:
            配置字典
        """
        yaml_content = self.parse_markdown_to_yaml(markdown_file)
        return yaml.safe_load(yaml_content)
