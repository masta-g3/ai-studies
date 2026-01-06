# Plan: Tufte-Aligned Visualization Improvements

**ID**: viz-improve-001
**Status**: Complete
**Target**: `studies/20250103_paper_selection/publish/`

---

## Tufte Assessment

### Current State Analysis

The visualization shows LLM paper selection experiment results comparing single-shot vs consensus voting. Reviewing against Tufte's principles:

#### What Works Well
- **High data-ink ratio** in bar charts (minimal decoration)
- **Direct labeling** on bars (percentage values)
- **Monochrome palette** avoids chartjunk
- **Sparkline** for run similarity is appropriate density

#### Issues Identified

| Issue | Tufte Principle Violated | Severity |
|-------|-------------------------|----------|
| Truncated titles hide data | "Show the data" | High |
| Column widths waste space | "Maximum info in minimum space" | High |
| Bar semantics unclear | "Clear labeling" | High |
| Markers (`*`, `·`) unexplained | "Clear labeling" | Medium |
| Stats row lacks context | "Reveal data at several levels" | Medium |
| Tooltip position bug | (VISUAL_GUIDE compliance) | Low |

---

## Surgical Improvements

### 1. Column Width: Prevent Title Truncation

**Problem**: At current `grid-template-columns: 1fr 1fr`, titles truncate around 40 characters. Paper titles average 60-80 characters.

**Before**:
```
Single-shot (3)                    Consensus >50% (4)
─────────────────                  ─────────────────
Alternative positional encod...    SPARK: Stepwise Process-A...
```

**Solution**: Allow columns to breathe with minimum widths and wrapping.

```css
/* style.css - REPLACE lines 95-99 */

/* Current (remove): */
.comparison-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 64px;
}

/* New: */
.comparison-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 48px;
}
```

```css
/* style.css - REPLACE lines 134-140 */

/* Current (remove): */
.paper-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

/* New: Allow 2-line wrapping */
.paper-title {
  flex: 1;
  min-width: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

**Rationale**: Tufte's "show the data" principle—truncated titles hide information. Two-line clamp balances readability with space. Tooltip still shows full title on hover.

---

### 2. Bar Chart Semantics: Direct Labels

**Problem**: What does the bar represent? 70% of what? The percentage shows "frequency across runs" but this isn't clear without reading the code.

**Before**:
```
SPARK: Stepwise Process-Aware...  70% ████████████
```

**Solution**: Add column subtitles and axis label explaining the metric.

```html
<!-- app.html: Replace lines 10-19 with subtitled columns -->
<section id="sel-comparison">
  <div class="comparison-container">
    <div class="column" id="sel-single-column">
      <h3>Single-shot <span class="count"></span></h3>
      <div class="column-subtitle">Papers from one sampled run</div>
      <div class="paper-list"></div>
    </div>
    <div class="column" id="sel-consensus-column">
      <h3>Consensus <span class="threshold">>50%</span> <span class="count"></span></h3>
      <div class="column-subtitle">Selected in majority of 30 runs</div>
      <div class="paper-list"></div>
    </div>
  </div>
</section>
```

Note: Column subtitles are static HTML—no JS changes needed.

```css
/* style.css - ADD after line 118 */
.column-subtitle {
  font-size: 12px;
  color: var(--mid-gray);
  margin-top: -12px;
  margin-bottom: 16px;
}
```

**For the frequency list**, add an axis annotation:

```html
<!-- app.html: Replace lines 22-31 -->
<section id="sel-frequency">
  <h3 class="collapsible">
    <span class="toggle-icon">&#x25BC;</span>
    All Selections <span class="count"></span>
    <span class="bar-label">% of 30 runs</span>
    <select id="sel-sort">
      <option value="frequency">Sort by frequency</option>
      <option value="title">Sort by title</option>
    </select>
  </h3>
  <div class="paper-list" id="sel-freq-list"></div>
</section>
```

```css
/* style.css - ADD after line 204 */
.bar-label {
  font-size: 11px;
  color: var(--mid-gray);
  font-weight: 400;
}
```

**Rationale**: Tufte's "clear labeling" principle. The reader shouldn't need to decode what 70% means.

---

### 3. Marker Legend: Explain `*` and `·`

**Problem**: The markers `*` (consensus) and `·` (single-shot/overlap) appear in the frequency list without explanation.

**Before**:
```
SPARK: Stepwise Process-Aware...  70% ████████████  *
When AI Takes the Couch...        57% █████████     *·
```

**Solution**: Add inline legend directly where markers appear (Tufte prefers direct labels over separate legends).

```html
<!-- app.html: Add after the h3 in sel-frequency, before paper-list -->
<div class="marker-legend">
  <span><span class="marker-consensus">*</span> in consensus</span>
  <span><span class="marker-single">·</span> in single-shot</span>
</div>
<div class="paper-list" id="sel-freq-list"></div>
```

```css
/* style.css - ADD after .bar-label */
.marker-legend {
  font-size: 11px;
  color: var(--mid-gray);
  margin-bottom: 12px;
  display: flex;
  gap: 16px;
}

.marker-legend span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
```

**Rationale**: Eliminates cognitive load of marker decoding. Legend is inline with the data, not separate.

---

### 4. Stats Row → Stats Sentence

**Problem**: `30 runs · 22 unique · 4 consensus · 1/5 overlap` lacks context for new readers.

**Before**:
```
30 runs  ·  22 unique  ·  4 consensus  ·  1/5 overlap
```

**Solution**: Replace stat chips with prose that integrates statistical and verbal descriptions (Tufte's principle).

```javascript
/* main.js - REPLACE renderHeadlineStats function (lines 41-77) */

function renderHeadlineStats(summary, runSimilarities) {
  const container = d3.select('#sel-stats');

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
```

```css
/* style.css - REPLACE .stats-row block (lines 37-63) */

/* Remove: .stats-row, .stat, .stat-value, .stat-label, .stat-separator */

/* Add: */
.stats-sentence {
  font-size: 13px;
  color: var(--mid-gray);
  line-height: 1.6;
  max-width: 600px;
  margin-bottom: 16px;
}

.stats-sentence strong {
  color: var(--black);
  font-weight: 600;
}
```

**Rationale**: Tufte advocates "words, not symbols" where possible. A sentence integrates statistical and verbal descriptions, making the experiment immediately comprehensible.

---

### 5. Tooltip Position Bug Fix

**Problem**: Current CSS uses `position: absolute` but VISUAL_GUIDE.md requires `position: fixed` because Quarto containers break absolute positioning.

```css
/* style.css - FIX line 304 */

/* Current (broken): */
.viz-tooltip {
  position: absolute;
  ...
}

/* Fixed: */
.viz-tooltip {
  position: fixed;
  ...
}
```

---

## Implementation Phases

### Phase 1: Critical Clarity Fixes
- [x] Column width: `minmax(400px, 1fr)` and remove 64px gap → 48px
- [x] Title wrapping: Replace `nowrap`/`ellipsis` with `-webkit-line-clamp: 2`
- [x] Tooltip: Change `position: absolute` → `position: fixed`

### Phase 2: Labeling
- [x] Add column subtitles (static HTML)
- [x] Add bar axis label "% of 30 runs"
- [x] Add marker legend inline

### Phase 3: Context
- [x] Replace stats chips with prose sentence

### Phase 4: Verification
- [x] Test harness renders correctly
- [x] All text readable without truncation
- [x] Semantics clear to naive reader
- [x] Dark mode works (CSS variables cascade)
- [x] Delete test.html

---

## Files to Modify

| File | Changes |
|------|---------|
| `viz/app.html` | Column subtitles, marker legend, bar label |
| `viz/style.css` | Column widths, title wrapping, legend styles, stats sentence, tooltip fix |
| `viz/main.js` | Replace `renderHeadlineStats` with prose version |

---

## Design Rationale Summary

Per Tufte:
1. **"Show the data"** → Wider columns, 2-line titles instead of truncation
2. **"Clear labeling"** → Axis labels, marker legend, column subtitles
3. **"Integrate verbal and statistical"** → Prose sentence instead of cryptic stat chips
4. **"Maximize data-ink ratio"** → No new decoration, only clarity improvements
5. **VISUAL_GUIDE compliance** → Fixed tooltip positioning
