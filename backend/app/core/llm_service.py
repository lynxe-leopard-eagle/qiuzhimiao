"""LLM 统一服务层 — 支持多模型路由与 fallback。

支持的模型：
  - DeepSeek (https://api.deepseek.com/v1) — 主力推荐，性价比高
  - 豆包/火山引擎 (https://ark.cn-beijing.volces.com/api/v3)
  - 通义千问 (https://dashscope.aliyuncs.com/compatible-mode/v1)

使用方式：
  1. 在 .env 中设置对应 API Key 即可启用
  2. 未设置或请求失败时自动回退到本地模拟模式
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """单个 LLM 提供商的配置。"""
    name: str
    api_key: str = ""
    base_url: str = ""
    model: str = "default"
    max_tokens: int = 2048
    temperature: float = 0.7


class LLMService:
    """统一 LLM 调用服务，支持多 provider + 自动 fallback。"""

    _DEFAULT_MODELS = {
        "deepseek": "deepseek-chat",
        "doubao": "ep-20240515162406-z8l7h",  # 需要按实际 endpoint_id 替换
        "qwen": "qwen-turbo",
        "mock": "",
    }

    def __init__(self):
        from app.core.config import settings

        self._providers: list[LLMConfig] = []
        # 按 priority 排序：deepseek > doubao > qwen > mock
        if settings.DEEPSEEK_API_KEY:
            self._providers.append(LLMConfig(
                name="deepseek",
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL or "https://api.deepseek.com/v1",
                model=self._DEFAULT_MODELS["deepseek"],
            ))
        if settings.DOUBAO_API_KEY:
            self._providers.append(LLMConfig(
                name="doubao",
                api_key=settings.DOUBAO_API_KEY,
                base_url=settings.DOUBAO_BASE_URL or "https://ark.cn-beijing.volces.com/api/v3",
                model=self._DEFAULT_MODELS["doubao"],
            ))
        if settings.QWEN_API_KEY:
            self._providers.append(LLMConfig(
                name="qwen",
                api_key=settings.QWEN_API_KEY,
                base_url=settings.QWEN_BASE_URL or "https://dashscope.aliyuncs.com/compatible-mode/v1",
                model=self._DEFAULT_MODELS["qwen"],
            ))
        # mock 始终作为最后的 fallback
        self._providers.append(LLMConfig(name="mock"))

        self._available_providers: list[str] = [
            p.name for p in self._providers if p.name != "mock"
        ]
        logger.info("LLM 服务初始化完成，可用 providers: %s", self._available_providers)

    @property
    def is_real_llm_available(self) -> bool:
        """是否有真实 LLM 可用。"""
        return len(self._available_providers) > 0

    async def chat(
        self,
        messages: list[dict],
        *,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict | None = None,
        timeout: float = 30.0,
    ) -> str:
        """同步调用 LLM，返回文本回复。

        Args:
            messages: 对话消息列表 [{"role": "user", "content": "..."}]
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大 token 数
            response_format: 输出格式约束 {"type": "json_object"}
            timeout: 超时时间(秒)

        Returns:
            模型返回的文本内容
        """
        if system_prompt:
            full_messages = [{"role": "system", "content": system_prompt}] + messages
        else:
            full_messages = messages

        for provider in self._providers:
            try:
                result = await self._call_provider(
                    provider, full_messages, temperature=temperature,
                    max_tokens=max_tokens, response_format=response_format, timeout=timeout,
                )
                return result
            except Exception as e:
                logger.warning("Provider %s 调用失败: %s", provider.name, e)
                continue

        # 所有 provider 都失败后回退到 mock
        logger.warning("所有 LLM provider 失败，使用 mock 回退")
        return self._fallback_response(messages[-1].get("content", "") if messages else "")

    async def chat_stream(
        self,
        messages: list[dict],
        *,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        """流式调用 LLM，异步生成 SSE 文本块。

        Yields:
            字符串文本片段
        """
        if system_prompt:
            full_messages = [{"role": "system", "content": system_prompt}] + messages
        else:
            full_messages = messages

        for provider in self._providers:
            if provider.name == "mock":
                break  # 流式模式下 mock 单独处理
            try:
                async for chunk in self._call_provider_stream(
                    provider, full_messages,
                    temperature=temperature, max_tokens=max_tokens,
                ):
                    yield chunk
                return
            except Exception as e:
                logger.warning("Provider %s 流式调用失败: %s", provider.name, e)
                continue

        # 回退到 mock 流式输出
        text = self._fallback_response(messages[-1].get("content", "") if messages else "")
        # 模拟打字机效果
        words = list(text)
        chunk_size = max(1, len(words) // 20)
        for i in range(0, len(words), chunk_size):
            yield "".join(words[i : i + chunk_size])
            await asyncio.sleep(0.05)

    async def _call_provider(
        self,
        provider: LLMConfig,
        messages: list[dict],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict | None = None,
        timeout: float = 30.0,
    ) -> str:
        """调用单个 provider。"""
        if provider.name == "mock":
            return self._fallback_response(
                messages[-1].get("content", "") if messages else ""
            )

        body: dict = {
            "model": provider.model,
            "messages": messages,
            "temperature": temperature or provider.temperature,
            "max_tokens": max_tokens or provider.max_tokens,
        }
        if response_format:
            body["response_format"] = response_format

        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                f"{provider.base_url}/chat/completions",
                json=body,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def _call_provider_stream(
        self,
        provider: LLMConfig,
        messages: list[dict],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        """流式调用单个 provider。"""
        body: dict = {
            "model": provider.model,
            "messages": messages,
            "temperature": temperature or provider.temperature,
            "max_tokens": max_tokens or provider.max_tokens,
            "stream": True,
        }

        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{provider.base_url}/chat/completions",
                json=body,
                headers=headers,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    line = line.strip()
                    if not line.startswith("data: ") or line == "data: [DONE]":
                        continue
                    try:
                        chunk_data = json.loads(line[6:])
                        delta = chunk_data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

    @staticmethod
    def _fallback_response(user_message: str) -> str:
        """Mock 回退响应 — 当没有真实 LLM 时使用。"""
        user_lower = user_message.lower()[:100]

        if any(kw in user_lower for kw in ["简历", "优化", "诊断"]):
            return (
                "根据你提供的简历信息，我建议从以下几个方面进行优化：\n\n"
                "**结构完整性**：确保简历包含教育背景、工作经历、项目经验、技能清单等核心板块。\n\n"
                "**量化成果**：用具体数字描述你的贡献，如「提升系统性能 30%」「支撑日均 QPS 10w+」。\n\n"
                "**关键词匹配**：根据目标岗位 JD 调整技能关键词密度，提升 ATS 通过率。\n\n"
                "**项目深度**：按 STAR 法则描述核心项目，突出你的技术决策和实际影响。\n\n"
                "建议上传完整简历后进行详细诊断，获取更精准的分析结果。"
            )

        if any(kw in user_lower for kw in ["面试", "模拟", "练习"]):
            return (
                "关于模拟面试，我有以下建议：\n\n"
                "1. **自我介绍**：准备 1 分钟和 3 分钟两个版本，突出核心竞争力。\n\n"
                "2. **项目深挖**：挑选 2-3 个最有代表性的项目，准备详细的技术实现方案。\n\n"
                "3. **技术追问**：熟悉常见技术问题的深度回答框架（原理→实践→优化）。\n\n"
                "4. **行为面试**：提前准备 3-5 个 STAR 法则案例（情境、任务、行动、结果）。\n\n"
                "建议先上传简历，这样我可以根据你的背景定制更针对性的面试题目和反馈。"
            )

        if any(kw in user_lower for kw in ["岗位", "匹配", "jd", "职位"]):
            return (
                "针对岗位分析与简历匹配，我的建议是：\n\n"
                "1. **提取核心要求**：从 JD 中识别硬性条件（学历/年限）和软性要求（技能栈）。\n\n"
                "2. **对标自身**：将简历中的经历、技能逐一映射到岗位要求上。\n\n"
                "3. **找差距**：明确哪些能力已达标、哪些需要补充、哪些可以迁移。\n\n"
                "4. **制定计划**：针对差距制定具体的学习和实践路径。\n\n"
                "你可以粘贴目标岗位的 JD，我来帮你做详细的匹配度分析和改进建议。"
            )

        if any(kw in user_lower for kw in ["报告", "总结", "作战"]):
            return (
                "## 求职作战报告\n\n"
                "**当前状态**：请上传简历并完成至少一次模拟面试，我将为你生成个性化的作战报告。\n\n"
                "**下一步建议**：\n"
                "- 上传简历，建立求职资产库\n"
                "- 进行一轮模拟面试，了解当前水平\n"
                "- 记录投递进度，管理求职节奏\n"
                "- 定期复盘，持续优化回答策略"
            )

        return (
            "你好！我是你的 AI 求职教练，很高兴能帮助你。我可以提供以下方面的支持：\n\n"
            "📋 **简历诊断与优化** — ATS 分析、关键词优化、结构完整性检查\n\n"
            "🎯 **岗位分析与匹配** — JD 解读、技能差距评估、匹配度量化\n\n"
            "💬 **模拟面试训练** — 多轮面试练习、实时评判反馈、针对性追问\n\n"
            "📊 **复盘成长追踪** — 面试复盘、能力雷达图、成长趋势曲线\n\n"
            "请问你想从哪个方面开始？或者直接告诉我你的具体需求。"
        )


# 全局单例
_llm_service_instance: LLMService | None = None


def get_llm_service() -> LLMService:
    """获取全局 LLM 服务单例。"""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance
