document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');
    const loadingIndicator = document.getElementById('loading-indicator');
    const resultTemplate = document.getElementById('result-template');
    const suggestionsBox = document.getElementById('suggestions-box');

    // Animation Canvas
    initParticleCanvas();

    // State
    let currentQuery = '';
    let debounceTimer;

    // --- FILE UPLOAD LOGIC (SAFE ADDITION) ---
    const uploadBtn = document.getElementById('upload-trigger-btn');
    const fileInput = document.getElementById('file-upload-input');
    const uploadStatus = document.getElementById('upload-status');

    if (uploadBtn && fileInput) {
        uploadBtn.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', async () => {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];

                // Show status
                uploadStatus.textContent = `Uploading ${file.name}...`;
                uploadStatus.style.display = 'block';
                uploadBtn.style.opacity = '0.7';

                const formData = new FormData();
                formData.append('file', file);

                try {
                    const res = await fetch('/api/upload-file', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();

                    if (data.success) {
                        uploadStatus.textContent = '✅ Indexed! Search for it now.';
                        uploadStatus.style.color = '#4ade80';
                        setTimeout(() => { uploadStatus.style.display = 'none'; }, 3000);
                    } else {
                        throw new Error(data.error);
                    }
                } catch (err) {
                    uploadStatus.textContent = '❌ Error: ' + err.message;
                    uploadStatus.style.color = '#f87171';
                } finally {
                    uploadBtn.style.opacity = '1';
                    fileInput.value = ''; // Reset
                }
            }
        });
    }

    // --- SEARCH LOGIC ---
    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const query = searchInput.value.trim();
            if (query) {
                performSearch(query);
            }
        });
    }

    // --- AUTOCOMPLETE LOGIC ---
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            currentQuery = query;

            // Clear suggestions if empty
            if (query.length < 1) {
                suggestionsBox.innerHTML = '';
                suggestionsBox.classList.remove('active');
                return;
            }

            // Debounce API call
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                fetchSuggestions(query);
            }, 200);
        });

        // Hide suggestions on click outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
                suggestionsBox.classList.remove('active');
            }
        });
    }

    async function fetchSuggestions(query) {
        try {
            // Updated endpoint to /api/autocomplete
            const response = await fetch(`/api/autocomplete?q=${encodeURIComponent(query)}`);
            if (!response.ok) return;

            const data = await response.json();

            // Handle new response format {suggestions, corrections, ...} or list
            let suggestions = [];
            if (Array.isArray(data)) {
                suggestions = data;
            } else if (data.suggestions) {
                suggestions = data.suggestions;
                // You could also use data.corrections or data.recommendations here
            }

            renderSuggestions(suggestions);
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    }

    function renderSuggestions(suggestions) {
        if (!suggestions || suggestions.length === 0) {
            suggestionsBox.classList.remove('active');
            return;
        }

        const html = suggestions.map(s => {
            // Check if suggestion is object or string
            const text = typeof s === 'string' ? s : s.word;
            // Highlight match
            const re = new RegExp(`(${currentQuery})`, 'gi');
            const highlighted = text.replace(re, '<strong>$1</strong>');

            return `<div class="suggestion-item" data-value="${text}">
                <span class="suggestion-icon">🔍</span>
                <span class="suggestion-text">${highlighted}</span>
            </div>`;
        }).join('');

        suggestionsBox.innerHTML = html;
        suggestionsBox.classList.add('active');

        // Add click handlers
        document.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const value = item.getAttribute('data-value');
                searchInput.value = value;
                suggestionsBox.classList.remove('active');
                performSearch(value);
            });
        });
    }

    async function performSearch(query) {
        // UI Updates
        resultsContainer.innerHTML = ''; // Clear previous
        resultsContainer.appendChild(loadingIndicator);
        loadingIndicator.style.display = 'flex';

        // Update URL without reload
        const url = new URL(window.location);
        url.searchParams.set('query', query);
        window.history.pushState({}, '', url);

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const results = await response.json();

            // Clear loading
            loadingIndicator.style.display = 'none';

            if (results.error) {
                showError(results.error);
                return;
            }

            if (results.length === 0) {
                showNoResults(query);
            } else {
                renderResults(results);
            }

        } catch (error) {
            console.error('Search error:', error);
            loadingIndicator.style.display = 'none';
            showError('Failed to connect to search server.');
        }
    }

    function renderResults(results) {
        resultsContainer.innerHTML = ''; // Ensure clear

        // Add summary
        const summary = document.createElement('div');
        summary.className = 'results-summary';
        summary.textContent = `Found ${results.length} result(s)`;
        resultsContainer.appendChild(summary);

        results.forEach(result => {
            const clone = resultTemplate.content.cloneNode(true);
            const card = clone.querySelector('.result-item');

            // Title & Link
            const link = clone.querySelector('.result-title a');
            const displayTitle = result.title || result.filename || `Document ${result.doc_id}`;
            link.textContent = displayTitle;
            link.href = `/view/${result.doc_id}`;

            // Score visualization
            const scoreColor = result.score > 0.8 ? '✨' : result.score > 0.5 ? '⭐' : '📄';
            const scorePercentage = (result.score * 100).toFixed(1);

            // Clean up filename for display (formal shape)
            let cleanFilename = (result.filename || '').replace(/_/g, ' ').replace('.txt', '').replace('.json', '');
            if (cleanFilename.length > 30) cleanFilename = "Scientific Article"; // Fallback if too messy
            if (cleanFilename.match(/\d{5,}/)) cleanFilename = "Research Document";

            card.innerHTML = `
                <div class="result-title"><a href="/view/${result.doc_id}" target="_blank" title="${displayTitle}">${displayTitle}</a></div>
                <div class="result-meta">
                    <span>📄 ${cleanFilename}</span>
                    <span class="result-score">${scoreColor} Relevance: ${scorePercentage}%</span>
                </div>
                <div class="result-abstract">
                    ${result.abstract || 'No preview available'}
                </div>
            `;

            card.addEventListener('click', (e) => {
                // If they clicked the link, let it handle it. if they clicked card, open it.
                if (!e.target.closest('a')) {
                    window.open(`/view/${result.doc_id}`, '_blank');
                }
            });

            // Add hover ripple effect
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                card.style.setProperty('--x', `${x}px`);
                card.style.setProperty('--y', `${y}px`);
            });

            resultsContainer.appendChild(card);
        });
    }

    function showNoResults(query) {
        resultsContainer.innerHTML = `
            <div class="no-results">
                <div class="placeholder-icon">😕</div>
                <h3>No results found for "${query}"</h3>
                <p>Try different keywords or check your spelling.</p>
            </div>
        `;
    }

    function showError(msg) {
        resultsContainer.innerHTML = `
            <div class="error-message">
                <h3>⚠️ Error</h3>
                <p>${msg}</p>
            </div>
        `;
    }

    // --- ANIMATION ---
    function initParticleCanvas() {
        const canvas = document.getElementById('particle-canvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        let width, height;
        let particles = [];

        function resize() {
            width = window.innerWidth;
            height = window.innerHeight;
            canvas.width = width;
            canvas.height = height;
        }

        class Particle {
            constructor() {
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                this.vx = (Math.random() - 0.5) * 0.5;
                this.vy = (Math.random() - 0.5) * 0.5;
                this.size = Math.random() * 2;
                this.alpha = Math.random() * 0.5;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;

                if (this.x < 0) this.x = width;
                if (this.x > width) this.x = 0;
                if (this.y < 0) this.y = height;
                if (this.y > height) this.y = 0;
            }

            draw() {
                ctx.fillStyle = `rgba(255, 255, 255, ${this.alpha})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        function init() {
            resize();
            for (let i = 0; i < 50; i++) {
                particles.push(new Particle());
            }
        }

        function animate() {
            ctx.clearRect(0, 0, width, height);
            particles.forEach(p => {
                p.update();
                p.draw();
            });
            requestAnimationFrame(animate);
        }

        window.addEventListener('resize', resize);
        init();
        animate();
    }
});
