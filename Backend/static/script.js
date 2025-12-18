document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const resultsContainer = document.getElementById('results-container');
    const suggestionsBox = document.getElementById('suggestions-box');

    // Event Listeners
    searchBtn.addEventListener('click', performSearch);

    // Keypress for Search (Enter)
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            suggestionsBox.classList.remove('active');
            performSearch();
        }
    });

    // Autocomplete Input Listener
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
            } else {
                suggestionsBox.classList.remove('active');
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    }, 300)); // 300ms debounce

    // Hide suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.classList.remove('active');
        }
    });

    function renderSuggestions(suggestions) {
        suggestionsBox.innerHTML = '';
        suggestions.forEach(word => {
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
        suggestionsBox.classList.add('active');
    }

    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;

        // UI Feedback
        resultsContainer.innerHTML = '<div class="placeholder-text">Searching...</div>';

        try {
            // Defaulting semantic to true, we could add a toggle in UI later
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&semantic=true`);
            const results = await response.json();

            renderResults(results);
        } catch (error) {
            console.error('Error fetching results:', error);
            resultsContainer.innerHTML = '<div class="placeholder-text">An error occurred while searching.</div>';
        }
    }

    function renderResults(results) {
        resultsContainer.innerHTML = '';

        if (results.length === 0) {
            resultsContainer.innerHTML = '<div class="placeholder-text">No results found (Strict Match + Synonyms).</div>';
            return;
        }

        results.forEach(result => {
            const card = document.createElement('div');
            card.className = 'result-card';

            // Truncate title if too long
            const displayTitle = result.title.length > 150 ? result.title.substring(0, 150) + '...' : result.title;

            card.innerHTML = `
                <div class="result-title">${displayTitle}</div>
                <div class="result-meta">
                    <span>${result.filename}</span>
                    <span class="result-score">Score: ${result.score}</span>
                </div>
                <div class="result-abstract" style="margin-top: 10px; color: rgba(255,255,255,0.6); font-size: 0.9em;">
                    ${result.abstract || ''}
                </div>
            `;

            card.addEventListener('click', () => {
                alert(`You clicked on document ${result.doc_id}: ${result.filename}`);
            });

            resultsContainer.appendChild(card);
        });
    }

    // Debounce Utility
    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            const context = this;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), wait);
        };
    }
});
