/**
 * FitMind AI – Intelligent Health & Fitness Coach
 * Frontend Application Logic
 */

// Application State
const state = {
    currentConversationId: null,
    conversations: [],
    isLoading: false,
    selectedFile: null,
    selectedFileType: null, // 'image' or 'document'
    currentDocId: null,
    lastUserMessage: null,
    charts: {
        macroChart: null,
        calorieChart: null,
        progressChart: null,
    },
    fitnessData: {
        hydration: 1750,
        hydrationGoal: 2500,
        streak: 6,
        progress: [
            { date: 'Mon', weight: 71.2 },
            { date: 'Tue', weight: 71.0 },
            { date: 'Wed', weight: 70.8 },
            { date: 'Thu', weight: 70.9 },
            { date: 'Fri', weight: 70.5 },
            { date: 'Sat', weight: 70.3 },
            { date: 'Sun', weight: 70.1 },
        ],
        habits: [
            { id: 'h1', text: '7.5+ Hours Sleep & Recovery', icon: 'fa-moon', checked: true },
            { id: 'h2', text: 'Daily Hydration Target (2.5L)', icon: 'fa-droplet', checked: true },
            { id: 'h3', text: '30+ Min Exercise / Movement', icon: 'fa-person-running', checked: true },
            { id: 'h4', text: 'Nutrient-Dense Whole Foods', icon: 'fa-apple-whole', checked: true },
            { id: 'h5', text: '10 Min Posture & Stretching', icon: 'fa-child-reaching', checked: false },
            { id: 'h6', text: '5 Min Mindful Breathing / Zen', icon: 'fa-wind', checked: true },
        ],
        workouts: [
            { day: 'Monday', title: 'Upper Body Strength', exercises: ['Bench Press 4x8', 'Overhead Press 3x10', 'Barbell Row 4x10'], done: true },
            { day: 'Tuesday', title: 'Lower Body & Core', exercises: ['Barbell Squats 4x8', 'Romanian Deadlift 3x10', 'Plank 3x60s'], done: true },
            { day: 'Wednesday', title: 'Active Recovery & Yoga', exercises: ['Mobility Flow 25m', 'Zone 2 Walk 45m'], done: true },
            { day: 'Thursday', title: 'Push Hypertrophy', exercises: ['Incline DB Press 3x12', 'Dips 3x10', 'Lateral Raises 4x15'], done: true },
            { day: 'Friday', title: 'Pull & Posterior Chain', exercises: ['Pull-ups 4x8', 'Seated Cable Row 3x12', 'Face Pulls 4x15'], done: false },
            { day: 'Saturday', title: 'HIIT & Core Conditioning', exercises: ['Kettlebell Swings 4x20', 'Box Jumps 4x10', 'Hanging Leg Raises 3x12'], done: false },
            { day: 'Sunday', title: 'Rest & Meal Prep', exercises: ['Light Stretch 15m', 'Full Recovery Day'], done: false },
        ]
    }
};

// DOM Elements
const elements = {
    sidebar: document.getElementById('sidebar'),
    toggleSidebarBtn: document.getElementById('toggleSidebarBtn'),
    closeSidebarBtn: document.getElementById('closeSidebarBtn'),
    newChatBtn: document.getElementById('newChatBtn'),
    conversationList: document.getElementById('conversationList'),
    clearAllBtn: document.getElementById('clearAllBtn'),
    topbarChatTitle: document.getElementById('topbarChatTitle'),
    apiStatusBadge: document.getElementById('apiStatusBadge'),
    apiStatusText: document.getElementById('apiStatusText'),

    chatContainer: document.getElementById('chatContainer'),
    welcomeScreen: document.getElementById('welcomeScreen'),
    messagesList: document.getElementById('messagesList'),
    typingIndicator: document.getElementById('typingIndicator'),
    messageInput: document.getElementById('messageInput'),
    sendBtn: document.getElementById('sendBtn'),
    
    // Attachments & Drag Drop
    attachBtn: document.getElementById('attachBtn'),
    attachMenu: document.getElementById('attachMenu'),
    optUploadImage: document.getElementById('optUploadImage'),
    optUploadDoc: document.getElementById('optUploadDoc'),
    imageFileInput: document.getElementById('imageFileInput'),
    docFileInput: document.getElementById('docFileInput'),
    filePreviewStrip: document.getElementById('filePreviewStrip'),
    previewFileName: document.getElementById('previewFileName'),
    previewFileType: document.getElementById('previewFileType'),
    previewIcon: document.getElementById('previewIcon'),
    previewRemoveBtn: document.getElementById('previewRemoveBtn'),
    dragDropOverlay: document.getElementById('dragDropOverlay'),

    // Dashboard
    dashboardPanel: document.getElementById('dashboardPanel'),
    openDashboardTopBtn: document.getElementById('openDashboardTopBtn'),
    closeDashboardBtn: document.getElementById('closeDashboardBtn'),
    navDashboardBtn: document.getElementById('navDashboardBtn'),
    navChatBtn: document.getElementById('navChatBtn'),
    dashTabs: document.querySelectorAll('.dash-tab'),
    tabContents: document.querySelectorAll('.tab-content'),

    // BMI
    bmiHeight: document.getElementById('bmiHeight'),
    bmiWeight: document.getElementById('bmiWeight'),
    calcBmiBtn: document.getElementById('calcBmiBtn'),
    bmiScore: document.getElementById('bmiScore'),
    bmiCategory: document.getElementById('bmiCategory'),
    bmiExplanation: document.getElementById('bmiExplanation'),

    // Hydration
    hydroCurrent: document.getElementById('hydroCurrent'),
    hydroGoal: document.getElementById('hydroGoal'),
    hydroPercent: document.getElementById('hydroPercent'),
    hydrationCircle: document.getElementById('hydrationCircle'),
    addWater250: document.getElementById('addWater250'),
    addWater500: document.getElementById('addWater500'),
    resetWater: document.getElementById('resetWater'),

    // Lists
    workoutDaysList: document.getElementById('workoutDaysList'),
    habitItemsList: document.getElementById('habitItemsList'),
    toastContainer: document.getElementById('toastContainer'),
};

// -------------------------------------------------------------
// INITIALIZATION
// -------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    // Configure Marked
    if (window.marked) {
        marked.setOptions({
            breaks: true,
            gfm: true
        });
    }

    loadStoredFitnessData();
    setupEventListeners();
    setupCharts();
    renderWorkoutDays();
    renderHabitItems();
    updateHydrationMeter();
    checkApiHealth();
    loadConversations();
});

function loadStoredFitnessData() {
    const saved = localStorage.getItem('fitmind_data');
    if (saved) {
        try {
            const parsed = JSON.parse(saved);
            state.fitnessData = { ...state.fitnessData, ...parsed };
        } catch (e) {
            console.error('Error loading stored fitness data', e);
        }
    }
}

function saveFitnessData() {
    localStorage.setItem('fitmind_data', JSON.stringify(state.fitnessData));
}

// -------------------------------------------------------------
// EVENT LISTENERS
// -------------------------------------------------------------
function setupEventListeners() {
    // Sidebar
    elements.toggleSidebarBtn?.addEventListener('click', () => {
        elements.sidebar.classList.toggle('open');
    });
    elements.closeSidebarBtn?.addEventListener('click', () => {
        elements.sidebar.classList.remove('open');
    });

    // Navigation
    elements.newChatBtn?.addEventListener('click', () => {
        createNewChat();
        if (window.innerWidth <= 768) elements.sidebar.classList.remove('open');
    });

    elements.navChatBtn?.addEventListener('click', () => {
        elements.navChatBtn.classList.add('active');
        elements.navDashboardBtn.classList.remove('active');
        elements.dashboardPanel.classList.remove('open');
    });

    elements.navDashboardBtn?.addEventListener('click', () => {
        elements.dashboardPanel.classList.add('open');
        elements.navDashboardBtn.classList.add('active');
        elements.navChatBtn.classList.remove('active');
        if (window.innerWidth <= 768) elements.sidebar.classList.remove('open');
    });

    elements.openDashboardTopBtn?.addEventListener('click', () => {
        elements.dashboardPanel.classList.toggle('open');
    });
    elements.closeDashboardBtn?.addEventListener('click', () => {
        elements.dashboardPanel.classList.remove('open');
        elements.navDashboardBtn?.classList.remove('active');
        elements.navChatBtn?.classList.add('active');
    });

    // Clear all history
    elements.clearAllBtn?.addEventListener('click', handleClearAllHistory);

    // Chat Input
    elements.sendBtn?.addEventListener('click', handleSendMessage);
    elements.messageInput?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    elements.messageInput?.addEventListener('input', () => {
        elements.messageInput.style.height = 'auto';
        elements.messageInput.style.height = (elements.messageInput.scrollHeight) + 'px';
    });

    // Suggestions click
    document.querySelectorAll('.suggestion-card').forEach(card => {
        card.addEventListener('click', () => {
            const prompt = card.getAttribute('data-prompt');
            if (prompt) {
                elements.messageInput.value = prompt;
                elements.messageInput.style.height = 'auto';
                elements.messageInput.style.height = (elements.messageInput.scrollHeight) + 'px';
                handleSendMessage();
            }
        });
    });

    // Attachment dropdown
    elements.attachBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        elements.attachMenu.classList.toggle('hidden');
    });

    document.addEventListener('click', () => {
        elements.attachMenu?.classList.add('hidden');
    });

    elements.optUploadImage?.addEventListener('click', () => {
        elements.imageFileInput.click();
    });

    elements.optUploadDoc?.addEventListener('click', () => {
        elements.docFileInput.click();
    });

    elements.imageFileInput?.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            stageFile(e.target.files[0], 'image');
        }
    });

    elements.docFileInput?.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            stageFile(e.target.files[0], 'document');
        }
    });

    elements.previewRemoveBtn?.addEventListener('click', unstageFile);

    // Drag and Drop
    setupDragAndDrop();

    // Dashboard Tabs
    elements.dashTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            elements.dashTabs.forEach(t => t.classList.remove('active'));
            elements.tabContents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            const targetId = `tab-${tab.getAttribute('data-tab')}`;
            document.getElementById(targetId)?.classList.add('active');
        });
    });

    // BMI Calculator
    elements.calcBmiBtn?.addEventListener('click', calculateBMI);

    // Hydration buttons
    elements.addWater250?.addEventListener('click', () => addWater(250));
    elements.addWater500?.addEventListener('click', () => addWater(500));
    elements.resetWater?.addEventListener('click', resetWater);

    // Progress record
    document.getElementById('addProgressBtn')?.addEventListener('click', handleAddProgress);
}

// -------------------------------------------------------------
// DRAG AND DROP
// -------------------------------------------------------------
function setupDragAndDrop() {
    const dropArea = document.querySelector('.main-content');
    if (!dropArea) return;

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            elements.dragDropOverlay?.classList.add('active');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (e.type === 'drop') {
                elements.dragDropOverlay?.classList.remove('active');
                const dt = e.dataTransfer;
                if (dt.files && dt.files.length > 0) {
                    const file = dt.files[0];
                    if (file.type.startsWith('image/')) {
                        stageFile(file, 'image');
                    } else if (file.name.match(/\.(pdf|docx|txt)$/i)) {
                        stageFile(file, 'document');
                    } else {
                        showToast('Unsupported file type. Please upload JPG, PNG, PDF, DOCX, or TXT.', 'error');
                    }
                }
            } else if (e.relatedTarget === null || !dropArea.contains(e.relatedTarget)) {
                elements.dragDropOverlay?.classList.remove('active');
            }
        }, false);
    });
}

function stageFile(file, type) {
    state.selectedFile = file;
    state.selectedFileType = type;

    elements.previewFileName.textContent = file.name;
    elements.previewFileType.textContent = type === 'image' ? 'Food / Workout Image' : 'Fitness Document';
    elements.previewIcon.innerHTML = type === 'image' 
        ? '<i class="fa-solid fa-camera"></i>' 
        : '<i class="fa-solid fa-file-pdf"></i>';

    elements.filePreviewStrip.classList.remove('hidden');
    elements.messageInput.placeholder = type === 'image'
        ? "Add a note or question about this image (optional)..."
        : "Ask a question about this document or leave blank for a summary...";
    elements.messageInput.focus();
}

function unstageFile() {
    state.selectedFile = null;
    state.selectedFileType = null;
    elements.filePreviewStrip.classList.add('hidden');
    elements.imageFileInput.value = '';
    elements.docFileInput.value = '';
    elements.messageInput.placeholder = "Ask FitMind about workouts, nutrition, meals, fitness documents...";
}

// -------------------------------------------------------------
// CHAT FUNCTIONALITY
// -------------------------------------------------------------
async function handleSendMessage() {
    if (state.isLoading) return;

    const message = elements.messageInput.value.trim();
    const hasFile = state.selectedFile !== null;

    if (!message && !hasFile) return;

    // Reset input
    elements.messageInput.value = '';
    elements.messageInput.style.height = 'auto';

    // Switch from welcome screen to messages list
    elements.welcomeScreen.classList.add('hidden');
    elements.messagesList.classList.remove('hidden');

    state.lastUserMessage = message;

    // 1. FILE UPLOAD FLOW
    if (hasFile) {
        const file = state.selectedFile;
        const fileType = state.selectedFileType;
        unstageFile();

        // Render user message bubble
        const userMsgText = message ? `${message}\n\n*[Attached ${file.name}]*` : `Uploaded ${file.name}`;
        appendMessage('user', userMsgText);

        setLoading(true);

        try {
            const formData = new FormData();
            formData.append('file', file);
            if (state.currentConversationId) {
                formData.append('conversation_id', state.currentConversationId);
            }

            let endpoint = '';
            if (fileType === 'image') {
                formData.append('message', message);
                endpoint = '/api/analyze-image';
            } else {
                endpoint = '/api/analyze-document';
            }

            const res = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || 'Upload and analysis failed.');
            }

            const data = await res.json();
            if (data.conversation_id && !state.currentConversationId) {
                state.currentConversationId = data.conversation_id;
                loadConversations();
            }

            if (data.doc_id) {
                state.currentDocId = data.doc_id;
            }

            appendMessage('assistant', data.response);
        } catch (err) {
            console.error('Error analyzing file:', err);
            appendMessage('assistant', `⚠️ **Error analyzing file:** ${err.message}`);
            showToast(err.message, 'error');
        } finally {
            setLoading(false);
        }
        return;
    }

    // 2. TEXT / RAG FLOW
    appendMessage('user', message);
    setLoading(true);

    try {
        let endpoint = '/api/chat';
        let bodyPayload = {
            message: message,
            conversation_id: state.currentConversationId
        };

        // If we have an active document in context and user asks a question
        if (state.currentDocId) {
            endpoint = '/api/rag/question';
            bodyPayload = {
                question: message,
                conversation_id: state.currentConversationId,
                document_id: state.currentDocId
            };
        }

        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bodyPayload)
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || 'Failed to get AI response.');
        }

        const data = await res.json();

        if (data.conversation_id && !state.currentConversationId) {
            state.currentConversationId = data.conversation_id;
            loadConversations();
        }

        appendMessage('assistant', data.response);
    } catch (err) {
        console.error('Chat error:', err);
        appendMessage('assistant', `⚠️ **Sorry, something went wrong:** ${err.message}`);
        showToast(err.message, 'error');
    } finally {
        setLoading(false);
    }
}

function appendMessage(role, content) {
    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ${role}`;

    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    let parsedHtml = content;
    if (window.marked && role === 'assistant') {
        parsedHtml = marked.parse(content);
    } else {
        parsedHtml = content.replace(/\n/g, '<br>');
    }

    if (role === 'assistant') {
        wrapper.innerHTML = `
            <div class="bot-avatar">
                <i class="fa-solid fa-heart-pulse"></i>
            </div>
            <div class="message-bubble">
                <div class="message-header">
                    <span class="sender-name">FitMind AI</span>
                    <span class="message-time">${timeStr}</span>
                </div>
                <div class="message-content">${parsedHtml}</div>
                <div class="message-actions">
                    <button class="msg-btn copy-btn" title="Copy response">
                        <i class="fa-regular fa-copy"></i> Copy
                    </button>
                    <button class="msg-btn regen-btn" title="Regenerate response">
                        <i class="fa-solid fa-rotate"></i> Regenerate
                    </button>
                </div>
            </div>
        `;

        // Attach action listeners
        const copyBtn = wrapper.querySelector('.copy-btn');
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(content);
            showToast('Copied to clipboard!', 'success');
        });

        const regenBtn = wrapper.querySelector('.regen-btn');
        regenBtn.addEventListener('click', () => {
            if (state.lastUserMessage) {
                elements.messageInput.value = state.lastUserMessage;
                handleSendMessage();
            }
        });
    } else {
        wrapper.innerHTML = `
            <div class="message-bubble">
                <div class="message-header">
                    <span class="message-time">${timeStr}</span>
                </div>
                <div class="message-content">${parsedHtml}</div>
            </div>
            <div class="user-avatar">
                <i class="fa-solid fa-user"></i>
            </div>
        `;
    }

    elements.messagesList.appendChild(wrapper);
    scrollToBottom();
}

function scrollToBottom() {
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}

function setLoading(isLoading) {
    state.isLoading = isLoading;
    if (isLoading) {
        elements.typingIndicator.classList.remove('hidden');
        elements.sendBtn.disabled = true;
        scrollToBottom();
    } else {
        elements.typingIndicator.classList.add('hidden');
        elements.sendBtn.disabled = false;
        elements.messageInput.focus();
    }
}

// -------------------------------------------------------------
// CONVERSATION MANAGEMENT
// -------------------------------------------------------------
async function loadConversations() {
    try {
        const res = await fetch('/api/conversations');
        if (!res.ok) return;
        const data = await res.json();
        state.conversations = data.conversations || [];
        renderConversationList();
    } catch (err) {
        console.error('Failed to load conversations:', err);
    }
}

function renderConversationList() {
    if (!elements.conversationList) return;

    if (state.conversations.length === 0) {
        elements.conversationList.innerHTML = `
            <div class="text-muted p-2" style="font-size:0.8rem; text-align:center;">
                No conversations yet.<br>Start a new chat!
            </div>
        `;
        return;
    }

    elements.conversationList.innerHTML = '';
    state.conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = `conv-item ${conv.id === state.currentConversationId ? 'active' : ''}`;
        item.innerHTML = `
            <i class="fa-regular fa-message" style="font-size:0.8rem; margin-right:6px; color:var(--accent-cyan);"></i>
            <span class="conv-title">${escapeHtml(conv.title || 'Conversation')}</span>
            <div class="conv-actions">
                <button class="conv-action-btn delete" title="Delete chat">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        `;

        item.addEventListener('click', (e) => {
            if (e.target.closest('.delete')) {
                e.stopPropagation();
                deleteConversation(conv.id);
            } else {
                switchConversation(conv.id);
            }
        });

        elements.conversationList.appendChild(item);
    });
}

async function createNewChat() {
    state.currentConversationId = null;
    state.currentDocId = null;
    state.lastUserMessage = null;

    elements.messagesList.innerHTML = '';
    elements.messagesList.classList.add('hidden');
    elements.welcomeScreen.classList.remove('hidden');

    if (elements.topbarChatTitle) {
        elements.topbarChatTitle.innerHTML = `<i class="fa-solid fa-dumbbell"></i> <span>FitMind AI Coach</span>`;
    }

    renderConversationList();
    showToast('New conversation started', 'info');
}

async function switchConversation(convId) {
    if (state.currentConversationId === convId) return;

    setLoading(true);
    try {
        const res = await fetch(`/api/conversations/${convId}`);
        if (!res.ok) throw new Error('Conversation not found');
        const conv = await res.json();

        state.currentConversationId = conv.id;
        state.currentDocId = conv.documents && conv.documents.length > 0 ? conv.documents[0].id : null;

        elements.topbarChatTitle.innerHTML = `<i class="fa-solid fa-comments"></i> <span>${escapeHtml(conv.title)}</span>`;

        // Render messages
        elements.messagesList.innerHTML = '';
        if (conv.messages && conv.messages.length > 0) {
            elements.welcomeScreen.classList.add('hidden');
            elements.messagesList.classList.remove('hidden');

            conv.messages.forEach(msg => {
                appendMessage(msg.role, msg.content);
            });
        } else {
            elements.welcomeScreen.classList.remove('hidden');
            elements.messagesList.classList.add('hidden');
        }

        renderConversationList();
    } catch (err) {
        showToast('Error loading conversation: ' + err.message, 'error');
    } finally {
        setLoading(false);
    }
}

async function deleteConversation(convId) {
    try {
        const res = await fetch(`/api/conversations/${convId}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to delete');

        state.conversations = state.conversations.filter(c => c.id !== convId);
        if (state.currentConversationId === convId) {
            createNewChat();
        } else {
            renderConversationList();
        }
        showToast('Conversation removed', 'info');
    } catch (err) {
        showToast('Could not delete conversation', 'error');
    }
}

async function handleClearAllHistory() {
    if (!confirm('Are you sure you want to clear all conversation history? This cannot be undone.')) return;

    try {
        const res = await fetch('/api/conversations', { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to clear');

        state.conversations = [];
        createNewChat();
        showToast('All conversations cleared', 'info');
    } catch (err) {
        showToast('Could not clear history', 'error');
    }
}

// -------------------------------------------------------------
// FITNESS DASHBOARD & VISUALIZATIONS
// -------------------------------------------------------------
function setupCharts() {
    // 1. MACROS DOUGHNUT CHART
    const macroCtx = document.getElementById('macroChart')?.getContext('2d');
    if (macroCtx) {
        state.charts.macroChart = new Chart(macroCtx, {
            type: 'doughnut',
            data: {
                labels: ['Protein (g)', 'Carbs (g)', 'Fats (g)'],
                datasets: [{
                    data: [140, 180, 45],
                    backgroundColor: ['#9d4edd', '#00f2fe', '#f59e0b'],
                    borderWidth: 0,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                cutout: '72%'
            }
        });
    }

    // 2. CALORIES BAR CHART
    const calCtx = document.getElementById('calorieChart')?.getContext('2d');
    if (calCtx) {
        state.charts.calorieChart = new Chart(calCtx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Calories (kcal)',
                    data: [2100, 1950, 1820, 2250, 2040, 1890, 1850],
                    backgroundColor: 'rgba(0, 242, 254, 0.4)',
                    borderColor: '#00f2fe',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
                    y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }
                }
            }
        });
    }

    // 3. PROGRESS LINE CHART
    const progCtx = document.getElementById('progressChart')?.getContext('2d');
    if (progCtx) {
        state.charts.progressChart = new Chart(progCtx, {
            type: 'line',
            data: {
                labels: state.fitnessData.progress.map(p => p.date),
                datasets: [{
                    label: 'Weight (kg)',
                    data: state.fitnessData.progress.map(p => p.weight),
                    borderColor: '#9d4edd',
                    backgroundColor: 'rgba(157, 78, 221, 0.1)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2,
                    pointBackgroundColor: '#00f2fe',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
                    y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }
                }
            }
        });
    }
}

// BMI Calculator
function calculateBMI() {
    const h = parseFloat(elements.bmiHeight.value);
    const w = parseFloat(elements.bmiWeight.value);

    if (!h || !w || h <= 0 || w <= 0) {
        showToast('Please enter valid height and weight values.', 'error');
        return;
    }

    const heightInMeters = h / 100;
    const bmi = (w / (heightInMeters * heightInMeters)).toFixed(1);

    elements.bmiScore.textContent = bmi;

    let category = '';
    let catClass = '';
    let explanation = '';

    if (bmi < 18.5) {
        category = 'Underweight';
        catClass = 'underweight';
        explanation = 'Your BMI suggests underweight status. Focusing on nutrient-dense meals and progressive resistance training may support healthy weight gain.';
    } else if (bmi >= 18.5 && bmi < 25.0) {
        category = 'Normal Weight';
        catClass = 'normal';
        explanation = 'Your BMI falls within the healthy adult range. Continuing a balanced routine of wholesome food and regular physical activity supports longevity.';
    } else if (bmi >= 25.0 && bmi < 30.0) {
        category = 'Overweight';
        catClass = 'overweight';
        explanation = 'Your BMI indicates overweight classification. Small daily adjustments in physical activity and fiber intake can yield notable metabolic benefits.';
    } else {
        category = 'Obesity Category';
        catClass = 'obese';
        explanation = 'Your BMI falls in the obesity classification. We recommend consulting a healthcare provider for comprehensive metabolic and lifestyle guidance.';
    }

    elements.bmiCategory.textContent = category;
    elements.bmiCategory.className = `bmi-category ${catClass}`;
    elements.bmiExplanation.textContent = explanation;

    showToast(`BMI Calculated: ${bmi} (${category})`, 'success');
}

// Hydration Tracker
function addWater(amount) {
    state.fitnessData.hydration = Math.min(5000, state.fitnessData.hydration + amount);
    updateHydrationMeter();
    saveFitnessData();
    showToast(`+${amount}ml Water logged!`, 'success');
}

function resetWater() {
    state.fitnessData.hydration = 0;
    updateHydrationMeter();
    saveFitnessData();
    showToast('Daily water intake reset.', 'info');
}

function updateHydrationMeter() {
    const current = state.fitnessData.hydration;
    const goal = state.fitnessData.hydrationGoal;
    const percent = Math.min(100, Math.round((current / goal) * 100));

    if (elements.hydroCurrent) elements.hydroCurrent.textContent = current;
    if (elements.hydroGoal) elements.hydroGoal.textContent = goal;
    if (elements.hydroPercent) elements.hydroPercent.textContent = `${percent}%`;

    const statHydration = document.getElementById('statHydration');
    if (statHydration) statHydration.innerHTML = `${current} <small>ml</small>`;

    if (elements.hydrationCircle) {
        elements.hydrationCircle.style.background = `conic-gradient(var(--accent-cyan) 0% ${percent}%, rgba(255, 255, 255, 0.08) ${percent}% 100%)`;
    }
}

// Workout Planner List
function renderWorkoutDays() {
    if (!elements.workoutDaysList) return;

    elements.workoutDaysList.innerHTML = '';
    state.fitnessData.workouts.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = 'workout-day-card';
        card.innerHTML = `
            <div class="workout-day-header">
                <span>${item.day}: ${item.title}</span>
                <label style="cursor:pointer; display:flex; align-items:center; gap:4px; font-size:0.75rem; color:${item.done ? 'var(--success)' : 'var(--text-muted)'};">
                    <input type="checkbox" ${item.done ? 'checked' : ''} data-index="${index}">
                    ${item.done ? 'Done' : 'Pending'}
                </label>
            </div>
            ${item.exercises.map(ex => `
                <div class="workout-exercise-item">
                    <span>${ex}</span>
                </div>
            `).join('')}
        `;

        card.querySelector('input[type="checkbox"]').addEventListener('change', (e) => {
            state.fitnessData.workouts[index].done = e.target.checked;
            renderWorkoutDays();
            saveFitnessData();
            updateWorkoutStat();
        });

        elements.workoutDaysList.appendChild(card);
    });

    updateWorkoutStat();
}

function updateWorkoutStat() {
    const completed = state.fitnessData.workouts.filter(w => w.done).length;
    const stat = document.getElementById('statWorkouts');
    if (stat) stat.textContent = `${completed} / 7`;
}

// Habit Items
function renderHabitItems() {
    if (!elements.habitItemsList) return;

    elements.habitItemsList.innerHTML = '';
    state.fitnessData.habits.forEach((habit, index) => {
        const item = document.createElement('div');
        item.className = 'habit-item';
        item.innerHTML = `
            <div class="habit-info">
                <i class="fa-solid ${habit.icon}" style="color:var(--accent-cyan);"></i>
                <span>${habit.text}</span>
            </div>
            <input type="checkbox" class="habit-checkbox" ${habit.checked ? 'checked' : ''} data-index="${index}">
        `;

        item.querySelector('.habit-checkbox').addEventListener('change', (e) => {
            state.fitnessData.habits[index].checked = e.target.checked;
            saveFitnessData();
        });

        elements.habitItemsList.appendChild(item);
    });
}

// Progress Entry
function handleAddProgress() {
    const weightInput = document.getElementById('progWeight');
    const notesInput = document.getElementById('progNotes');

    const w = parseFloat(weightInput?.value);
    if (!w || w <= 0) {
        showToast('Please enter a valid weight value.', 'error');
        return;
    }

    const today = new Date().toLocaleDateString('en-US', { weekday: 'short' });
    state.fitnessData.progress.push({ date: today, weight: w });
    saveFitnessData();

    if (state.charts.progressChart) {
        state.charts.progressChart.data.labels = state.fitnessData.progress.map(p => p.date);
        state.charts.progressChart.data.datasets[0].data = state.fitnessData.progress.map(p => p.weight);
        state.charts.progressChart.update();
    }

    weightInput.value = '';
    if (notesInput) notesInput.value = '';
    showToast(`Weight entry ${w}kg logged successfully!`, 'success');
}

// -------------------------------------------------------------
// API HEALTH CHECK
// -------------------------------------------------------------
async function checkApiHealth() {
    try {
        const res = await fetch('/api/health');
        if (!res.ok) throw new Error('API offline');
        const data = await res.json();

        if (elements.apiStatusBadge && elements.apiStatusText) {
            if (data.gemini_configured) {
                elements.apiStatusBadge.querySelector('.status-dot').className = 'status-dot healthy';
                elements.apiStatusText.textContent = 'Gemini 2.0 Connected';
            } else {
                elements.apiStatusBadge.querySelector('.status-dot').className = 'status-dot';
                elements.apiStatusText.textContent = 'API Key Missing';
            }
        }
    } catch (err) {
        if (elements.apiStatusText) elements.apiStatusText.textContent = 'Server Offline';
    }
}

// -------------------------------------------------------------
// UTILITIES
// -------------------------------------------------------------
function showToast(message, type = 'info') {
    if (!elements.toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let icon = 'fa-info-circle';
    if (type === 'success') icon = 'fa-circle-check';
    if (type === 'error') icon = 'fa-triangle-exclamation';

    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
