(function() {
    'use strict';
    
    let previewTimeout = null;
    let previewPopover = null;

    // Polyfill for closest method
    function closest(element, selector) {
        while (element && element.nodeType === 1) {
            if (element.matches && element.matches(selector)) {
                return element;
            }
            if (element.msMatchesSelector && element.msMatchesSelector(selector)) {
                return element;
            }
            element = element.parentNode;
        }
        return null;
    }

    // Polyfill for matches method
    if (!Element.prototype.matches) {
        Element.prototype.matches = Element.prototype.msMatchesSelector || 
                                   Element.prototype.webkitMatchesSelector;
    }

    function findPDFAttachments() {
        // Look for various PDF attachment selectors
        var selectors = [
            '.o_attachment[data-mimetype*="pdf"]',
            '.o_attachment_wrap .o_attachment[data-mimetype="application/pdf"]',
            '.o_attachment[title*=".pdf"]',
            '.o_attachment[data-original-title*=".pdf"]',
            'a[data-mimetype*="pdf"]',
            '[data-mimetype="application/pdf"]',
            '.o_attachment_download[data-mimetype*="pdf"]'
        ];
        
        var attachments = [];
        selectors.forEach(function(selector) {
            var elements = document.querySelectorAll(selector);
            for (var i = 0; i < elements.length; i++) {
                if (attachments.indexOf(elements[i]) === -1) {
                    attachments.push(elements[i]);
                }
            }
        });
        
        console.log('Found PDF attachments:', attachments.length);
        attachments.forEach(function(att, index) {
            console.log('Attachment ' + index + ':', {
                element: att,
                id: getAttachmentId(att),
                mimetype: att.getAttribute('data-mimetype'),
                title: att.title || att.getAttribute('data-original-title'),
                href: att.href
            });
        });
        
        return attachments;
    }

    function getAttachmentId(attachment) {
        // Try multiple ways to get the attachment ID
        var id = attachment.getAttribute('data-id') || 
                 attachment.getAttribute('data-attachment-id') ||
                 attachment.getAttribute('data-attachment_id');
        
        if (!id && attachment.dataset) {
            id = attachment.dataset.id || attachment.dataset.attachmentId;
        }
        
        if (!id) {
            var dataIdEl = attachment.querySelector('[data-id]');
            if (dataIdEl) {
                id = dataIdEl.getAttribute('data-id');
            }
        }
        
        // Try to extract from href
        if (!id && attachment.href) {
            var match = attachment.href.match(/\/web\/content\/(\d+)/);
            if (match) {
                id = match[1];
            }
        }
        
        console.log('Found attachment ID:', id, 'for element:', attachment);
        return id;
    }

    function makeRPCCall(url) {
        console.log('Making RPC call to:', url);
        
        return new Promise(function(resolve, reject) {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', url, true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    console.log('RPC Response status:', xhr.status);
                    console.log('RPC Response text:', xhr.responseText);
                    
                    if (xhr.status === 200) {
                        try {
                            var result = JSON.parse(xhr.responseText);
                            console.log('Parsed result:', result);
                            resolve(result.result || result);
                        } catch (e) {
                            console.error('JSON parse error:', e);
                            reject(e);
                        }
                    } else {
                        reject(new Error('HTTP error: ' + xhr.status));
                    }
                }
            };
            
            xhr.onerror = function() {
                console.error('XHR Error');
                reject(new Error('Network error'));
            };
            
            xhr.send(JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {},
                id: Math.floor(Math.random() * 1000000)
            }));
        });
    }

    function showPreview(attachment, attachmentId) {
        console.log('Showing preview for attachment ID:', attachmentId);
        hidePreview();
        
        previewPopover = createPreviewPopover();
        positionPopover(previewPopover, attachment);
        document.body.appendChild(previewPopover);
        
        // Load preview data
        makeRPCCall('/web/s3_preview_data/' + attachmentId)
            .then(function(result) {
                console.log('Preview data received:', result);
                
                if (result && result.success) {
                    var filename = previewPopover.querySelector('.s3-pdf-filename');
                    var content = previewPopover.querySelector('.s3-pdf-preview-content');
                    
                    filename.textContent = result.filename;
                    
                    var iframe = document.createElement('iframe');
                    iframe.src = result.preview_url;
                    iframe.width = '100%';
                    iframe.height = '100%';
                    iframe.frameBorder = '0';
                    iframe.className = 's3-pdf-iframe';
                    
                    content.innerHTML = '';
                    content.appendChild(iframe);
                } else {
                    var content = previewPopover.querySelector('.s3-pdf-preview-content');
                    var error = document.createElement('div');
                    error.className = 's3-error';
                    error.textContent = (result && result.error) || 'Preview not available';
                    content.innerHTML = '';
                    content.appendChild(error);
                }
            })
            .catch(function(error) {
                console.error('Preview load error:', error);
                var content = previewPopover.querySelector('.s3-pdf-preview-content');
                var errorDiv = document.createElement('div');
                errorDiv.className = 's3-error';
                errorDiv.textContent = 'Failed to load preview: ' + error.message;
                content.innerHTML = '';
                content.appendChild(errorDiv);
            });
    }

    function createPreviewPopover() {
        var popover = document.createElement('div');
        popover.className = 's3-pdf-preview-popover';
        
        var header = document.createElement('div');
        header.className = 's3-pdf-preview-header';
        
        var filename = document.createElement('span');
        filename.className = 's3-pdf-filename';
        filename.textContent = 'Loading...';
        
        var closeBtn = document.createElement('button');
        closeBtn.className = 's3-pdf-close';
        closeBtn.textContent = '×';
        closeBtn.onclick = hidePreview;
        
        header.appendChild(filename);
        header.appendChild(closeBtn);
        
        var content = document.createElement('div');
        content.className = 's3-pdf-preview-content';
        
        var loading = document.createElement('div');
        loading.className = 's3-loading';
        loading.textContent = 'Loading PDF preview...';
        content.appendChild(loading);
        
        popover.appendChild(header);
        popover.appendChild(content);
        
        return popover;
    }

    function positionPopover(popover, attachment) {
        var rect = attachment.getBoundingClientRect();
        var windowWidth = window.innerWidth;
        var windowHeight = window.innerHeight;
        var popoverWidth = 500;
        var popoverHeight = 400;
        
        var leftPos = rect.left;
        var topPos = rect.bottom + 10;
        
        if (leftPos + popoverWidth > windowWidth) {
            leftPos = windowWidth - popoverWidth - 20;
        }
        if (leftPos < 20) {
            leftPos = 20;
        }
        
        if (topPos + popoverHeight > windowHeight) {
            topPos = rect.top - popoverHeight - 10;
        }
        if (topPos < 20) {
            topPos = 20;
        }
        
        popover.style.position = 'fixed';
        popover.style.top = topPos + 'px';
        popover.style.left = leftPos + 'px';
        popover.style.zIndex = '9999';
        popover.style.width = popoverWidth + 'px';
        popover.style.height = popoverHeight + 'px';
    }

    function hidePreview() {
        if (previewPopover) {
            previewPopover.style.opacity = '0';
            previewPopover.style.transition = 'opacity 0.2s';
            setTimeout(function() {
                if (previewPopover && previewPopover.parentNode) {
                    previewPopover.parentNode.removeChild(previewPopover);
                    previewPopover = null;
                }
            }, 200);
        }
        clearTimeout(previewTimeout);
    }

    function addHoverListenersToAttachments() {
        var attachments = findPDFAttachments();
        attachments.forEach(function(attachment) {
            // Remove existing listeners
            attachment.removeEventListener('mouseenter', handleMouseEnter);
            attachment.removeEventListener('mouseleave', handleMouseLeave);
            
            // Add new listeners
            attachment.addEventListener('mouseenter', handleMouseEnter);
            attachment.addEventListener('mouseleave', handleMouseLeave);
            
            // Add visual indicator for S3 PDFs
            attachment.style.position = 'relative';
            attachment.title = (attachment.title || '') + ' (Hover for S3 preview)';
        });
        
        console.log('Added hover listeners to', attachments.length, 'PDF attachments');
    }

    function handleMouseEnter(e) {
        console.log('Mouse enter on PDF attachment:', e.target);
        var attachment = e.currentTarget;
        var attachmentId = getAttachmentId(attachment);
        
        if (!attachmentId) {
            console.log('No attachment ID found for:', attachment);
            return;
        }
        
        clearTimeout(previewTimeout);
        previewTimeout = setTimeout(function() {
            showPreview(attachment, attachmentId);
        }, 800);
    }

    function handleMouseLeave(e) {
        console.log('Mouse leave PDF attachment:', e.target);
        clearTimeout(previewTimeout);
        setTimeout(hidePreview, 300);
    }

    // Global event listeners as fallback
    document.addEventListener('mouseenter', function(e) {
        var attachment = closest(e.target, '.o_attachment[data-mimetype*="pdf"]');
        if (!attachment) return;
        
        var attachmentId = getAttachmentId(attachment);
        if (!attachmentId) return;
        
        clearTimeout(previewTimeout);
        previewTimeout = setTimeout(function() {
            showPreview(attachment, attachmentId);
        }, 800);
    }, true);

    document.addEventListener('click', function(e) {
        if (previewPopover && 
            !closest(e.target, '.s3-pdf-preview-popover') && 
            !closest(e.target, '.o_attachment')) {
            hidePreview();
        }
    });

    // Initialize and periodically refresh
    function init() {
        console.log('Initializing S3 PDF Preview...');
        findPDFAttachments();
        addHoverListenersToAttachments();
        
        // Re-scan for new attachments every 3 seconds
        setInterval(function() {
            addHoverListenersToAttachments();
        }, 3000);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    console.log('S3 PDF Preview script loaded');
})();