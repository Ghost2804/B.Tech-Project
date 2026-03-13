
document.addEventListener('DOMContentLoaded', () => {

    // ===== INTERACTIVE ENHANCEMENTS =====

    // --- Dark Mode ---
    function initDarkMode() {
        const savedMode = localStorage.getItem('darkMode');
        if (savedMode === 'true') {
            document.body.classList.add('dark-mode');
        }
    }
    initDarkMode();

    window.toggleDarkMode = function () {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
        showToast('Theme changed', 'info');
    };

    // --- Sidebar Toggle ---
    function initSidebar() {
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true') {
            document.getElementById('sidebar')?.classList.add('collapsed');
            updateToggleIcon(true);
        }
    }
    initSidebar();

    window.toggleSidebar = function () {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;

        sidebar.classList.toggle('collapsed');
        const isCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarCollapsed', isCollapsed);
        updateToggleIcon(isCollapsed);
    };

    function updateToggleIcon(isCollapsed) {
        const btn = document.getElementById('btn-toggle-sidebar');
        if (btn) {
            const icon = btn.querySelector('i');
            if (icon) {
                icon.className = isCollapsed ? 'fa-solid fa-bars' : 'fa-solid fa-xmark';
            }
        }
    }

    // Dark mode toggle button
    const darkModeBtn = document.getElementById('dark-mode-toggle');
    if (darkModeBtn) {
        darkModeBtn.addEventListener('click', toggleDarkMode);
    }

    // --- Toast Notifications ---
    window.showToast = function (message, type = 'info', duration = 3000) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const icons = {
            success: 'fa-circle-check',
            error: 'fa-circle-xmark',
            warning: 'fa-triangle-exclamation',
            info: 'fa-circle-info'
        };

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="fa-solid ${icons[type] || icons.info}"></i>
            <span class="toast-message">${message}</span>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('leaving');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    };

    // --- Typing Indicator ---
    window.showTypingIndicator = function () {
        const div = document.createElement('div');
        div.className = 'message bot';
        div.id = 'typing-indicator-msg';
        div.innerHTML = `
            <div class="msg-avatar">
                <i class="fa-solid fa-robot"></i>
            </div>
            <div class="typing-indicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        `;
        const chatStream = document.getElementById('chat-stream');
        chatStream.appendChild(div);
        chatStream.scrollTop = chatStream.scrollHeight;
        return div.id;
    };

    window.hideTypingIndicator = function () {
        const indicator = document.getElementById('typing-indicator-msg');
        if (indicator) indicator.remove();
    };

    // --- Loading Skeleton ---
    window.showLoadingSkeleton = function (lines = 3) {
        const div = document.createElement('div');
        div.className = 'message bot';
        div.id = 'loading-skeleton-msg';

        let skeletonHtml = '<div class="skeleton-card">';
        for (let i = 0; i < lines; i++) {
            const widthClass = ['full', 'medium', 'short'][i % 3];
            skeletonHtml += `<div class="skeleton skeleton-line ${widthClass}"></div>`;
        }
        skeletonHtml += '</div>';

        div.innerHTML = `
            <div class="msg-avatar">
                <i class="fa-solid fa-robot"></i>
            </div>
            <div class="msg-content">${skeletonHtml}</div>
        `;
        const chatStream = document.getElementById('chat-stream');
        chatStream.appendChild(div);
        chatStream.scrollTop = chatStream.scrollHeight;
        return div.id;
    };

    window.hideLoadingSkeleton = function () {
        const skeleton = document.getElementById('loading-skeleton-msg');
        if (skeleton) skeleton.remove();
    };

    // --- Keyboard Shortcuts ---
    window.toggleShortcutsModal = function () {
        const modal = document.getElementById('shortcuts-modal');
        if (modal) modal.classList.toggle('visible');
    };

    document.addEventListener('keydown', (e) => {
        // Don't trigger shortcuts when typing in input
        const isTyping = document.activeElement.tagName === 'INPUT' ||
            document.activeElement.tagName === 'TEXTAREA';

        // Escape - close modals
        if (e.key === 'Escape') {
            const modal = document.getElementById('shortcuts-modal');
            if (modal && modal.classList.contains('visible')) {
                modal.classList.remove('visible');
            }
            return;
        }

        // Ctrl+Enter - send message
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            document.getElementById('btn-send')?.click();
            return;
        }

        // Ctrl+N - new research
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            document.getElementById('btn-new-chat')?.click();
            return;
        }

        // Ctrl+D - toggle dark mode
        if (e.ctrlKey && e.key === 'd') {
            e.preventDefault();
            toggleDarkMode();
            return;
        }

        if (!isTyping) {
            // / - focus search
            if (e.key === '/') {
                e.preventDefault();
                document.getElementById('user-input')?.focus();
                return;
            }

            // ? - show shortcuts
            if (e.key === '?') {
                e.preventDefault();
                toggleShortcutsModal();
                return;
            }
        }
    });

    // --- Ripple Effect ---
    function createRipple(event) {
        const button = event.currentTarget;
        const circle = document.createElement('span');
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;

        const rect = button.getBoundingClientRect();
        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${event.clientX - rect.left - radius}px`;
        circle.style.top = `${event.clientY - rect.top - radius}px`;
        circle.className = 'ripple';

        const existingRipple = button.querySelector('.ripple');
        if (existingRipple) existingRipple.remove();

        button.appendChild(circle);
    }

    document.querySelectorAll('.ripple-container').forEach(btn => {
        btn.addEventListener('click', createRipple);
    });

    // --- Floating Action Button ---
    window.toggleFab = function () {
        const container = document.getElementById('fab-container');
        if (container) container.classList.toggle('open');
    };

    window.scrollToTop = function () {
        const chatStream = document.getElementById('chat-stream');
        if (chatStream) {
            chatStream.scrollTo({ top: 0, behavior: 'smooth' });
        }
        toggleFab();
    };

    // --- Confetti Celebration ---
    window.showConfetti = function () {
        const container = document.createElement('div');
        container.className = 'confetti-container';
        document.body.appendChild(container);

        const colors = ['#6366f1', '#ec4899', '#22c55e', '#f59e0b', '#3b82f6'];

        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.animationDelay = Math.random() * 2 + 's';
            confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
            container.appendChild(confetti);
        }

        setTimeout(() => container.remove(), 4000);
    };

    // --- Progress Bar ---
    window.showProgress = function (containerId = 'progress-holder') {
        const holder = document.getElementById(containerId);
        if (!holder) return;

        holder.innerHTML = `
            <div class="progress-container">
                <div class="progress-bar" id="progress-bar"></div>
            </div>
        `;
    };

    window.updateProgress = function (percent) {
        const bar = document.getElementById('progress-bar');
        if (bar) bar.style.width = percent + '%';
    };

    // ===== CHAT HISTORY MANAGEMENT (ChatGPT-style) =====

    const chatHistory = {
        chats: JSON.parse(localStorage.getItem('researchCompassChats') || '[]'),
        currentChatId: null,

        init() {
            // Create initial chat if none exists
            if (this.chats.length === 0) {
                this.createNewChat('New Research');
            } else {
                this.currentChatId = this.chats[0].id;
            }
            this.render();
        },

        createNewChat(title = 'New Research') {
            const chat = {
                id: 'chat_' + Date.now(),
                title: title,
                createdAt: new Date().toISOString(),
                messages: []
            };
            this.chats.unshift(chat);
            this.currentChatId = chat.id;
            this.save();
            this.render();
            return chat;
        },

        save() {
            localStorage.setItem('researchCompassChats', JSON.stringify(this.chats));
        },

        deleteChat(chatId) {
            this.chats = this.chats.filter(c => c.id !== chatId);
            if (this.currentChatId === chatId) {
                this.currentChatId = this.chats.length > 0 ? this.chats[0].id : null;
                if (!this.currentChatId) {
                    this.createNewChat();
                }
            }
            this.save();
            this.render();
            showToast('Chat deleted', 'info');
        },

        renameChat(chatId, newTitle) {
            const chat = this.chats.find(c => c.id === chatId);
            if (chat) {
                chat.title = newTitle;
                this.save();
                this.render();
            }
        },

        selectChat(chatId) {
            // Save current chat messages before switching
            this.saveCurrentMessages();

            this.currentChatId = chatId;
            this.render();

            // Load selected chat messages
            this.loadChatMessages(chatId);
            showToast('Switched to chat', 'info');
        },

        saveCurrentMessages() {
            const chat = this.chats.find(c => c.id === this.currentChatId);
            if (chat) {
                // Save the current chat stream HTML
                const chatStream = document.getElementById('chat-stream');
                chat.messagesHtml = chatStream.innerHTML;

                // Also save state data
                if (window.currentPapers) {
                    chat.papers = window.currentPapers;
                }
                if (window.currentSummaries) {
                    chat.summaries = window.currentSummaries;
                }
                this.save();
            }
        },

        loadChatMessages(chatId) {
            const chat = this.chats.find(c => c.id === chatId);
            const chatStream = document.getElementById('chat-stream');

            if (chat && chat.messagesHtml) {
                // Restore saved messages
                chatStream.innerHTML = chat.messagesHtml;

                // Restore state data
                if (chat.papers) {
                    window.currentPapers = chat.papers;
                }
                if (chat.summaries) {
                    window.currentSummaries = chat.summaries;
                }
            } else {
                // New chat - show welcome message
                chatStream.innerHTML = '';
                // Trigger welcome message
                const event = new CustomEvent('newChatLoaded');
                document.dispatchEvent(event);
            }
        },

        updateCurrentChatTitle(title) {
            const chat = this.chats.find(c => c.id === this.currentChatId);
            if (chat && chat.title === 'New Research') {
                chat.title = title.substring(0, 30) + (title.length > 30 ? '...' : '');
                this.save();
                this.render();
            }
        },

        isToday(dateStr) {
            const date = new Date(dateStr);
            const today = new Date();
            return date.toDateString() === today.toDateString();
        },

        render() {
            const todayContainer = document.getElementById('chat-history-today');
            const previousContainer = document.getElementById('chat-history-previous');

            if (!todayContainer || !previousContainer) return;

            const todayChats = this.chats.filter(c => this.isToday(c.createdAt));
            const previousChats = this.chats.filter(c => !this.isToday(c.createdAt));

            todayContainer.innerHTML = todayChats.length === 0
                ? '<div class="chat-history-empty">No chats today</div>'
                : todayChats.map(c => this.renderChatItem(c)).join('');

            previousContainer.innerHTML = previousChats.length === 0
                ? '<div class="chat-history-empty">No previous chats</div>'
                : previousChats.map(c => this.renderChatItem(c)).join('');
        },

        renderChatItem(chat) {
            const isActive = chat.id === this.currentChatId;
            return `
                <div class="chat-item ${isActive ? 'active' : ''}" data-chat-id="${chat.id}" onclick="chatHistory.selectChat('${chat.id}')">
                    <div class="chat-item-icon">
                        <i class="fa-regular fa-message"></i>
                    </div>
                    <span class="chat-item-title">${chat.title}</span>
                    <div class="chat-item-actions">
                        <button class="chat-action-btn" onclick="event.stopPropagation(); chatHistory.startRename('${chat.id}')" title="Rename">
                            <i class="fa-solid fa-pen"></i>
                        </button>
                        <button class="chat-action-btn delete" onclick="event.stopPropagation(); chatHistory.deleteChat('${chat.id}')" title="Delete">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        },

        startRename(chatId) {
            const chatItem = document.querySelector(`[data-chat-id="${chatId}"]`);
            const titleSpan = chatItem.querySelector('.chat-item-title');
            const currentTitle = titleSpan.textContent;

            titleSpan.outerHTML = `<input type="text" class="chat-item-input" value="${currentTitle}" 
                onblur="chatHistory.finishRename('${chatId}', this.value)"
                onkeydown="if(event.key==='Enter'){this.blur();} if(event.key==='Escape'){this.value='${currentTitle}';this.blur();}"
                onclick="event.stopPropagation()">`;

            const input = chatItem.querySelector('.chat-item-input');
            input.focus();
            input.select();
        },

        finishRename(chatId, newTitle) {
            if (newTitle.trim()) {
                this.renameChat(chatId, newTitle.trim());
            } else {
                this.render(); // Reset to original
            }
        }
    };

    // Make chatHistory globally accessible
    window.chatHistory = chatHistory;

    // Initialize chat history
    chatHistory.init();

    // ===== EXISTING CODE CONTINUES BELOW =====

    // --- State Management ---
    const state = {
        mode: 'IDLE', // IDLE, SEARCHING, READING, CHATTING
        papers: [],
        summaries: [],
        currentTopic: '',
        currentQuery: '',
        currentOffset: 0,
        sessionSeenDois: new Set(),
        selectedPapers: [] // For comparison feature
    };

    // Sync state with window for chat persistence
    window.currentPapers = state.papers;
    window.currentSummaries = state.summaries;
    window.getState = () => state;

    // --- Elements ---
    const els = {
        chatStream: document.getElementById('chat-stream'),
        input: document.getElementById('user-input'),
        btnSend: document.getElementById('btn-send'),
        btnNew: document.getElementById('btn-new-chat'),
        status: document.getElementById('agent-status')
    };

    // --- Initial Greeting ---
    addMessage({
        role: 'bot',
        text: "## Welcome to Research Compass\nI am your AI Research Agent. You can:\n- Ask me to find research papers (e.g., *'Find papers on 3D printing with LLM'*)\n- Ask questions about papers I've found\n- Switch topics anytime by asking for a new search\n\n**Tip:** Press `?` to see keyboard shortcuts!"
    });

    // --- Event Listeners ---
    els.btnSend.addEventListener('click', handleInput);
    els.input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleInput();
    });

    els.btnNew.addEventListener('click', () => {
        // Save current chat before creating new one
        chatHistory.saveCurrentMessages();

        // Create new chat and clear the stream
        chatHistory.createNewChat('New Research');
        document.getElementById('chat-stream').innerHTML = '';

        // Reset state
        state.mode = 'IDLE';
        state.papers = [];
        state.summaries = [];
        state.currentTopic = '';
        state.currentQuery = '';
        state.currentOffset = 0;
        state.sessionSeenDois = new Set();

        // Show welcome message
        addMessage({
            role: 'bot',
            text: "## Welcome to Research Compass\nI am your AI Research Agent. You can:\n- Ask me to find research papers (e.g., *'Find papers on 3D printing with LLM'*)\n- Ask questions about papers I've found\n- Switch topics anytime by asking for a new search\n\n**Tip:** Press `?` to see keyboard shortcuts!"
        });

        showToast('Started new research', 'success');
    });

    // ---Core Logic with Intent Detection ---
    async function handleInput() {
        const text = els.input.value.trim();
        if (!text) return;

        // Clear input
        els.input.value = '';
        els.input.placeholder = "Analyzing...";
        els.input.disabled = true;
        els.btnSend.disabled = true;

        // User Message
        addMessage({ role: 'user', text: text });

        try {
            // Step 1: Detect Intent using LLM
            const intentRes = await fetch('/intent', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, papers_loaded: state.papers.length > 0 })
            });
            const intent = await intentRes.json();

            console.log('Intent detected:', intent);

            // Step 2: Route based on intent
            if (intent.intent === 'SEARCH_REQUEST') {
                // User wants to search for papers
                const searchQuery = intent.keywords.join(' ');
                await performSearch(searchQuery);
            } else if (intent.intent === 'SUMMARY_REQUEST') {
                // User wants to generate summaries
                if (state.papers.length === 0) {
                    addMessage({
                        role: 'bot',
                        text: "I don't have any papers loaded yet. Please search for papers first, then I can summarize them."
                    });
                } else if (state.summaries.length > 0) {
                    addMessage({
                        role: 'bot',
                        text: "I've already generated summaries for these papers! You can see them above. Ask me questions about them or search for a new topic."
                    });
                } else {
                    await performSummary();
                }
            } else if (intent.intent === 'QUESTION') {
                //User is asking a question about existing papers
                if (state.papers.length === 0) {
                    addMessage({
                        role: 'bot',
                        text: "I don't have any papers loaded yet. Please ask me to search for papers first (e.g., 'Find papers on machine learning')"
                    });
                } else {
                    await performQA(text);
                }
            } else {
                // Chitchat - guide user
                addMessage({
                    role: 'bot',
                    text: "I can help you:\n- **Search for research papers** (e.g., 'Find papers on quantum computing')\n- **Answer questions** about papers I've found\n\nWhat would you like to do?"
                });
            }

        } catch (e) {
            addMessage({ role: 'bot', text: `**Error:** ${e.message}` });
        } finally {
            els.input.disabled = false;
            els.btnSend.disabled = false;
            els.input.focus();

            if (state.mode === 'CHATTING') {
                els.input.placeholder = "Ask a question or search for new papers...";
                els.status.textContent = "Ready";
            } else {
                els.input.placeholder = "Enter a topic to search or ask a question...";
            }
        }
    }

    // --- Agent Actions ---

    // Helper to log what papers we've seen this chat session
    function markPapersSeen(papersList) {
        if (!papersList) return;
        papersList.forEach(p => {
            const id = (p.doi || p.title || '').trim().toLowerCase();
            if (id) state.sessionSeenDois.add(id);
        });
    }

    async function performSearch(query) {
        state.mode = 'SEARCHING';
        els.status.textContent = "Searching papers...";

        // Reset pagination state for a brand-new topic search
        state.currentQuery = query;
        state.currentOffset = 0;
        // NOTE: sessionSeenDois is NOT reset here — it persists for the whole chat

        // Auto-update chat title based on search query
        chatHistory.updateCurrentChatTitle(query);

        // Show typing indicator instead of text message
        addMessage({ role: 'bot', text: `🔍 Searching for papers on **"${query}"**...` });
        showTypingIndicator();

        // API Call — send list of all UIDs already shown this session
        const res = await fetch('/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                offset: 0,
                seen_dois: [...state.sessionSeenDois]
            })
        });
        const data = await res.json();

        hideTypingIndicator();

        if (data.error || !data.results || data.results.length === 0) {
            addMessage({ role: 'bot', text: "I couldn't find any papers on that topic. Try different keywords or a broader topic." });
            showToast('No papers found', 'warning');
            state.mode = 'IDLE';
            return;
        }

        // Register these papers as seen for the rest of the session
        markPapersSeen(data.results);
        state.currentOffset = 20; // Springer API fetches 20 at a time, so next page starts at 20

        state.papers = data.results;
        window.currentPapers = data.results; // Store globally for comparison feature
        window.selectedPapersData = []; // Reset selection for new search
        window.selectedSummaryPapers = []; // Reset summary selection for new search
        state.mode = 'READING';

        // Success toast
        showToast(`Found ${state.papers.length} papers!`, 'success');

        // Render Papers Card (includes both summary + compare checkboxes and buttons)
        const cardMsgId = addMessage({
            role: 'bot',
            text: `I found **${state.papers.length} papers**. Tick the papers you want to summarize or compare below!`,
            type: 'papers_card',
            data: state.papers
        });

        // Add the initial Fetch More button
        if (cardMsgId) {
            const newMsgEl = document.getElementById(cardMsgId);
            if (newMsgEl) {
                const wrapper = document.createElement('div');
                wrapper.className = 'fetch-more-wrapper';
                wrapper.innerHTML = `
                    <button class="btn-fetch-more" id="btn-fetch-more-${cardMsgId}" onclick="fetchMorePapers()">
                        <i class="fa-solid fa-rotate-right"></i>
                        Fetch More Papers
                    </button>
                `;
                newMsgEl.querySelector('.msg-content').appendChild(wrapper);
            }
        }

        state.mode = 'CHATTING'; // Allow questions immediately
    }

    // Global handler for summary button - uses selected papers
    window.triggerSummary = async function () {
        if (!window.selectedSummaryPapers || window.selectedSummaryPapers.length === 0) {
            showToast('Please select at least 1 paper to summarize', 'warning');
            return;
        }
        await performSummary();
    };

    async function performSummary() {
        state.mode = 'READING';
        els.status.textContent = "Analyzing papers...";

        const papersToSummarize = window.selectedSummaryPapers || [];
        const count = papersToSummarize.length;

        // Show loading skeleton for summary
        addMessage({ role: 'bot', text: `📖 Reading and analyzing ${count} selected paper${count !== 1 ? 's' : ''}... (This may take 10-15 seconds)` });
        showLoadingSkeleton(5);

        const res = await fetch('/summarize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ papers: papersToSummarize })
        });
        const data = await res.json();

        hideLoadingSkeleton();

        if (data.error) {
            addMessage({ role: 'bot', text: `Error generating summary: ${data.error}` });
            showToast('Summary generation failed', 'error');
        } else {
            state.summaries = data.summaries;
            window.currentSummaries = data.summaries; // Store globally for chat persistence
            addMessage({
                role: 'bot',
                text: `Here are the detailed summaries for your ${count} selected paper${count !== 1 ? 's' : ''}:`,
                type: 'summary_card',
                data: state.summaries
            });

            addMessage({ role: 'bot', text: "**Ready for questions!** You can ask about these papers or search for a new topic." });
            showToast('Summaries generated!', 'success');
        }

        state.mode = 'CHATTING';
    }

    async function performQA(question) {
        els.status.textContent = "Analyzing...";

        // Show typing indicator for Q&A
        showTypingIndicator();

        // Context is the papers/summaries
        const context = JSON.stringify(state.summaries.length > 0 ? state.summaries : state.papers);

        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: question, context: context })
        });
        const data = await res.json();

        hideTypingIndicator();

        if (data.error) {
            addMessage({ role: 'bot', text: `Error: ${data.error}` });
            showToast('Failed to answer question', 'error');
        } else {
            addMessage({ role: 'bot', text: data.answer });
        }
    }

    //--- UI Helpers ---

    function addMessage({ role, text, type, data }) {
        const div = document.createElement('div');
        div.className = `message ${role}`;
        div.id = 'msg-' + Date.now();

        let contentHtml = role === 'bot' ? marked.parse(text) : `<p>${text}</p>`;

        // Special Cards
        if (type === 'papers_card') {
            const ts = Date.now();
            contentHtml += `<div class="card-grid">`;
            data.forEach((p, idx) => {
                const authors = Array.isArray(p.authors) ? p.authors.join(', ') : (p.authors || 'Authors not listed');
                const paperId = `paper-${ts}-${idx}`;
                contentHtml += `
                    <div class="mini-paper-card" id="${paperId}">
                        <span class="meta">${p.year || 'N/A'} • ${p.venue || 'Journal'}</span>
                        <h4>${p.title}</h4>
                        <p class="authors">${authors.substring(0, 80)}${authors.length > 80 ? '...' : ''}</p>
                        <a href="${p.url}" target="_blank" class="link">View Paper <i class="fa-solid fa-arrow-up-right-from-square"></i></a>
                        <div class="paper-checkboxes">
                            <label class="check-label summary-check-label">
                                <input type="checkbox" id="sum-${paperId}" onchange="toggleSummarySelection('${paperId}', ${idx})">
                                <span class="check-icon"><i class="fa-solid fa-file-lines"></i></span>
                                Summarize
                            </label>
                            <label class="check-label compare-check-label">
                                <input type="checkbox" id="cmp-${paperId}" onchange="togglePaperSelection('${paperId}', ${idx})">
                                <span class="check-icon"><i class="fa-solid fa-code-compare"></i></span>
                                Compare
                            </label>
                        </div>
                    </div>
                `;
            });
            contentHtml += `</div>`;

            // Summary button
            const summaryButtonId = `btn-summary-papers-${ts}`;
            window.currentSummaryButtonId = summaryButtonId;

            // Compare button
            const compareButtonId = `btn-compare-papers-${ts}`;
            window.currentCompareButtonId = compareButtonId;

            contentHtml += `
                <div class="action-buttons-row">
                    <div class="action-btn-group">
                        <button id="${summaryButtonId}" class="btn-summarize-selected" onclick="triggerSummary()" disabled>
                            <i class="fa-solid fa-wand-magic-sparkles"></i>
                            Generate Summary (0 selected)
                        </button>
                        <span class="action-hint">Tick papers to summarize</span>
                    </div>
                    <div class="action-btn-group">
                        <button id="${compareButtonId}" class="btn-compare" onclick="compareSelectedPapers()" disabled>
                            <i class="fa-solid fa-code-compare"></i>
                            Compare Papers (0 selected)
                        </button>
                        <span class="action-hint">Select 2–5 to compare</span>
                    </div>
                </div>
            `;
        }

        // Document-style Summary Cards
        if (type === 'summary_card') {
            data.forEach((s, idx) => {
                const summaryId = `summary-${Date.now()}-${idx}`;
                const takeaways = Array.isArray(s.key_takeaways) ? s.key_takeaways : [];
                const ni = '<span class="meta-not-provided">Info not provided</span>';

                // Authors display
                let authorsDisplay = ni;
                if (s.authors && Array.isArray(s.authors) && s.authors.length > 0) {
                    authorsDisplay = s.authors.join(', ');
                } else if (s.authors && typeof s.authors === 'string' && s.authors.trim()) {
                    authorsDisplay = s.authors;
                }

                const metaVal = (v) => (v && String(v).trim()) ? String(v).trim() : ni;
                const websiteVal = (v) => (v && String(v).trim() && v !== '#')
                    ? `<a href="${v}" target="_blank" class="meta-link">${v}</a>` : ni;

                contentHtml += `
                    <div class="summary-doc-card" id="${summaryId}">

                        <div class="summary-doc-header">
                            <span class="summary-paper-badge">Paper ${idx + 1}</span>
                            <h3 class="summary-doc-title">${s.title || 'Untitled'}</h3>
                        </div>

                        <div class="summary-meta-block">
                            <div class="summary-meta-heading"><i class="fa-solid fa-circle-info"></i> Paper Information</div>
                            <div class="summary-meta-grid">
                                <div class="summary-meta-row">
                                    <span class="meta-label"><i class="fa-solid fa-book-open"></i> Journal / Venue</span>
                                    <span class="meta-value">${metaVal(s.journal || s.venue)}</span>
                                </div>
                                <div class="summary-meta-row">
                                    <span class="meta-label"><i class="fa-solid fa-fingerprint"></i> DOI</span>
                                    <span class="meta-value">${metaVal(s.doi)}</span>
                                </div>
                                <div class="summary-meta-row">
                                    <span class="meta-label"><i class="fa-solid fa-barcode"></i> ISSN</span>
                                    <span class="meta-value">${metaVal(s.issn)}</span>
                                </div>
                                <div class="summary-meta-row">
                                    <span class="meta-label"><i class="fa-solid fa-calendar"></i> Year</span>
                                    <span class="meta-value">${metaVal(s.year)}</span>
                                </div>
                                <div class="summary-meta-row">
                                    <span class="meta-label"><i class="fa-solid fa-users"></i> Authors</span>
                                    <span class="meta-value">${authorsDisplay}</span>
                                </div>
                                <div class="summary-meta-row">
                                    <span class="meta-label"><i class="fa-solid fa-database"></i> Scopus Indexed</span>
                                    <span class="meta-value">${metaVal(s.scopus)}</span>
                                </div>
                                <div class="summary-meta-row">
                                    <span class="meta-label"><i class="fa-solid fa-link"></i> Website</span>
                                    <span class="meta-value">${websiteVal(s.website || s.url)}</span>
                                </div>
                            </div>
                        </div>

                        <div class="summary-doc-overview">
                            <i class="fa-solid fa-quote-left overview-icon"></i>
                            <p>${s.overview || 'Overview not available.'}</p>
                        </div>

                        <div class="summary-doc-sections">
                            <div class="summary-doc-section">
                                <div class="summary-section-title"><i class="fa-solid fa-magnifying-glass"></i> Research Problem</div>
                                <div class="summary-section-body">${s.research_problem || 'Not available.'}</div>
                            </div>
                            <div class="summary-doc-section">
                                <div class="summary-section-title"><i class="fa-solid fa-gears"></i> Methodology</div>
                                <div class="summary-section-body">${s.methodology || 'Not available.'}</div>
                            </div>
                            <div class="summary-doc-section">
                                <div class="summary-section-title"><i class="fa-solid fa-flask"></i> Experimental Setup</div>
                                <div class="summary-section-body">${s.experimental_setup || 'Not available.'}</div>
                            </div>
                            <div class="summary-doc-section">
                                <div class="summary-section-title"><i class="fa-solid fa-chart-bar"></i> Results</div>
                                <div class="summary-section-body">${s.results || 'Not available.'}</div>
                            </div>
                            <div class="summary-doc-section">
                                <div class="summary-section-title"><i class="fa-solid fa-triangle-exclamation"></i> Limitations</div>
                                <div class="summary-section-body">${s.limitations || 'Not available.'}</div>
                            </div>
                        </div>

                        ${takeaways.length > 0 ? `
                        <div class="summary-doc-takeaways">
                            <div class="takeaways-heading"><i class="fa-solid fa-star"></i> Key Takeaways</div>
                            <ul class="takeaways-list">
                                ${takeaways.map(t => `<li><span class="takeaway-bullet">✓</span> ${t}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}

                        ${s.potential_research_topics && s.potential_research_topics.length > 0 ? `
                        <div class="summary-doc-takeaways" style="margin-top:1rem; background:rgba(99,102,241,0.05); border-left-color:var(--primary);">
                            <div class="takeaways-heading"><i class="fa-solid fa-lightbulb"></i> Potential Research Topics</div>
                            <ul class="takeaways-list">
                                ${s.potential_research_topics.map(t => `<li><span class="takeaway-bullet" style="color:var(--primary);">💡</span> ${t}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}

                    </div>
                `;
            });
        }

        div.innerHTML = `
            <div class="msg-avatar">
                <i class="fa-solid fa-${role === 'user' ? 'user' : 'robot'}"></i>
            </div>
            <div class="msg-content">
                ${contentHtml}
            </div>
        `;

        els.chatStream.appendChild(div);
        els.chatStream.scrollTop = els.chatStream.scrollHeight;
        return div.id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    // Expose addMessage globally so external functions (e.g. fetchMorePapers)
    // can render new cards from outside the DOMContentLoaded closure.
    window._addMessageGlobal = addMessage;

});

// ── Fetch More Papers ────────────────────────────────────────────────────────
/**
 * Called by the "Fetch More Papers" button.
 * Uses the current query + offset stored in state to fetch the next page,
 * excluding everything already seen this session.
 */
window.fetchMorePapers = async function () {
    const s = window.getState ? window.getState() : null;
    if (!s || !s.currentQuery) {
        showToast('No active search to fetch more from', 'warning');
        return;
    }
    if (s.mode === 'SEARCHING') {
        showToast('Already fetching — please wait', 'info');
        return;
    }

    const prevMode = s.mode;
    s.mode = 'SEARCHING';

    // Disable all Fetch More buttons while loading
    document.querySelectorAll('.btn-fetch-more').forEach(b => {
        b.disabled = true;
        b.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Fetching...';
    });

    // We can't use the private showTypingIndicator here, so we just use the Toast
    showToast('Fetching more papers...', 'info', 2000);

    try {
        const res = await fetch('/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: s.currentQuery,
                offset: s.currentOffset,
                seen_dois: [...s.sessionSeenDois]
            })
        });
        const data = await res.json();
        
        if (data.error || !data.results || data.results.length === 0) {
            showToast('No more papers found for this topic', 'warning');
            // Replace button with a soft message
            document.querySelectorAll('.btn-fetch-more').forEach(b => {
                b.disabled = true;
                b.innerHTML = '<i class="fa-solid fa-check"></i> No more papers';
            });
            s.mode = prevMode;
            return;
        }

        const newPapers = data.results;

        // Register new papers as seen
        newPapers.forEach(p => {
            s.sessionSeenDois.add(((p.doi || p.title || '')).trim().toLowerCase());
        });
        s.currentOffset += 20; // Advance API offset by 20 for the next fetch

        // Append new papers to global list
        if (window.currentPapers) {
            window.currentPapers.push(...newPapers);
        } else {
            window.currentPapers = newPapers;
        }
        s.papers = window.currentPapers;

        showToast(`Fetched ${newPapers.length} more papers!`, 'success');

        // Render a new card for ONLY the new papers
        const cardMsgId = window._addMessageGlobal({
            role: 'bot',
            text: `Here are **${newPapers.length} more papers** on **"${s.currentQuery}"**:`,
            type: 'papers_card',
            data: newPapers
        });

        // Re-enable old buttons with updated offset indicator
        document.querySelectorAll(`.btn-fetch-more:not([id^="btn-fetch-more-${cardMsgId}"])`).forEach(b => {
            b.disabled = false;
            b.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Fetch More Papers';
        });

        // Append fresh Fetch More button to new card
        if (cardMsgId) {
            const newMsgEl = document.getElementById(cardMsgId);
            if (newMsgEl) {
                const wrapper = document.createElement('div');
                wrapper.className = 'fetch-more-wrapper';
                wrapper.innerHTML = `
                    <button class="btn-fetch-more" onclick="fetchMorePapers()">
                        <i class="fa-solid fa-rotate-right"></i>
                        Fetch More Papers
                    </button>
                `;
                newMsgEl.querySelector('.msg-content').appendChild(wrapper);
            }
        }

        s.mode = prevMode;

    } catch (e) {
        document.querySelectorAll('.btn-fetch-more').forEach(b => {
            b.disabled = false;
            b.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Fetch More Papers';
        });
        showToast('Failed to fetch more papers: ' + e.message, 'error');
        s.mode = prevMode;
    }
};

// Global function for tab switching (called from onclick in HTML)
function showTab(summaryId, tabName) {
    const summary = document.getElementById(summaryId);
    if (!summary) return;

    // Update button states
    summary.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Show selected content
    summary.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    summary.querySelector(`.tab-content[data-tab="${tabName}"]`).classList.add('active');
}

// Global function for paper selection (comparison)
function togglePaperSelection(paperId, paperIndex) {
    const checkbox = document.getElementById(`cmp-${paperId}`);
    const paperData = window.currentPapers ? window.currentPapers[paperIndex] : null;

    if (!paperData) return;

    if (checkbox.checked) {
        if (!window.selectedPapersData) window.selectedPapersData = [];
        if (window.selectedPapersData.length < 5) {
            window.selectedPapersData.push(paperData);
        } else {
            checkbox.checked = false;
            if (window.showToast) showToast('You can compare up to 5 papers at once', 'warning');
            return;
        }
    } else {
        if (window.selectedPapersData) {
            window.selectedPapersData = window.selectedPapersData.filter(p => p.title !== paperData.title);
        }
    }
    updateCompareButton();
}

// Update compare button state
function updateCompareButton() {
    const buttonId = window.currentCompareButtonId;
    if (!buttonId) return;
    const btn = document.getElementById(buttonId);
    if (!btn) return;
    const count = window.selectedPapersData ? window.selectedPapersData.length : 0;
    btn.disabled = count < 2;
    btn.innerHTML = `<i class="fa-solid fa-code-compare"></i> Compare Papers (${count} selected)`;
}

// Global function for summary selection
function toggleSummarySelection(paperId, paperIndex) {
    const checkbox = document.getElementById(`sum-${paperId}`);
    const paperData = window.currentPapers ? window.currentPapers[paperIndex] : null;
    if (!paperData) return;

    if (checkbox.checked) {
        if (!window.selectedSummaryPapers) window.selectedSummaryPapers = [];
        window.selectedSummaryPapers.push(paperData);
    } else {
        if (window.selectedSummaryPapers) {
            window.selectedSummaryPapers = window.selectedSummaryPapers.filter(p => p.title !== paperData.title);
        }
    }
    updateSummaryButton();
}

// Update summary button state
function updateSummaryButton() {
    const buttonId = window.currentSummaryButtonId;
    if (!buttonId) return;
    const btn = document.getElementById(buttonId);
    if (!btn) return;
    const count = window.selectedSummaryPapers ? window.selectedSummaryPapers.length : 0;
    btn.disabled = count < 1;
    btn.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> Generate Summary (${count} selected)`;
}

// Perform comparison
async function compareSelectedPapers() {
    if (!window.selectedPapersData || window.selectedPapersData.length < 2) {
        alert('Please select at least 2 papers to compare');
        return;
    }

    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'message bot';
    loadingMsg.innerHTML = `
        <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
        <div class="msg-content">
            <p>Generating comprehensive comparison of ${window.selectedPapersData.length} papers...</p>
        </div>
    `;
    document.getElementById('chat-stream').appendChild(loadingMsg);

    try {
        const res = await fetch('/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ papers: window.selectedPapersData })
        });

        const comparison = await res.json();
        loadingMsg.remove();

        if (comparison.error) {
            alert(`Comparison failed: ${comparison.error}`);
            return;
        }

        // Display comparison
        displayComparison(comparison);

    } catch (e) {
        loadingMsg.remove();
        alert('Comparison failed: ' + e.message);
    }
}

// Display comparison results
function displayComparison(comparison) {
    let html = `
        <div class="comparison-container">
            <h2>Paper Comparison Analysis</h2>
            <p class="comparison-overview">${comparison.overview || ''}</p>
    `;

    // Methodology comparison table
    if (comparison.methodology_comparison) {
        html += `
            <h3>Methodology Comparison</h3>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Paper</th>
                        <th>Approach</th>
                        <th>Architecture</th>
                        <th>Key Technique</th>
                        <th>Novelty</th>
                    </tr>
                </thead>
                <tbody>
        `;
        comparison.methodology_comparison.papers.forEach(p => {
            html += `
                <tr>
                    <td><strong>${p.title}</strong></td>
                    <td>${p.approach || 'N/A'}</td>
                    <td>${p.architecture || 'N/A'}</td>
                    <td>${p.key_technique || 'N/A'}</td>
                    <td>${p.novelty || 'N/A'}</td>
                </tr>
            `;
        });
        html += `</tbody></table>`;
    }

    // Results comparison
    if (comparison.results_comparison) {
        html += `
            <h3>Results Comparison</h3>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Paper</th>
                        <th>Metrics</th>
                        <th>Best Performance</th>
                    </tr>
                </thead>
                <tbody>
        `;
        comparison.results_comparison.papers.forEach(p => {
            const isBest = comparison.results_comparison.winner && comparison.results_comparison.winner.includes(p.title);
            html += `
                <tr>
                    <td><strong>${p.title}</strong> ${isBest ? '<span class="winner-badge">⭐ Best</span>' : ''}</td>
                    <td>${p.accuracy || p.other || 'N/A'}</td>
                    <td>${p.best_at || 'N/A'}</td>
                </tr>
            `;
        });
        html += `</tbody></table>`;

        if (comparison.results_comparison.winner) {
            html += `<p><strong>Overall Winner:</strong> ${comparison.results_comparison.winner}</p>`;
        }
    }

    // Key differences
    if (comparison.key_differences) {
        html += `<h3>Key Differences</h3><ul>`;
        comparison.key_differences.forEach(diff => {
            html += `<li>${diff}</li>`;
        });
        html += `</ul>`;
    }

    html += `</div>`;

    // Add to chat stream
    const div = document.createElement('div');
    div.className = 'message bot';
    div.innerHTML = `
        <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
        <div class="msg-content">${html}</div>
    `;
    document.getElementById('chat-stream').appendChild(div);

    // Smooth scroll to show the comparison results
    const chatStream = document.getElementById('chat-stream');
    chatStream.scrollTo({
        top: chatStream.scrollHeight,
        behavior: 'smooth'
    });
}
