/** @odoo-module **/
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

// Global variables for preview
let previewTimeout = null;
let previewElement = null;

// Supported file types with their configurations
const SUPPORTED_TYPES = {
    // Documents
    pdf: { icon: '📄', label: 'PDF Preview', type: 'pdf' },
    docx: { icon: '📘', label: 'Word Document Preview', type: 'office' },
    doc: { icon: '📘', label: 'Word Document Preview', type: 'office' },
    xlsx: { icon: '📊', label: 'Excel Preview', type: 'office' },
    xls: { icon: '📊', label: 'Excel Preview', type: 'office' },
    pptx: { icon: '📽️', label: 'PowerPoint Preview', type: 'office' },
    ppt: { icon: '📽️', label: 'PowerPoint Preview', type: 'office' },
    
    // Text files
    txt: { icon: '📝', label: 'Text Preview', type: 'text' },
    csv: { icon: '📋', label: 'CSV Preview', type: 'text' },
    json: { icon: '📋', label: 'JSON Preview', type: 'text' },
    xml: { icon: '📋', label: 'XML Preview', type: 'text' },
    log: { icon: '📋', label: 'Log Preview', type: 'text' },
    
    // Images
    jpg: { icon: '🖼️', label: 'Image Preview', type: 'image' },
    jpeg: { icon: '🖼️', label: 'Image Preview', type: 'image' },
    png: { icon: '🖼️', label: 'Image Preview', type: 'image' },
    gif: { icon: '🖼️', label: 'GIF Preview', type: 'image' },
    bmp: { icon: '🖼️', label: 'Image Preview', type: 'image' },
    webp: { icon: '🖼️', label: 'Image Preview', type: 'image' },
    svg: { icon: '🖼️', label: 'SVG Preview', type: 'image' }
};

// Initialize after a delay to ensure DOM is ready
setTimeout(() => {
    console.log('File Preview: Initializing...');
    setupFilePreview();
}, 2000);

function setupFilePreview() {
    console.log('File Preview: Setting up event listeners');
    
    // Add global CSS styles
    addStyles();
    
    // Setup mutation observer to handle dynamically added elements
    const observer = new MutationObserver((mutations) => {
        attachEventListeners();
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Initial attachment
    attachEventListeners();
}

function attachEventListeners() {
    const attachmentCards = document.querySelectorAll('.o-mail-AttachmentCard');
    console.log(`File Preview: Found ${attachmentCards.length} attachment cards`);
    
    attachmentCards.forEach((card, index) => {
        // Avoid attaching multiple times
        if (card.dataset.filePreviewAttached === 'true') {
            return;
        }
        
        card.dataset.filePreviewAttached = 'true';
        
        card.addEventListener('mouseenter', function(e) {
            handleMouseEnter(e, card);
        });
        
        card.addEventListener('mouseleave', function(e) {
            handleMouseLeave();
        });
        
        console.log(`File Preview: Attached listeners to card ${index + 1}`);
    });
}

function getFileExtension(filename) {
    if (!filename) return null;
    const parts = filename.toLowerCase().split('.');
    if (parts.length < 2) return null;
    const ext = parts.pop();
    console.log(`File Preview: Extracted extension '${ext}' from filename '${filename}'`);
    return SUPPORTED_TYPES[ext] ? ext : null;
}

function handleMouseEnter(e, card) {
    const title = card.getAttribute('title') || card.getAttribute('aria-label') || '';
    console.log('File Preview: Mouse entered card:', title);
    
    // Check if it's a supported file type
    const fileExt = getFileExtension(title);
    if (!fileExt) {
        console.log('File Preview: Not a supported file type, skipping');
        return;
    }
    
    console.log(`File Preview: ${fileExt.toUpperCase()} detected, will show preview in 500ms`);
    
    // Get attachment data
    const attachmentData = extractAttachmentData(card);
    if (!attachmentData) {
        console.log('File Preview: Could not find attachment data');
        return;
    }
    
    console.log('File Preview: Attachment data:', attachmentData);
    
    // Validate that the attachment name matches the card title
    if (attachmentData.name !== title) {
        console.warn(`File Preview: Mismatch detected! Card title: "${title}", Attachment: "${attachmentData.name}"`);
        return;
    }
    
    // Clear any existing timeout
    if (previewTimeout) {
        clearTimeout(previewTimeout);
    }
    
    // Delay preview by 500ms
    previewTimeout = setTimeout(() => {
        console.log('File Preview: Showing preview');
        showPreviewWithS3(card, attachmentData, fileExt);
    }, 500);
}

function handleMouseLeave() {
    console.log('File Preview: Mouse left, clearing timeout');
    
    if (previewTimeout) {
        clearTimeout(previewTimeout);
        previewTimeout = null;
    }
    
    // Small delay before hiding to allow moving to preview
    setTimeout(() => {
        if (!previewElement || !previewElement.matches(':hover')) {
            hidePreview();
        }
    }, 100);
}

function extractAttachmentData(card) {
    console.log('File Preview: Attempting to extract attachment data...');
    console.log('File Preview: Card HTML:', card.outerHTML.substring(0, 500));
    
    const cardTitle = card.getAttribute('title') || card.getAttribute('aria-label') || '';
    console.log('File Preview: Card title:', cardTitle);
    
    // Log all attributes
    console.log('File Preview: Card attributes:');
    for (const attr of card.attributes) {
        console.log(`  - ${attr.name}: ${attr.value}`);
    }
    
    // Log all properties to find OWL data
    console.log('File Preview: Inspecting card properties for OWL data...');
    const allKeys = Object.keys(card);
    const owlKeys = allKeys.filter(k => k.includes('owl') || k.includes('__'));
    console.log('File Preview: Found potential OWL keys:', owlKeys);
    
    // Also check event handlers
    const eventKeys = allKeys.filter(k => k.startsWith('__event'));
    console.log('File Preview: Found event keys:', eventKeys);
    
    if (eventKeys.length > 0) {
        console.log('File Preview: Inspecting first event handler...');
        const firstEvent = card[eventKeys[0]];
        console.log('File Preview: Event handler structure:', typeof firstEvent, Array.isArray(firstEvent));
        if (Array.isArray(firstEvent)) {
            console.log('File Preview: Event handler length:', firstEvent.length);
            if (firstEvent.length >= 2) {
                const component = firstEvent[1];
                console.log('File Preview: Component type:', typeof component);
                console.log('File Preview: Component keys:', Object.keys(component).slice(0, 20));
                if (component.attachment) {
                    console.log('File Preview: Component has attachment:', component.attachment.name, 'ID:', component.attachment.id);
                }
                if (component.props) {
                    console.log('File Preview: Component props keys:', Object.keys(component.props));
                    
                    // Check the attachments array in props!
                    if (component.props.attachments && Array.isArray(component.props.attachments)) {
                        console.log('File Preview: Found attachments array in props with', component.props.attachments.length, 'items:');
                        component.props.attachments.forEach((att, idx) => {
                            console.log(`  [${idx}] ID: ${att.id}, Name: ${att.name}`);
                        });
                        
                        // Find the matching attachment by name
                        const match = component.props.attachments.find(att => att.name === cardTitle);
                        if (match) {
                            console.log('File Preview: ✓ Found matching attachment!');
                            return {
                                id: match.id,
                                size: match.size,
                                name: match.name,
                                url: match.url,
                                s3_url: match.s3_url,
                                type: match.type
                            };
                        } else {
                            console.log('File Preview: ✗ No matching attachment found for:', cardTitle);
                        }
                    }
                }
            }
        }
    }
    
    // Method 1: Look for attachment list in parent components
    let currentElement = card;
    let maxDepth = 10;
    
    while (currentElement && maxDepth > 0) {
        for (const key in currentElement) {
            if (key.startsWith('__owl__')) {
                try {
                    const owlData = currentElement[key];
                    if (owlData && owlData.component) {
                        const comp = owlData.component;
                        
                        console.log('File Preview: Found OWL component:', comp.constructor.name);
                        if (comp.props) {
                            console.log('File Preview: Component props keys:', Object.keys(comp.props));
                        }
                        
                        // Check for single attachment prop
                        if (comp.props && comp.props.attachment) {
                            const att = comp.props.attachment;
                            console.log('File Preview: Found single attachment:', att.name, 'ID:', att.id);
                            if (att.name === cardTitle) {
                                return {
                                    id: att.id,
                                    size: att.size,
                                    name: att.name,
                                    url: att.url,
                                    s3_url: att.s3_url,
                                    type: att.type
                                };
                            }
                        }
                        
                        // Check for attachments array (plural)
                        if (comp.props && comp.props.attachments && Array.isArray(comp.props.attachments)) {
                            console.log('File Preview: Found attachments array with', comp.props.attachments.length, 'items');
                            comp.props.attachments.forEach((att, idx) => {
                                console.log(`  [${idx}] ID: ${att.id}, Name: ${att.name}`);
                            });
                            const match = comp.props.attachments.find(att => att.name === cardTitle);
                            if (match) {
                                console.log('File Preview: Found matching attachment in props.attachments');
                                return {
                                    id: match.id,
                                    size: match.size,
                                    name: match.name,
                                    url: match.url,
                                    s3_url: match.s3_url,
                                    type: match.type
                                };
                            }
                        }
                        
                        // Check for thread.attachments
                        if (comp.props && comp.props.thread && comp.props.thread.attachments) {
                            console.log('File Preview: Found thread.attachments');
                            const match = comp.props.thread.attachments.find(att => att.name === cardTitle);
                            if (match) {
                                console.log('File Preview: Found matching attachment in thread.attachments');
                                return {
                                    id: match.id,
                                    size: match.size,
                                    name: match.name,
                                    url: match.url,
                                    s3_url: match.s3_url,
                                    type: match.type
                                };
                            }
                        }
                        
                        // Check for message.attachments
                        if (comp.props && comp.props.message && comp.props.message.attachments) {
                            console.log('File Preview: Found message.attachments');
                            const match = comp.props.message.attachments.find(att => att.name === cardTitle);
                            if (match) {
                                console.log('File Preview: Found matching attachment in message.attachments');
                                return {
                                    id: match.id,
                                    size: match.size,
                                    name: match.name,
                                    url: match.url,
                                    s3_url: match.s3_url,
                                    type: match.type
                                };
                            }
                        }
                        
                        // Check store/messaging service
                        if (comp.env && comp.env.services && comp.env.services.messaging) {
                            const messaging = comp.env.services.messaging;
                            if (messaging.store && messaging.store.Attachment) {
                                console.log('File Preview: Checking messaging store for attachments');
                                // Try to find in the store
                                for (const [id, att] of Object.entries(messaging.store.Attachment.records)) {
                                    if (att.name === cardTitle) {
                                        console.log('File Preview: Found matching attachment in messaging store');
                                        return {
                                            id: att.id,
                                            size: att.size,
                                            name: att.name,
                                            url: att.url,
                                            s3_url: att.s3_url,
                                            type: att.type
                                        };
                                    }
                                }
                            }
                        }
                    }
                } catch (e) {
                    console.log('File Preview: Error checking element:', e.message);
                }
            }
        }
        currentElement = currentElement.parentElement;
        maxDepth--;
    }
    
    // Method 2: Try the link/anchor href to extract attachment ID
    const link = card.querySelector('a[href*="/web/content/"]');
    if (link) {
        const href = link.getAttribute('href');
        console.log('File Preview: Found download link:', href);
        
        // Extract ID from URL like /web/content/1199
        const idMatch = href.match(/\/web\/content\/(\d+)/);
        if (idMatch) {
            const attachmentId = parseInt(idMatch[1]);
            console.log('File Preview: Extracted attachment ID from URL:', attachmentId);
            
            return {
                id: attachmentId,
                name: cardTitle,
                size: null,
                url: href,
                s3_url: null,
                type: null
            };
        }
    } else {
        console.log('File Preview: No download link found with /web/content/');
    }
    
    // Method 3: Check image src for attachment ID
    const img = card.querySelector('img[src*="/web/image/"]');
    if (img) {
        const src = img.getAttribute('src');
        console.log('File Preview: Found image src:', src);
        
        // Extract ID from URL like /web/image/1199
        const idMatch = src.match(/\/web\/image\/(\d+)/);
        if (idMatch) {
            const attachmentId = parseInt(idMatch[1]);
            console.log('File Preview: Extracted attachment ID from image:', attachmentId);
            
            return {
                id: attachmentId,
                name: cardTitle,
                size: null,
                url: src,
                s3_url: null,
                type: null
            };
        }
    } else {
        console.log('File Preview: No image found with /web/image/');
    }
    
    // Method 4: Check all links and images for any attachment ID
    console.log('File Preview: Searching all links and images...');
    const allLinks = card.querySelectorAll('a[href]');
    console.log('File Preview: Found', allLinks.length, 'links');
    for (const link of allLinks) {
        const href = link.getAttribute('href');
        console.log('File Preview: Link href:', href);
        const idMatch = href.match(/\/(\d+)/);
        if (idMatch) {
            console.log('File Preview: Found potential ID:', idMatch[1]);
        }
    }
    
    const allImages = card.querySelectorAll('img[src]');
    console.log('File Preview: Found', allImages.length, 'images');
    for (const img of allImages) {
        const src = img.getAttribute('src');
        console.log('File Preview: Image src:', src);
    }
    
    console.log('File Preview: Could not extract attachment data');
    return null;
}

function showPreviewWithS3(card, attachmentData, fileExt) {
    hidePreview();
    
    const rect = card.getBoundingClientRect();
    const previewWidth = 950;
    const previewHeight = 750;
    
    // Calculate position
    let left = rect.right + 20;
    let top = rect.top;
    
    // Adjust if not enough space on right
    if (left + previewWidth > window.innerWidth) {
        left = rect.left - previewWidth - 20;
    }
    
    // Adjust vertical position
    if (top + previewHeight > window.innerHeight) {
        top = window.innerHeight - previewHeight - 20;
    }
    if (top < 20) top = 20;
    
    const fileInfo = SUPPORTED_TYPES[fileExt];
    
    // Create preview with loading state
    previewElement = document.createElement('div');
    previewElement.className = 'pdf-preview-popup';
    previewElement.innerHTML = `
        <div class="pdf-preview-header">
            <span>${fileInfo.icon} ${fileInfo.label} (S3)</span>
            <button class="pdf-preview-close" onclick="this.closest('.pdf-preview-popup').remove()">✕</button>
        </div>
        <div class="pdf-preview-loading">
            <div class="spinner"></div>
            <div>Loading ${fileExt.toUpperCase()} from S3...</div>
        </div>
    `;
    
    previewElement.style.cssText = `
        position: fixed;
        top: ${top}px;
        left: ${left}px;
        width: ${previewWidth}px;
        height: ${previewHeight}px;
        z-index: 99999;
    `;
    
    document.body.appendChild(previewElement);
    
    // Keep preview visible when hovering over it
    previewElement.addEventListener('mouseleave', () => {
        setTimeout(() => {
            hidePreview();
        }, 200);
    });
    
    console.log('File Preview: Fetching S3 URL for attachment', attachmentData.id);
    
    // Fetch presigned URL from backend
    fetch('/web/s3_preview_data/' + attachmentData.id, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: {
                attachment_id: attachmentData.id
            }
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('File Preview: Full S3 response:', JSON.stringify(data, null, 2));
        console.log('File Preview: File extension:', fileExt);
        
        const loadingDiv = previewElement.querySelector('.pdf-preview-loading');
        
        // Handle different response structures
        let result = null;
        if (data.result) {
            result = data.result;
        } else if (data.success) {
            result = data;
        }
        
        console.log('File Preview: Parsed result:', result);
        
        if (result && result.success && result.preview_url) {
            const previewUrl = result.preview_url;
            console.log('File Preview: Got presigned URL:', previewUrl);
            
            // Render based on file type
            renderPreview(fileInfo.type, fileExt, previewUrl, attachmentData, loadingDiv);
        } else if (result && result.error) {
            console.error('File Preview: Error from server:', result.error);
            showError(loadingDiv, 'Failed to Load File', result.error);
        } else {
            console.error('File Preview: Unexpected response structure:', data);
            showError(loadingDiv, 'Failed to Load File', 'Unexpected server response. Check console for details.');
        }
    })
    .catch(error => {
        console.error('File Preview: Error fetching S3 URL:', error);
        const loadingDiv = previewElement.querySelector('.pdf-preview-loading');
        showError(loadingDiv, 'Network Error', error.message);
    });
    
    console.log('File Preview: Preview element added to DOM');
}

function renderPreview(type, fileExt, previewUrl, attachmentData, loadingDiv) {
    switch(type) {
        case 'pdf':
            console.log('File Preview: Rendering PDF');
            loadingDiv.innerHTML = `
                <object data="${previewUrl}" type="application/pdf" width="100%" height="100%">
                    <embed src="${previewUrl}" type="application/pdf" width="100%" height="100%" />
                </object>
            `;
            loadingDiv.className = 'pdf-preview-content';
            break;
            
        case 'office':
            console.log('File Preview: Rendering Office document');
            // Use Microsoft Office Online Viewer
            const officeViewerUrl = `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(previewUrl)}`;
            loadingDiv.innerHTML = `
                <iframe src="${officeViewerUrl}" frameborder="0"></iframe>
                <div class="office-preview-note">
                    Note: Rendering via Microsoft Office Online Viewer
                </div>
            `;
            loadingDiv.className = 'pdf-preview-content';
            break;
            
        case 'text':
            console.log('File Preview: Fetching and rendering text file');
            // Use Odoo proxy to avoid CORS issues
            fetch(`/web/s3_proxy/${attachmentData.id}`)
                .then(response => {
                    console.log('File Preview: Text fetch response status:', response.status);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.text();
                })
                .then(text => {
                    console.log('File Preview: Text content length:', text.length);
                    
                    // Format based on file type
                    let formattedContent = text;
                    if (fileExt === 'json') {
                        try {
                            const jsonObj = JSON.parse(text);
                            formattedContent = JSON.stringify(jsonObj, null, 2);
                        } catch (e) {
                            console.warn('Invalid JSON, displaying as plain text');
                        }
                    }
                    
                    loadingDiv.innerHTML = `
                        <div class="text-preview-container">
                            <div class="text-preview-toolbar">
                                <span class="text-preview-info">${attachmentData.name} • ${formatFileSize(attachmentData.size)}</span>
                                <button class="text-preview-btn" onclick="navigator.clipboard.writeText(\`${escapeForAttribute(formattedContent)}\`).then(() => alert('Copied to clipboard!'))">
                                    📋 Copy
                                </button>
                            </div>
                            <pre class="text-preview-content ${fileExt === 'json' ? 'json-highlight' : ''}">${escapeHtml(formattedContent)}</pre>
                        </div>
                    `;
                    loadingDiv.className = 'pdf-preview-content';
                })
                .catch(error => {
                    console.error('File Preview: Text fetch error:', error);
                    showError(loadingDiv, 'Failed to load text content', error.message);
                });
            break;
            
        case 'image':
            console.log('File Preview: Rendering image');
            // Use both direct URL and proxy fallback
            const imageUrl = `/web/s3_proxy/${attachmentData.id}`;
            loadingDiv.innerHTML = `
                <div class="image-preview-container">
                    <img src="${imageUrl}" alt="${attachmentData.name}" class="image-preview-content" 
                         onload="console.log('File Preview: Image loaded successfully')"
                         onerror="console.error('File Preview: Image failed to load'); this.src = '${previewUrl}';">
                    <div class="image-preview-info">
                        ${attachmentData.name} • ${formatFileSize(attachmentData.size)}
                    </div>
                </div>
            `;
            loadingDiv.className = 'pdf-preview-content';
            break;
            
        default:
            showError(loadingDiv, 'Unsupported Format', `Preview not available for .${fileExt} files`);
    }
}

function formatFileSize(bytes) {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function showError(container, title, message) {
    container.innerHTML = `
        <div style="padding: 20px; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 10px;">❌</div>
            <div style="color: #dc3545; font-weight: bold;">${title}</div>
            <div style="color: #6c757d; font-size: 12px; margin-top: 10px;">
                ${message}
            </div>
        </div>
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function escapeForAttribute(text) {
    return text.replace(/`/g, '\\`').replace(/\$/g, '\\$');
}

function hidePreview() {
    if (previewElement && previewElement.parentNode) {
        console.log('File Preview: Hiding preview');
        previewElement.remove();
        previewElement = null;
    }
}

function addStyles() {
    if (document.getElementById('pdf-preview-custom-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'pdf-preview-custom-styles';
    style.textContent = `
        .pdf-preview-popup {
            background: white;
            border: 2px solid #dee2e6;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            animation: slideIn 0.2s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .pdf-preview-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
            font-size: 14px;
        }
        
        .pdf-preview-close {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            transition: background 0.2s;
        }
        
        .pdf-preview-close:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .pdf-preview-popup iframe {
            width: 100%;
            height: calc(100% - 48px);
            border: none;
        }
        
        .pdf-preview-content {
            width: 100%;
            height: calc(100% - 48px);
            overflow: hidden;
        }
        
        .pdf-preview-content object,
        .pdf-preview-content embed {
            border: none;
        }
        
        .text-preview-container {
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            background: #f8f9fa;
        }
        
        .text-preview-toolbar {
            background: white;
            padding: 10px 15px;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .text-preview-info {
            font-size: 12px;
            color: #6c757d;
        }
        
        .text-preview-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.2s;
        }
        
        .text-preview-btn:hover {
            background: #5568d3;
        }
        
        .text-preview-content {
            flex: 1;
            margin: 0;
            padding: 20px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
            color: #212529;
            background: white;
            border: none;
            overflow: auto;
        }
        
        .text-preview-content.json-highlight {
            color: #2c3e50;
        }
        
        .image-preview-container {
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #2c3e50;
            overflow: auto;
            position: relative;
        }
        
        .image-preview-content {
            max-width: 95%;
            max-height: calc(100% - 40px);
            object-fit: contain;
            border-radius: 4px;
        }
        
        .image-preview-info {
            position: absolute;
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
        }
        
        .office-preview-note {
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: rgba(102, 126, 234, 0.9);
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 11px;
        }
        
        .pdf-preview-loading {
            width: 100%;
            height: calc(100% - 48px);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            color: #6c757d;
        }
        
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .o-mail-AttachmentCard {
            transition: all 0.2s ease;
        }
        
        .o-mail-AttachmentCard:hover {
            background-color: #f8f9fa !important;
            transform: translateX(2px);
            cursor: pointer;
        }
    `;
    
    document.head.appendChild(style);
    console.log('File Preview: Styles added');
}

console.log('File Preview: Module loaded');