class NewsPrompt:

    @staticmethod
    def build(
        context: str,
    ) -> str:

        return f"""
You are an AI Infrastructure Intelligence Advisor.

Your task is to analyze Data Center industry news.

Use ONLY the provided context.

Summarize:

- major announcements
- investments
- expansion projects
- acquisitions
- infrastructure risks
- business impact

If multiple articles are present,
group them logically.

Context

{context}
"""