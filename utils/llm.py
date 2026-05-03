"""
LLM调用封装
"""
import logging
from openai import OpenAI
from typing import Optional

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM客户端封装"""

    def __init__(self, config: dict):
        self.model = config.get("model", "gpt-4o")
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2000)

        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        self.client = OpenAI(**client_kwargs)

    def chat(self, prompt: str, system: str = "", model: Optional[str] = None) -> str:
        """
        发送对话请求
        成功返回响应文本，失败抛出异常
        """
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=model or self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content

    def chat_safe(self, prompt: str, system: str = "", model: Optional[str] = None,
                  fallback: str = "{}") -> str:
        """
        发送对话请求（安全模式）
        失败时返回 fallback 值，不抛出异常
        """
        try:
            return self.chat(prompt, system, model)
        except Exception as e:
            logger.warning("LLM 调用失败: %s", e)
            return fallback

    def analyze_sentiment(self, text: str) -> str:
        """分析情感"""
        prompt = f"""分析以下文本的情感倾向，返回 positive、neutral 或 negative：

{text}

只返回一个词。"""
        return self.chat_safe(prompt, fallback="neutral").strip().lower()

    def extract_keywords(self, text: str, max_count: int = 5) -> list:
        """提取关键词"""
        prompt = f"从以下文本中提取{max_count}个关键词，返回JSON数组：\n\n{text}\n\n格式：[关键词1, 关键词2, ...]"
        import json
        try:
            result = self.chat_safe(prompt, fallback="[]")
            return json.loads(result)
        except (json.JSONDecodeError, Exception):
            return []
