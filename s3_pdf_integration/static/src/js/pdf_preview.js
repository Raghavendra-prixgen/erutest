/** @odoo-module **/
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

// Global variables for preview
let previewTimeout = null;
let previewElement = null;

// Supported file types with their configurations
const SUPPORTED_TYPES = {
    // Documents
    pdf:  { icon: '📄', label: 'PDF Preview',         type: 'pdf' },
    docx: { icon: '📘', label: 'Word Document Preview', type: 'office' },
    doc:  { icon: '📘', label: 'Word Document Preview', type: 'office' },
    xlsx: { icon: '📊', label: 'Excel Preview',         type: 'office' },
    xls:  { icon: '📊', label: 'Excel Preview',         type: 'office' },
    pptx: { icon: '📽️', label: 'PowerPoint Preview',   type: 'office' },
    ppt:  { icon: '📽️', label: 'PowerPoint Preview',   type: 'office' },

    // Text files
    txt:  { icon: '📝', label: 'Text Preview', type: 'text' },
    csv:  { icon: '📋', label: 'CSV Preview',  type: 'text' },
    json: { icon: '📋', label: 'JSON Preview', type: 'text' },
    xml:  { icon: '📋', label: 'XML Preview',  type: 'text' },
    log:  { icon: '📋', label: 'Log Preview',  type: 'text' },

    // HTML files  ← NEW
    html: { icon: '🌐', label: 'HTML Preview', type: 'html' },
    htm:  { icon: '🌐', label: 'HTML Preview', type: 'html' },

    // Images
    jpg:  { icon: '🖼️', label: 'Image Preview', type: 'image' },
    jpeg: { icon: '🖼️', label: 'Image Preview', type: 'image' },
    png:  { icon: '🖼️', label: 'Image Preview', type: 'image' },
    gif:  { icon: '🖼️', label: 'GIF Preview',   type: 'image' },
    bmp:  { icon: '🖼️', label: 'Image Preview', type: 'image' },
    webp: { icon: '🖼️', label: 'Image Preview', type: 'image' },
    svg:  { icon: '🖼️', label: 'SVG Preview',   type: 'image' },
    jfif: { icon: '🖼️', label: 'Image Preview', type: 'image' },  // ← NEW: JFIF is JPEG
    tif:  { icon: '🖼️', label: 'TIFF Preview',  type: 'tiff' },   // ← NEW
    tiff: { icon: '🖼️', label: 'TIFF Preview',  type: 'tiff' },   // ← NEW

    // Email
    eml: { icon: '📧', label: 'Email Preview',  type: 'email' },
    msg: { icon: '📨', label: 'Outlook Email',  type: 'binary' },

    // Archive files
    zip: { icon: '🗜️', label: 'ZIP Archive', type: 'archive' },
    '7z':{ icon: '🗜️', label: '7Z Archive',  type: 'archive' },
    rar: { icon: '🗜️', label: 'RAR Archive', type: 'archive' },

    // Video
    mp4:  { icon: '🎬', label: 'Video Preview', type: 'video' },
    webm: { icon: '🎬', label: 'Video Preview', type: 'video' },
    mov:  { icon: '🎬', label: 'Video Preview', type: 'video' },

    // XPS / STEP CAD
    xps:  { icon: '📄', label: 'XPS Document', type: 'binary' },
    step: { icon: '🧩', label: '3D STEP File', type: 'binary' },
    stp:  { icon: '🧩', label: '3D STEP File', type: 'binary' },
};

const ATTACHMENT_SELECTOR = `
    .o-mail-AttachmentCard,
    .o-mail-AttachmentImage,
    .o_attachment,
    .o_attachments .o_attachment a
`;

// Initialize after a delay to ensure DOM is ready
setTimeout(() => {
    console.log('File Preview: Initializing...');
    setupFilePreview();
}, 2000);

function setupFilePreview() {
    console.log('File Preview: Setting up event listeners');
    addStyles();

    const observer = new MutationObserver(() => {
        attachEventListeners();
    });

    observer.observe(document.body, { childList: true, subtree: true });
    attachEventListeners();
}

function attachEventListeners() {
    const cards = document.querySelectorAll(ATTACHMENT_SELECTOR);
    console.log(`File Preview: Found ${cards.length} attachment cards`);

    cards.forEach((card, index) => {
        if (card.dataset.filePreviewAttached === 'true') return;
        card.dataset.filePreviewAttached = 'true';

        card.addEventListener('mouseenter', (e) => handleMouseEnter(e, card));
        card.addEventListener('mouseleave', () => handleMouseLeave());

        console.log(`File Preview: Attached listeners to card ${index + 1}`);
    });
}

function getFileExtension(filename) {
    if (!filename) return null;
    const parts = filename.toLowerCase().split('.');
    if (parts.length < 2) return null;
    const ext = parts.pop();
    console.log(`File Preview: Extracted extension '${ext}' from '${filename}'`);
    return SUPPORTED_TYPES[ext] ? ext : null;
}

function getTitleFromCard(card) {
    if (card.tagName === 'A') return card.textContent.trim();

    const link = card.querySelector('a');
    if (link) return link.textContent.trim();

    const fromAttr = card.getAttribute('title') || card.getAttribute('aria-label') || '';
    if (fromAttr) return fromAttr;

    const img = card.querySelector('img[alt]');
    if (img) return img.getAttribute('alt');

    return card.textContent.trim();
}

function handleMouseEnter(e, card) {
    const title = getTitleFromCard(card);
    console.log('File Preview: Mouse entered card, title:', title);

    const attachmentData = extractAttachmentData(card, title);
    if (!attachmentData) {
        console.log('File Preview: Could not find attachment data');
        return;
    }

    // ✅ FIX: detect extension AFTER getting real name
    const fileExt = getFileExtension(attachmentData.name || title);

    if (!fileExt) {
        console.log('File Preview: Not a supported file type, skipping');
        return;
    }

    console.log(`File Preview: ${fileExt.toUpperCase()} detected`);

    if (previewTimeout) clearTimeout(previewTimeout);

    previewTimeout = setTimeout(() => {
        showPreviewWithS3(card, attachmentData, fileExt);
    }, 500);
}

function handleMouseLeave() {
    if (previewTimeout) {
        clearTimeout(previewTimeout);
        previewTimeout = null;
    }
    setTimeout(() => {
        if (!previewElement || !previewElement.matches(':hover')) {
            hidePreview();
        }
    }, 100);
}

function extractAttachmentData(card, cardTitle) {
    console.log('File Preview: Extracting attachment data for:', cardTitle);

    // Priority 1: many2many_binary attachment links
    const binaryLink = card.querySelector('a[href*="/web/content/"]') ||
                       (card.matches('a[href*="/web/content/"]') ? card : null);
    if (binaryLink) {
        const href = binaryLink.getAttribute('href');
        const idMatch = href.match(/\/web\/content\/(\d+)/);
        if (idMatch) {
            return { id: parseInt(idMatch[1]), name: binaryLink.textContent.trim(),
                     size: null, url: href, s3_url: null, type: null };
        }
    }

    // Priority 2: /web/content/ download link
    const link = card.querySelector('a[href*="/web/content/"]');
    if (link) {
        const href = link.getAttribute('href');
        const idMatch = href.match(/\/web\/content\/(\d+)/);
        if (idMatch) {
            return { id: parseInt(idMatch[1]), name: cardTitle,
                     size: null, url: href, s3_url: null, type: null };
        }
    }

    // Priority 3: /web/image/ src on img tag
    const img = card.querySelector('img[src*="/web/image/"]');
    if (img) {
        const src = img.getAttribute('src');
        const idMatch = src.match(/\/web\/image\/(?:ir\.attachment\/)?(\d+)/);
        if (idMatch) {
            return { id: parseInt(idMatch[1]), name: cardTitle,
                     size: null, url: src, s3_url: null, type: null };
        }
    }

    // Priority 4: OWL component traversal
    const eventKeys = Object.keys(card).filter(k => k.startsWith('__event'));
    for (const key of eventKeys) {
        const handlers = card[key];
        if (Array.isArray(handlers) && handlers.length >= 2) {
            const component = handlers[1];
            if (component && component.props) {
                if (component.props.attachment) {
                    const att = component.props.attachment;
                    if (att.name === cardTitle)
                        return { id: att.id, size: att.size, name: att.name,
                                 url: att.url, s3_url: att.s3_url, type: att.type };
                }
                if (Array.isArray(component.props.attachments)) {
                    const match = component.props.attachments.find(a => a.name === cardTitle);
                    if (match)
                        return { id: match.id, size: match.size, name: match.name,
                                 url: match.url, s3_url: match.s3_url, type: match.type };
                }
            }
        }
    }

    // Priority 5: OWL parent traversal
    let el = card;
    let depth = 10;
    while (el && depth-- > 0) {
        for (const key in el) {
            if (key.startsWith('__owl__')) {
                try {
                    const owlData = el[key];
                    if (owlData && owlData.component) {
                        const comp = owlData.component;
                        const sources = [
                            comp.props && comp.props.attachment,
                            ...(comp.props && Array.isArray(comp.props.attachments) ? comp.props.attachments : []),
                            ...(comp.props && comp.props.thread && Array.isArray(comp.props.thread.attachments) ? comp.props.thread.attachments : []),
                            ...(comp.props && comp.props.message && Array.isArray(comp.props.message.attachments) ? comp.props.message.attachments : []),
                        ].filter(Boolean);

                        const match = sources.find(a => a && a.name === cardTitle);
                        if (match)
                            return { id: match.id, size: match.size, name: match.name,
                                     url: match.url, s3_url: match.s3_url, type: match.type };
                    }
                } catch (e) { /* skip */ }
            }
        }
        el = el.parentElement;
    }

    console.log('File Preview: Could not extract attachment data');
    return null;
}

function showPreviewWithS3(card, attachmentData, fileExt) {
    hidePreview();

    const rect = card.getBoundingClientRect();
    const previewWidth = 950;
    const previewHeight = 750;

    let left = rect.right + 20;
    let top  = rect.top;

    if (left + previewWidth > window.innerWidth)  left = rect.left - previewWidth - 20;
    if (left < 10)                                left = (window.innerWidth - previewWidth) / 2;
    if (top + previewHeight > window.innerHeight) top  = window.innerHeight - previewHeight - 20;
    if (top < 20)                                 top  = 20;

    const fileInfo = SUPPORTED_TYPES[fileExt];

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

    previewElement.addEventListener('mouseleave', () => {
        setTimeout(hidePreview, 200);
    });

    console.log('File Preview: Fetching S3 URL for attachment', attachmentData.id);

    fetch('/web/s3_preview_data/' + attachmentData.id, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: { attachment_id: attachmentData.id }
        })
    })
    .then(r => r.json())
    .then(data => {
        console.log('File Preview: S3 response:', data);
        const loadingDiv = previewElement ? previewElement.querySelector('.pdf-preview-loading') : null;
        if (!loadingDiv) return;

        const result = data.result || (data.success ? data : null);

        if (result && result.success && result.preview_url) {
            // ✅ OVERRIDE filename from backend (CRITICAL)
            attachmentData.name = result.filename || attachmentData.name;
            const newExt = getFileExtension(attachmentData.name);
            const finalExt = newExt || fileExt;
            const finalType = SUPPORTED_TYPES[finalExt]?.type || fileInfo.type;

            renderPreview(finalType, finalExt, result.preview_url, attachmentData, loadingDiv);
        } else {
            showError(loadingDiv, 'Failed to Load File',
                      (result && result.error) || 'Unexpected server response');
        }
    })
    .catch(error => {
        console.error('File Preview: Fetch error:', error);
        const loadingDiv = previewElement ? previewElement.querySelector('.pdf-preview-loading') : null;
        if (loadingDiv) showError(loadingDiv, 'Network Error', error.message);
    });
}

function renderPreview(type, fileExt, previewUrl, attachmentData, loadingDiv) {
    switch (type) {

        // ── PDF ──────────────────────────────────────────────────────────────
        case 'pdf':
            loadingDiv.innerHTML = `
                <object data="${previewUrl}" type="application/pdf" width="100%" height="100%">
                    <embed src="${previewUrl}" type="application/pdf" width="100%" height="100%" />
                </object>`;
            loadingDiv.className = 'pdf-preview-content';
            break;

        // ── Office via Microsoft Viewer ──────────────────────────────────────
        case 'office': {
            const viewerUrl = `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(previewUrl)}`;
            loadingDiv.innerHTML = `
                <div style="position:relative; width:100%; height:100%;">
                    <div style="position:absolute;top:10px;right:10px;z-index:10;">
                        <a href="/web/s3_proxy/${attachmentData.id}"
                           download="${attachmentData.name}"
                           style="background:#667eea;color:white;padding:6px 12px;
                                  border-radius:4px;text-decoration:none;font-size:12px;">
                           ⬇ Download File
                        </a>
                    </div>
                    <iframe src="${viewerUrl}" frameborder="0"
                        style="width:100%; height:100%; border:none;">
                    </iframe>
                    <div class="office-preview-note">Rendering via Microsoft Office Online Viewer</div>
                </div>`;
            loadingDiv.className = 'pdf-preview-content';
            break;
        }

        // ── HTML  ← NEW ──────────────────────────────────────────────────────
        // Fetch raw HTML via the proxy and render it in a sandboxed iframe
        // so it cannot break the parent Odoo page.
        case 'html':
            fetch(`/web/s3_proxy/${attachmentData.id}`)
                .then(r => r.text())
                .then(htmlText => {

                    // ✅ CREATE blobUrl (missing in your code)
                    const blob = new Blob([htmlText], { type: 'text/html' });
                    const blobUrl = window.URL.createObjectURL(blob);

                    const iframe = document.createElement('iframe');
                    iframe.src = blobUrl;
                    iframe.style.width = '100%';
                    iframe.style.height = '100%';
                    iframe.style.border = 'none';
                    iframe.style.background = 'white';
                    iframe.setAttribute('sandbox', 'allow-same-origin allow-scripts allow-forms');

                    // ✅ Safe cleanup
                    iframe.onload = () => {
                        if (window.URL && window.URL.revokeObjectURL) {
                            window.URL.revokeObjectURL(blobUrl);
                        }
                    };

                    loadingDiv.innerHTML = `
                        <div style="position:relative; width:100%; height:100%;">
                            <div style="
                                position:absolute; top:10px; right:10px; z-index:10;
                                display:flex; gap:8px;">
                                <a href="${previewUrl}" target="_blank"
                                   style="background:#28a745;color:white;padding:6px 12px;
                                          border-radius:4px;text-decoration:none;font-size:12px;">
                                   🔗 Open in Tab
                                </a>
                                <a href="/web/s3_proxy/${attachmentData.id}"
                                   download="${attachmentData.name}"
                                   style="background:#667eea;color:white;padding:6px 12px;
                                          border-radius:4px;text-decoration:none;font-size:12px;">
                                   ⬇ Download HTML
                                </a>
                            </div>
                            <div id="html-frame-container" style="width:100%; height:100%;"></div>
                        </div>
                    `;

                    loadingDiv.querySelector('#html-frame-container').appendChild(iframe);
                })
                .catch(err => showError(loadingDiv, 'Failed to load HTML', err.message));
            break;

        // ── TIFF  ← NEW ──────────────────────────────────────────────────────
        // Browsers do NOT render TIFF natively.
        // We use the lightweight tiff.js library (loaded on-demand from CDN)
        // to decode the image to a canvas, then export as PNG data-URL.
        case 'tiff':
                loadingDiv.innerHTML = `
                    <div style="display:flex;flex-direction:column;height:100%;
                                align-items:center;justify-content:center;text-align:center;">

                        <div id="tiff-loader">
                            <div class="spinner"></div>
                            <div style="margin-top:10px;">Loading TIFF preview...</div>
                        </div>

                        <canvas id="tiffCanvas"
                            style="display:none;max-width:95%;max-height:80%;margin-top:10px;"></canvas>

                        <div id="tiff-error"
                            style="display:none;color:#dc3545;margin-top:15px;">
                            Preview not available for this TIFF format
                        </div>

                        <!-- ✅ ALWAYS AVAILABLE DOWNLOAD BUTTON -->
                        <div style="margin-top:20px;">
                            <a href="/web/s3_proxy/${attachmentData.id}"
                               target="_blank"
                               style="background:#667eea;color:white;padding:10px 20px;
                                      border-radius:6px;text-decoration:none;font-weight:500;">
                               ⬇ Download File
                            </a>
                        </div>
                    </div>
                `;
                loadingDiv.className = 'pdf-preview-content';

                function loadTiffScript(callback) {
                    if (window.Tiff) return callback();

                    const script = document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/tiff.js@1.0.0/tiff.min.js';
                    script.onload = callback;
                    script.onerror = () => {
                        document.getElementById('tiff-loader').style.display = 'none';
                        document.getElementById('tiff-error').style.display = 'block';
                    };
                    document.head.appendChild(script);
                }

                loadTiffScript(() => {
                    fetch(`/web/s3_proxy/${attachmentData.id}`)
                        .then(r => r.arrayBuffer())
                        .then(buffer => {
                            try {
                                const tiff = new Tiff({ buffer });
                                const canvas = tiff.toCanvas();

                                const target = document.getElementById('tiffCanvas');

                                target.width = canvas.width;
                                target.height = canvas.height;

                                const ctx = target.getContext('2d');
                                ctx.drawImage(canvas, 0, 0);

                                // ✅ Show preview
                                target.style.display = 'block';
                                document.getElementById('tiff-loader').style.display = 'none';

                            } catch (e) {
                                console.warn("TIFF preview not supported:", e);

                                document.getElementById('tiff-loader').style.display = 'none';
                                document.getElementById('tiff-error').style.display = 'block';
                            }
                        })
                        .catch(() => {
                            document.getElementById('tiff-loader').style.display = 'none';
                            document.getElementById('tiff-error').style.display = 'block';
                        });
                });

                break;

        // ── Video ────────────────────────────────────────────────────────────
        case 'video':
            loadingDiv.innerHTML = `
                <div style="width:100%; height:100%; background:black;
                            display:flex; flex-direction:column;">
                    <video controls autoplay
                        style="width:100%; height:100%; object-fit:contain;"
                        onerror="this.onerror=null; this.src='/web/s3_proxy/${attachmentData.id}';">
                        <source src="${previewUrl}" type="video/mp4">
                        Your browser does not support video playback.
                    </video>
                </div>`;
            loadingDiv.className = 'pdf-preview-content';
            break;

        // ── Text / CSV / JSON / XML ──────────────────────────────────────────
        case 'text':
            fetch(`/web/s3_proxy/${attachmentData.id}`)
                .then(r => r.text())
                .then(text => {
                    if (fileExt === 'csv') {
                        const rows = text.split(/\r?\n/).map(r => r.split(','));
                        let tableHtml = `
                            <div class="csv-table-container">
                                <div style="padding:10px;background:#f1f3f5;border-bottom:1px solid #ddd;
                                            display:flex;justify-content:space-between;align-items:center;">
                                    <strong>${attachmentData.name}</strong>
                                    <a href="${previewUrl}" target="_blank"
                                       style="background:#667eea;color:white;padding:6px 12px;
                                              border-radius:4px;text-decoration:none;font-size:12px;">
                                        ⬇ Download CSV
                                    </a>
                                </div>
                                <div style="overflow:auto;height:calc(100% - 50px);">
                                    <table class="csv-table">`;
                        rows.forEach((cols, ri) => {
                            tableHtml += '<tr>';
                            cols.forEach(col => {
                                tableHtml += ri === 0
                                    ? `<th>${escapeHtml(col)}</th>`
                                    : `<td>${escapeHtml(col)}</td>`;
                            });
                            tableHtml += '</tr>';
                        });
                        tableHtml += '</table></div></div>';
                        loadingDiv.innerHTML = tableHtml;
                    } else {
                        loadingDiv.innerHTML = `
                            <div class="text-preview-container">
                                <pre class="text-preview-content">${escapeHtml(text)}</pre>
                            </div>`;
                    }
                    loadingDiv.className = 'pdf-preview-content';
                })
                .catch(err => showError(loadingDiv, 'Failed to load text', err.message));
            break;

        // ── Email (.eml) ─────────────────────────────────────────────────────
        case 'email':
            fetch(`/web/s3_proxy/${attachmentData.id}`)
                .then(r => r.text())
                .then(text => {
                    loadingDiv.innerHTML = `
                        <div class="text-preview-container">
                            <div class="text-preview-toolbar">
                                <span class="text-preview-info">📧 ${attachmentData.name}</span>
                                <a href="${previewUrl}" target="_blank"
                                   style="background:#667eea;color:white;padding:6px 12px;
                                          border-radius:4px;text-decoration:none;font-size:12px;">
                                   ⬇ Download EML
                                </a>
                            </div>
                            <pre class="text-preview-content">${escapeHtml(text)}</pre>
                        </div>`;
                    loadingDiv.className = 'pdf-preview-content';
                })
                .catch(err => showError(loadingDiv, 'Failed to load email', err.message));
            break;

        // ── Archive (.zip / .7z / .rar) ──────────────────────────────────────
        case 'archive':
            loadingDiv.innerHTML = `
                <div style="padding:30px;text-align:center;">
                    <div style="font-size:60px;">🗜️</div>
                    <div style="font-weight:bold;margin-top:15px;">${attachmentData.name}</div>
                    <div style="margin-top:10px;color:#6c757d;">
                        Archive files (ZIP / 7Z / RAR) cannot be previewed in browser.
                    </div>
                    <a href="${previewUrl}" target="_blank"
                       style="display:inline-block;margin-top:20px;background:#667eea;color:white;
                              padding:10px 20px;border-radius:6px;text-decoration:none;">
                        ⬇ Download File
                    </a>
                </div>`;
            loadingDiv.className = 'pdf-preview-content';
            break;

        // ── Binary / MSG / XPS / STEP ─────────────────────────────────────────
        case 'binary':
            loadingDiv.innerHTML = `
                <div style="padding:30px;text-align:center;">
                    <div style="font-size:60px;">📨</div>
                    <div style="font-weight:bold;margin-top:15px;">${attachmentData.name}</div>
                    <div style="margin-top:10px;color:#6c757d;">
                        This file type cannot be previewed in the browser.
                    </div>
                    <a href="${previewUrl}" target="_blank"
                       style="display:inline-block;margin-top:20px;background:#667eea;color:white;
                              padding:10px 20px;border-radius:6px;text-decoration:none;">
                        ⬇ Download File
                    </a>
                </div>`;
            loadingDiv.className = 'pdf-preview-content';
            break;

        // ── Image (jpg / png / gif / bmp / webp / svg / jfif) ────────────────
        case 'image':
            loadingDiv.innerHTML = `
                <div class="image-preview-container">
                    <div style="position:absolute;top:10px;right:10px;z-index:10;">
                        <a href="${previewUrl}" target="_blank"
                           style="background:#667eea;color:white;padding:6px 12px;
                                  border-radius:4px;text-decoration:none;font-size:12px;">
                           ⬇ Download Image
                        </a>
                    </div>
                    <img
                        src="${previewUrl}"
                        alt="${attachmentData.name}"
                        class="image-preview-content"
                        onload="console.log('File Preview: Image loaded from S3')"
                        onerror="this.onerror=null;
                                 this.src='/web/s3_proxy/${attachmentData.id}';">
                    <div class="image-preview-info">
                        ${attachmentData.name}${attachmentData.size ? ' • ' + formatFileSize(attachmentData.size) : ''}
                    </div>
                </div>`;
            loadingDiv.className = 'pdf-preview-content';
            break;

        default:
            showError(loadingDiv, 'Unsupported Format',
                      `Preview not available for .${fileExt} files`);
    }
}

// ─── TIFF decoder helper ───────────────────────────────────────────────────────
// Loads tiff.js from CDN on demand, fetches the binary TIFF via proxy,
// decodes it to a canvas and shows a download button.
function _loadTiff(previewUrl, attachmentData, loadingDiv) {
    function _decodeTiff(arrayBuffer) {
        try {
            const tiff = new Tiff({ buffer: arrayBuffer });
            const canvas = tiff.toCanvas();

            const previewCanvas = document.getElementById('tiff-preview-canvas');
            const spinner = loadingDiv.querySelector('.spinner');
            const spinnerText = loadingDiv.querySelector('div[style*="Decoding"]');

            if (!previewCanvas) return;

            // Copy decoded pixels onto the existing canvas element
            previewCanvas.width  = canvas.width;
            previewCanvas.height = canvas.height;
            const ctx = previewCanvas.getContext('2d');
            ctx.drawImage(canvas, 0, 0);

            previewCanvas.style.display = 'block';
            if (spinner)     spinner.style.display     = 'none';
            if (spinnerText) spinnerText.style.display = 'none';

            // Download button
            const btnContainer = document.getElementById('tiff-download-btn-container');
            if (btnContainer) {
                btnContainer.innerHTML = `
                    <a href="${previewUrl}" target="_blank"
                       style="background:#667eea;color:white;padding:6px 12px;
                              border-radius:4px;text-decoration:none;font-size:12px;">
                       ⬇ Download TIFF
                    </a>`;
            }

            // Info bar
            const infoDiv = document.getElementById('tiff-info');
            if (infoDiv) {
                infoDiv.textContent = `${attachmentData.name} — ${canvas.width}×${canvas.height}px`;
                infoDiv.style.display = 'block';
            }
        } catch (decodeErr) {
            console.error('TIFF decode error:', decodeErr);
            const previewCanvas = document.getElementById('tiff-preview-canvas');
            if (previewCanvas) {
                showError(previewCanvas.parentElement,
                          'TIFF Decode Error', decodeErr.message);
            }
        }
    }

    function _fetchAndDecode() {
        fetch(`/web/s3_proxy/${attachmentData.id}`)
            .then(r => {
                if (!r.ok) throw new Error(`HTTP ${r.status}`);
                return r.arrayBuffer();
            })
            .then(buf => _decodeTiff(buf))
            .catch(err => {
                const el = document.getElementById('tiff-preview-canvas');
                if (el) showError(el.parentElement, 'Failed to load TIFF', err.message);
            });
    }

    // Load tiff.js from CDN if not already present
    if (window.Tiff) {
        _fetchAndDecode();
    } else {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/tiff.js@1.0.0/tiff.min.js';
        script.onload = () => {
            console.log('File Preview: tiff.js loaded');
            _fetchAndDecode();
        };
        script.onerror = () => {
            const el = document.getElementById('tiff-preview-canvas');
            if (el) showError(el.parentElement, 'TIFF library failed to load',
                              'Could not load tiff.js from CDN');
        };
        document.head.appendChild(script);
    }
}
// ──────────────────────────────────────────────────────────────────────────────

function formatFileSize(bytes) {
    if (!bytes) return '';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function showError(container, title, message) {
    container.innerHTML = `
        <div style="padding:20px;text-align:center;">
            <div style="font-size:48px;margin-bottom:10px;">❌</div>
            <div style="color:#dc3545;font-weight:bold;">${title}</div>
            <div style="color:#6c757d;font-size:12px;margin-top:10px;">${message}</div>
        </div>`;
}

function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}

function hidePreview() {
    if (previewElement && previewElement.parentNode) {
        previewElement.remove();
        previewElement = null;
    }
}

function addStyles() {
    if (document.getElementById('pdf-preview-custom-styles')) return;

    const style = document.createElement('style');
    style.id = 'pdf-preview-custom-styles';
    style.textContent = `
        .csv-table-container { overflow:auto; height:100%; background:white; }
        .csv-table { border-collapse:collapse; width:max-content; min-width:100%; font-size:13px; }
        .csv-table th { background:#667eea; color:white; padding:8px 12px;
                        border:1px solid #ddd; position:sticky; top:0; }
        .csv-table td { padding:6px 10px; border:1px solid #eee; white-space:nowrap; }
        .csv-table tr:nth-child(even) { background:#f8f9fa; }

        .pdf-preview-popup {
            background:white; border:2px solid #dee2e6; border-radius:12px;
            box-shadow:0 20px 60px rgba(0,0,0,0.3); overflow:hidden;
            animation:slideIn 0.2s ease-out;
        }
        @keyframes slideIn {
            from { opacity:0; transform:translateY(-10px); }
            to   { opacity:1; transform:translateY(0); }
        }
        .pdf-preview-header {
            background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
            color:white; padding:12px 16px;
            display:flex; justify-content:space-between; align-items:center;
            font-weight:600; font-size:14px;
        }
        .pdf-preview-close {
            background:rgba(255,255,255,0.2); border:none; color:white;
            width:24px; height:24px; border-radius:50%; cursor:pointer;
            display:flex; align-items:center; justify-content:center;
            font-size:16px; transition:background 0.2s;
        }
        .pdf-preview-close:hover { background:rgba(255,255,255,0.3); }
        .pdf-preview-popup iframe { width:100%; height:calc(100% - 48px); border:none; }
        .pdf-preview-content { width:100%; height:calc(100% - 48px); overflow:hidden; }
        .pdf-preview-content object,
        .pdf-preview-content embed { border:none; }

        .text-preview-container { width:100%; height:100%; display:flex;
            flex-direction:column; background:#f8f9fa; }
        .text-preview-toolbar { background:white; padding:10px 15px;
            border-bottom:1px solid #dee2e6;
            display:flex; justify-content:space-between; align-items:center; }
        .text-preview-info { font-size:12px; color:#6c757d; }
        .text-preview-content {
            flex:1; margin:0; padding:20px;
            font-family:'Courier New',monospace; font-size:13px; line-height:1.6;
            white-space:pre-wrap; word-wrap:break-word; color:#212529;
            background:white; border:none; overflow:auto;
        }

        .image-preview-container {
            width:100%; height:100%;
            display:flex; flex-direction:column; align-items:center; justify-content:center;
            background:#2c3e50; overflow:auto; position:relative;
        }
        .image-preview-content {
            max-width:95%; max-height:calc(100% - 40px);
            object-fit:contain; border-radius:4px;
        }
        .image-preview-info {
            position:absolute; bottom:10px; left:50%; transform:translateX(-50%);
            background:rgba(0,0,0,0.7); color:white;
            padding:8px 16px; border-radius:20px; font-size:12px; white-space:nowrap;
        }
        .office-preview-note {
            position:absolute; bottom:10px; right:10px;
            background:rgba(102,126,234,0.9); color:white;
            padding:6px 12px; border-radius:4px; font-size:11px;
        }
        .pdf-preview-loading {
            width:100%; height:calc(100% - 48px);
            display:flex; flex-direction:column;
            align-items:center; justify-content:center;
            font-size:14px; color:#6c757d;
        }
        .spinner {
            width:40px; height:40px;
            border:4px solid #f3f3f3; border-top:4px solid #667eea;
            border-radius:50%; animation:spin 1s linear infinite; margin-bottom:15px;
        }
        @keyframes spin { 0% { transform:rotate(0deg); } 100% { transform:rotate(360deg); } }

        .o-mail-AttachmentCard, .o-mail-AttachmentImage { transition:all 0.2s ease; }
        .o-mail-AttachmentCard:hover, .o-mail-AttachmentImage:hover {
            background-color:rgba(255,255,255,0.1) !important; cursor:pointer;
        }
    `;

    document.head.appendChild(style);
    console.log('File Preview: Styles added');
}

console.log('File Preview: Module loaded');