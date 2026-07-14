"""Personality Analyzer — Flask application."""

import json
import os
import time
from collections import defaultdict
from datetime import timedelta

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from config import Config
from utils.gemini_client import generate_analysis
from utils.session_manager import (
    clear_session,
    get_session_data,
    save_answers,
    save_demographics,
    save_selected_types,
)

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
app.permanent_session_lifetime = timedelta(seconds=Config.PERMANENT_SESSION_LIFETIME)

# ── In-memory rate limiter ──────────────────────────────────────────────────────
rate_limit_store = defaultdict(list)


def is_rate_limited(ip):
    """Check if an IP has exceeded the rate limit for Gemini API calls."""
    now = time.time()
    window = Config.RATE_LIMIT_WINDOW_SECONDS
    max_requests = Config.RATE_LIMIT_MAX_REQUESTS

    # Clean old entries
    rate_limit_store[ip] = [t for t in rate_limit_store[ip] if now - t < window]

    if len(rate_limit_store[ip]) >= max_requests:
        return True

    rate_limit_store[ip].append(now)
    return False


# ── Question loader ─────────────────────────────────────────────────────────────
QUESTIONS_DIR = os.path.join(os.path.dirname(__file__), "questions")


def load_questions(category, count=10):
    """Load questions from JSON file for a given category and count."""
    filepath = os.path.join(QUESTIONS_DIR, category, f"q{count}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# ── Routes ──────────────────────────────────────────────────────────────────────


@app.route("/")
def index():
    """Landing page with rotating hero messages and privacy notice."""
    return render_template("index.html")


@app.route("/pretest", methods=["GET", "POST"])
def pretest():
    """Pre-test demographic info form (all optional)."""
    if request.method == "POST":
        save_demographics(
            session,
            {
                "age_range": request.form.get("age_range", "Prefer not to say"),
                "gender": request.form.get("gender", "Prefer not to say"),
                "occupation": request.form.get("occupation", "Prefer not to say"),
            },
        )
        session.modified = True
        return redirect(url_for("select_types"))
    return render_template("pretest_form.html")


@app.route("/select-types", methods=["GET", "POST"])
def select_types():
    """Multi-select personality test categories."""
    if request.method == "POST":
        selected = request.form.getlist("categories")
        if not selected:
            return render_template(
                "select_types.html",
                categories=Config.CATEGORIES,
                error="Please select at least one category.",
            )
        save_selected_types(session, selected)
        session.modified = True
        return redirect(url_for("test"))
    return render_template("select_types.html", categories=Config.CATEGORIES)


@app.route("/test")
def test():
    """Test-taking page — JS-driven single-page experience."""
    selected = session.get("selected_types", [])
    if not selected:
        return redirect(url_for("select_types"))
    return render_template(
        "test.html", selected_types=selected, categories=Config.CATEGORIES
    )


@app.route("/api/questions")
def api_questions():
    """API endpoint returning merged question sets for selected categories."""
    selected = session.get("selected_types", [])
    if not selected:
        return jsonify({"error": "No categories selected"}), 400

    question_sets = []
    for cat in selected:
        questions = load_questions(cat)
        cat_info = Config.CATEGORIES.get(cat, {})
        question_sets.append(
            {
                "category": cat,
                "category_name": cat_info.get("name", cat),
                "category_icon": cat_info.get("icon", "📋"),
                "questions": questions,
            }
        )

    return jsonify({"question_sets": question_sets})


@app.route("/api/submit", methods=["POST"])
def api_submit():
    """Receive all answers, call Gemini API, return analysis HTML."""
    # Rate limiting
    client_ip = request.remote_addr
    if is_rate_limited(client_ip):
        return (
            jsonify(
                {
                    "error": "Too many requests. Please wait a moment before trying again."
                }
            ),
            429,
        )

    data = request.get_json()
    if not data or "answers" not in data:
        return jsonify({"error": "No answers provided"}), 400

    answers = data["answers"]
    save_answers(session, answers)
    session.modified = True

    session_data = get_session_data(session)
    selected_types = session_data["selected_types"]
    demographics = session_data["demographics"]

    # Build questions map {id: text} for prompt context
    questions_map = {}
    for cat in selected_types:
        questions = load_questions(cat)
        for q in questions:
            questions_map[q["id"]] = q["text"]

    # Generate analysis via Gemini
    result_html = generate_analysis(
        demographics, selected_types, answers, questions_map
    )

    # Store result in session for the result page
    session["result"] = result_html
    session.modified = True

    return jsonify({"success": True, "redirect": url_for("result")})


@app.route("/result")
def result():
    """Display the personality analysis result, then clear session."""
    result_html = session.get("result", None)
    if not result_html:
        return redirect(url_for("index"))

    selected_types = session.get("selected_types", [])
    demographics = session.get("demographics", {})

    # Clear session data after rendering
    clear_session(session)
    session.modified = True

    return render_template(
        "result.html",
        result_html=result_html,
        selected_types=selected_types,
        demographics=demographics,
        categories=Config.CATEGORIES,
    )


@app.route("/privacy")
def privacy():
    """Privacy policy page."""
    return render_template("privacy.html")


# ── Main ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
