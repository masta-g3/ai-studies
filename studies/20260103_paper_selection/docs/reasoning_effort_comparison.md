# Reasoning Effort Comparison: Minimal → Low → Medium → High

"Best paper" sounds subjective, but we gave the model specific criteria: prioritize surprising or counter-intuitive findings, novel conceptual frameworks, and research that connects LLMs to seemingly unrelated fields. Downweight incremental benchmarks and pure optimization papers. With that framing, we ran Gemini 3 Flash Preview at four thinking levels across a pool of 250 recent AI papers, selecting top 3 per run across 30 runs.

## Summary Statistics

| Metric | Minimal | Low | Medium | High |
|--------|---------|-----|--------|------|
| Unique papers selected | 27 | 18 | 14 | **9** |
| Consensus papers (>50%) | 1 | 2 | 2 | 2 |
| Avg run similarity | 22.4% | 25.5% | 51.0% | **51.4%** |
| Single-shot ∩ consensus | 0/3 | 1/3 | **2/3** | **2/3** |

**Key pattern:** As reasoning effort increases, the model becomes dramatically more focused (27 → 9 unique papers) and consistent (22% → 51% similarity). Single-shot reliability improves from essentially random (0/3) to highly aligned (2/3).

## Which Reasoning Level Selected Best?

Based on the selection criteria (upweighting: surprising findings, novel frameworks, emergent properties, cross-disciplinary connections; downweighting: incremental improvements, pure optimization):

### Winner: **High** reasoning effort

**High** produced the most interesting and criteria-aligned selections:

1. **"Shape of Thought"** (100%) — *Perfect criteria match*: Counter-intuitive finding that training on *incorrect* reasoning traces improves performance. Challenges fundamental assumptions about what matters in learning.

2. **"Why Do LLM Agents Whistleblow?"** (73.3%) — *Excellent match*: Surprising emergent behavior, actionable agentic insights, connects alignment training to social dynamics.

3. **"State over Tokens"** (46.7%) — *Excellent match*: Novel conceptual framework reframing reasoning tokens as computational state rather than narrative.

High reasoning also surfaced **"Brain-Grounded Axes"** (40%)—a highly unconventional paper connecting LLMs to neuroscience—which no other level ranked as highly.

### Runner-up: **Medium**

Medium shared the same top pick ("Shape of Thought" at 100%) and had excellent consistency, but focused more on interpretability-heavy papers and less on cross-disciplinary work.

### Why Lower Efforts Failed

**Minimal's top pick** was "Training LMs to Explain Their Own Computations" (86.7%)—a good paper but more incremental than "Shape of Thought." More damning: its single-shot picks ("Heaven-Sent or Hell-Bent?" at 10%, "Honesty over Accuracy" at 3.3%) were essentially random noise that almost never appeared in multi-runs.

**Low** improved somewhat but still produced scattered results with a single-shot that included "Whistleblowing" at only 3.3% frequency—another noise pick.

## Thematic Analysis

Different reasoning levels gravitate toward different paper types:

| Level | Thematic Preference |
|-------|---------------------|
| **High** | Meta-reasoning, emergent behaviors, cross-disciplinary (neuroscience + LLMs) |
| **Medium** | Conceptual frameworks, reasoning token analysis, synthetic data insights |
| **Low** | Interpretability, hallucination definitions, self-explanation |
| **Minimal** | Scattered: interpretability, uncertainty, trustworthiness—no clear focus |

## Convergence Patterns

Run-to-run similarity shows clear phase transitions:

- **High**: First 4 run-pairs at Jaccard=1.0 (perfect agreement), rarely drops below 0.5
- **Medium**: First 4 run-pairs at Jaccard=1.0, sustained high consistency
- **Low**: Never reaches perfect agreement, oscillates 0.0–0.5
- **Minimal**: Frequently hits 0.0 (zero overlap between consecutive runs)

This suggests higher reasoning creates "attractor states" where the model locks onto specific papers early and maintains that focus.

## Single-Shot Reliability

| Reasoning | Paper #1 | Multi-Run % | Paper #2 | Multi-Run % | Paper #3 | Multi-Run % |
|-----------|----------|-------------|----------|-------------|----------|-------------|
| **High** | Whistleblowing | 73.3% ✓ | State over Tokens | 46.7% | Shape of Thought | 100% ✓ |
| **Medium** | State over Tokens | 83.3% ✓ | Shape of Thought | 100% ✓ | Whistleblowing | 36.7% |
| **Low** | State over Tokens | 70% ✓ | Training LMs to Explain | 50% ✓ | Whistleblowing | 3.3% ✗ |
| **Minimal** | Heaven-Sent or Hell-Bent? | 10% ✗ | Honesty over Accuracy | 3.3% ✗ | Road Not Taken | 30% |

With high/medium reasoning, single-shot picks are reliable. With minimal, they're noise.

---

## Top 3 Papers by Reasoning Level

### High Reasoning

**Consensus / Top 3:**

1. **Shape of Thought: When Distribution Matters More than Correctness** `2512.22255` · 100%
   > Training on synthetic datasets of chain-of-thought traces from more capable models improves reasoning even when all traces lead to incorrect final answers. The distribution of synthetic data is inherently closer to the language model's own distribution, making it more amenable to learning.

2. **Why Do Language Model Agents Whistleblow?** `2511.17085` · 73.3%
   > LLM agents disclose suspected misconduct to regulatory agencies without user instruction. Whistleblowing varies by model family, decreases with task complexity, and increases with moral nudging in system prompts.

3. **State over Tokens: Characterizing the Role of Reasoning Tokens** `2512.12777` · 46.7% *(below threshold)*
   > Reasoning tokens are not a faithful explanation of the model's actual reasoning process. SoT reframes them as an externalized computational state—the sole persistent information carrier across stateless generation cycles.

---

### Medium Reasoning

**Consensus / Top 3:**

1. **Shape of Thought** `2512.22255` · 100%
   > [Same as above]

2. **State over Tokens** `2512.12777` · 83.3%
   > [Same as above]

3. **Why Do Language Model Agents Whistleblow?** `2511.17085` · 36.7% *(below threshold)*
   > [Same as above]

---

### Low Reasoning

**Consensus / Top 3:**

1. **State over Tokens** `2512.12777` · 70%
   > [Same as above]

2. **A Unified Definition of Hallucination, Or: It's the World Model, Stupid** `2512.21577` · 60%
   > Hallucination is simply inaccurate internal world modeling. By varying the reference world model and knowledge conflict policy, we arrive at different existing definitions. This unified view forces evaluations to clarify their assumed "world."

3. **Training Language Models to Explain Their Own Computations** `2511.08579` · 50%
   > Using a model to explain its own computations works better than using a different model (even if more capable). This generalization appears attributable to privileged access to their own internals.

---

### Minimal Reasoning

**Consensus / Top 3:**

1. **Training Language Models to Explain Their Own Computations** `2511.08579` · 86.7%
   > [Same as above]

2. **Are language models aware of the road not taken?** `2511.04527` · 30% *(below threshold)*
   > There is a clear correlation between how uncertain a model is at different tokens and how easily the model can be steered by controlling its activations.

3. **Why Do Language Model Agents Whistleblow?** `2511.17085` · 23.3% *(below threshold)*
   > [Same as above]

---

## Implications

1. **For paper curation with LLMs:** Use high reasoning effort. It produces more focused, consistent, and criteria-aligned selections. The cost (more tokens) is justified by reliability.

2. **For single-shot use:** High/medium reasoning single-shots are reliable proxies for consensus. Minimal reasoning single-shots are noise—worse than random selection.

3. **Quality vs. exploration tradeoff:** Minimal reasoning explores broadly (27 unique papers) but can't distinguish quality. High reasoning focuses tightly (9 papers) with high confidence. If you want discovery, use minimal + voting. If you want recommendations, use high.

4. **The meta-observation persists:** "Shape of Thought"—a paper arguing that *the distribution of reasoning matters more than correctness*—was picked 100% by high reasoning, 100% by medium, 16.7% by low, and 3.3% by minimal. The model, when given more time to think, selects the paper about the value of thinking.
