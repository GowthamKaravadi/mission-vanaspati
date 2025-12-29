const API_URL = 'http://localhost:8000';

let analysisHistory = [];
let currentMode = 'single';
let confidenceThreshold = 0.5;
let selectedFiles = [];
let authToken = null;

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    initializeEventListeners();
    loadHistoryFromStorage();
});

function checkAuth() {
    authToken = localStorage.getItem('token');
    const email = localStorage.getItem('email');
    
    if (!authToken) {
        window.location.href = 'login.html';
        return;
    }
    
    const isAdmin = localStorage.getItem('isAdmin') === 'true';
    if (isAdmin) {
        addAdminLink();
    }
    
    addUserInfo(email);
}

function addAdminLink() {
    const sidebar = document.querySelector('.sidebar') || document.querySelector('main');
    const adminLink = document.createElement('div');
    adminLink.style.cssText = 'margin-bottom: 20px; padding: 15px; background: var(--light-gray); border-radius: var(--radius);';
    adminLink.innerHTML = `
        <a href="admin.html" style="color: var(--primary); text-decoration: none; font-weight: 600;">
            🛡️ Admin Dashboard
        </a>
    `;
    sidebar.insertBefore(adminLink, sidebar.firstChild);
}

function addUserInfo(email) {
    const header = document.querySelector('header .header-content');
    const userInfo = document.createElement('div');
    userInfo.style.cssText = 'margin-top: 15px; display: flex; justify-content: center; gap: 15px; align-items: center;';
    userInfo.innerHTML = `
        <span style="color: var(--gray);">👤 ${email}</span>
        <button onclick="logout()" style="padding: 8px 16px; background: var(--danger); color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;">
            Logout
        </button>
    `;
    header.appendChild(userInfo);
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.clear();
        window.location.href = 'login.html';
    }
}

function initializeEventListeners() {
    const modeButtons = document.querySelectorAll('.mode-btn');
    modeButtons.forEach(btn => {
        btn.addEventListener('click', () => switchMode(btn.dataset.mode));
    });

    const confidenceSlider = document.getElementById('confidenceThreshold');
    confidenceSlider.addEventListener('input', (e) => {
        confidenceThreshold = e.target.value / 100;
        document.getElementById('thresholdValue').textContent = e.target.value + '%';
    });

    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    const batchUploadArea = document.getElementById('batchUploadArea');
    const batchFileInput = document.getElementById('batchFileInput');
    batchUploadArea.addEventListener('click', () => batchFileInput.click());
    batchFileInput.addEventListener('change', handleBatchFileSelect);

    setupDragAndDrop(uploadArea, fileInput);
    setupDragAndDrop(batchUploadArea, batchFileInput);

    document.getElementById('removeImage').addEventListener('click', resetSingleUpload);
    document.getElementById('analyzeBtn').addEventListener('click', analyzeSingleImage);
    document.getElementById('clearBatch').addEventListener('click', clearBatchFiles);
    document.getElementById('analyzeBatchBtn').addEventListener('click', analyzeBatchImages);
    document.getElementById('clearHistory').addEventListener('click', clearHistory);
}

function switchMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });
    
    document.getElementById('singleMode').classList.toggle('active', mode === 'single');
    document.getElementById('batchMode').classList.toggle('active', mode === 'batch');
    
    resetSingleUpload();
    clearBatchFiles();
}

function setupDragAndDrop(area, input) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        area.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        area.addEventListener(eventName, () => area.classList.add('drag-over'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        area.addEventListener(eventName, () => area.classList.remove('drag-over'), false);
    });

    area.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        input.files = files;
        input.dispatchEvent(new Event('change'));
    }, false);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('previewImage').src = e.target.result;
        document.getElementById('uploadArea').style.display = 'none';
        document.getElementById('previewSection').classList.remove('hidden');
        document.getElementById('resultsSection').classList.add('hidden');
    };
    reader.readAsDataURL(file);
}

function resetSingleUpload() {
    document.getElementById('fileInput').value = '';
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('previewSection').classList.add('hidden');
    document.getElementById('resultsSection').classList.add('hidden');
}

async function analyzeSingleImage() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) return;

    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoader = analyzeBtn.querySelector('.btn-loader');
    
    analyzeBtn.disabled = true;
    btnText.classList.add('hidden');
    btnLoader.classList.remove('hidden');

    try {
        const result = await predictImage(file);
        
        if (result.confidence >= confidenceThreshold) {
            displaySingleResult(result);
            addToHistory(result);
        } else {
            showLowConfidenceWarning(result.confidence);
        }
    } catch (error) {
        showError('Analysis failed: ' + error.message);
    } finally {
        analyzeBtn.disabled = false;
        btnText.classList.remove('hidden');
        btnLoader.classList.add('hidden');
    }
}

async function predictImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${authToken}`
        },
        body: formData
    });

    if (response.status === 401) {
        localStorage.clear();
        window.location.href = 'login.html';
        throw new Error('Session expired. Please login again.');
    }

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    return await response.json();
}

function displaySingleResult(result) {
    const resultsSection = document.getElementById('resultsSection');
    const resultContent = document.getElementById('resultContent');

    const confidencePercent = (result.confidence * 100).toFixed(1);
    let confidenceClass = 'confidence-low';
    if (result.confidence >= 0.8) confidenceClass = 'confidence-high';
    else if (result.confidence >= 0.5) confidenceClass = 'confidence-medium';

    let html = `
        <div class="prediction-main">
            <div class="prediction-name">${result.class_name}</div>
            <div class="confidence-bar">
                <div class="confidence-fill ${confidenceClass}" style="width: ${confidencePercent}%">
                    ${confidencePercent}%
                </div>
            </div>
        </div>
    `;

    if (result.top_k && result.top_k.length > 1) {
        html += `
            <div class="alternatives">
                <h4>Alternative Predictions:</h4>
        `;
        result.top_k.slice(1).forEach((pred, idx) => {
            html += `
                <div class="alternative-item">
                    <span>${idx + 2}. ${pred.class_name}</span>
                    <span>${(pred.confidence * 100).toFixed(1)}%</span>
                </div>
            `;
        });
        html += `</div>`;
    }

    if (result.description || result.remedies) {
        html += `<div class="disease-info">`;
        
        if (result.description) {
            html += `
                <h3>Disease Information</h3>
                <p>${result.description}</p>
            `;
        }
        
        if (result.remedies && result.remedies.length > 0) {
            html += `
                <h3 style="margin-top: 20px;">Recommended Treatment</h3>
                <ul class="remedies-list">
            `;
            result.remedies.forEach(remedy => {
                html += `<li>${remedy}</li>`;
            });
            html += `</ul>`;
        }
        
        html += `</div>`;
    }

    resultContent.innerHTML = html;
    resultsSection.classList.remove('hidden');
}

function showLowConfidenceWarning(confidence) {
    const resultsSection = document.getElementById('resultsSection');
    const resultContent = document.getElementById('resultContent');
    
    resultContent.innerHTML = `
        <div class="prediction-main" style="border-left-color: var(--warning);">
            <h3 style="color: var(--warning);">⚠️ Low Confidence</h3>
            <p style="margin-top: 10px;">
                The prediction confidence (${(confidence * 100).toFixed(1)}%) is below the threshold 
                (${(confidenceThreshold * 100).toFixed(0)}%). Please try:
            </p>
            <ul style="margin-top: 15px; padding-left: 20px;">
                <li>Upload a clearer image</li>
                <li>Ensure good lighting</li>
                <li>Focus on a single leaf</li>
                <li>Adjust the confidence threshold</li>
            </ul>
        </div>
    `;
    
    resultsSection.classList.remove('hidden');
}

function showError(message) {
    const resultsSection = document.getElementById('resultsSection');
    const resultContent = document.getElementById('resultContent');
    
    resultContent.innerHTML = `
        <div class="prediction-main" style="border-left-color: var(--danger);">
            <h3 style="color: var(--danger);">❌ Error</h3>
            <p style="margin-top: 10px;">${message}</p>
        </div>
    `;
    
    resultsSection.classList.remove('hidden');
}

function handleBatchFileSelect(e) {
    const files = Array.from(e.target.files);
    
    if (files.length === 0) return;

    const validFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (validFiles.length === 0) {
        alert('Please select image files');
        return;
    }

    selectedFiles = validFiles;
    displayBatchPreview();
}

function displayBatchPreview() {
    const previewGrid = document.getElementById('batchPreviewGrid');
    const imageCount = document.getElementById('imageCount');
    
    imageCount.textContent = selectedFiles.length;
    previewGrid.innerHTML = '';

    selectedFiles.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const div = document.createElement('div');
            div.className = 'batch-item';
            div.innerHTML = `
                <img src="${e.target.result}" alt="Preview ${index + 1}">
                <button class="remove-btn" onclick="removeBatchFile(${index})">✕</button>
            `;
            previewGrid.appendChild(div);
        };
        reader.readAsDataURL(file);
    });

    document.getElementById('batchUploadArea').style.display = 'none';
    document.getElementById('batchPreviewSection').classList.remove('hidden');
    document.getElementById('batchResultsSection').classList.add('hidden');
}

function removeBatchFile(index) {
    selectedFiles.splice(index, 1);
    
    if (selectedFiles.length === 0) {
        clearBatchFiles();
    } else {
        displayBatchPreview();
    }
}

function clearBatchFiles() {
    selectedFiles = [];
    document.getElementById('batchFileInput').value = '';
    document.getElementById('batchUploadArea').style.display = 'block';
    document.getElementById('batchPreviewSection').classList.add('hidden');
    document.getElementById('batchResultsSection').classList.add('hidden');
}

async function analyzeBatchImages() {
    if (selectedFiles.length === 0) return;

    const analyzeBtn = document.getElementById('analyzeBatchBtn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoader = analyzeBtn.querySelector('.btn-loader');
    const progressContainer = document.getElementById('batchProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    analyzeBtn.disabled = true;
    btnText.classList.add('hidden');
    btnLoader.classList.remove('hidden');
    progressContainer.classList.remove('hidden');

    const results = [];
    
    for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        progressText.textContent = `Processing ${i + 1}/${selectedFiles.length}`;
        progressFill.style.width = `${((i + 1) / selectedFiles.length) * 100}%`;

        try {
            const result = await predictImage(file);
            
            if (result.confidence >= confidenceThreshold) {
                result.filename = file.name;
                result.fileUrl = URL.createObjectURL(file);
                results.push(result);
                addToHistory(result);
            }
        } catch (error) {
            console.error(`Failed to process ${file.name}:`, error);
        }
    }

    displayBatchResults(results);

    analyzeBtn.disabled = false;
    btnText.classList.remove('hidden');
    btnLoader.classList.add('hidden');
    progressContainer.classList.add('hidden');
}

function displayBatchResults(results) {
    const resultsSection = document.getElementById('batchResultsSection');
    const statsCards = document.getElementById('statsCards');
    const resultsGrid = document.getElementById('batchResultsGrid');

    if (results.length === 0) {
        resultsGrid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                No predictions met the confidence threshold. Try lowering the threshold.
            </div>
        `;
        statsCards.innerHTML = '';
        resultsSection.classList.remove('hidden');
        return;
    }

    const avgConfidence = results.reduce((sum, r) => sum + r.confidence, 0) / results.length;
    const diseaseCount = results.filter(r => !r.class_name.toLowerCase().includes('healthy')).length;

    statsCards.innerHTML = `
        <div class="stat-card">
            <h3>${results.length}</h3>
            <p>Images Analyzed</p>
        </div>
        <div class="stat-card">
            <h3>${(avgConfidence * 100).toFixed(1)}%</h3>
            <p>Avg Confidence</p>
        </div>
        <div class="stat-card">
            <h3>${diseaseCount}</h3>
            <p>Diseases Detected</p>
        </div>
    `;

    resultsGrid.innerHTML = '';
    results.forEach(result => {
        const confidencePercent = (result.confidence * 100).toFixed(1);
        let confidenceColor = 'var(--danger)';
        if (result.confidence >= 0.8) confidenceColor = 'var(--primary)';
        else if (result.confidence >= 0.5) confidenceColor = 'var(--warning)';

        const card = document.createElement('div');
        card.className = 'batch-result-card';
        card.innerHTML = `
            <img src="${result.fileUrl}" alt="${result.class_name}">
            <div class="batch-result-info">
                <h4>${result.class_name}</h4>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${confidencePercent}%; background: ${confidenceColor}">
                        ${confidencePercent}%
                    </div>
                </div>
                <p style="margin-top: 10px; font-size: 0.9rem; color: var(--gray);">${result.filename}</p>
            </div>
        `;
        resultsGrid.appendChild(card);
    });

    resultsSection.classList.remove('hidden');
}

function addToHistory(result) {
    const historyItem = {
        class_name: result.class_name,
        confidence: result.confidence,
        timestamp: new Date().toLocaleString()
    };

    analysisHistory.unshift(historyItem);
    
    if (analysisHistory.length > 50) {
        analysisHistory = analysisHistory.slice(0, 50);
    }

    saveHistoryToStorage();
    updateHistoryDisplay();
}

function updateHistoryDisplay() {
    const historyList = document.getElementById('historyList');
    
    if (analysisHistory.length === 0) {
        historyList.innerHTML = '<p class="empty-state">No analyses yet</p>';
        return;
    }

    historyList.innerHTML = '';
    analysisHistory.slice(0, 10).forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'history-item';
        
        let confidenceColor = 'var(--danger)';
        if (item.confidence >= 0.8) confidenceColor = 'var(--primary)';
        else if (item.confidence >= 0.5) confidenceColor = 'var(--warning)';

        div.innerHTML = `
            <div class="history-info">
                <h4>${item.class_name}</h4>
                <p>${item.timestamp}</p>
            </div>
            <div style="color: ${confidenceColor}; font-weight: 600;">
                ${(item.confidence * 100).toFixed(1)}%
            </div>
        `;
        historyList.appendChild(div);
    });
}

function clearHistory() {
    if (confirm('Are you sure you want to clear all history?')) {
        analysisHistory = [];
        saveHistoryToStorage();
        updateHistoryDisplay();
    }
}

function saveHistoryToStorage() {
    localStorage.setItem('vanaspatiHistory', JSON.stringify(analysisHistory));
}

function loadHistoryFromStorage() {
    const stored = localStorage.getItem('vanaspatiHistory');
    if (stored) {
        analysisHistory = JSON.parse(stored);
        updateHistoryDisplay();
    }
}
