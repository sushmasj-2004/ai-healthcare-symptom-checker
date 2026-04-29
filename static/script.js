class AIHealthChecker {
    constructor() {
        this.currentLang = 'en';
        this.timeoutId = null;
        this.init();
    }

    init() {
        this.bindEvents();
        document.querySelector('.lang-btn[data-lang="en"]').classList.add('active');
        this.updatePlaceholder();
        console.log('🚀 AI HealthChecker Ready!');
    }

    bindEvents() {
        // Language buttons
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.selectLanguage(e));
        });

        // Analyze button
        document.getElementById('analyzeBtn').addEventListener('click', () => this.analyze());

        // Speech
        document.getElementById('speechBtn').addEventListener('click', () => this.toggleSpeech());

        // Clear
        document.getElementById('clearBtn').addEventListener('click', () => this.clearAll());

        // Speak result
        document.getElementById('speakResult')?.addEventListener('click', () => this.speakAdvice());

        // Enter key
        document.getElementById('symptomsInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) this.analyze();
        });
    }

    selectLanguage(e) {
        document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
        e.currentTarget.classList.add('active');
        this.currentLang = e.currentTarget.dataset.lang;
        this.updatePlaceholder();
    }

    updatePlaceholder() {
        const placeholders = {
            'en': 'Describe symptoms (fever, cough, chest pain...)',
            'hi': 'लक्षण बताएं (बुखार, खांसी, सीने में दर्द...)',
            'kn': 'ಲಕ್ಷಣಗಳನ್ನು ಹೇಳಿ (ಜ್ವರ, ಶೀತ...)',
            'ta': 'அறிகுறிகளை சொல்லுங்கள்...',
            'te': 'లక్షణాలు చెప్పండి...',
            'mr': 'लक्षण सांगा...',
            'ml': 'ലക്ഷണങ്ങൾ പറയൂ...'
        };
        const input = document.getElementById('symptomsInput');
        input.placeholder = placeholders[this.currentLang] || placeholders['en'];
    }

    async analyze() {
        const symptoms = document.getElementById('symptomsInput').value.trim();
        if (!symptoms) {
            this.showError('Please describe your symptoms first');
            return;
        }

        // Show loading
        this.showLoading(true);

        // Clear previous timeout
        if (this.timeoutId) clearTimeout(this.timeoutId);

        try {
            // API call with 10s timeout
            const controller = new AbortController();
            this.timeoutId = setTimeout(() => controller.abort(), 10000);

            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symptoms, language: this.currentLang }),
                signal: controller.signal
            });

            const data = await response.json();

            if (data.success) {
                this.showResults(data);
            } else {
                this.showError(data.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('API Error:', error);
            this.showError('Connection timeout. Please try again.');
        } finally {
            this.showLoading(false);
            if (this.timeoutId) clearTimeout(this.timeoutId);
        }
    }

    showResults(data) {
        document.getElementById('diseaseName').textContent = data.disease;

        const confidence = data.confidence;
        document.getElementById('confidence').textContent = `Confidence: ${confidence}%`;

        const severity = data.severity.toUpperCase();
        const severityEl = document.getElementById('severity');
        severityEl.textContent = `Severity: ${severity}`;
        severityEl.className = `severity-badge severity-${data.severity}`;

        document.getElementById('advice').innerHTML = `
            <div class="advice-text">${data.advice}</div>
            ${data.precautions ? `<div class="precautions"><i class="fas fa-shield-alt"></i> ${data.precautions}</div>` : ''}
        `;

        document.getElementById('results').classList.remove('hidden');
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        const btn = document.getElementById('analyzeBtn');

        if (btn) btn.disabled = show;
        if (loading) loading.classList.toggle('hidden', !show);
    }

    showError(message) {
        const errorEl = document.getElementById('error');
        if (!errorEl) { console.error('UI Error:', message); return; }
        errorEl.textContent = message;
        errorEl.classList.remove('hidden');
        setTimeout(() => errorEl.classList.add('hidden'), 5000);
    }

    clearAll() {
        document.getElementById('symptomsInput').value = '';
        document.getElementById('results').classList.add('hidden');
        this.showLoading(false);
    }

    toggleSpeech() {
        if (!('webkitSpeechRecognition' in window)) {
            this.showError('Speech not supported. Use Chrome/Edge');
            return;
        }

        const btn = document.getElementById('speechBtn');
        if (btn.classList.contains('listening')) {
            this.stopSpeech();
        } else {
            this.startSpeech();
        }
    }

    startSpeech() {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = this.currentLang === 'en' ? 'en-US' : `${this.currentLang}-IN`;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            document.getElementById('speechBtn').classList.add('listening');
            document.getElementById('speechBtn').innerHTML = '<i class="fas fa-stop"></i> <span>Stop</span>';
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById('symptomsInput').value = transcript;
        };

        recognition.onend = () => this.stopSpeech();
        recognition.start();
        this.recognition = recognition;
    }

    stopSpeech() {
        if (this.recognition) {
            this.recognition.stop();
            this.recognition = null;
        }
        document.getElementById('speechBtn').classList.remove('listening');
        document.getElementById('speechBtn').innerHTML = '<i class="fas fa-microphone"></i> <span>Speak</span>';
    }

    speakAdvice() {
        const advice = document.getElementById('advice').textContent;
        const utterance = new SpeechSynthesisUtterance(advice);
        utterance.lang = this.currentLang === 'en' ? 'en-US' : `${this.currentLang}-IN`;
        utterance.rate = 0.9;
        speechSynthesis.speak(utterance);
    }
}

// ---- Dropdown ----
window.toggleDropdown = function() {
    const dropdown = document.getElementById('consultDropdown');
    dropdown.classList.toggle('hidden');

    document.addEventListener('click', function closeDropdown(e) {
        if (!e.target.closest('.consult-dropdown')) {
            dropdown.classList.add('hidden');
            document.removeEventListener('click', closeDropdown);
        }
    });
}

// ---- User Session Management ----
async function getDeviceInfo() {
    let ip = localStorage.getItem('hc_ip') || 'Detecting...';
    try {
        const res = await fetch('https://api.ipify.org?format=json');
        const data = await res.json();
        ip = data.ip;
        localStorage.setItem('hc_ip', ip);
    } catch(e) {}

    const deviceId = localStorage.getItem('deviceId') || (() => {
        const id = 'dev_' + Math.random().toString(36).substr(2, 12) + '_' + Date.now();
        localStorage.setItem('deviceId', id);
        return id;
    })();

    return { ip, deviceId };
}

async function initUserBar() {
    const raw = sessionStorage.getItem('hc_current_user');
    if (!raw) {
        window.location.href = '/auth';
        return;
    }

    const user = JSON.parse(raw);
    const deviceInfo = await getDeviceInfo();

    // Update user bar
    const initial = (user.firstName || 'G')[0].toUpperCase();
    document.getElementById('userAvatar').textContent = initial;
    document.getElementById('profileAvatarBig').textContent = initial;
    document.getElementById('userName').textContent = user.isGuest ? 'Guest User' : `${user.firstName} ${user.lastName || ''}`.trim();
    document.getElementById('userMeta').textContent = user.isGuest ? 'guest session' : user.email;

    // Update profile panel
    document.getElementById('profileNameBig').textContent = user.isGuest ? 'Guest User' : `${user.firstName} ${user.lastName || ''}`.trim();
    document.getElementById('profileEmailBig').textContent = user.email || '—';
    document.getElementById('profilePhone').textContent = user.phone || '—';
    document.getElementById('profileGender').textContent = user.gender ? user.gender.charAt(0).toUpperCase() + user.gender.slice(1) : '—';
    document.getElementById('profileLocation').textContent = user.location || '—';
    document.getElementById('profileDeviceId').textContent = '••••••••••••••••';
    document.getElementById('profileIp').textContent = '•••.•••.•••.•••';
    document.getElementById('profileSession').textContent = user.sessionStart ? new Date(user.sessionStart).toLocaleString() : '—';
}

function toggleProfilePanel() {
    document.getElementById('profilePanel').classList.toggle('hidden');
    document.getElementById('profileOverlay').classList.toggle('hidden');
}

function handleLogout() {
    sessionStorage.removeItem('hc_current_user');
    window.location.href = '/auth';
}

// ---- Initialize ----
document.addEventListener('DOMContentLoaded', () => {
    window.healthChecker = new AIHealthChecker();
    initUserBar();
});