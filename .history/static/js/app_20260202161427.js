// Cyber SRS Learning Hub - Minimalist Vocabulary Trainer
class LearningSession {
    constructor() {
        if (window.sessionInitialized) {
            console.log('Session already initialized, skipping...');
            return;
        }
        window.sessionInitialized = true;

        this.dailyGoal = 10; // Changed from 20 to 10
        this.completedCount = 0;
        this.sessionActive = true;
        this.sessionToken = this.generateToken();
        this.startTime = new Date();
        this.answers = [];
        console.log('🔧 SessionTracker initialized');
        console.log('Daily goal:', this.dailyGoal);
        this.startSession();
    }

    generateToken() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    async startSession() {
        console.log('Session started:', this.sessionToken);
        try {
            await fetch('/api/session-start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    token: this.sessionToken,
                    start_time: this.startTime.toISOString()
                })
            });
        } catch (e) {
            // Fail silently
        }
    }

    incrementProgress() {
        this.completedCount++;

        console.log(`📊 Progress: ${this.completedCount}/${this.dailyGoal}`);

        // Update UI progress
        document.getElementById('progress-text').textContent =
            `${this.completedCount}/${this.dailyGoal}`;

        // Update progress bar width
        const progressPercent = (this.completedCount / this.dailyGoal) * 100;
        document.getElementById('progress-fill').style.width = `${progressPercent}%`;

        // Check if session is complete
        if (this.completedCount >= this.dailyGoal) {
            console.log('✅ GOAL REACHED! Calling completeSession()');
            this.completeSession();
        } else {
            console.log('➡️ Not yet reached:', this.completedCount, '/', this.dailyGoal);
        }
    }

    async completeSession() {
        this.sessionActive = false;

        // DISABLE INPUT FIELD & BUTTON
        const input = document.getElementById('answer-input');
        const button = document.getElementById('submit-btn');

        input.disabled = true;
        input.placeholder = "Session completed!";
        button.disabled = true;
        button.textContent = "Completed";

        // REMOVE ENTER KEY LISTENER
        document.removeEventListener('keydown', window.app.enterKeyHandler);

        this.showCompletionScreen();

        // HITUNG DATA SEBELUM KIRIM
        const totalQuestions = this.answers.length;
        const correctAnswers = this.answers.filter(a => a.isCorrect).length;
        const accuracy = totalQuestions > 0 ? (correctAnswers / totalQuestions) * 100 : 0;

        console.log('Completing session:', {
            token: this.sessionToken,
            totalQuestions,
            correctAnswers,
            accuracy
        });

        try {
            const response = await fetch('/api/session/complete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_token: this.sessionToken,
                    end_time: new Date().toISOString(),
                    total_questions: totalQuestions,      // ← PASTIKAN INI ADA
                    correct_answers: correctAnswers,      // ← PASTIKAN INI ADA
                    accuracy_rate: accuracy               // ← PASTIKAN INI ADA
                })
            });

            const result = await response.json();
            console.log('Session completion response:', result);

        } catch (error) {
            console.error('Failed to complete session:', error);
        }

        // Juga update database dengan semua jawaban
        await this.saveAllAnswers();
    }

    showCompletionScreen() {
        // ELEMENT SELECTION WITH NULL CHECKS
        const elements = {
            wordSection: document.querySelector('.word-section'),
            inputArea: document.querySelector('.input-area'),
            mainContent: document.querySelector('.main-content')
        };

        // HIDE ELEMENTS IF EXIST
        if (elements.wordSection) elements.wordSection.style.opacity = '0.3';
        if (elements.inputArea) elements.inputArea.style.display = 'none';

        // Tampilkan pesan
        const message = `
            <div style="
                text-align: center;
                padding: 30px;
                background: #1a1a2a;
                border-radius: 15px;
                margin: 20px 0;
                border: 2px solid #00d4ff;
            ">
                <h2 style="color: #00d4ff;">🎉 Session Complete!</h2>
                <p>You've completed 10 words today.</p>
                <button onclick="location.reload()" style="
                    padding: 10px 20px;
                    background: #00d4ff;
                    color: black;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    margin-top: 15px;
                ">
                    Restart Session
                </button>
            </div>
        `;

        // INSERT SAFELY
        if (elements.inputArea) {
            elements.inputArea.insertAdjacentHTML('afterend', message);
        } else if (elements.mainContent) {
            elements.mainContent.insertAdjacentHTML('beforeend', message);
        } else {
            document.body.insertAdjacentHTML('beforeend', message);
        }
    }

    continueSession() {
        // Hide completion screen
        document.querySelector('.completion-screen').remove();

        // Show learning elements again
        document.querySelector('.word-section').style.display = 'block';
        document.querySelector('.input-area').style.display = 'block';

        // RE-ENABLE INPUT FIELD & BUTTON
        const input = document.getElementById('answer-input');
        const button = document.getElementById('submit-btn');

        input.disabled = false;
        input.placeholder = "Type your answer here...";
        button.disabled = false;
        button.textContent = "Submit";

        // RE-ADD ENTER KEY LISTENER
        document.addEventListener('keydown', window.app.enterKeyHandler);

        // Keep counter at goal but allow continuation
        this.completedCount = this.dailyGoal;
        this.sessionActive = true;
    }

    restartSession() {
        // Full reset - reload page
        window.location.reload();
    }

    sendCompletionToServer() {
        fetch('/api/session-complete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                completed_count: this.completedCount,
                daily_goal: this.dailyGoal,
                completed_at: new Date().toISOString()
            })
        }).catch(e => console.error('Failed to save completion:', e));
    }

    trackAnswer(wordId, userAnswer, isCorrect, responseTime) {
        const answer = {
            wordId, userAnswer, isCorrect, responseTime,
            timestamp: new Date().toISOString()
        };
        this.answers.push(answer);
    }

    async saveAllAnswers() {
        // Simpan semua answers ke endpoint terpisah
        for (const answer of this.answers) {
            await fetch('/api/session/answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_token: this.sessionToken,
                    word_id: answer.wordId,
                    user_answer: answer.userAnswer,
                    correct: answer.isCorrect,
                    response_time: answer.responseTime,
                    answered_at: answer.timestamp
                })
            });
        }
    }
}

class CyberSRSApp {
    constructor() {
        this.apiEndpoint = 'http://localhost:5000';
        this.currentWord = null;
        this.currentWordId = null;
        this.sessionProgress = 0;
        this.sessionTotal = 10; // Changed from 20 to 10
        this.learningSession = new LearningSession();
        this.isSubmitting = false; // Anti-spam flag
        this.lastSubmitTime = 0; // For debouncing

        this.init();
    }

    init() {
        this.createParticles();
        this.setupEventListeners();
        this.loadNextWord();

        console.log('🚀 Cyber SRS Learning Hub initialized!');
    }

    // Particle Background Animation
    createParticles() {
        const particlesContainer = document.getElementById('particles');
        if (particlesContainer) {
            for (let i = 0; i < 20; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = Math.random() * 100 + '%';
                particle.style.width = Math.random() * 3 + 1 + 'px';
                particle.style.height = particle.style.width;
                particle.style.animationDelay = Math.random() * 6 + 's';
                particlesContainer.appendChild(particle);
            }
        }
    }

    // Event Listeners
    setupEventListeners() {
        // Submit button
        const submitBtn = document.getElementById('submit-btn');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitAnswer());
        }

        // Enter key for input field with debouncing
        this.enterKeyHandler = (e) => {
            if (e.key === 'Enter' &&
                e.target.id === 'answer-input' &&
                !this.isSubmitting &&
                this.learningSession.sessionActive &&
                this.learningSession.completedCount < this.learningSession.dailyGoal) {

                e.preventDefault();
                e.stopImmediatePropagation();

                // Debounce: only one submission per 500ms
                if (this.lastSubmitTime && Date.now() - this.lastSubmitTime < 500) {
                    return;
                }

                this.lastSubmitTime = Date.now();
                this.submitAnswer();
            }
        };

        document.addEventListener('keydown', this.enterKeyHandler);
    }

    // API Integration
    async apiCall(endpoint, method = 'GET', data = null) {
        try {
            const config = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                }
            };
            if (data) config.body = JSON.stringify(data);

            const response = await fetch(`${this.apiEndpoint}${endpoint}`, config);
            const result = await response.json();
            return { success: response.ok, data: result };
        } catch (error) {
            console.error('API Error:', error);
            return { success: false, error: error.message };
        }
    }

    // Load Next Word
    async loadNextWord() {
        try {
            const result = await this.apiCall('/api/next-word');
            if (result.success && result.data) {
                this.currentWord = result.data;
                this.currentWordId = result.data.id;
                this.showTypingExercise();
            } else {
                this.showDemoWord();
            }
        } catch (error) {
            console.error('Failed to load word:', error);
            this.showDemoWord();
        }
    }

    showDemoWord() {
        // Demo word for offline mode
        this.currentWord = {
            id: 1,
            english: 'apple',
            indonesian: 'apel',
            part_of_speech: 'noun',
            example_sentence: 'I eat an apple every day.',
            interval: 1,
            repetitions: 0,
            ease_factor: 2.5,
            streak: 0
        };
        this.showTypingExercise();
    }

    showTypingExercise() {
        if (!this.currentWord) return;

        // Update word information
        document.getElementById('english-word').textContent = this.currentWord.english || 'apple';
        document.getElementById('part-of-speech').textContent = `[${this.currentWord.part_of_speech || 'noun'}]`;
        document.getElementById('example-sentence').textContent = `"${this.currentWord.example_sentence || 'I eat an apple every day.'}"`;

        // Clear input and focus
        const answerInput = document.getElementById('answer-input');
        answerInput.value = '';
        // Remove feedback classes but keep base styling
        answerInput.classList.remove('correct', 'incorrect');
        answerInput.focus();

        // Re-enable submit button for new word
        document.getElementById('submit-btn').disabled = false;

        // Clear feedback
        const feedbackEl = document.getElementById('feedback-message');
        if (feedbackEl) {
            feedbackEl.textContent = '';
            const feedbackContainer = document.getElementById('feedback-container');
            if (feedbackContainer) {
                feedbackContainer.style.display = 'none';
            }
        }

        // Update progress
        this.updateProgressBar();
    }

    // Submit Answer
    async submitAnswer() {
        // PREVENT SPAM
        if (this.isSubmitting) {
            console.log('Already submitting, please wait...');
            return;
        }

        // PREVENT EXCEEDING GOAL
        if (this.learningSession.completedCount >= this.learningSession.dailyGoal) {
            console.log('Daily goal already reached');
            this.showFeedback('Daily goal reached!', 'info');
            return;
        }

        if (!this.currentWord) return;

        const answerInput = document.getElementById('answer-input');
        const userAnswer = answerInput.value.trim();

        if (!userAnswer) {
            this.showFeedback('Please enter an answer', 'warning');
            return;
        }

        // LOCK SUBMISSION
        this.isSubmitting = true;

        try {
            // Disable submit button
            document.getElementById('submit-btn').disabled = true;

            // Submit answer to API
            const startTime = Date.now();
            const result = await this.apiCall('/api/submit-answer', 'POST', {
                word_id: this.currentWord.id,
                user_answer: userAnswer,
                response_time: (Date.now() - startTime) / 1000  // in seconds
            });

            if (result.success) {
                // Track answer for session
                this.learningSession.trackAnswer(
                    this.currentWord.id,
                    userAnswer,
                    result.data.correct,
                    result.data.response_time || (Date.now() - startTime) / 1000
                );

                // Increment progress and show feedback
                this.learningSession.incrementProgress();
                this.showAnswerFeedback(result.data);
            } else {
                this.showFeedback('Failed to submit answer', 'error');
                document.getElementById('submit-btn').disabled = false;
            }
        } finally {
            // RELEASE LOCK AFTER TIMEOUT (prevent rapid re-submit)
            setTimeout(() => {
                this.isSubmitting = false;
            }, 500); // 500ms cooldown
        }
    }

    showAnswerFeedback(data) {
        const answerInput = document.getElementById('answer-input');

        // Remove existing feedback classes and add new one
        answerInput.classList.remove('correct', 'incorrect');
        answerInput.classList.add(data.correct ? 'correct' : 'incorrect');

        // Show feedback
        const feedbackText = data.correct ?
            `✅ Correct!` :
            `❌ Incorrect. The answer is: "${data.actual_answer}"`;

        this.showFeedback(feedbackText, data.correct ? 'success' : 'error');

        // Update streak
        this.currentStreak = data.streak || 0;
        const streakEl = document.getElementById('streak-info');
        if (streakEl) {
            streakEl.textContent = `Streak: ${this.currentStreak}`;
        }

        // Add confetti for correct answers
        if (data.correct) {
            this.createConfetti();
        }

        // Auto-advance after 1.5 seconds and remove feedback classes
        setTimeout(() => {
            // Reset input field
            answerInput.value = '';
            answerInput.classList.remove('correct', 'incorrect');

            // Load next word (ensure proper context)
            window.app.sessionProgress++;
            window.app.loadNextWord();

            // Focus to input for new word
            setTimeout(() => {
                answerInput.focus();
            }, 100);
        }, 1500);
    }

    createConfetti() {
        for (let i = 0; i < 20; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.animationDelay = Math.random() * 2 + 's';
            confetti.style.backgroundColor = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b'][Math.floor(Math.random() * 5)];
            document.body.appendChild(confetti);

            setTimeout(() => {
                confetti.remove();
            }, 3000);
        }
    }

    updateProgressBar() {
        const progress = (this.sessionProgress / this.sessionTotal) * 100;
        const progressFill = document.getElementById('progress-fill');
        if (progressFill) {
            progressFill.style.width = `${progress}%`;
        }
        const progressText = document.getElementById('progress-text');
        if (progressText) {
            progressText.textContent = `${this.sessionProgress}/${this.sessionTotal}`;
        }
    }

    updateProgress() {
        // Fetch stats from backend or update counter locally
        this.apiCall('/api/stats').then(result => {
            if (result.success) {
                const stats = result.data;
                document.getElementById('progress-text').textContent =
                    `${stats.today_reviews || this.sessionProgress}/${stats.daily_goal || this.sessionTotal}`;
            }
        }).catch(error => {
            console.error('Failed to update progress:', error);
        });
    }

    showFeedback(message, type = 'info') {
        const feedbackEl = document.getElementById('feedback-message');
        if (feedbackEl) {
            feedbackEl.textContent = message;
            feedbackEl.className = `feedback-message ${type}`;
            // Show the feedback container
            const feedbackContainer = document.getElementById('feedback-container');
            if (feedbackContainer) {
                feedbackContainer.style.display = 'block';
            }
        } else {
            console.error('Feedback element not found');
        }
    }


}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CyberSRSApp();
});

// Session tracking - simpan ke database
async function trackSessionStart() {
    const sessionToken = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    window.currentSessionToken = sessionToken;
    
    try {
        await fetch('/api/session/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_token: sessionToken,
                user_agent: navigator.userAgent,
                start_time: new Date().toISOString()
            })
        });
        console.log('Session started:', sessionToken);
    } catch (e) {
        console.error('Failed to track session start:', e);
    }
}

async function trackAnswer(wordId, userAnswer, isCorrect, responseTime) {
    if (!window.currentSessionToken) return;
    
    try {
        await fetch('/api/session/answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_token: window.currentSessionToken,
                word_id: wordId,
                user_answer: userAnswer,
                correct: isCorrect,
                response_time: responseTime,
                answered_at: new Date().toISOString()
            })
        });
    } catch (e) {
        console.error('Failed to track answer:', e);
    }
}

async function trackSessionComplete(totalQuestions, correctAnswers) {
    if (!window.currentSessionToken) return;
    
    try {
        await fetch('/api/session/complete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_token: window.currentSessionToken,
                end_time: new Date().toISOString(),
                total_questions: totalQuestions,
                correct_answers: correctAnswers,
                accuracy_rate: (correctAnswers / totalQuestions) * 100
            })
        });
        console.log('Session completed in database');
    } catch (e) {
        console.error('Failed to track session completion:', e);
    }
}

// Saat app start
trackSessionStart();

// Di fungsi submitAnswer():
async function submitAnswer() {
    const startTime = Date.now();
    // ... existing logic ...
    
    // Track answer
    await trackAnswer(
        currentWord.id, 
        userAnswer, 
        isCorrect, 
        (Date.now() - startTime) / 1000
    );
    
    // Jika selesai 10 kata
    if (completedCount >= 10) {
        await trackSessionComplete(10, correctCount);
    }
}