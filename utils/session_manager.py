"""Session manager — stores and clears in-memory session data with zero persistence."""


def save_demographics(session, data):
    """Save optional demographic info into the session."""
    session["demographics"] = {
        "age_range": data.get("age_range", "Prefer not to say"),
        "gender": data.get("gender", "Prefer not to say"),
        "occupation": data.get("occupation", "Prefer not to say"),
    }


def save_selected_types(session, types):
    """Save list of selected personality test category keys."""
    session["selected_types"] = types


def save_answers(session, answers):
    """Save all Q&A pairs. `answers` is a dict of {question_id: chosen_option}."""
    session["answers"] = answers


def get_session_data(session):
    """Retrieve all session data as a single dict for prompt construction."""
    return {
        "demographics": session.get("demographics", {}),
        "selected_types": session.get("selected_types", []),
        "answers": session.get("answers", {}),
    }


def clear_session(session):
    """Wipe all personality-related session keys. Called after result is shown."""
    keys_to_clear = ["demographics", "selected_types", "answers", "result"]
    for key in keys_to_clear:
        session.pop(key, None)
