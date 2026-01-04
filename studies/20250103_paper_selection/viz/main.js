// Paper Selection Experiment Visualization

const DATA_PATH = '/data/20250103_paper_selection/viz_data.json';

let data = null;
let expandedPaper = null;

// Tooltip
const tooltip = d3.select('#tooltip');

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
    .style('left', (event.pageX + 12) + 'px')
    .style('top', (event.pageY - 12) + 'px');
}

function hideTooltip() {
  tooltip.classed('visible', false);
}

// Render headline stats
function renderHeadlineStats(summary, runSimilarities) {
  const container = d3.select('#headline-stats');

  // Stats row
  const statsRow = container.append('div').attr('class', 'stats-row');

  const stats = [
    { value: summary.total_runs, label: 'runs' },
    { value: summary.unique_papers_selected, label: 'unique' },
    { value: summary.consensus_count, label: 'consensus' },
    { value: `${summary.single_in_consensus}/${summary.papers_per_run}`, label: 'overlap' },
  ];

  stats.forEach((s, i) => {
    if (i > 0) {
      statsRow.append('span').attr('class', 'stat-separator').text('·');
    }
    const stat = statsRow.append('div').attr('class', 'stat');
    stat.append('span').attr('class', 'stat-value').text(s.value);
    stat.append('span').attr('class', 'stat-label').text(s.label);
  });

  // Similarity row with sparkline
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

  const row = container.append('div')
    .attr('class', 'paper-row')
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

    if (inConsensus) markers.append('span').attr('class', 'marker-consensus').text('★');
    if (inSingle) markers.append('span').attr('class', 'marker-single').text('●');
  } else if (options.showOverlap) {
    const markers = row.append('div').attr('class', 'paper-markers');
    const isOverlap = singleShotCodes.has(paper.arxiv_code) && consensusCodes.has(paper.arxiv_code);
    if (isOverlap) markers.append('span').attr('class', 'marker-overlap').text('●');
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
      ul.append('li').style('color', 'var(--text-secondary)').text(`... and ${unique.length - 5} more`);
    }
  }

  detail.append('a')
    .attr('class', 'arxiv-link')
    .attr('href', `https://arxiv.org/abs/${arxivCode}`)
    .attr('target', '_blank')
    .text('→ View on arXiv');
}

// Render comparison section
function renderComparison(singleShot, consensus) {
  const singleShotCodes = new Set(singleShot.map(p => p.arxiv_code));
  const consensusCodes = new Set(consensus.map(p => p.arxiv_code));

  // Single-shot column
  const singleColumn = d3.select('#single-shot-column');
  singleColumn.select('.count').text(`(${singleShot.length})`);
  const singleList = singleColumn.select('.paper-list');
  singleShot.forEach(paper => {
    renderPaperRow(singleList, paper, { showOverlap: true, singleShotCodes, consensusCodes });
  });

  // Consensus column
  const consensusColumn = d3.select('#consensus-column');
  consensusColumn.select('.count').text(`(${consensus.length})`);
  const consensusList = consensusColumn.select('.paper-list');
  consensus.forEach(paper => {
    renderPaperRow(consensusList, paper, { showOverlap: true, singleShotCodes, consensusCodes });
  });
}

// Render frequency list
function renderFrequencyList(papers, sortBy = 'frequency') {
  const singleShotCodes = new Set(data.single_shot.map(p => p.arxiv_code));
  const consensusCodes = new Set(data.consensus.map(p => p.arxiv_code));

  const sorted = [...papers].sort((a, b) => {
    if (sortBy === 'frequency') return b.frequency - a.frequency;
    return a.title.localeCompare(b.title);
  });

  const section = d3.select('#frequency-section');
  section.select('.count').text(`(${papers.length} papers)`);

  const list = d3.select('#frequency-list');
  list.html('');

  sorted.forEach(paper => {
    renderPaperRow(list, paper, { showMarkers: true, singleShotCodes, consensusCodes });
  });
}

// Setup event handlers
function setupHandlers() {
  // Collapsible frequency section
  d3.select('#frequency-section h2').on('click', function(event) {
    if (event.target.tagName === 'SELECT') return;
    const section = d3.select('#frequency-section');
    const isCollapsed = section.classed('collapsed');
    section.classed('collapsed', !isCollapsed);
    d3.select('#frequency-list').classed('hidden', !isCollapsed);
  });

  // Sort select
  d3.select('#sort-select').on('change', function() {
    renderFrequencyList(data.frequency_distribution, this.value);
  });
}

// Load and render
async function init() {
  try {
    data = await d3.json(DATA_PATH);
  } catch (e) {
    console.error('Failed to load data:', e);
    d3.select('main').html(`<p>Error loading data. Make sure viz_data.json exists at ${DATA_PATH}</p>`);
    return;
  }

  renderHeadlineStats(data.summary, data.run_similarities);
  renderComparison(data.single_shot, data.consensus);
  renderFrequencyList(data.frequency_distribution);
  setupHandlers();
}

init();
