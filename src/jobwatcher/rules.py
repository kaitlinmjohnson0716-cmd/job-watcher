"""Title rule: is a posting a Marketing Data Analyst role?

A title is in role when it contains BOTH
  * an analysis word:   analyst, analytics, insights, measurement, data scientist
  * a marketing word:   marketing, growth, acquisition, lifecycle, campaign, brand,
                        crm, martech, advertising, performance marketing, ...
Matching is case-insensitive on whole words.
"""
import re

ANALYSIS = r"analyst|analytics|insights?|measurement|data scientist"
MARKETING = (r"marketing|growth|acquisition|lifecycle|campaigns?|brand|crm|martech|"
             r"advertising|demand gen(?:eration)?|customer analytics|digital|seo|sem")

_ANALYSIS = re.compile(rf"\b(?:{ANALYSIS})\b", re.I)
_MARKETING = re.compile(rf"\b(?:{MARKETING})\b", re.I)


def in_role(title):
    title = title or ""
    return bool(_ANALYSIS.search(title) and _MARKETING.search(title))
