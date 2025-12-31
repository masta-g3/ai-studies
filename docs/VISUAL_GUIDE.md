# Visual Guide

Design principles for publication-ready visualizations.

> **Skills**: Use `/tufte-design` for design decisions and `/d3js-skill` for implementation patterns.

## Philosophy

Follow Tufte: maximize data, minimize ink.

- Every pixel must earn its place
- Data speaks; decoration distracts
- Comparison should be effortless
- Reveal structure through whitespace, not lines

## Design Tokens

```css
/* Typography */
--font-mono: "IBM Plex Mono", monospace;
--font-size-base: 14px;
--font-size-small: 12px;

/* Colors */
--text-primary: #1a1a1a;
--text-secondary: #666;
--accent: #2563eb;          /* Blue-600 */
--accent-hover: #1d4ed8;    /* Blue-700 */
--structure: #d1d5db;       /* Gray-300 */
--bg: #ffffff;
```

## Principles

### Data First
- Labels are data—show them directly, not in legends
- Sort by magnitude (largest first) unless order is meaningful
- Truncate gracefully with `…`, show full on hover

### Minimal Structure
- No gridlines (or barely visible if essential)
- No borders or boxes
- Light gray for structural elements (lines, icons)
- Black for data (labels, values)

### Single Accent
- One color for emphasis (bars, highlights)
- Hover state: slightly darker shade
- Never rainbow; never gradients

### Whitespace as Hierarchy
- Indentation encodes nesting
- Vertical spacing groups related items
- No need for tree lines when indent is clear

## D3.js Patterns

### Standard Setup
```javascript
const ROW_HEIGHT = 28;
const INDENT = 28;

const svg = d3.select('#chart')
  .attr('width', width)
  .attr('height', height);
```

### Tooltip
```javascript
const tooltip = d3.select('#tooltip');

selection
  .on('mouseenter', (e, d) => {
    tooltip.style('opacity', 1).html(d.description);
  })
  .on('mousemove', (e) => {
    tooltip
      .style('left', (e.pageX + 12) + 'px')
      .style('top', (e.pageY - 12) + 'px');
  })
  .on('mouseleave', () => tooltip.style('opacity', 0));
```

### Transitions
```javascript
selection.transition()
  .duration(300)
  .attr('transform', d => `translate(0, ${d.y})`);
```

## Checklist

Before publishing:

- [ ] Can anything be removed without losing information?
- [ ] Is data sorted meaningfully?
- [ ] Are labels direct (no legend lookup)?
- [ ] Single accent color only?
- [ ] Tooltips for truncated/detailed content?
- [ ] Transitions smooth (200-300ms)?
