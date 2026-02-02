// Cyber SRS Learning Hub - Minimalist Vocabulary Trainer
class SessionTracker {
    constructor() {
        this.sessionToken = this.generateToken();
        this.startTime = new Date();
        this.answers = [];
        this.startSession();
    }

    generateToken() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    async startSession() {
        // Hanya log ke console untuk dev
        console.log('Session started:', this.sessionToken);

        // Optional: send to backend
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
            // Fail silently - tidak critical
        }
    }

    trackAnswer(wordId, userAnswer, isCorrect, responseTime) {
        const answer = {
            wordId, userAnswer, isCorrect, responseTime,
            timestamp: new Date().toISOString()
        };
        this.answers.push(answer);

        // Jika sudah 20 jawaban, complete session
        if (this.answers.length >= 20) {
            this.completeSession();
        }
    }

    async completeSession() {
        const correct = this.answers.filter(a => a.isCorrect).length;
        const accuracy = (correct / this.answers.length) * 100;

        try {
            await fetch('/api/session-complete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    token: this.sessionToken,
                    end_time: new Date().toISOString(),
                    total_questions: this.answers.length,
                    correct_answers: correct,
                    accuracy_rate: accuracy,
                    answers: this.answers
                })
            });
            console.log('Session completed and saved');
        } catch (e) {
            console.error('Failed to save session:', e);
        }
    }
}

class CyberSRSApp {
    constructor() {
        this.apiEndpoint = 'http://localhost:5000';
        this.currentWord = null;
        this.currentWordId = null;
        this.sessionProgress = 0;
        this.sessionTotal = 20;
        this.sessionTracker = new SessionTracker();

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

        // Enter key for input field
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target.id === 'answer-input') {
                e.preventDefault();
                this.submitAnswer();
            }
        });
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
        if (!this.currentWord) return;

        const answerInput = document.getElementById('answer-input');
        const userAnswer = answerInput.value.trim();

        if (!userAnswer) {
            this.showFeedback('Please enter an answer', 'warning');
            return;
        }

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
            this.sessionTracker.trackAnswer(
                this.currentWord.id,
                userAnswer,
                result.data.correct,
                result.data.response_time || (Date.now() - startTime) / 1000
            );

            this.showAnswerFeedback(result.data);
        } else {
            this.showFeedback('Failed to submit answer', 'error');
            document.getElementById('submit-btn').disabled = false;
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
