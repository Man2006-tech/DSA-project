document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const resultsContainer = document.getElementById('results-container');
    const suggestionsBox = document.getElementById('suggestions-box');

    // Search on button click
    searchBtn.addEventListener('click', performSearch);

    // Search on Enter key
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            suggestionsBox.classList.remove('active');
            performSearch();
        }
    });

    // Autocomplete
    searchInput.addEventListener('input', debounce(async (e) => {
        const query = e.target.value.trim();
        if (query.length < 2) {
            suggestionsBox.classList.remove('active');
            return;
        }

        try {
            const response = await fetch(`/api/suggest?q=${encodeURIComponent(query)}`);
            const suggestions = await response.json();

            if (suggestions.length > 0) {
                renderSuggestions(suggestions);
                suggestionsBox.classList.add('active');
            } else {
                suggestionsBox.classList.remove('active');
            }
        } catch (error) {
            console.error('Autocomplete error:', error);
        }
    }, 300));

    // Hide suggestions on outside click
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.classList.remove('active');
        }
    });

    function renderSuggestions(suggestions) {
        suggestionsBox.innerHTML = '';
        suggestions.slice(0, 8).forEach(word => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.textContent = word;
            item.addEventListener('click', () => {
                searchInput.value = word;
                suggestionsBox.classList.remove('active');
                performSearch();
            });
            suggestionsBox.appendChild(item);
        });
    }

    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;

        // Show loading
        resultsContainer.innerHTML = `
            <div class="placeholder-content">
                <div class="placeholder-icon">⏳</div>
                <div class="placeholder-text">Searching...</div>
            </div>
        `;

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&semantic=true`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const results = await response.json();
            console.log('Search results:', results);

            renderResults(results, query);
        } catch (error) {
            console.error('Search error:', error);
            resultsContainer.innerHTML = `
                <div class="placeholder-content">
                    <div class="placeholder-icon">⚠️</div>
                    <div class="placeholder-text">Search Error</div>
                    <p style="color: rgba(255,255,255,0.6); margin-top: 10px;">
                        ${error.message}
                    </p>
                </div>
            `;
        }
    }

    function renderResults(results, query) {
        resultsContainer.innerHTML = '';

        if (!Array.isArray(results)) {
            console.error("Results is not an array:", results);
            resultsContainer.innerHTML = `
                <div class="placeholder-content">
                    <div class="placeholder-icon">⚠️</div>
                    <div class="placeholder-text">Server Error</div>
                    <p style="color: rgba(255,255,255,0.6); margin-top: 10px;">
                        The server returned an unexpected response.
                    </p>
                </div>
            `;
            return;
        }

        if (results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="placeholder-content">
                    <div class="placeholder-icon">🔍</div>
                    <div class="placeholder-text">No results found</div>
                    <p style="color: rgba(255,255,255,0.6); margin-top: 10px;">
                        Try different keywords for "${query}"
                    </p>
                </div>
            `;
            return;
        }

        // Result count header
        const countDiv = document.createElement('div');
        countDiv.style.cssText = `
            text-align: center;
            padding: 1rem;
            font-size: 1.1rem;
            color: rgba(0,212,255,0.8);
            margin-bottom: 1rem;
        `;
        countDiv.innerHTML = `📊 Found <strong>${results.length}</strong> results for "<strong>${query}</strong>"`;
        resultsContainer.appendChild(countDiv);

        // Render each result
        results.forEach((result, index) => {
            const card = document.createElement('div');
            card.className = 'result-card';
            card.style.animationDelay = `${index * 0.05}s`;

            // Truncate long titles
            const displayTitle = result.title.length > 150
                ? result.title.substring(0, 150) + '...'
                : result.title;

            // Score display
            const scorePercent = (result.score * 10).toFixed(0);
            const scoreEmoji = result.score > 3 ? '✨' : result.score > 1 ? '⭐' : '📄';

            card.innerHTML = `
                <div class="result-title">
                    <a href="#" title="${result.title}">${displayTitle}</a>
                </div>
                <div class="result-meta">
                    <span>📁 ${result.filename || 'Unknown'}</span>
                    <span class="result-score">${scoreEmoji} Score: ${scorePercent}%</span>
                </div>
                <div class="result-abstract" style="margin-top: 10px; color: rgba(255,255,255,0.6); font-size: 0.95em;">
                    ${result.abstract || 'No preview available'}
                </div>
            `;

            // Click to view details
            card.addEventListener('click', (e) => {
                e.preventDefault();
                showDocumentModal(result);
            });

            resultsContainer.appendChild(card);
        });
    }

    function showDocumentModal(result) {
        // Create modal to show document details
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            padding: 2rem;
        `;

        const content = document.createElement('div');
        content.style.cssText = `
            background: #1a1f3a;
            border: 2px solid rgba(0,212,255,0.3);
            border-radius: 16px;
            padding: 2rem;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
            position: relative;
        `;

        content.innerHTML = `
            <button style="
                position: absolute;
                top: 1rem;
                right: 1rem;
                background: rgba(255,0,0,0.2);
                border: 1px solid rgba(255,0,0,0.5);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                cursor: pointer;
            " onclick="this.closest('div').parentElement.remove()">✕ Close</button>
            
            <h2 style="color: #00d4ff; margin-bottom: 1rem;">${result.title}</h2>
            
            <div style="margin-bottom: 1rem; padding: 1rem; background: rgba(0,212,255,0.1); border-radius: 8px;">
                <p><strong>📁 File:</strong> ${result.filename}</p>
                <p><strong>🆔 Document ID:</strong> ${result.doc_id}</p>
                <p><strong>⭐ Relevance Score:</strong> ${result.score}</p>
            </div>
            
            <div style="margin-top: 1.5rem;">
                <h3 style="color: #00d4ff; margin-bottom: 0.5rem;">Content Preview:</h3>
                <p style="color: rgba(255,255,255,0.8); line-height: 1.6;">
                    ${result.abstract || 'No content preview available'}
                </p>
            </div>
        `;

        modal.appendChild(content);
        document.body.appendChild(modal);

        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
});