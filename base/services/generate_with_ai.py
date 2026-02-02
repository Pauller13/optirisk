import os
import json
import logging
from typing import Any, List, Dict
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv


load_dotenv()
logger = logging.getLogger(__name__)


class GenerateIA:
    """Thin wrapper around LangChain/OpenAI to generate structured outputs for the frontend."""

    def __init__(self, temperature: float = 0.2, max_tokens: int = 800):
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY not set in environment. LLM calls may fail.")

        # Initialize chat model correctly
        self.llm = init_chat_model(
            "gpt-4.1",
            temperature=temperature,
            max_tokens=max_tokens,
        )
        self.max_tokens = max_tokens

    def _call_llm(self, prompt: str) -> str:
        logger.debug("LLM prompt: %s", prompt[:400])
        try:
            result = self.llm.invoke(prompt)
            content = result.content if hasattr(result, "content") else str(result)
            logger.debug("LLM result: %s", content[:400])
            return content
        except Exception as e:
            logger.exception("LLM call failed: %s", e)
            raise

    # ---------- Helpers ----------

    def _safe_json_load(self, text: str, default):
        try:
            return json.loads(text)
        except Exception:
            try:
                start = text.index("{")
                end = text.rindex("}") + 1
                return json.loads(text[start:end])
            except Exception:
                return default

    def _safe_json_array(self, text: str):
        try:
            return json.loads(text)
        except Exception:
            try:
                start = text.index("[")
                end = text.rindex("]") + 1
                return json.loads(text[start:end])
            except Exception:
                return []

    # ---------- Generators ----------

    def generate_swot(self, context: str) -> Dict[str, List[str]]:
        prompt = (
            f"You are a security risk analyst. Given the professional context: '{context}', "
            "produce a concise SWOT analysis.\n"
            "Return ONLY valid JSON with keys: forces, faiblesses, opportunites, menaces. "
            "Each value must be a list of short strings."
        )

        text = self._call_llm(prompt)
        data = self._safe_json_load(text, {})

        return {
            "forces": data.get("forces", []),
            "faiblesses": data.get("faiblesses", []),
            "opportunites": data.get("opportunites", []),
            "menaces": data.get("menaces", []),
        }

    def generate_strategic_scenarios(
        self,
        business_values: List[Dict[str, Any]],
        risk_sources: List[Dict[str, Any]],
        max_scenarios: int = 3,
    ) -> List[Dict[str, Any]]:

        bv_sample = [bv.get("name") or bv.get("nom") for bv in business_values][:3]
        rs_sample = [rs.get("name") or rs.get("nom") for rs in risk_sources][:3]

        prompt = (
            f"You are a security analyst. Based on the business values: {bv_sample} "
            f"and risk sources: {rs_sample}, propose up to {max_scenarios} high-level "
            "strategic scenarios.\n"
            "Return ONLY a JSON array. Each scenario must have: "
            "id, title, targetBusinessValue, riskSource, attackPath, fearedEvent, gravity, "
            "stakeholders (array of objects with name, exposure, reliability, threatLevel)."
        )

        text = self._call_llm(prompt)
        return self._safe_json_array(text)

    def suggest_assets(self, context: str, max_assets: int = 6) -> List[Dict[str, Any]]:
        prompt = (
            f"You are a security architect. For context '{context}', suggest up to {max_assets} "
            "supporting assets (servers, applications, data, equipment).\n"
            "Return ONLY a JSON array with objects having: "
            "name, type, description, criticality."
        )

        text = self._call_llm(prompt)
        return self._safe_json_array(text)

    def generate_measures(
        self,
        risks: List[Dict[str, Any]],
        max_measures: int = 8,
    ) -> List[Dict[str, Any]]:

        prompt = (
            f"You are a cybersecurity consultant. Given the following risks:\n"
            f"{json.dumps(risks)[:1000]}\n"
            f"Suggest up to {max_measures} security measures.\n"
            "Return ONLY a JSON array with fields: "
            "id, title, category, description, priority, cost, "
            "implementationTime, responsible, status."
        )

        text = self._call_llm(prompt)
        return self._safe_json_array(text)
