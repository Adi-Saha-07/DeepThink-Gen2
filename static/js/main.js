/* ============================================================
   DeepThink — Main JavaScript
   Hero rotation, test engine, loading states, PDF download
   ============================================================ */

// ── Hero Message Rotation ──────────────────────────────────────
(function initHeroRotation() {
    const messages = document.querySelectorAll('.hero-message');
    if (messages.length === 0) return;

    let currentIndex = 0;
    setInterval(() => {
        messages[currentIndex].classList.remove('active');
        currentIndex = (currentIndex + 1) % messages.length;
        messages[currentIndex].classList.add('active');
    }, 4000);
})();


// ── Test Engine ────────────────────────────────────────────────
// Only runs on the test page
if (document.getElementById('test-page')) {
    initTestEngine();
}

// State
let allQuestionSets = [];      // Array of { category, category_name, category_icon, questions[] }
let flatQuestions = [];         // Flat list of all questions across categories
let currentQuestionIndex = 0;
let answers = {};              // { question_id: selected_option_text }
let currentCategoryIndex = 0;
let totalQuestions = 0;
let showingTransition = false;

// Encouragement messages
const encouragements = [
    "Nice, one step closer! 🌟",
    "You're doing great — keep going. 💪",
    "Honest answers make the best insights. ✨",
    "Almost there — stay with it! 🎯",
    "Every answer counts. You've got this! 🌈",
    "Self-discovery in progress... 🔮",
    "Keep going, you're on a roll! 🚀",
    "Halfway there — stay honest with yourself. 💜",
    "Your answers are painting a picture. 🎨",
    "One question at a time. You're doing amazing. 🌻"
];

// Loading messages rotation
let loadingMsgInterval = null;

async function initTestEngine() {
    try {
        const response = await fetch('/api/questions');
        const data = await response.json();

        if (data.error) {
            console.error('Error loading questions:', data.error);
            return;
        }

        allQuestionSets = data.question_sets;

        // Build flat question list with category metadata
        allQuestionSets.forEach((set, setIndex) => {
            set.questions.forEach((q, qIndex) => {
                flatQuestions.push({
                    ...q,
                    category: set.category,
                    category_name: set.category_name,
                    category_icon: set.category_icon,
                    setIndex: setIndex,
                    indexInSet: qIndex,
                    isFirstInSet: qIndex === 0,
                    isLastInSet: qIndex === set.questions.length - 1
                });
            });
        });

        totalQuestions = flatQuestions.length;
        renderQuestion();
    } catch (err) {
        console.error('Failed to load questions:', err);
    }
}


function renderQuestion() {
    if (currentQuestionIndex >= totalQuestions) {
        submitTest();
        return;
    }

    const q = flatQuestions[currentQuestionIndex];

    // Check if we need a category transition
    if (q.isFirstInSet && q.setIndex > 0 && !showingTransition) {
        showCategoryTransition(q);
        return;
    }

    showingTransition = false;

    // Update progress
    const progress = ((currentQuestionIndex) / totalQuestions) * 100;
    document.getElementById('progress-fill').style.width = progress + '%';
    document.getElementById('progress-text').textContent =
        `Question ${currentQuestionIndex + 1} of ${totalQuestions}`;

    // Update category badge
    document.getElementById('badge-icon').textContent = q.category_icon;
    document.getElementById('badge-text').textContent = q.category_name;

    // Update question text
    document.getElementById('question-text').textContent = q.text;

    // Render options
    const optionsList = document.getElementById('options-list');
    optionsList.innerHTML = '';

    q.options.forEach((opt, i) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.textContent = opt;
        btn.setAttribute('tabindex', '0');
        btn.setAttribute('role', 'radio');
        btn.setAttribute('aria-checked', answers[q.id] === opt ? 'true' : 'false');

        if (answers[q.id] === opt) {
            btn.classList.add('selected');
        }

        btn.addEventListener('click', () => selectOption(q.id, opt));
        btn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                selectOption(q.id, opt);
            }
        });

        optionsList.appendChild(btn);
    });

    // Back button
    const backBtn = document.getElementById('back-btn');
    backBtn.disabled = currentQuestionIndex === 0;

    // Counter
    document.getElementById('question-counter').textContent =
        `${q.indexInSet + 1}/${allQuestionSets[q.setIndex].questions.length} in ${q.category_name}`;

    // Hide encouragement
    document.getElementById('encouragement').classList.add('hidden');

    // Re-trigger card animation
    const card = document.getElementById('question-card');
    card.style.animation = 'none';
    card.offsetHeight; // trigger reflow
    card.style.animation = 'fadeInUp 0.4s var(--ease-out) both';

    // Show question container, hide others
    document.getElementById('question-container').classList.remove('hidden');
    document.getElementById('category-transition').classList.add('hidden');
    document.getElementById('loading-container').classList.add('hidden');
}


function selectOption(questionId, optionText) {
    answers[questionId] = optionText;

    // Visual feedback — mark selected
    const buttons = document.querySelectorAll('.option-btn');
    buttons.forEach(btn => {
        btn.classList.remove('selected');
        btn.setAttribute('aria-checked', 'false');
        if (btn.textContent === optionText) {
            btn.classList.add('selected');
            btn.setAttribute('aria-checked', 'true');
        }
    });

    // Show encouragement
    showEncouragement();

    // Auto-advance after a brief delay
    setTimeout(() => {
        currentQuestionIndex++;
        renderQuestion();
    }, 600);
}


function showEncouragement() {
    const el = document.getElementById('encouragement');
    const textEl = document.getElementById('encouragement-text');
    const randomMsg = encouragements[Math.floor(Math.random() * encouragements.length)];
    textEl.textContent = randomMsg;
    el.classList.remove('hidden');
    el.style.animation = 'none';
    el.offsetHeight;
    el.style.animation = 'fadeIn 0.4s var(--ease-out)';
}


function showCategoryTransition(q) {
    showingTransition = true;

    // Get the previous category name for the "Great job" message
    const prevSet = allQuestionSets[q.setIndex - 1];

    document.getElementById('transition-icon').textContent = q.category_icon;
    document.getElementById('transition-title').textContent = `Great job on ${prevSet.category_name}!`;
    document.getElementById('transition-subtitle').textContent = `Next up: ${q.category_name} questions`;

    document.getElementById('question-container').classList.add('hidden');
    document.getElementById('category-transition').classList.remove('hidden');
    document.getElementById('loading-container').classList.add('hidden');
}


function continueToNextCategory() {
    showingTransition = false;
    renderQuestion();
}


function goBack() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        showingTransition = false;
        renderQuestion();
    }
}


async function submitTest() {
    // Show loading state
    document.getElementById('question-container').classList.add('hidden');
    document.getElementById('category-transition').classList.add('hidden');
    document.getElementById('loading-container').classList.remove('hidden');
    document.getElementById('progress-container').classList.add('hidden');

    // Update progress bar to 100%
    document.getElementById('progress-fill').style.width = '100%';

    // Rotate loading messages
    startLoadingMessages();

    try {
        const response = await fetch('/api/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers })
        });

        const data = await response.json();
        stopLoadingMessages();

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        if (data.redirect) {
            window.location.href = data.redirect;
        }
    } catch (err) {
        stopLoadingMessages();
        console.error('Submit error:', err);
        alert('Something went wrong. Please try again.');
    }
}


function startLoadingMessages() {
    const messages = document.querySelectorAll('.loading-msg');
    if (messages.length === 0) return;

    let idx = 0;
    loadingMsgInterval = setInterval(() => {
        messages[idx].classList.remove('active');
        idx = (idx + 1) % messages.length;
        messages[idx].classList.add('active');
    }, 3000);
}


function stopLoadingMessages() {
    if (loadingMsgInterval) {
        clearInterval(loadingMsgInterval);
        loadingMsgInterval = null;
    }
}


// ── Intersection Observer for fade-in animations ───────────────
(function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.feature-card, .step, .privacy-section').forEach(el => {
        observer.observe(el);
    });
})();
