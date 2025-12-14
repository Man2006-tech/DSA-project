// Initialize particles
function initParticles() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = [];
    const particleCount = 50;

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 0.5;
            this.speedX = (Math.random() - 0.5) * 0.5;
            this.speedY = (Math.random() - 0.5) * 0.5;
            this.opacity = Math.random() * 0.5 + 0.2;
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            if (this.x > canvas.width) this.x = 0;
            if (this.x < 0) this.x = canvas.width;
            if (this.y > canvas.height) this.y = 0;
            if (this.y < 0) this.y = canvas.height;
        }

        draw() {
            ctx.fillStyle = `rgba(0, 212, 255, ${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach((particle, index) => {
            particle.update();
            particle.draw();

            // Draw connections
            particles.forEach((other, otherIndex) => {
                if (index < otherIndex) {
                    const dx = particle.x - other.x;
                    const dy = particle.y - other.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < 150) {
                        ctx.strokeStyle = `rgba(0, 212, 255, ${0.1 * (1 - distance / 150)})`;
                        ctx.lineWidth = 0.5;
                        ctx.beginPath();
                        ctx.moveTo(particle.x, particle.y);
                        ctx.lineTo(other.x, other.y);
                        ctx.stroke();
                    }
                }
            });
        });

        requestAnimationFrame(animate);
    }

    animate();

    // Resize canvas on window resize
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

// AI-Powered Autocomplete System
class AIAutocomplete {
    constructor() {
        this.cache = new Map();
        this.cacheExpiry = 5 * 60 * 1000; // 5 minutes
    }

    async fetchAutocomplete(query) {
        const cacheKey = query.toLowerCase();
        const cached = this.cache.get(cacheKey);
        
        if (cached && Date.now() - cached.time < this.cacheExpiry) {
            return cached.data;
        }

        try {
            const response = await fetch(`/api/autocomplete?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            this.cache.set(cacheKey, {
                data: data,
                time: Date.now()
            });
            
            return data;
        } catch (error) {
            console.error('Autocomplete error:', error);
            return { suggestions: [], corrections: {}, recommendations: [] };
        }
    }

    clearCache() {
        this.cache.clear();
    }
}

const aiAutocomplete = new AIAutocomplete();

// Main Search App
document.addEventListener('DOMContentLoaded', () => {
    initParticles();

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
        // Arrow key navigation
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            const items = suggestionsBox.querySelectorAll('.suggestion-item');
            if (items.length > 0) {
                items[0].focus();
            }
        }
    });

    // Enhanced Autocomplete Input Listener with AI features
    searchInput.addEventListener('input', debounce(async (e) => {
        const query = e.target.value.trim();
        if (query.length < 1) {
            suggestionsBox.classList.remove('active');
            return;
        }

        try {
            const autocompleteData = await aiAutocomplete.fetchAutocomplete(query);
            renderAdvancedSuggestions(autocompleteData, query);
        } catch (error) {
            console.error('Error in autocomplete:', error);
        }
    }, 250));

    // Hide suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.classList.remove('active');
        }
    });

    function renderAdvancedSuggestions(data, originalQuery) {
        suggestionsBox.innerHTML = '';

        const { suggestions, corrections, recommendations } = data;

        // Show correction if available
        if (corrections && corrections.word) {
            const correctionDiv = document.createElement('div');
            correctionDiv.className = 'suggestion-category';
            correctionDiv.innerHTML = `
                <div class="category-label">✏️ Did you mean?</div>
                <div class="correction-item" data-word="${corrections.word}">
                    <span class="correction-text">${corrections.word}</span>
                    <span class="correction-icon">💡</span>
                </div>
            `;
            correctionDiv.querySelector('.correction-item').addEventListener('click', () => {
                searchInput.value = corrections.word;
                suggestionsBox.classList.remove('active');
                performSearch();
            });
            suggestionsBox.appendChild(correctionDiv);
        }

        // Show suggestions
        if (suggestions && suggestions.length > 0) {
            const suggestionsDiv = document.createElement('div');
            suggestionsDiv.className = 'suggestion-category';
            suggestionsDiv.innerHTML = '<div class="category-label">🔍 Suggestions</div>';
            
            suggestions.slice(0, 6).forEach((word, index) => {
                const item = document.createElement('div');
                item.className = 'suggestion-item';
                item.innerHTML = `
                    <span class="suggestion-text">${word}</span>
                    <span class="suggestion-count">+</span>
                `;
                item.style.animationDelay = `${index * 0.04}s`;
                item.addEventListener('click', () => {
                    searchInput.value = word;
                    suggestionsBox.classList.remove('active');
                    performSearch();
                });
                item.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        searchInput.value = word;
                        suggestionsBox.classList.remove('active');
                        performSearch();
                    }
                });
                suggestionsDiv.appendChild(item);
            });
            suggestionsBox.appendChild(suggestionsDiv);
        }

        // Show recommendations
        if (recommendations && recommendations.length > 0) {
            const recommendDiv = document.createElement('div');
            recommendDiv.className = 'suggestion-category';
            recommendDiv.innerHTML = '<div class="category-label">⭐ Related Topics</div>';
            
            recommendations.slice(0, 4).forEach((word, index) => {
                const item = document.createElement('div');
                item.className = 'recommendation-item';
                item.innerHTML = `
                    <span class="tag-icon">🏷️</span>
                    <span class="tag-text">${word}</span>
                `;
                item.style.animationDelay = `${(index + suggestions.length) * 0.04}s`;
                item.addEventListener('click', () => {
                    searchInput.value = (originalQuery.split(' ').slice(0, -1).join(' ') + ' ' + word).trim();
                    suggestionsBox.classList.remove('active');
                    performSearch();
                });
                recommendDiv.appendChild(item);
            });
            suggestionsBox.appendChild(recommendDiv);
        }

        // Show no results message
        if (!corrections && (!suggestions || suggestions.length === 0) && (!recommendations || recommendations.length === 0)) {
            const noResultsDiv = document.createElement('div');
            noResultsDiv.className = 'suggestion-no-results';
            noResultsDiv.innerHTML = '<span>No suggestions found</span>';
            suggestionsBox.appendChild(noResultsDiv);
        }

        if (suggestionsBox.children.length > 0) {
            suggestionsBox.classList.add('active');
        }
    }

    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;

        // Show loading state
        resultsContainer.innerHTML = `
            <div class="placeholder-content">
                <div class="placeholder-icon">⏳</div>
                <div class="placeholder-text">Searching...</div>
            </div>
        `;

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&semantic=true`);
            const results = await response.json();

            renderResults(results, query);
        } catch (error) {
            console.error('Error fetching results:', error);
            resultsContainer.innerHTML = `
                <div class="placeholder-content">
                    <div class="placeholder-icon">⚠️</div>
                    <div class="placeholder-text">Search Error</div>
                    <p class="placeholder-hint">An error occurred while searching. Please try again.</p>
                </div>
            `;
        }
    }

    function renderResults(results, query) {
        resultsContainer.innerHTML = '';

        if (results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="placeholder-content">
                    <div class="placeholder-icon">🔍</div>
                    <div class="placeholder-text">No results found</div>
                    <p class="placeholder-hint">Try different keywords: "${query}"</p>
                </div>
            `;
            return;
        }

        // Show result count
        const resultCountDiv = document.createElement('div');
        resultCountDiv.className = 'result-count-header';
        resultCountDiv.innerHTML = `📊 Found <strong>${results.length}</strong> results for "<strong>${query}</strong>"`;
        resultsContainer.appendChild(resultCountDiv);

        results.forEach((result, index) => {
            const card = document.createElement('div');
            card.className = 'result-card';
            card.style.animationDelay = `${index * 0.05}s`;

            // Truncate title if too long
            const displayTitle = result.title.length > 150 ? result.title.substring(0, 150) + '...' : result.title;
            
            // Format score with color coding
            const scoreColor = result.score > 0.8 ? '✨' : result.score > 0.5 ? '⭐' : '📄';
            const scorePercentage = (result.score * 100).toFixed(1);

            card.innerHTML = `
                <div class="result-title"><a href="#" title="${result.title}">${displayTitle}</a></div>
                <div class="result-meta">
                    <span>📁 ${result.filename}</span>
                    <span class="result-score">${scoreColor} Relevance: ${scorePercentage}%</span>
                </div>
                <div class="result-abstract">
                    ${result.abstract || 'No preview available'}
                </div>
            `;

            card.addEventListener('click', () => {
                alert(`Document: ${result.filename}\nID: ${result.doc_id}\nRelevance: ${scorePercentage}%`);
            });

            // Add hover ripple effect
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-8px)';
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
