// API Service
class APIService {
  constructor(baseURL = 'http://127.0.0.1:5000') {
    this.baseURL = baseURL;
    this.retryAttempts = 3;
    this.retryDelay = 1000; // 1 second
  }

  async request(endpoint, options = {}, retryCount = 0) {
    const url = `${this.baseURL}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);

      if (error.name === 'AbortError') {
        throw new Error('Request timed out');
      }

      if (retryCount < this.retryAttempts && this.isRetryableError(error)) {
        console.warn(`Request failed, retrying (${retryCount + 1}/${this.retryAttempts}):`, error.message);
        await this.delay(this.retryDelay * Math.pow(2, retryCount)); // Exponential backoff
        return this.request(endpoint, options, retryCount + 1);
      }

      throw error;
    }
  }

  isRetryableError(error) {
    // Retry on network errors, 5xx server errors, but not 4xx client errors
    return error.message.includes('fetch') ||
           error.message.includes('NetworkError') ||
           (error.message.includes('HTTP') && error.message.match(/HTTP 5\d{2}/));
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // API Methods
  async getWords(userId = 1, size = 10) {
    return this.request(`/session/start?user_id=${userId}&size=${size}`);
  }

  async submitAnswer(word, quality) {
    return this.request('/answer', {
      method: 'POST',
      body: JSON.stringify({ word, quality })
    });
  }

  async getStats(userId = 1) {
    return this.request(`/stats?user_id=${userId}`);
  }

  async addWord(english, indonesian) {
    return this.request('/add-word', {
      method: 'POST',
      body: JSON.stringify({ english, indonesian })
    });
  }
}

// State Management
class StateManager {
  constructor() {
    this.state = {
      currentSession: null,
      vocabList: [],
      sessionProgress: {
        currentIndex: 0,
        totalItems: 0,
        correct: 0,
        partial: 0,
        wrong: 0
      },
      userStats: {
        totalWords: 0,
        masteredWords: 0,
        averageScore: 0
      },
      notifications: [],
      loading: false,
      error: null
    };
    this.listeners = [];
  }

  getState() {
    return { ...this.state };
  }

  setState(newState) {
    this.state = { ...this.state, ...newState };
    this.notifyListeners();
  }

  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  notifyListeners() {
    this.listeners.forEach(listener => listener(this.state));
  }

  // State update methods
  startSession(vocabList) {
    this.setState({
      currentSession: {
        startTime: Date.now(),
        vocabList: vocabList
      },
      vocabList: vocabList,
      sessionProgress: {
        currentIndex: 0,
        totalItems: vocabList.length,
        correct: 0,
        partial: 0,
        wrong: 0
      }
    });
  }

  updateProgress(quality) {
    const progress = { ...this.state.sessionProgress };
    progress.currentIndex++;

    if (quality === 'correct') progress.correct++;
    else if (quality === 'partial') progress.partial++;
    else progress.wrong++;

    this.setState({ sessionProgress: progress });
  }

  addNotification(message, type = 'info') {
    const notification = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date()
    };

    this.setState({
      notifications: [...this.state.notifications, notification]
    });

    // Auto-remove notification after 5 seconds
    setTimeout(() => {
      this.removeNotification(notification.id);
    }, 5000);
  }

  removeNotification(id) {
    this.setState({
      notifications: this.state.notifications.filter(n => n.id !== id)
    });
  }

  setLoading(loading) {
    this.setState({ loading });
  }

  setError(error) {
    this.setState({ error });
    if (error) {
      this.addNotification(error.message, 'error');
    }
  }

  clearError() {
    this.setState({ error: null });
  }
}

// SRS Logic (Frontend implementation synchronized with backend)
class SRSLogic {
  constructor() {
    this.defaultEase = 2.5;
    this.minEase = 1.3;
  }

  calculateNextReview(qualityResponse, currentInterval = 1, currentEase = this.defaultEase, repetitionCount = 0) {
    // SM-2 Algorithm implementation
    let interval, ease, newRepetitionCount;

    if (qualityResponse < 3) {
      // Failed response - reset repetition count
      newRepetitionCount = 0;
      interval = 1;
    } else {
      // Successful response - increase repetition count
      newRepetitionCount = repetitionCount + 1;
      if (newRepetitionCount === 1) {
        interval = 1;
      } else if (newRepetitionCount === 2) {
        interval = 6;
      } else {
        interval = Math.round(currentInterval * currentEase);
      }
    }

    // Update ease factor
    ease = currentEase + (0.1 - (5 - qualityResponse) * (0.08 + (5 - qualityResponse) * 0.02));
    if (ease < this.minEase) {
      ease = this.minEase;
    }

    // Calculate next review date
    const today = new Date();
    const nextReviewDate = new Date(today);
    nextReviewDate.setDate(today.getDate() + interval);

    return {
      newInterval: interval,
      newEase: ease,
      newRepetitionCount: newRepetitionCount,
      nextReviewDate: nextReviewDate.toISOString().split('T')[0]
    };
  }

  scheduleVocab(vocabList) {
    // Sort vocab by priority: due date, difficulty, ease factor
    return vocabList.sort((a, b) => {
      // First priority: due date (earlier dates first)
      const dateA = new Date(a.nextReviewDate || '1970-01-01');
      const dateB = new Date(b.nextReviewDate || '1970-01-01');
      if (dateA < dateB) return -1;
      if (dateA > dateB) return 1;

      // Second priority: difficulty score (higher difficulty first)
      if (a.difficultyScore > b.difficultyScore) return -1;
      if (a.difficultyScore < b.difficultyScore) return 1;

      // Third priority: ease factor (lower ease first - needs more attention)
      if (a.easeFactor < b.easeFactor) return -1;
      if (a.easeFactor > b.easeFactor) return 1;

      return 0;
    });
  }

  simulateSpacedRepetition(vocabList, days = 30) {
    // Simulate spaced repetition over a period
    const simulation = [];
    let currentDate = new Date();

    for (let day = 0; day < days; day++) {
      const dueToday = vocabList.filter(vocab => {
        const reviewDate = new Date(vocab.nextReviewDate);
        return reviewDate <= currentDate;
      });

      simulation.push({
        date: currentDate.toISOString().split('T')[0],
        dueCount: dueToday.length,
        totalVocab: vocabList.length
      });

      // Advance to next day
      currentDate.setDate(currentDate.getDate() + 1);
    }

    return simulation;
  }
}

// UI Updates
class UIUpdater {
  constructor(stateManager) {
    this.stateManager = stateManager;
    this.stateManager.subscribe(this.updateUI.bind(this));
  }

  updateUI(state) {
    this.updateContent(state);
    this.updateProgress(state.sessionProgress);
    this.updateStats(state.userStats);
    this.updateNotifications(state.notifications);
    this.updateLoadingState(state.loading);
    this.updateErrorState(state.error);
  }

  updateContent(state) {
    // Update dynamic content based on current state
    const currentItem = state.vocabList[state.sessionProgress.currentIndex];

    if (currentItem) {
      this.renderFlashcard(currentItem);
    }

    // Update session info
    this.updateSessionInfo(state.currentSession, state.sessionProgress);
  }

  renderFlashcard(item) {
    const flashcardElement = document.querySelector('.flashcard');
    if (flashcardElement) {
      flashcardElement.innerHTML = `
        <h2>${item.word || item.english_word}</h2>
        <p>Meaning: ${item.meaning || item.indonesian_meaning}</p>
        ${item.example ? `<p>Example: ${item.example}</p>` : ''}
      `;
    }
  }

  updateProgress(progress) {
    const progressElements = document.querySelectorAll('.progress');
    progressElements.forEach(element => {
      const percentage = progress.totalItems > 0 ? (progress.currentIndex / progress.totalItems) * 100 : 0;
      element.style.width = `${percentage}%`;
    });

    // Update progress text
    const progressText = document.querySelector('.progress-text');
    if (progressText) {
      progressText.textContent = `${progress.currentIndex}/${progress.totalItems}`;
    }

    // Update counters
    this.updateCounter('.correct-count', progress.correct);
    this.updateCounter('.partial-count', progress.partial);
    this.updateCounter('.wrong-count', progress.wrong);
  }

  updateCounter(selector, value) {
    const element = document.querySelector(selector);
    if (element) {
      element.textContent = value;
    }
  }

  updateStats(stats) {
    this.updateCounter('.total-words', stats.totalWords);
    this.updateCounter('.mastered-words', stats.masteredWords);

    const avgScoreElement = document.querySelector('.average-score');
    if (avgScoreElement) {
      avgScoreElement.textContent = stats.averageScore.toFixed(1);
    }
  }

  updateNotifications(notifications) {
    const container = document.querySelector('.notifications');
    if (container) {
      container.innerHTML = notifications.map(notification => `
        <div class="notification notification-${notification.type}" data-id="${notification.id}">
          ${notification.message}
          <button class="notification-close" onclick="app.uiUpdater.removeNotification(${notification.id})">&times;</button>
        </div>
      `).join('');
    }
  }

  removeNotification(id) {
    this.stateManager.removeNotification(id);
  }

  updateLoadingState(loading) {
    const loadingElements = document.querySelectorAll('.loading');
    loadingElements.forEach(element => {
      element.style.display = loading ? 'block' : 'none';
    });
  }

  updateErrorState(error) {
    const errorElements = document.querySelectorAll('.error');
    errorElements.forEach(element => {
      element.textContent = error ? error.message : '';
      element.style.display = error ? 'block' : 'none';
    });
  }

  updateSessionInfo(session, progress) {
    if (!session) return;

    const elapsed = Math.floor((Date.now() - session.startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;

    const timeElement = document.querySelector('.session-time');
    if (timeElement) {
      timeElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
  }
}

// Main App Class
class App {
  constructor() {
    this.api = new APIService();
    this.stateManager = new StateManager();
    this.srsLogic = new SRSLogic();
    this.uiUpdater = new UIUpdater(this.stateManager);
  }

  async init() {
    try {
      this.stateManager.setLoading(true);
      const words = await this.api.getWords();
      this.stateManager.startSession(words);
      this.stateManager.setLoading(false);
    } catch (error) {
      this.stateManager.setError(error);
      this.stateManager.setLoading(false);
    }
  }

  async submitAnswer(quality) {
    const currentItem = this.stateManager.getState().vocabList[this.stateManager.getState().sessionProgress.currentIndex];

    if (!currentItem) return;

    try {
      this.stateManager.setLoading(true);
      await this.api.submitAnswer(currentItem.word || currentItem.english_word, quality);
      this.stateManager.updateProgress(quality);
      this.stateManager.addNotification(`Answer submitted: ${quality}`, 'success');
      this.stateManager.setLoading(false);
    } catch (error) {
      this.stateManager.setError(error);
      this.stateManager.setLoading(false);
    }
  }

  async loadStats() {
    try {
      const stats = await this.api.getStats();
      this.stateManager.setState({ userStats: stats });
    } catch (error) {
      this.stateManager.setError(error);
    }
  }

  async addWord(english, indonesian) {
    try {
      this.stateManager.setLoading(true);
      await this.api.addWord(english, indonesian);
      this.stateManager.addNotification('Word added successfully', 'success');
      this.stateManager.setLoading(false);
    } catch (error) {
      this.stateManager.setError(error);
      this.stateManager.setLoading(false);
    }
  }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.app = new App();
  window.app.init();
});

// Export for use in other scripts
window.APIService = APIService;
window.StateManager = StateManager;
window.SRSLogic = SRSLogic;
window.UIUpdater = UIUpdater;
window.App = App;
