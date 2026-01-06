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

// Render dynamic conclusion based on data
function renderConclusion(summary, topX) {
  const overlap = summary.single_in_consensus;
  const total = summary.papers_per_run;
  const similarity = Math.round(summary.avg_run_similarity * 100);
  const topPct = topX[0]?.percentage || 0;
  const unique = summary.unique_papers_selected;

  let text;
  if (unique <= 10 && similarity >= 50) {
    // High: best
    text = `Single-shot is enough. The model locks onto ${unique} papers with ${Math.round(topPct)}% top agreement—and the picks match the criteria (surprising findings, not benchmark increments).`;
  } else if (overlap >= 2 && similarity >= 45) {
    // Medium: good
    text = `Single-shot mostly works. Slightly more exploration (${unique} papers), similar top picks to higher effort. ${overlap}/${total} single-shot picks land in consensus.`;
  } else if (overlap >= 1 && similarity >= 20) {
    // Low: partial
    text = `Single-shot is unreliable. The model wanders across ${unique} papers with only ${similarity}% consistency—some strong picks buried in noise. Multi-run voting helps surface them.`;
  } else {
    // Minimal: noise
    text = `Don't trust this. ${unique} scattered papers, ${similarity}% consistency, and single-shot picks are essentially random (${overlap}/${total} consensus overlap). Even multi-run struggles to find signal.`;
  }

  d3.select('#sel-conclusion .conclusion').text(text);
}

// Render headline stats as sparkline only
function renderHeadlineStats(summary, runSimilarities) {
  const container = d3.select('#sel-stats');
  container.html('');

  const simRow = container.append('div').attr('class', 'similarity-row');
  simRow.append('span')
    .attr('class', 'similarity-label')
    .text(`Run-to-run consistency: ${Math.round(summary.avg_run_similarity * 100)}%`);

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
function renderComparison(singleShot, topX, papersPerRun) {
  const singleShotCodes = new Set(singleShot.map(p => p.arxiv_code));
  const topXCodes = new Set(topX.map(p => p.arxiv_code));

  // Single-shot column
  const singleColumn = d3.select('#sel-single-column');
  singleColumn.select('.count').text(`(${singleShot.length})`);
  const singleList = singleColumn.select('.paper-list');
  singleList.html('');
  singleShot.forEach(paper => {
    renderPaperRow(singleList, paper, { showOverlap: true, singleShotCodes, consensusCodes: topXCodes });
  });

  // Top X column
  const topXColumn = d3.select('#sel-consensus-column');
  topXColumn.select('h3').html(`Top ${papersPerRun} by frequency <span class="threshold"></span>`);
  const aboveCount = topX.filter(p => p.above_threshold).length;
  topXColumn.select('.threshold').text(`(${aboveCount} above 50%)`);
  topXColumn.select('.count').text(`(${topX.length})`);
  const topXList = topXColumn.select('.paper-list');
  topXList.html('');
  topX.forEach(paper => {
    renderPaperRow(topXList, paper, { showOverlap: true, singleShotCodes, consensusCodes: topXCodes });
  });
}

// Render frequency list
function renderFrequencyList(papers, sortBy = 'frequency') {
  const singleShotCodes = new Set(data.single_shot.map(p => p.arxiv_code));
  const topXCodes = new Set(data.top_x.map(p => p.arxiv_code));

  const sorted = [...papers].sort((a, b) => {
    if (sortBy === 'frequency') return b.frequency - a.frequency;
    return a.title.localeCompare(b.title);
  });

  const section = d3.select('#sel-frequency');
  section.select('.count').text(`(${papers.length} papers)`);

  const list = d3.select('#sel-freq-list');
  list.html('');

  sorted.forEach(paper => {
    renderPaperRow(list, paper, { showMarkers: true, singleShotCodes, consensusCodes: topXCodes });
  });
}

// Populate model dropdown from index
function populateModelDropdown() {
  const select = d3.select('#sel-model');
  select.html('');

  const effortOrder = ['minimal', 'low', 'medium', 'high'];
  const sorted = [...modelsIndex.models].sort((a, b) => {
    const aIdx = effortOrder.findIndex(e => a.id.endsWith(e));
    const bIdx = effortOrder.findIndex(e => b.id.endsWith(e));
    return aIdx - bIdx;
  });

  sorted.forEach(model => {
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

  renderConclusion(data.summary, data.top_x);
  renderHeadlineStats(data.summary, data.run_similarities);
  renderComparison(data.single_shot, data.top_x, data.summary.papers_per_run);
  renderFrequencyList(data.frequency_distribution);
  d3.select('#legend-top-x').text(data.summary.papers_per_run);
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
