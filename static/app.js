document.addEventListener('DOMContentLoaded', () => {
    // Elements will be null if they don't exist on the current page
    const form = document.getElementById('journal-form');
    const entriesContainer = document.getElementById('entries-container');

    // ==========================================
    // LOGIC FOR COMPOSE PAGE (index.html)
    // ==========================================
    if (form) {
        const textInput = document.getElementById('journal-text');
        const submitBtn = document.getElementById('submit-btn');
        const btnText = submitBtn.querySelector('.btn-text');
        const loader = submitBtn.querySelector('.loader');
        const errorMessage = document.getElementById('error-message');
        const successMessage = document.getElementById('success-message');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = textInput.value.trim();
            if (!text) return;

            // Show loading spinner on button
            submitBtn.disabled = true;
            btnText.textContent = 'Analyzing sentiment...';
            loader.classList.remove('hidden');
            errorMessage.classList.add('hidden');
            if (successMessage) successMessage.classList.add('hidden');

            try {
                const response = await fetch('/journal', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });

                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.detail || 'Failed to save entry');
                }

                // Show success message and redirect to the entries page
                if (successMessage) successMessage.classList.remove('hidden');
                
                setTimeout(() => {
                    window.location.href = '/entries';
                }, 1000);

            } catch (error) {
                // Show error message if something fails
                errorMessage.textContent = error.message;
                errorMessage.classList.remove('hidden');
            } finally {
                // Reset button state
                submitBtn.disabled = false;
                btnText.textContent = 'Save Entry';
                loader.classList.add('hidden');
            }
        });
    }

    // ==========================================
    // LOGIC FOR PAST ENTRIES PAGE (entries.html)
    // ==========================================
    if (entriesContainer) {
        fetchEntries();
    }

    // Fetches entries from the backend and renders them
    async function fetchEntries() {
        try {
            const response = await fetch('/journal');
            if (!response.ok) throw new Error('Failed to load entries');
            
            const entries = await response.json();
            
            if (entries.length === 0) {
                entriesContainer.innerHTML = '<div class="loading-state">No entries yet. Start journaling to see them here!</div>';
                return;
            }

            renderEntriesGrouped(entries);
        } catch (error) {
            entriesContainer.innerHTML = `<div class="error">Error loading entries: ${error.message}</div>`;
        }
    }

    // Groups entries by date and renders the HTML
    function renderEntriesGrouped(entries) {
        const groups = [];
        const groupMap = {};
        
        entries.forEach(entry => {
            // Append 'Z' to ensure it's parsed as UTC time
            const d = new Date(entry.created_at + (entry.created_at.endsWith('Z') ? '' : 'Z'));
            const dateStr = d.toLocaleDateString('en-US', {
                weekday: 'long', month: 'long', day: 'numeric', year: 'numeric'
            });
            
            if (!groupMap[dateStr]) {
                groupMap[dateStr] = [];
                groups.push(dateStr);
            }
            groupMap[dateStr].push(entry);
        });

        let html = '';
        groups.forEach(dateStr => {
            html += `<div class="date-group" style="margin-bottom: 2rem;">
                <h3 class="date-header" style="margin-bottom: 1rem; color: var(--text-secondary); border-bottom: 1px solid var(--panel-border); padding-bottom: 0.5rem; font-size: 1.1rem; font-weight: 500;">${dateStr}</h3>
                <div class="date-entries" style="display: flex; flex-direction: column; gap: 1.5rem;">
                    ${groupMap[dateStr].map(createEntryHTML).join('')}
                </div>
            </div>`;
        });
        
        entriesContainer.innerHTML = html;
    }

    // Creates the HTML structure for a single entry card
    function createEntryHTML(entry) {
        const d = new Date(entry.created_at + (entry.created_at.endsWith('Z') ? '' : 'Z'));
        const timeStr = d.toLocaleTimeString('en-US', {
            hour: '2-digit', minute: '2-digit'
        });

        let moodClass = 'mood-neutral';
        if (['joy', 'happy', 'excited', 'positive'].includes(entry.mood.toLowerCase())) moodClass = 'mood-positive';
        if (['sad', 'angry', 'fear', 'negative', 'anxious'].includes(entry.mood.toLowerCase())) moodClass = 'mood-negative';

        return `
            <div class="entry-card">
                <div class="entry-header">
                    <div class="entry-date">${timeStr}</div>
                    <div class="mood-badge ${moodClass}">${entry.mood}</div>
                </div>
                <div class="entry-text">${escapeHTML(entry.text)}</div>
                <div class="entry-reflection">
                    <div class="reflection-title">
                        AI Reflection
                    </div>
                    <div class="reflection-text">${escapeHTML(entry.reflection)}</div>
                </div>
            </div>
        `;
    }

    // Helper function to prevent XSS attacks
    function escapeHTML(str) {
        if (!str) return '';
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }
});
