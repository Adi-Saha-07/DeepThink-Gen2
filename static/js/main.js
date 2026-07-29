/* DeepThink - Main JavaScript */

(function initHeroRotation() {
    const messages = document.querySelectorAll('.hero-message');
    if (messages.length === 0) return;

    let currentIndex = 0;
    setInterval(() => {
        messages[currentIndex].classList.remove('active');
        currentIndex = (currentIndex + 1) % messages.length;
        messages[currentIndex].classList.add('active');
    }, 4200);
})();

if (document.getElementById('test-page')) {
    initTestEngine();
}

if (document.getElementById('category-form')) {
    initCategorySelectionGuide();
}

let allQuestionSets = [];
let flatQuestions = [];
let currentQuestionIndex = 0;
let answers = {};
let totalQuestions = 0;
let showingTransition = false;
let loadingMsgInterval = null;

const encouragements = [
    "Nice, one step closer.",
    "You're doing great - keep going.",
    "Honest answers make the best insights.",
    "Almost there - stay with it.",
    "Every answer counts. You've got this.",
    "Self-discovery in progress...",
    "Keep going, you're on a roll.",
    "Halfway there - stay honest with yourself.",
    "Your answers are painting a clearer picture.",
    "One question at a time. You're doing great."
];

async function initTestEngine() {
    try {
        const response = await fetch('/api/questions');
        const data = await response.json();

        if (data.error) {
            console.error('Error loading questions:', data.error);
            return;
        }

        allQuestionSets = data.question_sets;
        flatQuestions = [];

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

    if (q.isFirstInSet && q.setIndex > 0 && !showingTransition) {
        showCategoryTransition(q);
        return;
    }

    showingTransition = false;

    const progress = (currentQuestionIndex / totalQuestions) * 100;
    document.getElementById('progress-fill').style.width = progress + '%';
    document.getElementById('progress-text').textContent =
        `Question ${currentQuestionIndex + 1} of ${totalQuestions}`;

    document.getElementById('badge-icon').textContent = q.category_icon;
    document.getElementById('badge-text').textContent = q.category_name;
    document.getElementById('question-text').textContent = q.text;

    const optionsList = document.getElementById('options-list');
    optionsList.innerHTML = '';

    q.options.forEach((opt) => {
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

    const backBtn = document.getElementById('back-btn');
    backBtn.disabled = currentQuestionIndex === 0;

    document.getElementById('question-counter').textContent =
        `${q.indexInSet + 1}/${allQuestionSets[q.setIndex].questions.length} in ${q.category_name}`;

    document.getElementById('encouragement').classList.add('hidden');

    const card = document.getElementById('question-card');
    card.style.animation = 'none';
    card.offsetHeight;
    card.style.animation = 'fadeInUp 0.4s var(--ease-out) both';

    document.getElementById('question-container').classList.remove('hidden');
    document.getElementById('category-transition').classList.add('hidden');
    document.getElementById('loading-container').classList.add('hidden');
}

function selectOption(questionId, optionText) {
    answers[questionId] = optionText;

    const buttons = document.querySelectorAll('.option-btn');
    buttons.forEach(btn => {
        btn.classList.remove('selected');
        btn.setAttribute('aria-checked', 'false');
        if (btn.textContent === optionText) {
            btn.classList.add('selected');
            btn.setAttribute('aria-checked', 'true');
        }
    });

    showEncouragement();

    setTimeout(() => {
        currentQuestionIndex++;
        renderQuestion();
    }, 450);
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
    const prevSet = allQuestionSets[q.setIndex - 1];

    document.getElementById('transition-icon').textContent = q.category_icon;
    document.getElementById('transition-title').textContent = `Great job on ${prevSet.category_name}`;
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
    document.getElementById('question-container').classList.add('hidden');
    document.getElementById('category-transition').classList.add('hidden');
    document.getElementById('loading-container').classList.remove('hidden');
    document.getElementById('progress-container').classList.add('hidden');
    document.getElementById('progress-fill').style.width = '100%';

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
    }, 2800);
}

function stopLoadingMessages() {
    if (loadingMsgInterval) {
        clearInterval(loadingMsgInterval);
        loadingMsgInterval = null;
    }
}

function initCategorySelectionGuide() {
    const categoryInputs = document.querySelectorAll('.category-checkbox');
    const countSection = document.querySelector('.question-count-section');
    const countOptions = document.querySelectorAll('.count-option:not(.disabled)');
    const beginButton = document.getElementById('begin-test-btn');

    const scrollToElement = (el) => {
        if (!el) return;
        window.setTimeout(() => {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 120);
    };

    categoryInputs.forEach(input => {
        input.addEventListener('change', () => {
            if (input.checked) {
                scrollToElement(countSection);
            }
        });
    });

    countOptions.forEach(option => {
        option.addEventListener('click', () => {
            countOptions.forEach(item => item.classList.remove('active'));
            option.classList.add('active');
            scrollToElement(beginButton);
        });
    });
}

(function initScrollAnimations() {
    const animated = document.querySelectorAll('.feature-card, .step, .privacy-section');
    if (animated.length === 0 || !('IntersectionObserver' in window)) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    animated.forEach(el => observer.observe(el));
})();
