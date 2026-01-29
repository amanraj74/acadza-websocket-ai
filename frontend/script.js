/**
 * Acadza WebSocket Assignment - Frontend Client

 */

// ==========================================
// Configuration and State Management
// ==========================================

const CONFIG = {
    // WebSocket URL - Update this when deploying
    WS_URL: 'wss://acadza-websocket-ai.onrender.com/ws',
    
    // Reconnection settings
    RECONNECT_DELAY: 3000,
    MAX_RECONNECT_ATTEMPTS: 5,
    
    // UI settings
    TYPING_DELAY: 1000,
    AUTO_SCROLL_DELAY: 100
};

// Application state
const state = {
    websocket: null,
    isConnected: false,
    reconnectAttempts: 0,
    conversationActive: false,
    currentQuestionNumber: 0,
    totalQuestions: 3,
    isWaitingForChoice: false,
    countdownInterval: null
};

// ==========================================
// DOM Elements
// ==========================================

const elements = {
    // Status
    statusDot: document.getElementById('statusDot'),
    statusText: document.getElementById('statusText'),
    
    // Welcome screen
    welcomeScreen: document.getElementById('welcomeScreen'),
    initialInput: document.getElementById('initialInput'),
    charCount: document.getElementById('charCount'),
    launchBtn: document.getElementById('launchBtn'),
    
    // Chat screen
    chatScreen: document.getElementById('chatScreen'),
    chatMessages: document.getElementById('chatMessages'),
    progressFill: document.getElementById('progressFill'),
    currentQuestion: document.getElementById('currentQuestion'),
    totalQuestions: document.getElementById('totalQuestions'),
    
    // Chat input
    chatInputContainer: document.getElementById('chatInputContainer'),
    answerInput: document.getElementById('answerInput'),
    sendBtn: document.getElementById('sendBtn'),
    
    // Completion
    completionOverlay: document.getElementById('completionOverlay'),
    restartBtn: document.getElementById('restartBtn'),
    
    // Error
    errorMessage: document.getElementById('errorMessage'),
    errorText: document.getElementById('errorText'),
    
    // Templates
    typingTemplate: document.getElementById('typingTemplate')
};

// ==========================================
// WebSocket Connection Management
// ==========================================

/**
 * Initialize WebSocket connection
 */
function initializeWebSocket() {
    try {
        state.websocket = new WebSocket(CONFIG.WS_URL);
        
        state.websocket.onopen = handleWebSocketOpen;
        state.websocket.onmessage = handleWebSocketMessage;
        state.websocket.onerror = handleWebSocketError;
        state.websocket.onclose = handleWebSocketClose;
        
        console.log('WebSocket connection initiated...');
    } catch (error) {
        console.error('WebSocket initialization failed:', error);
        showError('Failed to connect to server. Please refresh the page.');
    }
}

/**
 * Handle WebSocket connection opened
 */
function handleWebSocketOpen() {
    console.log('WebSocket connected successfully');
    state.isConnected = true;
    state.reconnectAttempts = 0;
    updateConnectionStatus('connected', 'Connected');
}

/**
 * Handle incoming WebSocket messages
 * ULTIMATE VERSION: All 10 phases supported
 */
function handleWebSocketMessage(event) {
    try {
        const data = JSON.parse(event.data);
        console.log('Received message:', data);
        
        switch (data.type) {
            case 'follow_up':
                if (data.total) state.totalQuestions = data.total;
                handleFollowUpQuestion(data);
                break;
            
            case 'complete':
                handleInitialComplete(data);
                break;
            
            case 'thinking':
                handleThinkingMessage(data);
                break;
            
            case 'personality_reveal':
                handlePersonalityReveal(data);
                break;
            
            case 'mind_reading':
                handleMindReading(data);
                break;
            
            case 'secret_unlock':
                handleSecretUnlock(data);
                break;
            
            case 'interactive_choice':
                handleInteractiveChoice(data);
                break;
            
            case 'ultimate_reveal':
                handleUltimateReveal(data);
                break;
            
            case 'finale':
                handleFinale(data);
                break;
            
            case 'respectful_ending':
                handleRespectfulEnding(data);
                break;
            
            case 'error':
                showError(data.message);
                break;
            
            default:
                console.warn('Unknown message type:', data.type);
        }
    } catch (error) {
        console.error('Error parsing message:', error);
        showError('Failed to process server response.');
    }
}

/**
 * Handle WebSocket errors
 */
function handleWebSocketError(error) {
    console.error('WebSocket error:', error);
    updateConnectionStatus('error', 'Connection Error');
}

/**
 * Handle WebSocket connection closed
 */
function handleWebSocketClose(event) {
    console.log('WebSocket closed:', event.code, event.reason);
    state.isConnected = false;
    updateConnectionStatus('disconnected', 'Disconnected');
    
    // Attempt reconnection if conversation is active
    if (state.conversationActive && state.reconnectAttempts < CONFIG.MAX_RECONNECT_ATTEMPTS) {
        state.reconnectAttempts++;
        console.log(`Reconnection attempt ${state.reconnectAttempts}/${CONFIG.MAX_RECONNECT_ATTEMPTS}`);
        
        updateConnectionStatus('reconnecting', 'Reconnecting...');
        
        setTimeout(() => {
            initializeWebSocket();
        }, CONFIG.RECONNECT_DELAY);
    } else if (state.conversationActive) {
        showError('Connection lost. Please refresh the page to continue.');
    }
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(status, text) {
    elements.statusDot.className = 'pulse-dot';
    
    if (status === 'connected') {
        elements.statusDot.classList.add('connected');
    } else if (status === 'error') {
        elements.statusDot.classList.add('error');
    }
    
    elements.statusText.textContent = text;
}

/**
 * Send message via WebSocket
 */
function sendWebSocketMessage(type, message, choiceId = null) {
    if (!state.isConnected || !state.websocket) {
        showError('Not connected to server. Please refresh the page.');
        return false;
    }
    
    try {
        const payload = {
            type: type,
            message: message
        };
        
        if (choiceId) {
            payload.choice_id = choiceId;
        }
        
        state.websocket.send(JSON.stringify(payload));
        console.log('Sent message:', payload);
        return true;
    } catch (error) {
        console.error('Failed to send message:', error);
        showError('Failed to send message. Please try again.');
        return false;
    }
}

// ==========================================
// UI Update Functions
// ==========================================

/**
 * Show welcome screen
 */
function showWelcomeScreen() {
    elements.welcomeScreen.style.display = 'flex';
    elements.chatScreen.style.display = 'none';
    elements.initialInput.value = '';
    elements.charCount.textContent = '0';
    elements.launchBtn.disabled = true;
}

/**
 * Show chat screen
 */
function showChatScreen() {
    elements.welcomeScreen.style.display = 'none';
    elements.chatScreen.style.display = 'flex';
    elements.chatMessages.innerHTML = '';
    elements.answerInput.value = '';
    elements.completionOverlay.style.display = 'none';
    
    // Update progress
    state.currentQuestionNumber = 0;
    updateProgress();
}

/**
 * Add message to chat
 */
function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    
    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${isUser ? 'user-bubble' : 'ai-bubble'}`;
    bubble.textContent = content;
    
    const avatar = document.createElement('div');
    avatar.className = `message-avatar ${isUser ? 'user-avatar' : 'ai-avatar'}`;
    avatar.innerHTML = isUser 
        ? `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
             <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
             <circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2"/>
             <path d="M6.5 18.5C7.5 16.5 9.5 15 12 15C14.5 15 16.5 16.5 17.5 18.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
           </svg>`
        : `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
             <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
             <path d="M8 14C8 14 9.5 16 12 16C14.5 16 16 14 16 14M9 9H9.01M15 9H15.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
           </svg>`;
    
    messageDiv.appendChild(bubble);
    messageDiv.appendChild(avatar);
    elements.chatMessages.appendChild(messageDiv);
    
    scrollToBottom();
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    const typingClone = elements.typingTemplate.content.cloneNode(true);
    const typingElement = typingClone.querySelector('.typing-message');
    typingElement.id = 'typingIndicator';
    
    elements.chatMessages.appendChild(typingClone);
    scrollToBottom();
}

/**
 * Remove typing indicator
 */
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

/**
 * Update progress bar
 */
function updateProgress() {
    const progress = (state.currentQuestionNumber / state.totalQuestions) * 100;
    elements.progressFill.style.width = `${progress}%`;
    elements.currentQuestion.textContent = state.currentQuestionNumber;
    elements.totalQuestions.textContent = state.totalQuestions;
}

/**
 * Show error message
 */
function showError(message) {
    elements.errorText.textContent = message;
    elements.errorMessage.style.display = 'flex';
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        elements.errorMessage.style.display = 'none';
    }, 5000);
}

/**
 * Enable/disable chat input
 */
function setInputEnabled(enabled) {
    elements.answerInput.disabled = !enabled;
    elements.sendBtn.disabled = !enabled;
    
    if (enabled) {
        elements.answerInput.focus();
    }
}

/**
 * Scroll to bottom of chat
 */
function scrollToBottom() {
    setTimeout(() => {
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }, CONFIG.AUTO_SCROLL_DELAY);
}

// ==========================================
// NEW: Multi-Phase Message Handlers
// ==========================================

/**
 * Handle initial complete message
 */
function handleInitialComplete(data) {
    setInputEnabled(false);
    
    setTimeout(() => {
        removeTypingIndicator();
        if (data.message) {
            addMessage(data.message, false);
        }
    }, CONFIG.TYPING_DELAY);
}

/**
 * Handle thinking messages
 */
function handleThinkingMessage(data) {
    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'message ai-message thinking-message animate-slide-in';
    thinkingDiv.innerHTML = `
        <div class="message-bubble ai-bubble">
            <div class="thinking-dots">
                <span></span><span></span><span></span>
            </div>
            <span>${data.message}</span>
        </div>
    `;
    
    elements.chatMessages.appendChild(thinkingDiv);
    scrollToBottom();
}

/**
 * Handle personality reveal
 */
function handlePersonalityReveal(data) {
    const bonus = data.bonus;
    
    const personalityCard = document.createElement('div');
    personalityCard.className = 'personality-card animate-slide-in';
    personalityCard.innerHTML = `
        <div class="personality-header">
            <h2>${bonus.title}</h2>
            <p class="personality-subtitle">${bonus.subtitle}</p>
        </div>
        
        <div class="personality-content">
            <div class="personality-type">
                <h3>${bonus.personality_type}</h3>
            </div>
            
            <div class="personality-section">
                <h4>✨ Your Traits:</h4>
                <ul class="traits-list">
                    ${bonus.traits.map(trait => `<li>${trait}</li>`).join('')}
                </ul>
            </div>
            
            <div class="personality-section">
                <h4>🎯 Who You Are:</h4>
                <p>${bonus.description}</p>
            </div>
            
            <div class="personality-section">
                <h4>💡 What This Means:</h4>
                <p>${bonus.advice}</p>
            </div>
            
            <div class="personality-section prediction-section">
                <h4>🔮 Prediction:</h4>
                <p class="prediction-text">${bonus.prediction}</p>
            </div>
            
            <div class="personality-section strength-section">
                <h4>💪 Your Secret Strength:</h4>
                <p>${bonus.secret_strength}</p>
            </div>
            
            <div class="personality-scores">
                <div class="score-item">
                    <span class="score-label">Engagement Level</span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: 0%" data-target="${bonus.scores.engagement}"></div>
                    </div>
                    <span class="score-value">${bonus.scores.engagement}%</span>
                </div>
                <div class="score-item">
                    <span class="score-label">Honesty Level</span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: 0%" data-target="${bonus.scores.honesty}"></div>
                    </div>
                    <span class="score-value">${bonus.scores.honesty}%</span>
                </div>
            </div>
        </div>
    `;
    
    elements.chatMessages.appendChild(personalityCard);
    scrollToBottom();
    
    // Animate score bars
    setTimeout(() => {
        document.querySelectorAll('.score-fill').forEach(bar => {
            const target = bar.getAttribute('data-target');
            bar.style.width = target + '%';
        });
    }, 500);
}

/**
 * Handle mind reading game
 * UPDATED: Handles nested data structure
 */
function handleMindReading(data) {
    const mindData = data.data || data;
    
    const mindReadingCard = document.createElement('div');
    mindReadingCard.className = 'mind-reading-card animate-slide-in';
    mindReadingCard.innerHTML = `
        <div class="card-header">
            <h3>${mindData.title}</h3>
            <p>${mindData.subtitle}</p>
        </div>
        <div class="predictions-list">
            ${mindData.predictions.map((pred, idx) => `
                <div class="prediction-item" style="animation-delay: ${idx * 0.2}s">
                    <span class="prediction-number">${idx + 1}</span>
                    <span class="prediction-text">${pred}</span>
                </div>
            `).join('')}
        </div>
        <div class="challenge-text">${mindData.challenge}</div>
    `;
    
    elements.chatMessages.appendChild(mindReadingCard);
    scrollToBottom();
}

/**
 * Handle secret unlock
 * UPDATED: Handles nested data structure
 */
function handleSecretUnlock(data) {
    const secretData = data.data || data;
    
    const secretCard = document.createElement('div');
    secretCard.className = 'secret-unlock-card animate-unlock';
    secretCard.innerHTML = `
        <div class="unlock-icon">🔓</div>
        <h3>${secretData.title}</h3>
        <div class="secret-message">${secretData.message}</div>
        <div class="secret-from">— ${secretData.from}</div>
    `;
    
    elements.chatMessages.appendChild(secretCard);
    scrollToBottom();
}

/**
 * Handle interactive choice
 * UPDATED: Handles nested data structure
 */
function handleInteractiveChoice(data) {
    state.isWaitingForChoice = true;
    
    const choiceData = data.data || data;
    
    const choiceCard = document.createElement('div');
    choiceCard.className = 'interactive-choice-card animate-slide-in';
    choiceCard.innerHTML = `
        <div class="choice-header">
            <h3>${choiceData.title}</h3>
            <p class="choice-question">${choiceData.question}</p>
            <p class="choice-subtitle">${choiceData.subtitle}</p>
        </div>
        <div class="choice-buttons">
            ${choiceData.options.map(option => `
                <button class="choice-btn" data-choice="${option.id}">
                    <span class="choice-emoji">${option.emoji}</span>
                    <span class="choice-text">${option.text}</span>
                </button>
            `).join('')}
        </div>
    `;
    
    elements.chatMessages.appendChild(choiceCard);
    setInputEnabled(false);
    scrollToBottom();
    
    // Add click handlers to choice buttons
    choiceCard.querySelectorAll('.choice-btn').forEach(btn => {
        btn.addEventListener('click', () => handleChoiceClick(btn.dataset.choice));
    });
}

/**
 * Handle choice button click
 */
function handleChoiceClick(choiceId) {
    if (!state.isWaitingForChoice) return;
    
    state.isWaitingForChoice = false;
    sendWebSocketMessage('choice_response', '', choiceId);
    
    // Disable all choice buttons
    document.querySelectorAll('.choice-btn').forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.5';
    });
}

/**
 * Handle ultimate reveal
 * UPDATED: Handles nested data structure
 */
function handleUltimateReveal(data) {
    const revealData = data.data || data;
    
    const revealCard = document.createElement('div');
    revealCard.className = 'ultimate-reveal-card animate-slide-in';
    revealCard.innerHTML = `
        <div class="reveal-header">
            <h2>${revealData.title}</h2>
            <p>${revealData.intro}</p>
        </div>
        
        <div class="honest-take-section">
            <h3>The Real Talk:</h3>
            <div class="honest-take-text">${revealData.honest_take.replace(/\n/g, '<br>')}</div>
        </div>
        
        <div class="plot-twist-section">
            <h3>${revealData.plot_twist.title}</h3>
            <p class="plot-twist-reveal">${revealData.plot_twist.reveal}</p>
            <p class="plot-twist-insight">${revealData.plot_twist.insight}</p>
        </div>
        
        <div class="final-message-section">
            <h3>${revealData.final_message.title}</h3>
            <div class="final-message-text">${revealData.final_message.message.replace(/\n/g, '<br>')}</div>
            <p class="final-signature">${revealData.final_message.signature}</p>
        </div>
        
        <div class="shareable-card">
            <h4>${revealData.shareable.title}</h4>
            <div class="shareable-content">
                <div class="shareable-type">${revealData.shareable.type}</div>
                <div class="shareable-tagline">${revealData.shareable.tagline}</div>
            </div>
        </div>
    `;
    
    elements.chatMessages.appendChild(revealCard);
    scrollToBottom();
}

/**
 * Handle finale with countdown
 * UPDATED: Handles nested data structure
 */
function handleFinale(data) {
    const finaleData = data.data || data;
    
    const finaleCard = document.createElement('div');
    finaleCard.className = 'finale-card animate-fade-in';
    finaleCard.innerHTML = `
        <div class="finale-header">
            <h2>${finaleData.title}</h2>
        </div>
        
        <div class="stats-grid">
            <div class="stat-item">
                <span class="stat-label">Questions Answered</span>
                <span class="stat-value">${finaleData.stats.questions_answered}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Insights Shared</span>
                <span class="stat-value">${finaleData.stats.insights_shared}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Time Well Spent</span>
                <span class="stat-value">${finaleData.stats.time_well_spent}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Memories Created</span>
                <span class="stat-value">${finaleData.stats.memories_created}</span>
            </div>
        </div>
        
        <div class="achievement-box">
            <div class="achievement-icon">${finaleData.achievement.title}</div>
            <div class="achievement-name">${finaleData.achievement.name}</div>
            <div class="achievement-desc">${finaleData.achievement.description}</div>
        </div>
        
        <div class="easter-egg">${finaleData.easter_egg}</div>
        
        <div class="finale-countdown">
            <p>Restarting in <span id="countdown">10</span> seconds...</p>
            <button class="cancel-restart-btn" id="cancelBtn">Wait, I'm not done!</button>
        </div>
        
        <div class="finale-cta">
            <button class="cta-primary" id="manualRestartBtn">${finaleData.cta.primary}</button>
        </div>
    `;
    
    elements.chatMessages.appendChild(finaleCard);
    scrollToBottom();
    
    // Add event listeners
    document.getElementById('cancelBtn').addEventListener('click', cancelCountdown);
    document.getElementById('manualRestartBtn').addEventListener('click', handleRestart);
    
    // Start countdown
    startCountdown();
}

/**
 * Handle respectful ending with countdown
 * UPDATED: Handles nested data structure
 */
function handleRespectfulEnding(data) {
    const endingData = data.data || data;
    
    const endingCard = document.createElement('div');
    endingCard.className = 'respectful-ending-card animate-fade-in';
    endingCard.innerHTML = `
        <div class="ending-message">${endingData.message}</div>
        <div class="fun-fact">${endingData.fun_fact.replace(/\n/g, '<br>')}</div>
        <div class="final-words">${endingData.final_words}</div>
        
        <div class="finale-countdown">
            <p>Restarting in <span id="countdown">10</span> seconds...</p>
            <button class="cancel-restart-btn" id="cancelBtn">Cancel</button>
        </div>
        
        <button class="restart-btn" id="manualRestartBtn">${endingData.cta}</button>
    `;
    
    elements.chatMessages.appendChild(endingCard);
    scrollToBottom();
    
    // Add event listeners
    document.getElementById('cancelBtn').addEventListener('click', cancelCountdown);
    document.getElementById('manualRestartBtn').addEventListener('click', handleRestart);
    
    // Start countdown
    startCountdown();
}

/**
 * Start countdown timer
 */
function startCountdown() {
    let timeLeft = 10;
    const countdownElement = document.getElementById('countdown');
    
    state.countdownInterval = setInterval(() => {
        timeLeft--;
        if (countdownElement) {
            countdownElement.textContent = timeLeft;
        }
        
        if (timeLeft <= 0) {
            handleRestart();
        }
    }, 1000);
}

/**
 * Cancel countdown
 */
function cancelCountdown() {
    if (state.countdownInterval) {
        clearInterval(state.countdownInterval);
        state.countdownInterval = null;
        
        const countdownSection = document.querySelector('.finale-countdown');
        if (countdownSection) {
            countdownSection.innerHTML = '<p class="cancelled-text">Countdown cancelled. Take your time! ⏸️</p>';
        }
    }
}

// ==========================================
// Original Message Handlers (Enhanced)
// ==========================================

/**
 * Handle follow-up question from AI
 */
function handleFollowUpQuestion(data) {
    setTimeout(() => {
        removeTypingIndicator();
        addMessage(data.question, false);
        
        state.currentQuestionNumber = data.number;
        updateProgress();
        
        setInputEnabled(true);
    }, CONFIG.TYPING_DELAY);
}

// ==========================================
// User Action Handlers
// ==========================================

/**
 * Handle launch button click
 */
function handleLaunch() {
    const initialMessage = elements.initialInput.value.trim();
    
    if (!initialMessage) {
        showError('Please enter a message to start.');
        return;
    }
    
    if (!state.isConnected) {
        showError('Not connected to server. Please refresh the page.');
        return;
    }
    
    showChatScreen();
    addMessage(initialMessage, true);
    showTypingIndicator();
    
    const success = sendWebSocketMessage('initial', initialMessage);
    
    if (success) {
        state.conversationActive = true;
        setInputEnabled(false);
    }
}

/**
 * Handle send answer button click
 */
function handleSendAnswer() {
    const answer = elements.answerInput.value.trim();
    
    if (!answer) {
        showError('Please enter an answer.');
        return;
    }
    
    addMessage(answer, true);
    elements.answerInput.value = '';
    elements.answerInput.style.height = 'auto';
    
    setInputEnabled(false);
    showTypingIndicator();
    
    sendWebSocketMessage('answer', answer);
}

/**
 * Handle restart button click
 */
function handleRestart() {
    // Clear countdown if running
    if (state.countdownInterval) {
        clearInterval(state.countdownInterval);
        state.countdownInterval = null;
    }
    
    // Reset state
    state.currentQuestionNumber = 0;
    state.conversationActive = false;
    state.isWaitingForChoice = false;
    
    // Show welcome screen
    showWelcomeScreen();
    
    // Reconnect WebSocket if needed
    if (!state.isConnected) {
        initializeWebSocket();
    }
}

// ==========================================
// Enhanced UI Features
// ==========================================

/**
 * Handle suggestion chip clicks
 */
function handleSuggestionClick(text) {
    elements.initialInput.value = text;
    elements.charCount.textContent = text.length;
    elements.launchBtn.disabled = false;
    elements.initialInput.focus();
}

/**
 * Handle error toast close
 */
function handleErrorClose() {
    elements.errorMessage.style.display = 'none';
}

// ==========================================
// Event Listeners
// ==========================================

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    // Initial input character counter
    elements.initialInput.addEventListener('input', (e) => {
        const length = e.target.value.length;
        elements.charCount.textContent = length;
        elements.launchBtn.disabled = length === 0;
    });
    
    // Launch button
    elements.launchBtn.addEventListener('click', handleLaunch);
    
    // Initial input - Enter key
    elements.initialInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!elements.launchBtn.disabled) {
                handleLaunch();
            }
        }
    });
    
    // Answer input - auto resize
    elements.answerInput.addEventListener('input', (e) => {
        e.target.style.height = 'auto';
        e.target.style.height = e.target.scrollHeight + 'px';
        
        elements.sendBtn.disabled = e.target.value.trim().length === 0;
    });
    
    // Answer input - Enter key
    elements.answerInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!elements.sendBtn.disabled) {
                handleSendAnswer();
            }
        }
    });
    
    // Send button
    elements.sendBtn.addEventListener('click', handleSendAnswer);
    
    // Restart button
    elements.restartBtn.addEventListener('click', handleRestart);
    
    // Suggestion chips
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const text = chip.getAttribute('data-text');
            handleSuggestionClick(text);
        });
    });
    
    // Error toast close button
    const closeBtn = document.querySelector('.toast-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', handleErrorClose);
    }
}

// ==========================================
// Application Initialization
// ==========================================

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('Initializing Acadza Ultimate WebSocket AI...');
    
    initializeEventListeners();
    initializeWebSocket();
    showWelcomeScreen();
    
    console.log('Application initialized successfully');
}

// Start the application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

/**
 * Handle page unload
 */
window.addEventListener('beforeunload', () => {
    if (state.websocket && state.isConnected) {
        state.websocket.close();
    }
    if (state.countdownInterval) {
        clearInterval(state.countdownInterval);
    }
});