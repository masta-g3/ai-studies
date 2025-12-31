// Constants
const ROW_HEIGHT = 28;
const INDENT = 28;
const LABEL_AREA_WIDTH = 580;  // Wide label area for full use of space
const LABEL_PAD = 20;          // Padding between label end and bar start
const BAR_MAX_WIDTH = 180;
const LABEL_X = 20;

// State
let root = null;
let barScale = null;
let svg = null;
let tooltip = null;

// File list
const files = [
  'hierarchy_reasoning_models.json',
  'hierarchy_agentic_systems.json',
  'hierarchy_model_compression.json',
  'hierarchy_multimodal_integration.json'
];

// Data transformation
function transformData(json) {
  const children = json.subcategories.map(sub => ({
    name: sub.name,
    description: sub.description,
    paper_count: sub.paper_count,
    papers: sub.papers,
    children: sub.children?.map(child => ({
      name: child.name,
      description: child.description,
      paper_count: child.paper_count,
      papers: child.papers
    }))
  }));

  if (json.unassigned?.length > 0) {
    children.push({
      name: "Unassigned",
      description: "Papers not fitting any subcategory",
      paper_count: json.unassigned.length,
      papers: json.unassigned
    });
  }

  return {
    name: json.category,
    description: `${json.subcategories.length} subcategories`,
    paper_count: children.reduce((sum, c) => sum + c.paper_count, 0),
    children
  };
}

// Layout calculation
function computeLayout(node) {
  let y = 0;

  node.eachBefore(n => {
    const parentVisible = !n.parent || n.parent._visible;
    const parentExpanded = !n.parent || !n.parent._collapsed;
    n._visible = parentVisible && parentExpanded;

    if (n._visible) {
      n.x = n.depth * INDENT;
      n.y = y;
      y += ROW_HEIGHT;
    }
  });

  return node;
}

// Render the tree
function render() {
  const nodes = root.descendants().filter(d => d._visible);

  // Update SVG height
  const height = nodes.length * ROW_HEIGHT + 40;
  svg.attr('height', height);

  const rows = svg.selectAll('g.row')
    .data(nodes, d => d.id);

  // EXIT
  rows.exit()
    .transition().duration(200)
    .style('opacity', 0)
    .remove();

  // ENTER
  const enter = rows.enter()
    .append('g')
    .attr('class', 'row')
    .style('opacity', 0);

  enter.append('text')
    .attr('class', 'toggle')
    .attr('dy', '0.35em');

  enter.append('text')
    .attr('class', 'label')
    .attr('dy', '0.35em');

  enter.append('rect')
    .attr('class', 'bar')
    .attr('y', -8)
    .attr('height', 16);

  enter.append('text')
    .attr('class', 'count')
    .attr('dy', '0.35em');

  // UPDATE (merge enter + existing)
  const update = enter.merge(rows);

  update.transition().duration(300)
    .attr('transform', d => `translate(0, ${d.y + 20})`)
    .style('opacity', 1);

  // Toggle icon
  update.select('.toggle')
    .attr('x', d => d.x)
    .text(d => {
      if (!d.children) return '';
      return d._collapsed ? '▶' : '▼';
    })
    .on('click', toggle);

  // Label - truncate based on available space after indent, with padding
  update.select('.label')
    .attr('x', d => d.x + LABEL_X)
    .text(d => {
      const availableWidth = LABEL_AREA_WIDTH - d.x - LABEL_X - LABEL_PAD;
      const maxChars = Math.floor(availableWidth / 8.5);  // ~8.5px per char in mono
      return truncate(d.data.name, maxChars);
    });

  // Bar - position after label area
  const barX = LABEL_AREA_WIDTH + LABEL_PAD;
  update.select('.bar')
    .attr('x', barX)
    .transition().duration(300)
    .attr('width', d => barScale(d.data.paper_count));

  // Count
  update.select('.count')
    .attr('x', d => barX + barScale(d.data.paper_count) + 10)
    .text(d => d.data.paper_count);

  // Tooltip events
  update
    .on('mouseenter', showTooltip)
    .on('mousemove', moveTooltip)
    .on('mouseleave', hideTooltip);
}

// Toggle collapse/expand
function toggle(event, d) {
  event.stopPropagation();
  if (d.children) {
    d._collapsed = !d._collapsed;
  }
  computeLayout(root);
  render();
}

// Expand all nodes
function expandAll() {
  root.descendants().forEach(d => d._collapsed = false);
  computeLayout(root);
  render();
}

// Collapse all except root
function collapseAll() {
  root.descendants().forEach(d => d._collapsed = d.depth > 0);
  computeLayout(root);
  render();
}

// Tooltip functions
function showTooltip(event, d) {
  if (d.data.description) {
    tooltip
      .style('opacity', 1)
      .html(d.data.description);
  }
}

function moveTooltip(event) {
  tooltip
    .style('left', (event.pageX + 12) + 'px')
    .style('top', (event.pageY - 12) + 'px');
}

function hideTooltip() {
  tooltip.style('opacity', 0);
}

// Utility: truncate long strings
function truncate(str, maxLen) {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen - 1) + '…';
}

// Load hierarchy file
async function loadFile(filename) {
  try {
    const json = await d3.json(`../../../data/20251230_granularity/${filename}`);
    root = d3.hierarchy(transformData(json));
    // Sort children by paper_count descending at each level
    root.sort((a, b) => b.data.paper_count - a.data.paper_count);

    let nodeId = 0;
    root.descendants().forEach(d => {
      d.id = nodeId++;
      d._collapsed = d.depth > 0;
    });

    barScale = d3.scaleLinear()
      .domain([0, d3.max(root.descendants(), d => d.data.paper_count)])
      .range([0, BAR_MAX_WIDTH]);

    svg.selectAll('*').remove();
    computeLayout(root);
    render();
  } catch (err) {
    console.error('Failed to load:', filename, err);
  }
}

// Setup file selector
function setupFileSelector() {
  const select = d3.select('#file-select');

  select.selectAll('option')
    .data(files)
    .join('option')
    .text(d => d.replace('hierarchy_', '').replace('.json', '').replace(/_/g, ' '))
    .attr('value', d => d);

  select.on('change', function() {
    loadFile(this.value);
  });
}

// Setup controls
function setupControls() {
  d3.select('#expand-all').on('click', expandAll);
  d3.select('#collapse-all').on('click', collapseAll);
}

// Main
function main() {
  svg = d3.select('#tree')
    .attr('width', LABEL_AREA_WIDTH + LABEL_PAD + BAR_MAX_WIDTH + 80);

  tooltip = d3.select('#tooltip');

  setupFileSelector();
  setupControls();
  loadFile(files[0]);
}

main();
