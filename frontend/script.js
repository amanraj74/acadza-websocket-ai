/**
 * Acadza WebSocket Assignment - Frontend Client
 * Premium Professional WebSocket implementation
 * Enhanced with smooth animations and interactions
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
    totalQuestions: 3
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
 */
function handleWebSocketMessage(event) {
    try {
        const data = JSON.parse(event.data);
        console.log('Received message:', data);
        
        switch (data.type) {
            case 'follow_up':
                handleFollowUpQuestion(data);
                break;
            
            case 'complete':
                handleConversationComplete(data);
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
function sendWebSocketMessage(type, message) {
    if (!state.isConnected || !state.websocket) {
        showError('Not connected to server. Please refresh the page.');
        return false;
    }
    
    try {
        const payload = {
            type: type,
            message: message
        };
        
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
    
    // Auto scroll to bottom
    setTimeout(() => {
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }, CONFIG.AUTO_SCROLL_DELAY);
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    const typingClone = elements.typingTemplate.content.cloneNode(true);
    const typingElement = typingClone.querySelector('.typing-message');
    typingElement.id = 'typingIndicator';
    
    elements.chatMessages.appendChild(typingClone);
    
    setTimeout(() => {
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }, CONFIG.AUTO_SCROLL_DELAY);
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

// ==========================================
// Message Handlers
// ==========================================

/**
 * Handle follow-up question from AI
 */
function handleFollowUpQuestion(data) {
    // Remove typing indicator
    setTimeout(() => {
        removeTypingIndicator();
        
        // Add AI question
        addMessage(data.question, false);
        
        // Update progress
        state.currentQuestionNumber = data.number;
        updateProgress();
        
        // Enable input for user response
        setInputEnabled(true);
        
    }, CONFIG.TYPING_DELAY);
}

/**
 * Handle conversation completion
 */
function handleConversationComplete(data) {
    setTimeout(() => {
        removeTypingIndicator();
        
        // Show completion overlay
        elements.completionOverlay.style.display = 'flex';
        
        // Reset conversation state
        state.conversationActive = false;
        
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
    
    // Switch to chat screen
    showChatScreen();
    
    // Add user's initial message
    addMessage(initialMessage, true);
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send to backend
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
    
    // Add user's answer to chat
    addMessage(answer, true);
    
    // Clear input
    elements.answerInput.value = '';
    elements.answerInput.style.height = 'auto';
    
    // Disable input
    setInputEnabled(false);
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send to backend
    sendWebSocketMessage('answer', answer);
}

/**
 * Handle restart button click
 */
function handleRestart() {
    // Reset state
    state.currentQuestionNumber = 0;
    state.conversationActive = false;
    
    // Show welcome screen
    showWelcomeScreen();
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
    
    // Initial input - Enter key (with Shift for new line)
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
    
    // Answer input - Enter key (with Shift for new line)
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
    console.log('Initializing Acadza WebSocket AI Application...');
    
    // Set up event listeners
    initializeEventListeners();
    
    // Initialize WebSocket connection
    initializeWebSocket();
    
    // Show welcome screen
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
});
