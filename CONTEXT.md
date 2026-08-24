# DeepThink Context File

This file provides architectural context and logic flow for the DeepThink Personality Analyzer project. It is intended to help other developers or AI assistants understand how the codebase operates.

## Architecture Overview

DeepThink is a monolithic Flask application with a Vanilla JS frontend. It uses an **ephemeral data model**.

### 1. Data Privacy & Ephemeral State
- **Rule:** ZERO data persistence. 
- **Implementation:** `utils/session_manager.py` manages all data. User demographics, selected test categories, and answers are stored purely in `flask.session` (server-side memory/signed cookies depending on Flask config). 
- **Destruction:** The moment the user hits the `/result` endpoint and the AI analysis is generated, `clear_session(session)` is called, wiping all data irreversibly.

### 2. Backend Routing (`app.py`)
- `/`: Landing page.
- `/pretest`: Collects optional demographic info to pass to the AI for better context.
- `/select-types`: Allows multi-selection of 8 available test categories.
- `/test`: Renders the base HTML for the test. Handled as a Single Page Application (SPA) on the frontend.
- `/api/questions`: Exposes the JSON files from the `questions/` directory to the frontend JS engine.
- `/api/submit`: Accepts the final answers payload and stores them in the session.
- `/result`: Invokes the Gemini API client, passes the session data, generates the HTML report, and clears the session.

### 3. AI Integration (`utils/gemini_client.py`)
- Uses `google.generativeai` with the `gemini-flash-latest` model.
- Builds a highly structured system prompt enforcing non-clinical language, empathetic tone, and strict HTML layout output (e.g., `<div class="result-category">`, `<span class="trait-chip">`).
- **Error Handling:** If the API fails (e.g., rate limit, invalid key), the exception is caught, logged to `stderr`, and a safe, visually identical fallback HTML report is generated indicating the error.

### 4. Frontend Engine (`static/js/main.js`)
- **State Machine:** The test page does not reload. `main.js` fetches all questions, concatenates them based on selected categories, and tracks `currentQuestionIndex`.
- **Transitions:** When crossing the boundary between two different categories (e.g., from Social to Career), it pauses and shows an encouraging transition screen (`category-transition`).
- **Progress:** A progress bar calculates completion based on total loaded questions.
- **Submission:** Submits an object mapping `{ question_id: answer_text }` back to the server.

### 5. Styling (`static/css/style.css`)
- **Aesthetic:** Soft pastels, glassmorphism (`backdrop-filter: blur`), CSS variables for themes, and micro-animations (`@keyframes fadeInUp`).
- **Mobile First:** Fully responsive grids and flexbox layouts.

## Adding New Questions
To add more questions (e.g., upgrading a category from 10 to 20 questions):
1. Update or replace the corresponding JSON file in `questions/<category>/`.
2. The `app.py` `questions` endpoint dynamically reads whatever JSON file exists (preferring `q30.json`, then `q20.json`, then `q10.json`).
3. The frontend will automatically adjust the progress bar to account for the new length.
