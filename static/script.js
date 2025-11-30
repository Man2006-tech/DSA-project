document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const resultsContainer = document.getElementById('results-container');

    // Event Listeners
    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;

        // UI Feedback
        resultsContainer.innerHTML = '<div class="placeholder-text">Searching...</div>';
        
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
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
            resultsContainer.innerHTML = '<div class="placeholder-text">No results found.</div>';
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
            `;
            
            // Optional: Click to view document (endpoint not fully implemented yet, but good for future)
            card.addEventListener('click', () => {
                // window.location.href = `/document/${result.doc_id}`;
                alert(`You clicked on document ${result.doc_id}: ${result.filename}`);
            });

            resultsContainer.appendChild(card);
        });
    }
});
