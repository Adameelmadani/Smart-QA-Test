/**
 * ReqTracer, Frontend Application
 * AI-based Requirements Engineering & Test Plan Generation
 */

// ═══════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════
const state = {
    currentSection: 'upload',
    documents: [],
    currentDocId: null,
    requirements: [],
    testCases: [],
    filters: { type: 'all', priority: 'all' }
};

const API = '';

// ═══════════════════════════════════════════════════════════════════
// Init
// ═══════════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
    initUploadZone();
    initNavbar();
    refreshDocuments();
});

// ═══════════════════════════════════════════════════════════════════
// Navigation
// ═══════════════════════════════════════════════════════════════════
function showSection(section) {
    state.currentSection = section;

    // Hide all sections
    document.querySelectorAll('.section-panel').forEach(el => {
        el.classList.remove('active');
    });

    // Show target
    const target = document.getElementById(`section-${section}`);
    if (target) target.classList.add('active');

    // Update nav links
    document.querySelectorAll('.navbar-nav a').forEach(link => {
        link.classList.toggle('active', link.dataset.section === section);
    });

    // Refresh data for section
    if (section === 'requirements') updateDocSelects();
    if (section === 'tests') updateDocSelects();
    if (section === 'export') updateDocSelects();

    // Close mobile menu if open
    const navLinks = document.getElementById('navLinks');
    const hamburger = document.getElementById('hamburger');
    if (navLinks && navLinks.classList.contains('show-menu')) {
        navLinks.classList.remove('show-menu');
        hamburger.classList.remove('active');
    }
}

function toggleMobileMenu() {
    const navLinks = document.getElementById('navLinks');
    const hamburger = document.getElementById('hamburger');
    if (navLinks && hamburger) {
        navLinks.classList.toggle('show-menu');
        hamburger.classList.toggle('active');
    }
}

function initNavbar() {
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const navbar = document.getElementById('navbar');
        if (window.scrollY > 20) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// ═══════════════════════════════════════════════════════════════════
// Upload
// ═══════════════════════════════════════════════════════════════════
function initUploadZone() {
    const zone = document.getElementById('uploadZone');
    const input = document.getElementById('fileInput');

    zone.addEventListener('click', () => input.click());

    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    });

    zone.addEventListener('dragleave', () => {
        zone.classList.remove('dragover');
    });

    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) uploadFile(files[0]);
    });

    input.addEventListener('change', () => {
        if (input.files.length > 0) uploadFile(input.files[0]);
    });
}

async function uploadFile(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx', 'doc'].includes(ext)) {
        showToast('Please upload a PDF or DOCX file.', 'error');
        return;
    }

    showLoading('Uploading and analyzing document...');
    const progress = document.getElementById('uploadProgress');
    const fill = document.getElementById('uploadProgressFill');
    progress.classList.remove('hidden');

    // Animate progress
    let pct = 0;
    const progressInterval = setInterval(() => {
        pct = Math.min(pct + Math.random() * 15, 90);
        fill.style.width = pct + '%';
    }, 300);

    try {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch(`${API}/api/upload`, {
            method: 'POST',
            body: formData
        });

        clearInterval(progressInterval);
        fill.style.width = '100%';

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Upload failed');
        }

        const data = await res.json();
        showToast(`Document uploaded! ${data.message}`, 'success');
        state.currentDocId = data.document.doc_id;

        await refreshDocuments();
        updateStats();

        setTimeout(() => {
            progress.classList.add('hidden');
            fill.style.width = '0%';
        }, 1000);

    } catch (err) {
        clearInterval(progressInterval);
        progress.classList.add('hidden');
        fill.style.width = '0%';
        showToast(`Error: ${err.message}`, 'error');
    } finally {
        hideLoading();
        document.getElementById('fileInput').value = '';
    }
}

async function loadDomainPack(filename) {
    showLoading(`Loading domain pack: ${filename}...`);
    try {
        const res = await fetch(`${API}/api/load-domain-pack/${filename}`, { method: 'POST' });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to load pack');
        }
        const data = await res.json();
        showToast(`Domain pack loaded! ${data.message}`, 'success');
        state.currentDocId = data.document.doc_id;
        await refreshDocuments();
        updateStats();
    } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// ═══════════════════════════════════════════════════════════════════
// Documents
// ═══════════════════════════════════════════════════════════════════
async function refreshDocuments() {
    try {
        const res = await fetch(`${API}/api/documents`);
        const data = await res.json();
        state.documents = data.documents || [];
        renderDocumentList();
        updateDocSelects();
        updateStats();
    } catch (err) {
        console.error('Failed to load documents:', err);
    }
}

function renderDocumentList() {
    const container = document.getElementById('docList');
    const card = document.getElementById('documentsCard');

    if (state.documents.length === 0) {
        card.style.display = 'none';
        return;
    }

    card.style.display = 'block';
    container.innerHTML = state.documents.map(doc => `
        <div class="doc-item">
            <div class="doc-info">
                <div class="doc-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/></svg>
                </div>
                <div>
                    <div class="doc-name">${escapeHtml(doc.filename)}</div>
                    <div class="doc-meta">${doc.num_pages} pages · ${doc.num_chunks} chunks · ${doc.num_requirements} requirements · ${doc.num_test_cases || 0} tests</div>
                </div>
            </div>
            <div class="doc-actions">
                <button class="btn btn-secondary btn-sm" onclick="viewRequirements('${doc.doc_id}')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    View
                </button>
                <button class="btn btn-ghost btn-sm" onclick="deleteDocument('${doc.doc_id}')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                </button>
            </div>
        </div>
    `).join('');
}

function viewRequirements(docId) {
    state.currentDocId = docId;
    showSection('requirements');
    setTimeout(() => {
        document.getElementById('reqDocSelect').value = docId;
        loadRequirements(docId);
    }, 100);
}

async function deleteDocument(docId) {
    if (!confirm('Delete this document and all its data?')) return;
    try {
        await fetch(`${API}/api/documents/${docId}`, { method: 'DELETE' });
        showToast('Document deleted.', 'info');
        await refreshDocuments();
    } catch (err) {
        showToast('Failed to delete document.', 'error');
    }
}

function updateDocSelects() {
    const selects = ['reqDocSelect', 'testDocSelect', 'exportDocSelect'];
    selects.forEach(id => {
        const sel = document.getElementById(id);
        if (!sel) return;
        const currentVal = sel.value;
        sel.innerHTML = '<option value="">Select document...</option>' +
            state.documents.map(d =>
                `<option value="${d.doc_id}" ${d.doc_id === currentVal ? 'selected' : ''}>${escapeHtml(d.filename)}</option>`
            ).join('');
    });
}

// ═══════════════════════════════════════════════════════════════════
// Requirements
// ═══════════════════════════════════════════════════════════════════
async function loadRequirements(docId) {
    if (!docId) {
        document.getElementById('reqTableContainer').innerHTML = renderEmptyState('No Document Selected', 'Select a document to view its requirements.');
        document.getElementById('reqFilterBar').style.display = 'none';
        return;
    }

    state.currentDocId = docId;
    showLoading('Loading requirements...');

    try {
        const res = await fetch(`${API}/api/requirements/${docId}`);
        const data = await res.json();
        state.requirements = data.requirements || [];
        renderRequirementsTable();
        document.getElementById('reqFilterBar').style.display = state.requirements.length > 0 ? 'flex' : 'none';
    } catch (err) {
        showToast('Failed to load requirements.', 'error');
    } finally {
        hideLoading();
    }
}

function renderRequirementsTable() {
    const container = document.getElementById('reqTableContainer');
    let reqs = state.requirements;

    // Apply filters
    if (state.filters.type !== 'all') {
        reqs = reqs.filter(r => r.req_type === state.filters.type);
    }
    if (state.filters.priority !== 'all') {
        reqs = reqs.filter(r => r.priority === state.filters.priority);
    }

    if (reqs.length === 0) {
        container.innerHTML = renderEmptyState('No Requirements Found', 'No requirements match the current filters.');
        return;
    }

    container.innerHTML = `
        <div class="req-table-wrapper">
            <table class="req-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Type</th>
                        <th>Priority</th>
                        <th>Source</th>
                        <th>Page</th>
                    </tr>
                </thead>
                <tbody>
                    ${reqs.map(req => `
                        <tr>
                            <td><span class="font-mono" style="color:var(--orange-600);font-weight:600">${escapeHtml(req.req_id)}</span></td>
                            <td>${escapeHtml(req.title)}</td>
                            <td><span class="badge badge-${req.req_type}">${req.req_type}</span></td>
                            <td><span class="badge badge-${req.priority}">${req.priority}</span></td>
                            <td class="text-sm text-muted">${escapeHtml(req.source)}</td>
                            <td class="text-sm text-muted">${req.page}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        <div class="mt-2 text-sm text-muted">Showing ${reqs.length} of ${state.requirements.length} requirements</div>
    `;
}

function filterReqs(filterType, value) {
    state.filters[filterType] = value;

    // Update chip states
    const groupId = filterType === 'type' ? 'typeFilters' : 'priorityFilters';
    document.querySelectorAll(`#${groupId} .filter-chip`).forEach(chip => {
        chip.classList.toggle('active', chip.dataset.filter === value);
    });

    renderRequirementsTable();
}

// ═══════════════════════════════════════════════════════════════════
// Q/A (RAG)
// ═══════════════════════════════════════════════════════════════════
let qaHasMessages = false;

async function askQuestion() {
    const input = document.getElementById('qaInput');
    const question = input.value.trim();
    if (!question) return;

    const messagesContainer = document.getElementById('qaMessages');

    // Clear empty state on first message
    if (!qaHasMessages) {
        messagesContainer.innerHTML = '';
        qaHasMessages = true;
    }

    // Add question bubble
    messagesContainer.innerHTML += `
        <div class="qa-message question">${escapeHtml(question)}</div>
    `;
    input.value = '';
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Add typing indicator
    const typingId = 'typing-' + Date.now();
    messagesContainer.innerHTML += `
        <div class="qa-message answer" id="${typingId}">
            <div class="flex items-center gap-2">
                <div class="spinner"></div>
                <span class="text-sm text-muted">Searching documents...</span>
            </div>
        </div>
    `;
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        const res = await fetch(`${API}/api/qa`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, top_k: 5 })
        });

        const data = await res.json();
        const typingEl = document.getElementById(typingId);

        let citationsHtml = '';
        if (data.citations && data.citations.length > 0) {
            citationsHtml = `
                <div class="citations">
                    <div class="text-sm" style="font-weight:600;color:var(--gray-600);margin-bottom:4px">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline;vertical-align:middle;margin-right:4px"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/></svg>
                        Sources
                    </div>
                    ${data.citations.map(c => `
                        <div class="citation">
                            <div class="citation-rank">${c.rank}</div>
                            <div>
                                <div class="citation-text">${escapeHtml(c.text)}</div>
                                <div class="citation-source">${escapeHtml(c.source)}, Page ${c.page}${c.section ? ', ' + escapeHtml(c.section) : ''} (score: ${c.score.toFixed(3)})</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        typingEl.innerHTML = `
            <div class="answer-text">${escapeHtml(data.answer)}</div>
            ${citationsHtml}
        `;
    } catch (err) {
        const typingEl = document.getElementById(typingId);
        typingEl.innerHTML = `<div class="answer-text" style="color:var(--error)">Error: Failed to get answer. Make sure a document is uploaded.</div>`;
    }

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ═══════════════════════════════════════════════════════════════════
// Test Cases
// ═══════════════════════════════════════════════════════════════════
async function generateTests() {
    const docId = document.getElementById('testDocSelect').value;
    if (!docId) {
        showToast('Please select a document first.', 'warning');
        return;
    }

    showLoading('Generating test cases from requirements...');
    try {
        const res = await fetch(`${API}/api/generate-tests/${docId}`, { method: 'POST' });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Generation failed');
        }
        const data = await res.json();
        state.testCases = data.test_cases || [];
        showToast(`Generated ${data.total_test_cases} test cases!`, 'success');
        renderTestCases();
        renderTraceMatrix();
        updateStats();
        await refreshDocuments();
    } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function loadTests(docId) {
    if (!docId) return;
    state.currentDocId = docId;

    try {
        const res = await fetch(`${API}/api/test-cases/${docId}`);
        const data = await res.json();
        state.testCases = data.test_cases || [];
        if (state.testCases.length > 0) {
            renderTestCases();
            renderTraceMatrix();
        }
    } catch (err) {
        console.error('Failed to load tests:', err);
    }
}

function renderTestCases() {
    const container = document.getElementById('testCasesContainer');

    if (state.testCases.length === 0) {
        container.innerHTML = renderEmptyState('No Test Cases Yet', 'Select a document and click "Generate" to create test cases.');
        document.getElementById('traceCard').style.display = 'none';
        return;
    }

    container.innerHTML = `
        <div class="test-cases-grid">
            ${state.testCases.map((tc, idx) => `
                <div class="test-case-card">
                    <div class="tc-header" onclick="toggleTC(${idx})">
                        <div class="flex items-center gap-2">
                            <span class="tc-id">${escapeHtml(tc.tc_id)}</span>
                            <span style="font-size:13px;color:var(--gray-700)">${escapeHtml(tc.goal)}</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class="tc-req-link">${escapeHtml(tc.req_id)}</span>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--gray-400)" stroke-width="2" class="tc-chevron-${idx}" style="transition:transform 0.2s"><polyline points="6 9 12 15 18 9"/></svg>
                        </div>
                    </div>
                    <div class="tc-body" id="tc-body-${idx}">
                        <div class="tc-field">
                            <div class="tc-field-label">Prerequisites</div>
                            <div class="tc-field-value">${escapeHtml(tc.prerequisites)}</div>
                        </div>
                        <div class="tc-field">
                            <div class="tc-field-label">Procedure</div>
                            <div class="tc-field-value">${escapeHtml(tc.procedure)}</div>
                        </div>
                        <div class="tc-field">
                            <div class="tc-field-label">Inputs / Signals</div>
                            <div class="tc-field-value">${escapeHtml(tc.inputs_signals)}</div>
                        </div>
                        <div class="tc-field">
                            <div class="tc-field-label">Thresholds / Oracles</div>
                            <div class="tc-field-value">${escapeHtml(tc.thresholds_oracles)}</div>
                        </div>
                        <div class="tc-field">
                            <div class="tc-field-label">Expected, Pass</div>
                            <div class="tc-field-value tc-pass">${escapeHtml(tc.expected_pass)}</div>
                        </div>
                        <div class="tc-field">
                            <div class="tc-field-label">Expected, Fail</div>
                            <div class="tc-field-value tc-fail">${escapeHtml(tc.expected_fail)}</div>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function toggleTC(idx) {
    const body = document.getElementById(`tc-body-${idx}`);
    const chevron = document.querySelector(`.tc-chevron-${idx}`);
    body.classList.toggle('open');
    if (body.classList.contains('open')) {
        chevron.style.transform = 'rotate(180deg)';
    } else {
        chevron.style.transform = 'rotate(0deg)';
    }
}

function renderTraceMatrix() {
    const grid = document.getElementById('traceGrid');
    const card = document.getElementById('traceCard');

    if (state.testCases.length === 0) {
        card.style.display = 'none';
        return;
    }

    card.style.display = 'block';

    // Build trace map
    const traceMap = {};
    state.testCases.forEach(tc => {
        if (!traceMap[tc.req_id]) traceMap[tc.req_id] = [];
        traceMap[tc.req_id].push(tc.tc_id);
    });

    // Get unique req IDs
    const reqIds = [...new Set(state.testCases.map(tc => tc.req_id))].sort();

    grid.innerHTML = reqIds.map(reqId => `
        <div class="trace-item">
            <span class="trace-req-id">${escapeHtml(reqId)}</span>
            <span class="trace-arrow">→</span>
            <div class="trace-tc-ids">
                ${traceMap[reqId].map(tcId => `<span class="trace-tc-badge">${escapeHtml(tcId)}</span>`).join('')}
            </div>
        </div>
    `).join('');
}

// ═══════════════════════════════════════════════════════════════════
// Export
// ═══════════════════════════════════════════════════════════════════
async function exportData(format) {
    const docId = document.getElementById('exportDocSelect').value;
    if (!docId) {
        showToast('Please select a document first.', 'warning');
        return;
    }

    showLoading(`Exporting ${format.toUpperCase()}...`);
    try {
        const res = await fetch(`${API}/api/export/${docId}/${format}`);
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Export failed');
        }

        const blob = await res.blob();
        const filename = format === 'excel' ? 'test_plan.xlsx' : 'test_plan.json';
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showToast(`${format.toUpperCase()} exported successfully!`, 'success');
    } catch (err) {
        showToast(`Export error: ${err.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// ═══════════════════════════════════════════════════════════════════
// Stats
// ═══════════════════════════════════════════════════════════════════
async function updateStats() {
    try {
        const res = await fetch(`${API}/api/stats`);
        const data = await res.json();
        document.getElementById('statDocs').textContent = data.documents || 0;
        document.getElementById('statReqs').textContent = data.total_requirements || 0;
        document.getElementById('statTests').textContent = data.total_test_cases || 0;
    } catch (err) {
        // Stats are non-critical
    }
}

// ═══════════════════════════════════════════════════════════════════
// UI Helpers
// ═══════════════════════════════════════════════════════════════════
function showLoading(text) {
    const overlay = document.getElementById('loadingOverlay');
    document.getElementById('loadingText').textContent = text || 'Processing...';
    overlay.classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const icons = {
        success: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4CAF50" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        error: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F44336" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        warning: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FF9800" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        info: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2196F3" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-text">${escapeHtml(message)}</span>
        <span class="toast-close" onclick="this.parentElement.classList.add('hiding');setTimeout(()=>this.parentElement.remove(),300)">×</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function renderEmptyState(title, desc) {
    return `
        <div class="empty-state">
            <div class="empty-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/></svg>
            </div>
            <h3>${title}</h3>
            <p>${desc}</p>
        </div>
    `;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}
