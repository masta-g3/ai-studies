// Paper Selection Experiment Visualization

const MODELS_PATH = window.VIZ_MODELS_PATH || './viz/models.json';
const DATA_BASE_PATH = window.VIZ_DATA_BASE || './viz/';

let modelsIndex = null;
let data = null;
let expandedPaper = null;

// Tooltip
const tooltip = d3.select('#sel-tooltip');

function showTooltip(event, paper) {
  const abstract = paper.abstract.length > 200
    ? paper.abstract.slice(0, 200) + '...'
    : paper.abstract;

  const category = paper.categories?.[0] || 'unknown';
  const pct = paper.percentage ?? paper.multi_run_percentage ?? 0;
  const freq = paper.frequency ?? paper.multi_run_frequency ?? 0;

  tooltip.html(`
    <div class="tooltip-title">${paper.title}</div>
    <div class="tooltip-meta">${category} · ${pct}% (${freq}/${data.summary.total_runs} runs)</div>
    <div class="tooltip-abstract">${abstract}</div>
  `);

  tooltip.classed('visible', true);
  positionTooltip(event);
}

function positionTooltip(event) {
  tooltip
    .style('left', (event.clientX + 12) + 'px')
    .style('top', (event.clientY - 12) + 'px');
}

function hideTooltip() {
  tooltip.classed('visible', false);
}

// Render headline stats as prose sentence (Tufte: integrate verbal and statistical)
function renderHeadlineStats(summary, runSimilarities) {
  const container = d3.select('#sel-stats');
  container.html('');

  // Prose sentence instead of stat chips
  container.append('p')
    .attr('class', 'stats-sentence')
    .html(`Across <strong>${summary.total_runs}</strong> runs selecting <strong>${summary.papers_per_run}</strong> papers each from a pool of <strong>${summary.pool_size}</strong>, the LLM chose <strong>${summary.unique_papers_selected}</strong> unique papers. <strong>${summary.consensus_count}</strong> appeared in &gt;50% of runs (consensus). Only <strong>${summary.single_in_consensus}</strong> of the single-shot selection overlaps with consensus.`);

  // Keep sparkline for run similarity
  const simRow = container.append('div').attr('class', 'similarity-row');
  simRow.append('span')
    .attr('class', 'similarity-label')
    .text(`Run similarity: ${Math.round(summary.avg_run_similarity * 100)}%`);

  const sparkline = simRow.append('div').attr('class', 'sparkline');
  const maxJaccard = d3.max(runSimilarities, d => d.jaccard) || 1;

  runSimilarities.forEach(d => {
    sparkline.append('div')
      .attr('class', 'spark-bar')
      .style('height', `${(d.jaccard / maxJaccard) * 16}px`);
  });
}

// Render paper row
function renderPaperRow(container, paper, options = {}) {
  const { showMarkers = false, singleShotCodes = new Set(), consensusCodes = new Set() } = options;

  const pct = paper.percentage ?? paper.multi_run_percentage ?? 0;
  const title = paper.title.length > 50 ? paper.title.slice(0, 50) + '...' : paper.title;
  const belowThreshold = paper.above_threshold === false;

  const row = container.append('div')
    .attr('class', 'paper-row' + (belowThreshold ? ' below-threshold' : ''))
    .attr('data-arxiv', paper.arxiv_code)
    .on('mouseenter', (event) => showTooltip(event, paper))
    .on('mousemove', positionTooltip)
    .on('mouseleave', hideTooltip)
    .on('click', () => toggleDetail(container, paper, options));

  row.append('div').attr('class', 'paper-title').text(title);
  row.append('div').attr('class', 'paper-pct').text(`${Math.round(pct)}%`);

  const barContainer = row.append('div').attr('class', 'paper-bar-container');
  barContainer.append('div')
    .attr('class', 'paper-bar')
    .style('width', `${pct}%`);

  if (showMarkers) {
    const markers = row.append('div').attr('class', 'paper-markers');
    const inConsensus = consensusCodes.has(paper.arxiv_code);
    const inSingle = singleShotCodes.has(paper.arxiv_code);

    if (inConsensus) markers.append('span').attr('class', 'marker-consensus').text('*');
    if (inSingle) markers.append('span').attr('class', 'marker-single').text('·');
  } else if (options.showOverlap) {
    const markers = row.append('div').attr('class', 'paper-markers');
    const isOverlap = singleShotCodes.has(paper.arxiv_code) && consensusCodes.has(paper.arxiv_code);
    if (isOverlap) markers.append('span').attr('class', 'marker-overlap').text('·');
  }
}

// Toggle paper detail
function toggleDetail(container, paper, options) {
  const arxivCode = paper.arxiv_code;
  const existingDetail = container.select(`.paper-detail[data-arxiv="${arxivCode}"]`);

  if (!existingDetail.empty()) {
    existingDetail.remove();
    expandedPaper = null;
    return;
  }

  // Remove any other expanded detail
  d3.selectAll('.paper-detail').remove();
  expandedPaper = arxivCode;

  const row = container.select(`.paper-row[data-arxiv="${arxivCode}"]`);
  const pct = paper.percentage ?? paper.multi_run_percentage ?? 0;
  const freq = paper.frequency ?? paper.multi_run_frequency ?? 0;
  const category = paper.categories?.[0] || 'unknown';

  const detail = container.insert('div', `.paper-row[data-arxiv="${arxivCode}"] + *`)
    .attr('class', 'paper-detail')
    .attr('data-arxiv', arxivCode);

  detail.append('div').attr('class', 'detail-title').text(paper.title);
  detail.append('div').attr('class', 'detail-meta').text(`${category} · ${pct}% (${freq}/${data.summary.total_runs} runs)`);

  const abstractSection = detail.append('div').attr('class', 'detail-section');
  abstractSection.append('div').attr('class', 'detail-label').text('Abstract');
  abstractSection.append('div').attr('class', 'detail-abstract').text(paper.abstract);

  // Reasoning(s)
  const reasonings = paper.reasonings || (paper.reasoning ? [paper.reasoning] : []);
  if (reasonings.length > 0) {
    const reasoningSection = detail.append('div').attr('class', 'detail-section');
    reasoningSection.append('div').attr('class', 'detail-label').text('LLM Reasoning');
    const ul = reasoningSection.append('ul').attr('class', 'detail-reasoning');
    // Show unique reasonings
    const unique = [...new Set(reasonings)];
    unique.slice(0, 5).forEach(r => {
      ul.append('li').text(r);
    });
    if (unique.length > 5) {
      ul.append('li').style('color', 'var(--mid-gray)').text(`... and ${unique.length - 5} more`);
    }
  }

  detail.append('a')
    .attr('class', 'arxiv-link')
    .attr('href', `https://arxiv.org/abs/${arxivCode}`)
    .attr('target', '_blank')
    .text('View on arXiv');
}

// Render comparison section
function renderComparison(singleShot, top5, consensusCount) {
  const singleShotCodes = new Set(singleShot.map(p => p.arxiv_code));
  const top5Codes = new Set(top5.map(p => p.arxiv_code));

  // Single-shot column
  const singleColumn = d3.select('#sel-single-column');
  singleColumn.select('.count').text(`(${singleShot.length})`);
  const singleList = singleColumn.select('.paper-list');
  singleList.html('');
  singleShot.forEach(paper => {
    renderPaperRow(singleList, paper, { showOverlap: true, singleShotCodes, consensusCodes: top5Codes });
  });

  // Top 5 column (was consensus)
  const top5Column = d3.select('#sel-consensus-column');
  const aboveCount = top5.filter(p => p.above_threshold).length;
  top5Column.select('.threshold').text(`(${aboveCount} above 50%)`);
  top5Column.select('.count').text(`(${top5.length})`);
  const top5List = top5Column.select('.paper-list');
  top5List.html('');
  top5.forEach(paper => {
    renderPaperRow(top5List, paper, { showOverlap: true, singleShotCodes, consensusCodes: top5Codes });
  });
}

// Render frequency list
function renderFrequencyList(papers, sortBy = 'frequency') {
  const singleShotCodes = new Set(data.single_shot.map(p => p.arxiv_code));
  const top5Codes = new Set(data.top_5.map(p => p.arxiv_code));

  const sorted = [...papers].sort((a, b) => {
    if (sortBy === 'frequency') return b.frequency - a.frequency;
    return a.title.localeCompare(b.title);
  });

  const section = d3.select('#sel-frequency');
  section.select('.count').text(`(${papers.length} papers)`);

  const list = d3.select('#sel-freq-list');
  list.html('');

  sorted.forEach(paper => {
    renderPaperRow(list, paper, { showMarkers: true, singleShotCodes, consensusCodes: top5Codes });
  });
}

// Populate model dropdown from index
function populateModelDropdown() {
  const select = d3.select('#sel-model');
  select.html('');

  modelsIndex.models.forEach(model => {
    select.append('option')
      .attr('value', model.id)
      .text(model.name);
  });

  select.property('value', modelsIndex.default);
}

// Load model data and render
async function loadModelData(modelId) {
  const model = modelsIndex.models.find(m => m.id === modelId);
  if (!model) return;

  const dataPath = DATA_BASE_PATH + model.file;
  data = await d3.json(dataPath);

  renderHeadlineStats(data.summary, data.run_similarities);
  renderComparison(data.single_shot, data.top_5, data.summary.consensus_count);
  renderFrequencyList(data.frequency_distribution);
}

// Setup event handlers
function setupHandlers() {
  // Collapsible frequency section
  d3.select('#sel-frequency h3').on('click', function(event) {
    if (event.target.tagName === 'SELECT') return;
    const section = d3.select('#sel-frequency');
    const isCollapsed = section.classed('collapsed');
    section.classed('collapsed', !isCollapsed);
    d3.select('#sel-freq-list').classed('hidden', !isCollapsed);
  });

  // Sort select
  d3.select('#sel-sort').on('change', function() {
    renderFrequencyList(data.frequency_distribution, this.value);
  });

  // Model select
  d3.select('#sel-model').on('change', function() {
    loadModelData(this.value);
  });
}

// Load and render
async function init() {
  try {
    modelsIndex = await d3.json(MODELS_PATH);
  } catch (e) {
    d3.select('.viz-main').html(`<p>Error loading models index at ${MODELS_PATH}</p>`);
    return;
  }

  populateModelDropdown();
  setupHandlers();
  await loadModelData(modelsIndex.default);
}

document.addEventListener('DOMContentLoaded', init);
