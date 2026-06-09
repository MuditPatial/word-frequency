/* ══════════════════════════════════════════════════════════════
   WordLens — Dashboard JavaScript
   ══════════════════════════════════════════════════════════════ */

'use strict';

// ── State ────────────────────────────────────────────────────────
let barChartInstance   = null;
let letterChartInstance = null;
let analysisReady      = false;

// ── DOM Refs ────────────────────────────────────────────────────
const dropZone       = document.getElementById('drop-zone');
const fileInput      = document.getElementById('file-input');
const fileSelected   = document.getElementById('file-selected');
const fileNameDisp   = document.getElementById('file-name-display');
const fileSizeDisp   = document.getElementById('file-size-display');
const fileTypeIcon   = document.getElementById('file-type-icon');
const clearFileBtn   = document.getElementById('clear-file-btn');
const textInput      = document.getElementById('text-input');
const analyzeBtn     = document.getElementById('analyze-btn');
const swToggle       = document.getElementById('sw-toggle');
const topNSelect     = document.getElementById('top-n-select');
const samplesChips   = document.getElementById('samples-chips');

const searchInput    = document.getElementById('search-input');
const searchBtn      = document.getElementById('search-btn');
const searchResult   = document.getElementById('search-result');

const loaderOverlay  = document.getElementById('loader-overlay');
const loaderMsg      = document.getElementById('loader-msg');
const toast          = document.getElementById('toast');

const statTotal      = document.getElementById('stat-total');
const statFiltered   = document.getElementById('stat-filtered');
const statUnique     = document.getElementById('stat-unique');
const statSentences  = document.getElementById('stat-sentences');
const statReading    = document.getElementById('stat-reading');
const statDensity    = document.getElementById('stat-density');
const statAvgLen     = document.getElementById('stat-avglen');

// ── File Icon Map ─────────────────────────────────────────────────
const FILE_ICONS = { pdf: '📕', docx: '📘', doc: '📘', txt: '📄' };

// ── Utilities ─────────────────────────────────────────────────────
function fmtBytes(bytes) {
  if (bytes < 1024)       return bytes + ' B';
  if (bytes < 1048576)    return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / 1048576).toFixed(2) + ' MB';
}

function fmtNum(n) {
  return n == null ? '—' : Number(n).toLocaleString();
}

function fmtTime(secs) {
  if (!secs) return '—';
  if (secs < 60) return secs + 's';
  const m = Math.floor(secs / 60), s = Math.round(secs % 60);
  return s > 0 ? `${m}m ${s}s` : `${m}m`;
}

function showToast(msg, type = 'info') {
  toast.textContent = msg;
  toast.className = `toast toast-${type} show`;
  setTimeout(() => toast.classList.remove('show'), 3500);
}

function showLoader(msg = 'Analyzing document…') {
  loaderMsg.textContent = msg;
  loaderOverlay.classList.remove('hidden');
}

function hideLoader() { loaderOverlay.classList.add('hidden'); }

// ── File selection ────────────────────────────────────────────────
let selectedFile = null;

function setFile(file) {
  selectedFile = file;
  const ext = file.name.split('.').pop().toLowerCase();
  fileTypeIcon.textContent = FILE_ICONS[ext] || '📄';
  fileNameDisp.textContent = file.name;
  fileSizeDisp.textContent = fmtBytes(file.size);
  fileSelected.classList.remove('hidden');
  dropZone.style.display = 'none';
  textInput.value = '';
}

function clearFile() {
  selectedFile = null;
  fileInput.value = '';
  fileSelected.classList.add('hidden');
  dropZone.style.display = '';
}

// Drop Zone
dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') fileInput.click(); });

fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) setFile(fileInput.files[0]);
});

dropZone.addEventListener('dragover', e => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const f = e.dataTransfer.files[0];
  if (f) {
    const ext = f.name.split('.').pop().toLowerCase();
    if (['pdf', 'docx', 'doc', 'txt'].includes(ext)) {
      setFile(f);
    } else {
      showToast('Unsupported file type. Use PDF, DOCX, or TXT.', 'error');
    }
  }
});

clearFileBtn.addEventListener('click', clearFile);

// ── Load Samples ──────────────────────────────────────────────────
async function loadSamples() {
  try {
    const res = await fetch('/api/samples');
    const samples = await res.json();
    samplesChips.innerHTML = '';
    if (!samples.length) {
      samplesChips.innerHTML = '<span class="chip loading-chip">No samples</span>';
      return;
    }
    samples.forEach(s => {
      const chip = document.createElement('button');
      chip.className = 'chip';
      chip.textContent = s.name;
      chip.addEventListener('click', async () => {
        chip.textContent = '⏳ Loading…';
        chip.disabled = true;
        try {
          const r = await fetch(`/api/sample/${encodeURIComponent(s.file)}`);
          const d = await r.json();
          clearFile();
          textInput.value = d.text;
          showToast(`"${s.name}" loaded!`, 'success');
        } catch {
          showToast('Failed to load sample.', 'error');
        } finally {
          chip.textContent = s.name;
          chip.disabled = false;
        }
      });
      samplesChips.appendChild(chip);
    });
  } catch {
    samplesChips.innerHTML = '<span class="chip loading-chip">Unavailable</span>';
  }
}

// ── Analyze ───────────────────────────────────────────────────────
analyzeBtn.addEventListener('click', runAnalysis);

async function runAnalysis() {
  const hasFile = !!selectedFile;
  const hasText = textInput.value.trim().length > 0;

  if (!hasFile && !hasText) {
    showToast('Please upload a file or paste some text first.', 'error');
    return;
  }

  showLoader(hasFile ? `Reading ${selectedFile.name}…` : 'Analyzing text…');
  analyzeBtn.classList.add('loading');

  try {
    let res;
    if (hasFile) {
      const fd = new FormData();
      fd.append('file', selectedFile);
      fd.append('remove_stopwords', swToggle.checked ? 'true' : 'false');
      fd.append('top_n', topNSelect.value);
      res = await fetch('/api/analyze', { method: 'POST', body: fd });
    } else {
      res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: textInput.value,
          remove_stopwords: swToggle.checked,
          top_n: parseInt(topNSelect.value),
        }),
      });
    }

    const data = await res.json();
    if (!res.ok) { showToast(data.error || 'Analysis failed.', 'error'); return; }

    renderResults(data);
    analysisReady = true;
    showToast('Analysis complete!', 'success');

  } catch (err) {
    showToast('Network error: ' + err.message, 'error');
  } finally {
    hideLoader();
    analyzeBtn.classList.remove('loading');
  }
}

// ── Render Results ────────────────────────────────────────────────
function renderResults(data) {
  // Stats
  statTotal.textContent      = fmtNum(data.total_words);
  statFiltered.textContent   = fmtNum(data.filtered_words);
  statUnique.textContent     = fmtNum(data.unique_words);
  statSentences.textContent  = fmtNum(data.sentence_count);
  statReading.textContent    = fmtTime(data.reading_time_sec);
  statDensity.textContent    = data.lexical_density ? (data.lexical_density * 100).toFixed(1) + '%' : '—';
  statAvgLen.textContent     = data.avg_word_length ? data.avg_word_length.toFixed(1) : '—';

  renderBarChart(data.top_words || []);
  renderLetterChart(data.letter_freq || []);
  renderWordTable(data.top_words || []);
}

// ── Bar Chart ─────────────────────────────────────────────────────
function renderBarChart(words) {
  const placeholder = document.getElementById('bar-placeholder');
  const canvas = document.getElementById('bar-chart');

  if (!words.length) return;
  placeholder.classList.add('hidden');
  canvas.classList.remove('hidden');

  const labels  = words.map(w => w.word);
  const counts  = words.map(w => w.count);
  const maxC    = Math.max(...counts);

  // gradient color by rank
  const colors = counts.map((c) => {
    const ratio = c / maxC;
    const h = Math.round(220 + ratio * 40);
    return `hsl(${h}, 80%, ${50 + ratio * 12}%)`;
  });

  if (barChartInstance) barChartInstance.destroy();

  barChartInstance = new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Occurrences',
        data: counts,
        backgroundColor: colors,
        borderRadius: 6,
        borderSkipped: false,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 600, easing: 'easeOutQuart' },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#121828',
          borderColor: 'rgba(99,102,241,0.3)',
          borderWidth: 1,
          titleColor: '#e2e8f0',
          bodyColor: '#8892a4',
          callbacks: {
            label: ctx => ` ${ctx.parsed.x.toLocaleString()} occurrences (${words[ctx.dataIndex].percentage}%)`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: 'rgba(99,102,241,0.07)' },
          ticks: { color: '#4a5568', font: { family: 'JetBrains Mono', size: 11 } },
        },
        y: {
          grid: { display: false },
          ticks: { color: '#8892a4', font: { family: 'JetBrains Mono', size: 12 } },
        },
      },
    },
  });

  // set canvas height dynamically based on word count
  canvas.parentElement.style.minHeight = Math.max(380, words.length * 26 + 40) + 'px';
  canvas.style.height = Math.max(380, words.length * 26 + 40) + 'px';
  if (barChartInstance) barChartInstance.resize();
}

// ── Letter Chart ──────────────────────────────────────────────────
function renderLetterChart(letters) {
  const placeholder = document.getElementById('letter-placeholder');
  const canvas = document.getElementById('letter-chart');

  if (!letters.length) return;
  placeholder.classList.add('hidden');
  canvas.classList.remove('hidden');

  const labels = letters.map(l => l.letter.toUpperCase());
  const pcts   = letters.map(l => l.percentage);

  if (letterChartInstance) letterChartInstance.destroy();

  letterChartInstance = new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Frequency %',
        data: pcts,
        backgroundColor: labels.map((_, i) => `hsl(${190 + i * 6}, 70%, 55%)`),
        borderRadius: 4,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      animation: { duration: 600 },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#121828', borderColor: 'rgba(6,182,212,0.3)', borderWidth: 1,
          titleColor: '#e2e8f0', bodyColor: '#8892a4',
          callbacks: { label: ctx => ` ${ctx.parsed.y.toFixed(2)}% of all letters` },
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#8892a4', font: { family: 'JetBrains Mono', size: 12 } } },
        y: { grid: { color: 'rgba(6,182,212,0.07)' }, ticks: { color: '#4a5568', font: { size: 11 }, callback: v => v + '%' } },
      },
    },
  });
}

// ── Word Table ────────────────────────────────────────────────────
function renderWordTable(words) {
  const placeholder = document.getElementById('table-placeholder');
  const wrap        = document.getElementById('table-wrap');
  const tbody       = document.getElementById('word-table-body');

  if (!words.length) return;
  placeholder.classList.add('hidden');
  wrap.classList.remove('hidden');

  const maxPct = words[0]?.percentage || 1;

  tbody.innerHTML = words.map((w, i) => `
    <tr>
      <td class="rank-cell">${String(i + 1).padStart(2, '0')}</td>
      <td class="word-cell">${w.word}</td>
      <td class="count-cell">${w.count.toLocaleString()}</td>
      <td>
        <div class="pct-bar">
          <div class="pct-track"><div class="pct-fill" style="width:${(w.percentage / maxPct * 100).toFixed(1)}%"></div></div>
          <span class="pct-text">${w.percentage}%</span>
        </div>
      </td>
    </tr>
  `).join('');
}

// ── Tabs ──────────────────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => {
      c.classList.remove('active');
      c.classList.add('hidden');
    });
    tab.classList.add('active');
    const target = document.getElementById(tab.dataset.tab);
    target.classList.remove('hidden');
    target.classList.add('active');

    // Resize charts on tab reveal to fix canvas sizing issues
    if (tab.dataset.tab === 'bar-tab' && barChartInstance) barChartInstance.resize();
    if (tab.dataset.tab === 'letter-tab' && letterChartInstance) letterChartInstance.resize();
  });
});

// ── Word Search ───────────────────────────────────────────────────
searchBtn.addEventListener('click', runSearch);
searchInput.addEventListener('keydown', e => { if (e.key === 'Enter') runSearch(); });

async function runSearch() {
  const word = searchInput.value.trim();
  if (!word) { showToast('Please enter a word to search.', 'error'); return; }
  if (!analysisReady) { showToast('Analyze a document first.', 'error'); return; }

  try {
    const res = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ word }),
    });
    const data = await res.json();
    if (!res.ok) { showToast(data.error || 'Search failed.', 'error'); return; }

    renderSearchResult(data);
    searchResult.classList.remove('hidden');
  } catch (err) {
    showToast('Search error: ' + err.message, 'error');
  }
}

function renderSearchResult(data) {
  if (data.count === 0) {
    searchResult.innerHTML = `
      <div class="search-not-found">
        <span style="font-size:1.5rem">🔍</span><br/>
        "<strong>${data.word}</strong>" was not found in the document.
      </div>`;
    return;
  }

  const snippetsHTML = data.snippets.length
    ? `<p class="snippets-title">Context snippets (up to 10)</p>
       ${data.snippets.map(s => `<div class="snippet">…${s}…</div>`).join('')}`
    : '';

  searchResult.innerHTML = `
    <div class="search-hit">
      <span class="search-word">${data.word}</span>
      <span class="search-count-badge">${data.count.toLocaleString()} occurrence${data.count !== 1 ? 's' : ''}</span>
    </div>
    <p class="search-pct">Represents <strong>${data.percentage}%</strong> of filtered words${data.in_top_words ? ' · included in top words chart' : ''}</p>
    ${snippetsHTML}
  `;
}

// ── Init ──────────────────────────────────────────────────────────
loadSamples();
