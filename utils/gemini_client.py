"""Gemini API client for generating personality analysis reports."""

from html import escape

import google.generativeai as genai
from config import Config

# Category display names for the prompt
CATEGORY_NAMES = {
    "social": "Social Personality",
    "mental_health": "Mental Wellbeing",
    "big_five": "Big Five (OCEAN)",
    "emotional_intelligence": "Emotional Intelligence (EQ)",
    "stress_burnout": "Stress & Burnout Tendency",
    "career": "Work/Career Personality",
    "relationship": "Relationship & Attachment Style",
    "self_esteem": "Self-Esteem & Confidence",
}

PLACEHOLDER_API_KEYS = {
    "your_gemini_api_key_here",
}

SYSTEM_INSTRUCTION = """You are a friendly, empathetic personality analyst. Based on the user's demographic context and their answers to personality questions, generate a warm, insightful, non-clinical personality report.

IMPORTANT RULES:
1. For any mental-health-related category, NEVER use diagnostic language (never say "you have depression" or "you have anxiety"). Instead, describe tendencies gently and ALWAYS recommend professional consultation if answers suggest elevated distress.
2. Structure the output as valid HTML using the following format for EACH selected personality type:
   - A <div class="result-category"> wrapper
   - An <h2> header with the category name
   - A <p class="result-summary"> with a 2-3 sentence summary
   - A <div class="result-traits"> containing 3-5 <span class="trait-chip"> elements for key traits
   - A <p> with 2-3 sentences of deeper insight
3. After ALL categories, include a <div class="result-closing"> with one encouraging, uplifting closing note.
4. If the mental wellbeing answers suggest elevated distress, include a <div class="distress-banner"> with a gentle, supportive message recommending professional help. The banner should include the text: "If you're going through a tough time, talking to a licensed mental health professional can make a real difference. You deserve support."
5. Keep the tone warm, supportive, and conversational — like a caring friend who happens to know psychology.
6. Personalize the language based on the demographic info (e.g., use relatable examples for a student vs. a working professional).
7. Do NOT wrap the output in ```html``` code blocks. Return raw HTML only.
8. Use gender-neutral language unless the user specified a gender."""


def generate_analysis(demographics, selected_types, answers, questions_map):
    """
    Generate a personality analysis report using the Gemini API.

    Args:
        demographics: dict with age_range, gender, occupation
        selected_types: list of category keys
        answers: dict of {question_id: chosen_option_text}
        questions_map: dict of {question_id: question_text}

    Returns:
        str: HTML-formatted analysis report
    """
    api_key = (Config.GEMINI_API_KEY or "").strip()
    if not api_key:
        return _generate_fallback_report(
            selected_types,
            error_msg="GEMINI_API_KEY is missing from your .env file.",
        )

    if api_key in PLACEHOLDER_API_KEYS:
        return _generate_fallback_report(
            selected_types,
            error_msg=(
                "GEMINI_API_KEY is still set to the sample placeholder value. "
                "Replace it with a real Google AI Studio API key."
            ),
        )

    genai.configure(api_key=api_key)

    # Build the user prompt with all context
    prompt = _build_prompt(demographics, selected_types, answers, questions_map)

    try:
        model = genai.GenerativeModel(
            "gemini-flash-latest",
            system_instruction=SYSTEM_INSTRUCTION,
        )
        response = model.generate_content(prompt)
        result_html = (response.text or "").strip()
        if not result_html:
            return _generate_fallback_report(
                selected_types,
                error_msg="Gemini returned an empty response.",
            )
        return result_html
    except Exception as e:
        import sys
        print(f"Gemini API error: {e}", file=sys.stderr)
        return _generate_fallback_report(selected_types, error_msg=str(e))


def _build_prompt(demographics, selected_types, answers, questions_map):
    """Construct the structured prompt with demographics and all Q&A pairs."""
    lines = []
    lines.append("## User Context")
    lines.append(f"- Age Range: {demographics.get('age_range', 'Not provided')}")
    lines.append(f"- Gender: {demographics.get('gender', 'Not provided')}")
    lines.append(f"- Occupation: {demographics.get('occupation', 'Not provided')}")
    lines.append("")
    lines.append("## Selected Personality Categories")
    for cat in selected_types:
        lines.append(f"- {CATEGORY_NAMES.get(cat, cat)}")
    lines.append("")
    lines.append("## Questions and Answers")

    # Group answers by category
    for cat in selected_types:
        cat_name = CATEGORY_NAMES.get(cat, cat)
        lines.append(f"\n### {cat_name}")
        for qid, answer in answers.items():
            # Match question IDs to their category
            prefix_map = {
                "social": "social_",
                "mental_health": "mh_",
                "big_five": "bf_",
                "emotional_intelligence": "eq_",
                "stress_burnout": "sb_",
                "career": "career_",
                "relationship": "rel_",
                "self_esteem": "se_",
            }
            prefix = prefix_map.get(cat, "")
            if qid.startswith(prefix):
                q_text = questions_map.get(qid, qid)
                lines.append(f"- Q: {q_text}")
                lines.append(f"  A: {answer}")

    lines.append("")
    lines.append(
        "Please generate a comprehensive personality analysis report based on the above."
    )

    return "\n".join(lines)


def _generate_fallback_report(selected_types, error_msg=None):
    """Generate a placeholder report when the Gemini API is unavailable."""
    html_parts = []
    for cat in selected_types:
        cat_name = CATEGORY_NAMES.get(cat, cat)
        error_display = (
            "<p style='color: red; font-size: 0.9em; margin-top: 10px;'>"
            f"Error details: {escape(error_msg)}"
            "</p>"
            if error_msg
            else ""
        )
        
        html_parts.append(f"""
        <div class="result-category">
            <h2>{cat_name}</h2>
            <p class="result-summary">
                We weren't able to connect to our AI analysis engine at this time.
                This could be because the API key hasn't been configured yet.
            </p>
            <div class="result-traits">
                <span class="trait-chip">Analysis Pending</span>
            </div>
            <p>Please ensure the GEMINI_API_KEY is set in your .env file and try again.
            Your answers were interesting — we'd love to give you a full analysis!</p>
            {error_display}
        </div>
        """)

    html_parts.append("""
    <div class="result-closing">
        <p>💡 <strong>Setup Tip:</strong> Add your Google Gemini API key to the
        <code>.env</code> file to enable AI-powered personality analysis.
        Get a key at <a href="https://makersuite.google.com/app/apikey" target="_blank">Google AI Studio</a>.</p>
    </div>
    """)

    return "\n".join(html_parts)
