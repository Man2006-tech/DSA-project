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
    }, 300));

    // Hide suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.classList.remove('active');
        }
    });

    function renderSuggestions(suggestions) {
        suggestionsBox.innerHTML = '';
        suggestions.forEach((word, index) => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.textContent = word;
            item.style.animationDelay = `${index * 0.05}s`;
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

            renderResults(results);
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

    function renderResults(results) {
        resultsContainer.innerHTML = '';

        if (results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="placeholder-content">
                    <div class="placeholder-icon">🔍</div>
                    <div class="placeholder-text">No results found</div>
                    <p class="placeholder-hint">Try different keywords or search terms</p>
                </div>
            `;
            return;
        }

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
