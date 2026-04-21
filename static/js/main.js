// Филатова Юля, ИСП-422р

document.addEventListener('DOMContentLoaded', function() {
    
    // Инициализация всех компонентов
    initTooltips();
    initPopovers();
    initSearchSuggestions();
    initInfiniteScroll();
    initBookmarkButtons();
    initShareButtons();
    
});

// Инициализация Bootstrap tooltips
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Инициализация Bootstrap popovers
function initPopovers() {
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Поисковые подсказки
function initSearchSuggestions() {
    const searchInput = document.querySelector('input[name="query"]');
    if (!searchInput) return;
    
    let suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'search-suggestions position-absolute bg-white shadow-sm rounded mt-1 w-100';
    suggestionsContainer.style.zIndex = '1000';
    suggestionsContainer.style.maxHeight = '300px';
    suggestionsContainer.style.overflowY = 'auto';
    suggestionsContainer.style.display = 'none';
    
    searchInput.parentNode.style.position = 'relative';
    searchInput.parentNode.appendChild(suggestionsContainer);
    
    let timeoutId;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(timeoutId);
        const query = this.value.trim();
        
        if (query.length < 2) {
            suggestionsContainer.style.display = 'none';
            return;
        }
        
        timeoutId = setTimeout(function() {
            fetch(`/news/api/search/suggestions/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.suggestions.length > 0) {
                        suggestionsContainer.innerHTML = '';
                        data.suggestions.forEach(suggestion => {
                            const item = document.createElement('a');
                            item.href = suggestion.url;
                            item.className = 'd-flex align-items-center p-3 text-decoration-none hover-bg-light';
                            item.style.borderBottom = '1px solid #f1f3f5';
                            
                            item.innerHTML = `
                                <div class="flex-grow-1">
                                    <div class="fw-semibold text-dark">${suggestion.title}</div>
                                    <div class="small text-muted">${suggestion.source} • ${suggestion.date}</div>
                                </div>
                            `;
                            
                            suggestionsContainer.appendChild(item);
                        });
                        suggestionsContainer.style.display = 'block';
                    } else {
                        suggestionsContainer.innerHTML = '<div class="p-3 text-muted">Ничего не найдено</div>';
                        suggestionsContainer.style.display = 'block';
                    }
                });
        }, 300);
    });
    
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.style.display = 'none';
        }
    });
}

// AJAX для кнопок сохранения
function initBookmarkButtons() {
    document.querySelectorAll('.bookmark-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.href;
            
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                const icon = this.querySelector('i');
                if (data.saved) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    this.classList.add('active');
                    showNotification('Статья сохранена', 'success');
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    this.classList.remove('active');
                    showNotification('Статья удалена', 'info');
                }
            });
        });
    });
}

// Кнопки поделиться
function initShareButtons() {
    document.querySelectorAll('.share-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const url = window.location.origin + this.dataset.url;
            
            if (navigator.share) {
                navigator.share({
                    title: document.title,
                    url: url
                }).catch(console.error);
            } else {
                navigator.clipboard.writeText(url).then(() => {
                    showNotification('Ссылка скопирована в буфер обмена', 'success');
                });
            }
        });
    });
}

// Фильтры для мобильных устройств
function initMobileFilters() {
    const filterBtn = document.getElementById('filter-toggle');
    if (!filterBtn) return;
    
    filterBtn.addEventListener('click', function() {
        const filterPanel = document.querySelector('.filter-panel');
        filterPanel.classList.toggle('show');
    });
}