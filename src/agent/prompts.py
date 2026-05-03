# --- PROMPTS ---
RESEARCHER_PROMPT = """You are a search expert. 
Your previous search for "{topic}" was rejected with this critique: "{notes}".
Generate a more specific and effective search query to find factual data.
Return ONLY the text of the new query, no quotes or explanations."""

WRITER_PROMPT = """Write a comprehensive factual Markdown report on: "{topic}".
You have received data from MULTIPLE sources. 
Context data:
{context}
{critique_context}

Rules:
1. SYNTHESIZE information from ALL provided sources. Do not rely solely on the first source.
2. CROSS-REFERENCE the facts. Find and explicitly state any contradictions.
3. Extract only verified facts and core concepts. Ignore noise.
4. Structure dynamically with appropriate Markdown headings (##)."""

CRITIC_PROMPT = """EXAMINE THIS REPORT:

{report}

TASK: 
Evaluate the report strictly for basic factual accuracy regarding: "{topic}".

ACCEPTANCE CRITERIA:
1. Are the core facts (names, dates, basic descriptions) present and generally accurate based on the topic?
2. Are there any glaring off-topic errors?

DO NOT REQUIRE:
- Deep academic analysis or exhaustive examples.
- Perfect synthesis of every single source.

Decide the next action:
- Choose 'writer' ONLY if there are obvious factual errors or poorly synthesized data.
- Choose 'researcher' ONLY if critical facts are entirely missing.
- Choose 'end' if the report is generally factually correct and answers the prompt."""
