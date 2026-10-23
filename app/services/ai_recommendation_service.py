"""
AI Recommendation Service

Generates AI-powered recommendations
for Data Center Site Intelligence.

Model:
    GPT-5.5 Mini

Author:
    NRW BI Platform
"""

import os

from openai import OpenAI
from app.ai.prompts.site_analysis_prompt import SiteAnalysisPrompt


class AIRecommendationService:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.model = os.getenv(
            "OPENAI_MODEL",
            "gpt-4.1-mini",
        )

    # =====================================================
    # Public
    # =====================================================

    def generate(
        self,
        prompt: str,
    ) -> str:

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text.strip()
