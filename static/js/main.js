// File Drive - Main JavaScript File

// Theme Management
function initializeTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    updateThemeIcon(currentTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    updateThemeIcon(newTheme);
    
    // Save theme preference (this would normally make an AJAX request)
    localStorage.setItem('theme', newTheme);
    
    // Show theme change notification
    showNotification(`Switched to ${newTheme} mode`, 'info');
}

function updateThemeIcon(theme) {
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// Notification System
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed notification`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    notification.innerHTML = `
        <i class="fas fa-${getIconForType(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }, duration);
}

function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle',
        'primary': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// File Upload Enhancements
function initializeFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const files = e.target.files;
            if (files.length > 0) {
                validateFile(files[0]);
            }
        });
    });
}

function validateFile(file) {
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = [
        'text/plain',
        'text/markdown',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/svg+xml',
        'application/pdf'
    ];
    
    if (file.size > maxSize) {
        showNotification('File size must be less than 16MB', 'danger');
        return false;
    }
    
    if (!allowedTypes.includes(file.type)) {
        showNotification('File type not supported', 'danger');
        return false;
    }
    
    return true;
}

// Drag and Drop Enhancement
function initializeDragAndDrop() {
    const dropZones = document.querySelectorAll('.file-drop-zone');
    
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', handleDragOver);
        zone.addEventListener('dragleave', handleDragLeave);
        zone.addEventListener('drop', handleDrop);
    });
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const fileInput = e.currentTarget.querySelector('input[type="file"]');
        if (fileInput && validateFile(files[0])) {
            fileInput.files = files;
            
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(event);
        }
    }
}

// Search Functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('input[name="search"]');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            // Add loading state
            const form = this.closest('form');
            const submitButton = form.querySelector('button[type="submit"]');
            
            searchTimeout = setTimeout(() => {
                // Auto-submit search after 500ms of no typing
                if (this.value.length >= 2 || this.value.length === 0) {
                    form.submit();
                }
            }, 500);
        });
    });
}

// Auto-save for Text Editors
function initializeAutoSave() {
    const textareas = document.querySelectorAll('.code-editor');
    
    textareas.forEach(textarea => {
        let saveTimeout;
        
        textarea.addEventListener('input', function() {
            clearTimeout(saveTimeout);
            
            // Show unsaved changes indicator
            showUnsavedIndicator();
            
            // Auto-save after 3 seconds of inactivity
            saveTimeout = setTimeout(() => {
                autoSave(this);
            }, 3000);
        });
    });
}

function showUnsavedIndicator() {
    let indicator = document.querySelector('.unsaved-indicator');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'unsaved-indicator badge bg-warning position-fixed';
        indicator.style.cssText = 'top: 80px; right: 20px; z-index: 1000;';
        indicator.innerHTML = '<i class="fas fa-edit me-1"></i>Unsaved changes';
        document.body.appendChild(indicator);
    }
}

function hideUnsavedIndicator() {
    const indicator = document.querySelector('.unsaved-indicator');
    if (indicator) {
        indicator.remove();
    }
}

function autoSave(textarea) {
    // In a real implementation, this would make an AJAX request
    console.log('Auto-saving content...');
    hideUnsavedIndicator();
    showNotification('Changes auto-saved', 'success', 2000);
}

// Loading States
function setLoadingState(element, loading = true) {
    if (loading) {
        element.classList.add('loading');
        element.disabled = true;
    } else {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

// Form Enhancements
function initializeForms() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                setLoadingState(submitButton, true);
                
                // Prevent double submission
                setTimeout(() => {
                    setLoadingState(submitButton, false);
                }, 5000);
            }
        });
    });
}

// Keyboard Shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S for save
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            const activeForm = document.querySelector('form:focus-within');
            if (activeForm) {
                e.preventDefault();
                activeForm.submit();
            }
        }
        
        // Ctrl/Cmd + / for search
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // ESC to clear search
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('input[name="search"]:focus');
            if (searchInput) {
                searchInput.value = '';
                searchInput.blur();
            }
        }
    });
}

// Smooth Scrolling
function initializeSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Chat Enhancements
function initializeChat() {
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    
    if (chatMessages) {
        // Auto-scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Scroll to bottom when new messages are added
        const observer = new MutationObserver(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
        
        observer.observe(chatMessages, {
            childList: true,
            subtree: true
        });
    }
    
    if (messageInput) {
        // Auto-resize textarea
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
        
        // Send with Ctrl+Enter
        messageInput.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.closest('form').submit();
            }
        });
    }
}

// Tooltips and Popovers
function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Image Preview
function initializeImagePreview() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    showImagePreview(e.target.result);
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

function showImagePreview(src) {
    let preview = document.querySelector('.image-preview');
    
    if (!preview) {
        preview = document.createElement('div');
        preview.className = 'image-preview mt-3';
        preview.innerHTML = `
            <div class="card glass-card">
                <div class="card-header">
                    <h6 class="mb-0">Preview</h6>
                </div>
                <div class="card-body text-center">
                    <img class="img-fluid rounded" style="max-height: 200px;">
                </div>
            </div>
        `;
        
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.parentNode.appendChild(preview);
        }
    }
    
    const img = preview.querySelector('img');
    img.src = src;
}

// Progress Indicators
function createProgressBar(container, progress = 0) {
    const progressBar = document.createElement('div');
    progressBar.className = 'progress glass-item mt-2';
    progressBar.style.height = '4px';
    progressBar.innerHTML = `
        <div class="progress-bar" role="progressbar" style="width: ${progress}%"></div>
    `;
    
    container.appendChild(progressBar);
    return progressBar;
}

function updateProgress(progressBar, progress) {
    const bar = progressBar.querySelector('.progress-bar');
    bar.style.width = progress + '%';
    bar.setAttribute('aria-valuenow', progress);
}

// Utility Functions
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Copy to Clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Copied to clipboard', 'success');
    } catch (err) {
        showNotification('Failed to copy to clipboard', 'danger');
    }
    
    document.body.removeChild(textArea);
}

// Animation Utils
function fadeIn(element, duration = 300) {
    element.style.opacity = '0';
    element.style.display = 'block';
    
    const start = performance.now();
    
    function animate(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);
        
        element.style.opacity = progress;
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }
    
    requestAnimationFrame(animate);
}

function slideDown(element, duration = 300) {
    element.style.height = '0';
    element.style.overflow = 'hidden';
    element.style.display = 'block';
    
    const targetHeight = element.scrollHeight;
    const start = performance.now();
    
    function animate(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);
        
        element.style.height = (targetHeight * progress) + 'px';
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            element.style.height = '';
            element.style.overflow = '';
        }
    }
    
    requestAnimationFrame(animate);
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    initializeFileUpload();
    initializeDragAndDrop();
    initializeSearch();
    initializeAutoSave();
    initializeForms();
    initializeKeyboardShortcuts();
    initializeSmoothScrolling();
    initializeChat();
    initializeTooltips();
    initializeImagePreview();
    
    // Add smooth transitions
    document.body.style.transition = 'all 0.3s ease';
    
    // Load theme from localStorage if available
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme && savedTheme !== document.documentElement.getAttribute('data-theme')) {
        toggleTheme();
    }
    
    console.log('File Drive initialized successfully');
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .notification {
        animation: slideInRight 0.3s ease-out;
    }
`;
document.head.appendChild(style);

// Make functions available globally
window.FileDrive = {
    toggleTheme,
    showNotification,
    copyToClipboard,
    setLoadingState,
    createProgressBar,
    updateProgress,
    fadeIn,
    slideDown
};
