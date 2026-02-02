class CyberSRSApp {
=======
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
