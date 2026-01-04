# viz-migrate-001: Paper Selection Viz Migration

**Status**: Complete
**Scope**: Migrate `studies/20250103_paper_selection/viz/` to new VISUAL_GUIDE.md format

## Summary

Migrate the paper selection visualization from standalone HTML/CSS/JS to blog-embeddable fragments with scoped styles and monochrome palette.

## Change Analysis

### Current State

```
studies/20250103_paper_selection/viz/
├── index.html    # Full HTML document (doctype, head, body)
├── style.css     # Global styles with :root, *, body selectors
└── main.js       # Hardcoded DATA_PATH
```

**Issues to fix:**
- Full HTML document → needs to be fragment
- `:root {}` with custom variables → use blog variables
- `* {}` global reset → scoped reset only
- `body {}` selector → `.viz-main` container
- Blue accent color (#2563eb) → monochrome (use `var(--black)`)
- `border-radius` on bars, tooltips, select → 0
- `box-shadow` on tooltip → remove
- 300ms transitions → 150ms max
- Links use color accent → underline only
- Hardcoded data path → configurable

---

## Phase 1: HTML Fragment Conversion

**File**: `index.html` → `app.html`

### Changes

1. **Remove document wrapper**
   ```html
   <!-- DELETE these lines -->
   <!DOCTYPE html>
   <html lang="en">
   <head>
     <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <title>Paper Selection Experiment</title>
     <link rel="preconnect" href="https://fonts.googleapis.com">
     <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
     <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono&display=swap" rel="stylesheet">
     <link rel="stylesheet" href="style.css">
   </head>
   <body>
   ...
   <script src="https://d3js.org/d3.v7.min.js"></script>
   <script src="main.js"></script>
   </body>
   </html>
   ```

2. **Add scoping classes**
   ```html
   <!-- BEFORE -->
   <main>
     <header>
       <h1>LLM Paper Selection Experiment</h1>

   <!-- AFTER -->
   <main class="viz-main">
     <header class="viz-header">
       <h2>LLM Paper Selection Experiment</h2>
   ```

3. **Update tooltip**
   ```html
   <!-- BEFORE -->
   <div id="tooltip"></div>

   <!-- AFTER -->
   <div id="sel-tooltip" class="viz-tooltip"></div>
   ```

4. **Prefix IDs** (avoid conflicts with other page elements)
   - `#headline-stats` → `#sel-stats`
   - `#comparison` → `#sel-comparison`
   - `#single-shot-column` → `#sel-single-column`
   - `#consensus-column` → `#sel-consensus-column`
   - `#frequency-section` → `#sel-frequency`
   - `#frequency-list` → `#sel-freq-list`
   - `#sort-select` → `#sel-sort`

### Resulting `app.html`

```html
<main class="viz-main">
  <header class="viz-header">
    <h2>LLM Paper Selection Experiment</h2>
    <p class="subtitle">Comparing single-shot vs multi-run consensus</p>
  </header>

  <section id="sel-stats"></section>

  <section id="sel-comparison">
    <div class="comparison-container">
      <div class="column" id="sel-single-column">
        <h3>Single-shot <span class="count"></span></h3>
        <div class="paper-list"></div>
      </div>
      <div class="column" id="sel-consensus-column">
        <h3>Consensus <span class="threshold">>50%</span> <span class="count"></span></h3>
        <div class="paper-list"></div>
      </div>
    </div>
  </section>

  <section id="sel-frequency">
    <h3 class="collapsible">
      <span class="toggle-icon">&#x25BC;</span>
      All Selections <span class="count"></span>
      <select id="sel-sort">
        <option value="frequency">Sort by frequency</option>
        <option value="title">Sort by title</option>
      </select>
    </h3>
    <div class="paper-list" id="sel-freq-list"></div>
  </section>
</main>

<div id="sel-tooltip" class="viz-tooltip"></div>
```

**Verification**: File is pure HTML fragment with no doctype/html/head/body tags.

- [x] Remove doctype, html, head, body tags
- [x] Remove font imports
- [x] Remove script/link tags
- [x] Add `.viz-main` class to main
- [x] Add `.viz-tooltip` class to tooltip
- [x] Change h1 → h2, column h2 → h3
- [x] Prefix all IDs with `sel-`
- [x] Rename file to `app.html`

---

## Phase 2: CSS Migration

**File**: `style.css`

### 2.1 Delete Global Selectors

```css
/* DELETE entirely */
:root {
  --font-mono: "IBM Plex Mono", monospace;
  --font-size-base: 14px;
  /* ... all of it */
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: var(--font-mono);
  /* ... */
}
```

### 2.2 Add Scoped Container

```css
/* ADD at top of file */
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

### 2.3 Color Variable Mapping

| Old | New |
|-----|-----|
| `var(--text-primary)` | `var(--black)` |
| `var(--text-secondary)` | `var(--mid-gray)` |
| `var(--accent)` | `var(--black)` |
| `var(--accent-hover)` | `var(--black)` |
| `var(--structure)` | `var(--border-color)` |
| `var(--bg)` | `var(--paper)` |
| `var(--bar-empty)` | `var(--border-color)` |
| `#f9fafb` | `var(--code-bg)` |

**Also update these accent-colored elements:**
```css
/* Marker colors (lines 195-205) */
.marker-overlap { color: var(--black); }      /* was var(--accent) */
.marker-consensus { color: var(--mid-gray); } /* was var(--text-secondary) */
.marker-single { color: var(--black); }       /* was var(--accent) */

/* Detail panel border (line 261) */
.paper-detail { border-left: 3px solid var(--black); }  /* was var(--accent) */
```

### 2.4 Remove Decorations

**Border radius** — find all, set to 0:
```css
/* Lines with border-radius to fix */
.spark-bar { border-radius: 1px 1px 0 0; }     /* → 0 */
.paper-bar-container { border-radius: 2px; }   /* → 0 */
.paper-bar { border-radius: 2px; }             /* → 0 */
#sort-select { border-radius: 4px; }           /* → 0 */
```

**Box shadow** — remove:
```css
/* Line 330: DELETE box-shadow */
#tooltip {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);  /* DELETE */
}
```

### 2.5 Fix Transitions

```css
/* Line 151, 186: Reduce to 150ms */
.paper-row { transition: background 0.15s; }  /* OK */
.paper-bar { transition: width 0.3s; }        /* → 0.15s ease-out */

/* Line 232: Reduce */
.toggle-icon { transition: transform 0.2s; }  /* → 0.15s */

/* Lines 264-276: Simplify animation */
.paper-detail {
  animation: expand 0.15s ease-out;  /* was 0.2s */
}

@keyframes expand {
  from { opacity: 0; }
  to { opacity: 1; }
}
/* DELETE max-height animation - too complex */
```

### 2.6 Fix Links

```css
/* Lines 314-322: Replace link styles */
/* BEFORE */
.paper-detail .arxiv-link {
  color: var(--accent);
  text-decoration: none;
}
.paper-detail .arxiv-link:hover {
  text-decoration: underline;
}

/* AFTER */
.viz-main a {
  color: var(--black);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.viz-main a:hover {
  text-decoration-thickness: 2px;
}
```

### 2.7 Scope Generic Selectors

```css
/* BEFORE */
header { margin-bottom: var(--section-gap); }
h1 { font-size: var(--font-size-headline); }
main { max-width: 1200px; }

/* AFTER */
.viz-header { margin-bottom: 48px; }
.viz-main h2 { font-size: 1.5rem; font-weight: 600; margin-bottom: 8px; }
/* main styles moved to .viz-main container */
```

### 2.8 Update ID Selectors

All ID-based selectors need the `sel-` prefix:
```css
#headline-stats → #sel-stats
#comparison → #sel-comparison
#single-shot-column → #sel-single-column
#consensus-column → #sel-consensus-column
#frequency-section → #sel-frequency
#frequency-section h2 → #sel-frequency h3  /* also h2 → h3 */
#frequency-list → #sel-freq-list
#sort-select → #sel-sort
#tooltip → #sel-tooltip (also add .viz-tooltip)
```

### Verification Checklist

- [x] Delete `:root {}` block
- [x] Delete `* {}` global reset
- [x] Delete `body {}` selector
- [x] Add scoped `.viz-main *` reset
- [x] Add `.viz-main` container styles
- [x] Replace all color values with blog variables
- [x] Set all `border-radius` to 0
- [x] Remove `box-shadow`
- [x] Reduce transitions to ≤150ms
- [x] Fix link styles (underline, not color)
- [x] Update all ID selectors with `sel-` prefix
- [x] Scope generic selectors (header, h1, main)

---

## Phase 3: JavaScript Updates

**File**: `main.js`

### 3.1 Configurable Data Path

```javascript
/* Line 3: BEFORE */
const DATA_PATH = '/data/20250103_paper_selection/viz_data.json';

/* AFTER */
const DATA_PATH = window.VIZ_DATA_PATH || './viz/viz_data.json';
```

### 3.2 Update Selectors

All `d3.select('#...')` calls need prefix updates, and `h2` → `h3`:

```javascript
/* Line 9 */
const tooltip = d3.select('#sel-tooltip');

/* Line 42 */
const container = d3.select('#sel-stats');

/* Lines 176-177 */
const singleColumn = d3.select('#sel-single-column');

/* Lines 184-185 */
const consensusColumn = d3.select('#sel-consensus-column');

/* Lines 202-205 */
const section = d3.select('#sel-frequency');
const list = d3.select('#sel-freq-list');

/* Lines 216, 225: Note h2 → h3 */
d3.select('#sel-frequency h3').on('click', ...);  /* was #frequency-section h2 */
d3.select('#sel-sort').on('change', ...);
```

### 3.3 Update Inline Color References

```javascript
/* Line 159: Update inline style color */
ul.append('li').style('color', 'var(--mid-gray)')  /* was var(--text-secondary) */
```

### 3.4 Update Tooltip Class Toggle

```javascript
/* Lines 26, 38 */
tooltip.classed('visible', true);   /* still works with .viz-tooltip */
tooltip.classed('visible', false);
```

### 3.5 Update Collapsed Section Logic

```javascript
/* Line 221 */
d3.select('#sel-freq-list').classed('hidden', !isCollapsed);
```

### Verification Checklist

- [x] Use configurable `window.VIZ_DATA_PATH`
- [x] Update all selector strings to use `sel-` prefix
- [x] Update `h2` selectors to `h3` where applicable
- [x] Update inline color from `--text-secondary` to `--mid-gray`
- [x] Verify `DOMContentLoaded` present (wrapped init())

**Note**: Current code calls `init()` immediately at bottom. Should wrap:
```javascript
/* Line 246: BEFORE */
init();

/* AFTER */
document.addEventListener('DOMContentLoaded', init);
```

---

## Phase 4: Test with Harness

Create `test.html` per the "Standalone Test Harness" section in `docs/NEW_VISUAL_GUIDE.md` (lines 592-640).

Key points:
- Simulates blog CSS variables (light + dark mode)
- Include app.html content in `.viz-container`
- Set `window.VIZ_DATA_PATH = '../data/viz_data.json'`

### Verification Checklist

- [x] Renders correctly in light mode
- [x] Toggle system dark mode — colors adapt correctly
- [x] All interactions work (hover, click expand, tooltips)
- [x] No console errors (only favicon 404)
- [ ] Delete `test.html` before commit

---

## Implementation Summary

| File | Action |
|------|--------|
| `index.html` | Rename to `app.html`, strip to fragment |
| `style.css` | Remove globals, use blog vars, monochrome |
| `main.js` | Configurable path, updated selectors |
| `test.html` | Create for testing, delete after |

**Lines of change estimate**: ~150 lines modified across 3 files

---

## Final Checklist

- [x] Phase 1: HTML fragment conversion
- [x] Phase 2: CSS migration
- [x] Phase 3: JavaScript updates
- [x] Phase 4: Test with harness
- [ ] Delete test.html before commit
- [x] Verify in browser with dark mode toggle

## Output Location

Files created in `studies/20250103_paper_selection/new_viz/`:
- `app.html` - HTML fragment (1.1KB)
- `style.css` - Scoped CSS (5.2KB)
- `main.js` - JavaScript (8.9KB)
- `test.html` - Test harness (delete before commit)
