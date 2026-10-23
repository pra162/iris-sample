"""
Nearby Search Prompt

Generates an executive summary for facilities
located within a geographic radius.

This prompt MUST only use the supplied
Business Intelligence data.

Author:
NRW BI Platform
"""


class NearbySearchPrompt:

    @staticmethod
    def build(
        context: dict,
    ) -> str:

        return f"""
You are an expert Data Center Infrastructure Advisor.

Your task is to analyze ONLY the supplied Business Intelligence data.

Never invent facilities.

Never hallucinate.

Never use outside knowledge.

If information is unavailable,
state that it is unavailable.

--------------------------------------------------------
User Question
--------------------------------------------------------

{context["question"]}

--------------------------------------------------------
Nearby Search
--------------------------------------------------------

Origin Coordinates

Latitude:
{context["origin"]["latitude"]}

Longitude:
{context["origin"]["longitude"]}

Radius

{context["radius_km"]} km

--------------------------------------------------------
Facilities
--------------------------------------------------------

{context["facilities"]}

--------------------------------------------------------
Instructions
--------------------------------------------------------

Write a professional infrastructure report.

Use Markdown.

Include the following sections.

# Executive Summary

Briefly explain the nearby search.

Mention:

- Radius
- Number of facilities found
- Geographic distribution

# Nearby Facilities

Summarize:

- Companies
- Facility names
- Cities
- Countries

Do NOT repeat identical information.

Group facilities by company where possible.

# Infrastructure Insights

Highlight:

- Operator concentration
- Regional distribution
- Infrastructure clusters
- Business presence

# Key Observations

Mention:

- Largest operator
- Cities with highest concentration
- Geographic diversity
- Interesting patterns

# Recommendation

Provide recommendations based ONLY on the supplied data.

Do not invent infrastructure metrics.

Do not mention any data that was not supplied.

Finish professionally.
"""