# Visual Guide

Design principles for publication-ready visualizations that integrate with Linear Content blog.

> **Skills**: Use `/tufte-design` for design decisions and `/d3js-skill` for implementation patterns.

## Philosophy

Follow Tufte + Terminal-Minimalist aesthetic:

- Every pixel must earn its place
- Data speaks; decoration distracts
- Sort by magnitude; truncate labels (tooltip reveals full)
- Monochrome palette—no color accents
- Sharp edges—no rounded corners
- No shadows or gradients

## Integration Context

Visualizations are embedded in a Quarto blog with existing CSS variables. **Do not define your own variables**—inherit from the host page.

### Available Blog Variables

```css
/* Use these directly - they handle dark mode automatically */
var(--font-mono)      /* Berkeley Mono font stack */
var(--paper)          /* Background: #FAFAF9 light, #1E1D1B dark */
var(--black)          /* Primary: #000000 light, #E6E4DF dark */
var(--mid-gray)       /* Secondary text */
var(--border-color)   /* Structure, dividers, bar tracks */
var(--code-bg)        /* Hover backgrounds */
```

## Design Tokens

Use blog variables, with explicit sizing:

```css
/* Typography - inherit font, set sizes */
font-family: var(--font-mono);
font-size: 14px;           /* Base */
font-size: 12px;           /* Small/labels */
font-size: 1.5rem;         /* Headlines (match blog h1) */
line-height: 1.5;

/* Spacing */
--row-height: 32px;
--section-gap: 2rem;
--column-gap: 2rem;
```

## Output Structure

### HTML Fragment (Not Full Document)

Generate **fragments** that can be included in Quarto, not standalone pages:

```html
<!-- viz/app.html - NO doctype, html, head, or body -->
<main class="viz-main">
  <header class="viz-header">
    <p class="intro">Brief intro paragraph providing context for this study.
    Explain what was tested, why it matters, and what the reader will see below.
    This will be edited by the author.</p>
  </header>

  <section id="content-section">
    <!-- Visualization content -->
  </section>
</main>

<div id="tooltip" class="viz-tooltip"></div>
```

**Rules:**
- **NO title in viz** — Quarto provides `<h1>` via frontmatter
- Instead, provide a 1-2 sentence **intro paragraph** (`.intro`) giving context
- Prefix IDs with descriptive names to avoid conflicts
- Include tooltip div at end
- **Flush-left HTML** — Quarto's markdown parser treats indented HTML as code blocks; no indentation in `app.html`

### CSS Structure

```css
/* viz/style.css - scoped, no globals */

/* Container scope - reset only within viz */
.viz-main *,
.viz-main *::before,
.viz-main *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.viz-main {
  font-family: var(--font-mono);
  font-size: 14px;
  color: var(--black);
  line-height: 1.5;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Dark mode handled automatically via var() cascade */
```

**Forbidden in CSS:**
- `:root { }` definitions
- `* { margin: 0; padding: 0; }` global resets
- `body { }` selectors
- Hardcoded colors (use variables)
- `border-radius` > 0
- `box-shadow`

### JavaScript Structure

```javascript
// viz/main.js

// Data path - configurable from page context
const DATA_PATH = window.VIZ_DATA_PATH || './viz/viz_data.json';

// Wait for DOM
document.addEventListener('DOMContentLoaded', init);

async function init() {
  const data = await d3.json(DATA_PATH);
  // ... render
}
```

**Rules:**
- Data path must work from Quarto page context (`./viz/viz_data.json`)
- Use `DOMContentLoaded` or place script at end with `defer`
- Avoid ID conflicts with common names (use descriptive prefixes)

## Component Patterns

### Bars

```css
.bar {
  background: var(--black);
  border-radius: 0;
  height: 8px;
}

.bar-track {
  background: var(--border-color);
  border-radius: 0;
}
```

### Sparklines

```css
.spark-bar {
  background: var(--black);
  opacity: 0.6;
  border-radius: 0;
}
```

### Tooltips

```css
.viz-tooltip {
  position: fixed;  /* fixed, not absolute—Quarto containers break absolute offsets */
  pointer-events: none;
  background: var(--paper);
  border: 1px solid var(--border-color);
  padding: 12px;
  max-width: 400px;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.15s;
  z-index: 1000;
  /* NO box-shadow, NO border-radius */
}
```

### Expandable Details

```css
.detail-panel {
  border-left: 3px solid var(--black);
  padding-left: 1rem;
  margin: 8px 0;
  background: var(--paper);
}
```

### Interactive Rows

```css
.data-row {
  padding: 8px 0;
  cursor: pointer;
}

.data-row:hover {
  background: var(--code-bg);
}
```

### Links

```css
.viz-main a {
  color: var(--black);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.viz-main a:hover {
  text-decoration-thickness: 2px;
  /* NO color change */
}
```

### Form Controls

```css
.viz-main select {
  font-family: var(--font-mono);
  font-size: 12px;
  padding: 4px 8px;
  border: 1px solid var(--border-color);
  border-radius: 0;
  background: var(--paper);
  color: var(--black);
  cursor: pointer;
}

.viz-main select:focus {
  outline: none;
  border-color: var(--black);
}
```

## Data Emphasis Without Color

Since color accents are forbidden, use:

| Technique | Use Case |
|-----------|----------|
| **Opacity** (0.4-0.6) | Secondary/background data |
| **Bold weight** | Emphasis within text |
| **Border-left** (3px) | Panel/section emphasis |
| **Whitespace** | Group related items |
| **Direct labels** | Instead of legends |
| **Size variation** | Headline stats vs details |

## D3.js Patterns

### Standard Setup

```javascript
const ROW_HEIGHT = 32;
const SECTION_GAP = 32;

// Use CSS variables in JS when needed
const style = getComputedStyle(document.documentElement);
const black = style.getPropertyValue('--black').trim();
```

### Tooltip Pattern

```javascript
const tooltip = d3.select('.viz-tooltip');

selection
  .on('mouseenter', (e, d) => {
    tooltip.style('opacity', 1).html(formatTooltip(d));
  })
  .on('mousemove', (e) => {
    tooltip
      .style('left', (e.clientX + 12) + 'px')
      .style('top', (e.clientY - 12) + 'px');
  })
  .on('mouseleave', () => tooltip.style('opacity', 0));
```

### Transitions

```javascript
// Max 150ms, ease-out
selection.transition()
  .duration(150)
  .ease(d3.easeOut)
  .attr('transform', d => `translate(0, ${d.y})`);
```

## Checklist

Before generating output:

- [ ] HTML is a fragment (no doctype/html/head/body)
- [ ] CSS has no `:root` or global resets
- [ ] All colors use `var(--*)` blog variables
- [ ] No `border-radius` > 0 anywhere
- [ ] No `box-shadow` anywhere
- [ ] No color accents (monochrome only)
- [ ] Links use underline, not color
- [ ] Transitions <= 150ms
- [ ] Data labels direct (no legend lookup)
- [ ] IDs prefixed to avoid conflicts

## File Output Structure

Each study should produce a complete post folder:

```
YYYYMMDD_study-slug/
├── index.qmd      # Quarto wrapper (see template below)
└── viz/
    ├── app.html       # HTML fragment (no doctype/head/body)
    ├── style.css      # Scoped CSS (no :root, no global reset)
    ├── main.js        # D3 visualization
    └── viz_data.json  # Data file
```

### index.qmd Template

Generate this file with study-specific values for title, description, date, and categories:

```yaml
---
title: "Study Title Here"
description: "One-sentence description of what this study shows."
date: "YYYY-MM-DD"
categories: [experiments, llm]
resources:
  - "viz/viz_data.json"
format:
  html:
    page-layout: full
    toc: false
---

<div class="viz-container">
{{< include viz/app.html >}}
</div>

<link rel="stylesheet" href="viz/style.css">
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>window.VIZ_DATA_PATH = './viz/viz_data.json';</script>
<script src="viz/main.js" defer></script>
```

The folder name should follow the pattern `YYYYMMDD_slug` (e.g., `20260103_llm-resampling`).

## Quarto Integration

The generated `index.qmd` handles all integration. Key points:

- CSS must not conflict with blog styles (use `.viz-main` scoping)
- JS must read `window.VIZ_DATA_PATH` for data location
- Dark mode works automatically via CSS variable cascade
- The `resources` field ensures `viz_data.json` is copied to build output

---

## Migration Guide

For existing visualizations using the old format, follow these steps.

### 1. HTML: Convert to Fragment

**Before** (`index.html`):
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main>
    <header>
      <h1>Study Title</h1>
      ...
    </header>
    ...
  </main>
  <div id="tooltip"></div>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <script src="main.js"></script>
</body>
</html>
```

**After** (`app.html`):
```html
<main class="viz-main">
  <header class="viz-header">
    <p class="intro">Context paragraph explaining the study...</p>
  </header>
  ...
</main>
<div id="tooltip" class="viz-tooltip"></div>
```

**Changes:**
- Remove doctype, html, head, body tags
- Remove font imports (blog provides Berkeley Mono)
- Remove script/link tags (Quarto wrapper handles these)
- Add `.viz-main` class to `<main>`
- Add `.viz-tooltip` class to tooltip
- **Remove title entirely** — replace with intro paragraph (Quarto provides h1 from frontmatter)

### 2. CSS: Remove Globals, Use Variables

**Delete entirely:**
```css
/* DELETE - :root definitions */
:root {
  --font-mono: "IBM Plex Mono", monospace;
  --accent: #2563eb;
  ...
}

/* DELETE - global reset */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* DELETE - body selector */
body {
  font-family: var(--font-mono);
  ...
}
```

**Add at top:**
```css
/* Scoped reset */
.viz-main *,
.viz-main *::before,
.viz-main *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.viz-main {
  font-family: var(--font-mono);
  font-size: 14px;
  color: var(--black);
  line-height: 1.5;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}
```

### 3. CSS: Color Replacements

Find and replace throughout:

| Old | New |
|-----|-----|
| `var(--font-mono)` with IBM Plex | `var(--font-mono)` (now Berkeley) |
| `var(--text-primary)` or `#1a1a1a` | `var(--black)` |
| `var(--text-secondary)` or `#666` | `var(--mid-gray)` |
| `var(--accent)` or `#2563eb` | `var(--black)` |
| `var(--accent-hover)` or `#1d4ed8` | `var(--black)` |
| `var(--structure)` or `#d1d5db` | `var(--border-color)` |
| `var(--bg)` or `#ffffff` | `var(--paper)` |
| `var(--bar-empty)` or `#e5e7eb` | `var(--border-color)` |
| `#f9fafb` (hover bg) | `var(--code-bg)` |

### 4. CSS: Remove Decorations

**Border radius** — set all to 0:
```css
/* Before */
.paper-bar { border-radius: 2px; }
.spark-bar { border-radius: 1px 1px 0 0; }
#tooltip { border-radius: 4px; }
select { border-radius: 4px; }

/* After */
.paper-bar { border-radius: 0; }
.spark-bar { border-radius: 0; }
#tooltip { border-radius: 0; }  /* or .viz-tooltip */
select { border-radius: 0; }
```

**Shadows** — remove entirely:
```css
/* Before */
#tooltip {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* After */
.viz-tooltip {
  /* no box-shadow */
}
```

### 5. CSS: Fix Transitions

Reduce all transitions to 150ms max:

```css
/* Before */
.paper-bar { transition: width 0.3s; }
@keyframes expand { /* 200ms animation */ }

/* After */
.paper-bar { transition: width 0.15s ease-out; }
@keyframes expand {
  from { opacity: 0; }
  to { opacity: 1; }
}
/* Or remove animation entirely */
```

### 6. CSS: Fix Links

```css
/* Before */
.arxiv-link {
  color: var(--accent);
  text-decoration: none;
}
.arxiv-link:hover {
  text-decoration: underline;
}

/* After */
.viz-main a {
  color: var(--black);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.viz-main a:hover {
  text-decoration-thickness: 2px;
}
```

### 7. JavaScript: Configurable Data Path

```javascript
/* Before */
const DATA_PATH = '/data/study_name/viz_data.json';

/* After */
const DATA_PATH = window.VIZ_DATA_PATH || './viz/viz_data.json';
```

### 8. Selector Scoping

Prefix selectors that might conflict:

```css
/* Before - could conflict with Quarto */
header { ... }
main { ... }
h2 { ... }
select { ... }

/* After - scoped to viz */
.viz-main header, .viz-header { ... }
.viz-main { ... }
.viz-main h2 { ... }
.viz-main select { ... }
```

### Migration Checklist

For each existing visualization:

- [ ] **HTML**
  - [ ] Remove doctype, html, head, body
  - [ ] Remove font imports
  - [ ] Remove script/link tags
  - [ ] Add `.viz-main` to main element
  - [ ] Add `.viz-tooltip` to tooltip
  - [ ] Remove title, replace with `.intro` paragraph
  - [ ] Rename `index.html` → `app.html`

- [ ] **CSS**
  - [ ] Delete `:root { }` block
  - [ ] Delete `* { }` global reset
  - [ ] Delete `body { }` selector
  - [ ] Add scoped `.viz-main *` reset
  - [ ] Add `.viz-main` container styles
  - [ ] Replace all color values with blog variables
  - [ ] Set all `border-radius` to 0
  - [ ] Remove all `box-shadow`
  - [ ] Reduce transitions to <= 150ms
  - [ ] Fix link styles (underline, not color)
  - [ ] Scope generic selectors

- [ ] **JavaScript**
  - [ ] Use configurable `window.VIZ_DATA_PATH`
  - [ ] Verify `DOMContentLoaded` or `defer`

- [ ] **Test** (standalone, before handoff)
  - [ ] Create test harness HTML (see below)
  - [ ] Renders correctly in browser
  - [ ] Dark mode works (test harness provides variables)
  - [ ] All interactions functional
  - [ ] No console errors

### Standalone Test Harness

To test without blog access, create a temporary `test.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Viz Test</title>
  <style>
    /* Simulate blog CSS variables */
    :root {
      --font-mono: ui-monospace, 'SF Mono', monospace;
      --paper: #FAFAF9;
      --black: #000000;
      --mid-gray: #666666;
      --border-color: #CCCCCC;
      --code-bg: #F5F5F3;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --paper: #1E1D1B;
        --black: #E6E4DF;
        --mid-gray: #B8B6B0;
        --border-color: #3D3B37;
        --code-bg: #252422;
      }
    }
    body {
      background: var(--paper);
      margin: 0;
      padding: 2rem;
    }
  </style>
  <link rel="stylesheet" href="viz/style.css">
</head>
<body>
  <div class="viz-container">
    <!-- Paste app.html content here, or use JS to fetch it -->
  </div>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <script>window.VIZ_DATA_PATH = './viz/viz_data.json';</script>
  <script src="viz/main.js" defer></script>
</body>
</html>
```

Toggle system dark mode to verify colors adapt correctly. Delete `test.html` before handoff.
