import json
import re

import anthropic
import structlog

from app.config import get_settings

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert resume analyst and career coach.
Analyze the provided resume against the job description and respond with valid JSON only.
No markdown, no explanation, no code fences — just the raw JSON object."""

ANALYSIS_PROMPT = """Analyze this resume against the job description below.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return a JSON object with exactly this structure:
{{
  "overall_score": <integer 0-100>,
  "categories": [
    {{"name": "Skills Match", "score": <integer 0-100>, "rationale": "<one sentence>"}},
    {{"name": "Experience Level", "score": <integer 0-100>, "rationale": "<one sentence>"}},
    {{"name": "Education", "score": <integer 0-100>, "rationale": "<one sentence>"}},
    {{"name": "Keywords", "score": <integer 0-100>, "rationale": "<one sentence>"}},
    {{"name": "ATS Formatting", "score": <integer 0-100>, "rationale": "<one sentence>"}}
  ],
  "skills": ["<skill1>", "<skill2>"],
  "experience": [
    {{"title": "<job title>", "company": "<company>", "duration": "<e.g. 2021-2024>"}}
  ],
  "education": [
    {{"degree": "<degree name>", "institution": "<university>", "year": "<graduation year>"}}
  ],
  "suggestions": [
    "<specific actionable improvement 1>",
    "<specific actionable improvement 2>",
    "<specific actionable improvement 3>"
  ]
}}"""


def analyze_resume(resume_text: str, job_description: str) -> dict:  # type: ignore[type-arg]
    """Call Anthropic API directly to analyze resume against job description."""
    settings = get_settings()

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key.strip())

    user_message = ANALYSIS_PROMPT.format(
        resume_text=resume_text[:6000],
        job_description=job_description[:2000],
    )

    logger.info("anthropic_invoke", model=settings.anthropic_model_id)

    try:
        response = client.messages.create(
            model=settings.anthropic_model_id,
            max_tokens=2000,
            temperature=0.1,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ],
        )
    except anthropic.APIStatusError as e:
        logger.error("anthropic_failed", error=str(e), status=e.status_code)
        raise RuntimeError(f"AI analysis failed: {e}") from e
    except anthropic.APIConnectionError as e:
        logger.error("anthropic_connection_error", error=str(e), cause=repr(e.__cause__))
        raise RuntimeError("AI analysis timed out — try again in 30 seconds") from e

    content = response.content[0].text

    # Strip markdown fences if model adds them
    content = re.sub(r"```json|```", "", content).strip()

    # Find JSON object in response
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        content = match.group(0)

    logger.info("anthropic_response_received", content_length=len(content))

    try:
        result: dict = json.loads(content)  # type: ignore[type-arg]
    except json.JSONDecodeError as e:
        logger.error("anthropic_parse_failed", content=content[:200])
        raise RuntimeError("Failed to parse AI response — try again") from e

    logger.info("anthropic_complete", overall_score=result.get("overall_score"))
    return result
