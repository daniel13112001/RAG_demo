// static/script.js

const queryInput = document.getElementById('queryInput');
const submitBtn = document.getElementById('submitBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultSection = document.getElementById('resultSection');
const welcomeMsg = document.getElementById('welcomeMsg');
const errorMsg = document.getElementById('errorMsg');

// Handle Enter key press
queryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !submitBtn.disabled) {
        submitBtn.click();
    }
});

// Handle submit button click
submitBtn.addEventListener('click', async () => {
    const query = queryInput.value.trim();

    if (!query) {
        showError('Please enter a question.');
        return;
    }

    await submitQuery(query);
});

async function submitQuery(query) {
    // Clear input field immediately
    queryInput.value = '';

    // Hide welcome and results
    welcomeMsg.classList.add('hidden');
    resultSection.classList.add('hidden');
    errorMsg.classList.remove('show');

    // Show loading
    loadingSpinner.classList.remove('hidden');
    submitBtn.disabled = true;

    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to get response');
        }

        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred. Please try again.');
        welcomeMsg.classList.remove('hidden');
    } finally {
        loadingSpinner.classList.add('hidden');
        submitBtn.disabled = false;
        queryInput.focus();
    }
}

function displayResults(data) {
    // Display answer
    document.getElementById('answerText').textContent = data.answer;

    // Display sources
    const sourcesList = document.getElementById('sourcesList');
    sourcesList.innerHTML = '';
    if (data.sources && data.sources.length > 0) {
        data.sources.forEach((source) => {
            const sourceTag = document.createElement('span');
            sourceTag.className = 'source-tag';
            sourceTag.textContent = source;
            sourcesList.appendChild(sourceTag);
        });
    } else {
        sourcesList.innerHTML = '<span class="source-tag">No sources found</span>';
    }

    // Display context chunks
    const contextList = document.getElementById('contextList');
    contextList.innerHTML = '';
    if (data.context_chunks && data.context_chunks.length > 0) {
        data.context_chunks.forEach((chunk) => {
            const chunkDiv = document.createElement('div');
            chunkDiv.className = 'context-chunk';
            chunkDiv.innerHTML = `
                <p>${escapeHtml(chunk.content)}</p>
                <div class="context-chunk-source">
                    📄 ${escapeHtml(chunk.source)}
                    <span class="context-chunk-score">Distance: ${(chunk.score).toFixed(1)}</span>
                </div>
            `;
            contextList.appendChild(chunkDiv);
        });
    }

    // Show results
    resultSection.classList.remove('hidden');
}

function showError(message) {
    errorMsg.textContent = message;
    errorMsg.classList.add('show');
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;',
    };
    return text.replace(/[&<>"']/g, (m) => map[m]);
}

// Check server health on page load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/health');
        if (!response.ok) {
            showError('Server is not running properly. Please restart the app.');
        }
    } catch (error) {
        showError('Cannot connect to server. Is the app running?');
    }
});
