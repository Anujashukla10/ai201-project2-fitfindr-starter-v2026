"""
Capstone test scenarios — 3 trials each, matching criteria.md.
"""

SCENARIOS = [
    {"name": "vague query triggers clarification", "query": "something cute and cheap",
     "wardrobe": "example", "criterion": 1},
    {"name": "vague query triggers clarification v2", "query": "cool stuff",
     "wardrobe": "example", "criterion": 1},
    {"name": "vague query triggers clarification v3", "query": "nice things",
     "wardrobe": "example", "criterion": 1},

    {"name": "specific query proceeds normally", "query": "vintage graphic tee under $30",
     "wardrobe": "example", "criterion": 2},
    {"name": "specific query proceeds normally v2", "query": "90s track jacket in size M",
     "wardrobe": "example", "criterion": 2},
    {"name": "specific query proceeds normally v3", "query": "leather belt",
     "wardrobe": "example", "criterion": 2},

    {"name": "clarifying question is actionable", "query": "something trendy",
     "wardrobe": "example", "criterion": 3},
    {"name": "clarifying question is actionable v2", "query": "whatever looks good",
     "wardrobe": "example", "criterion": 3},
    {"name": "clarifying question is actionable v3", "query": "anything nice",
     "wardrobe": "example", "criterion": 3},

    {"name": "regression: matching query completes", "query": "denim jacket under $50",
     "wardrobe": "example", "criterion": 4},
    {"name": "regression: matching query completes v2", "query": "oversized cardigan under $40",
     "wardrobe": "example", "criterion": 4},
    {"name": "regression: matching query completes v3", "query": "platform sneakers size 8",
     "wardrobe": "example", "criterion": 4},

    {"name": "latency within target", "query": "silk slip dress in midi length under $40",
     "wardrobe": "example", "criterion": 5},
    {"name": "latency within target v2", "query": "vintage graphic tee under $30",
     "wardrobe": "example", "criterion": 5},
    {"name": "latency within target v3", "query": "denim jacket under $50",
     "wardrobe": "example", "criterion": 5},
]