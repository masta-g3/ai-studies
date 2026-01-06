# Research Notes: Related Papers for Paper Selection Study

**Goal**: Find papers that provide insights or additional context for the LLM paper selection experiment (single-shot vs consensus voting, reasoning effort effects).

**Study Key Findings**:
- High reasoning effort → single-shot is reliable (locks onto ~10 papers, 70%+ top agreement)
- Low reasoning effort → scattered selections, multi-run voting helps surface signal
- Question: Is consensus voting necessary, or does increased reasoning effort suffice?

---

## Consolidated Insights by Theme

### 1. Sequential vs Parallel: The Compute Tradeoff

**Key Paper**: [2511.02309] *The Sequential Edge: Inverse-Entropy Voting Beats Parallel Self-Consistency*

> "Sequential scaling where chains explicitly build upon previous attempts consistently outperforms the dominant parallel self-consistency paradigm in 95.6% of configurations with gains up to 46.7%."

**Insight for our study**: Our experiment used parallel runs with majority voting. This paper suggests that at matched compute budgets, sequential refinement (each chain correcting the previous) might outperform parallel voting. However, our finding that *high reasoning effort alone suffices* may be a special case—the model's internal "reasoning tokens" effectively perform sequential refinement within a single call.

**Connection**: High reasoning effort = implicit sequential refinement. Low effort + voting = explicit parallel ensemble. The paper's "inverse-entropy voting" (weighting by chain confidence) could improve our consensus method.

---

### 2. Theoretical Foundation for Self-Consistency

**Key Paper**: [2510.15444] *Bridging Internal Probability and Self-Consistency for LLM Reasoning*

> "Self-consistency suffers from high estimation error while perplexity exhibits substantial modeling error... RPC achieves reasoning performance comparable to self-consistency while reducing sampling costs by 50%."

**Key concepts**:
- **Estimation Error**: Noise from finite sampling (more samples → lower error)
- **Modeling Error**: Mismatch between model's implicit distribution and ground truth
- **Perplexity Consistency (PC)**: Weight chains by internal token probabilities, not just final answer agreement

**Insight for our study**: Our 30-run consensus is essentially naive self-consistency (equal vote per run). PC would weight runs by the model's confidence in each reasoning trace. This could surface high-quality selections even with fewer runs.

**Connection**: High reasoning effort likely produces lower-entropy (more confident) traces, explaining why single-shot works—the model's internal confidence is already high.

---

### 3. Markov Chain Framing of Voting

**Key Paper**: [2510.17498] *Deep Self-Evolving Reasoning (DSER)*

> "Conceptualize iterative reasoning as a Markov chain... convergence to a correct solution is guaranteed as long as the probability of improvement marginally exceeds that of degradation."

**Key insight**: Model voting as a two-state Markov chain (Correct ↔ Incorrect) with transition probabilities p_IC (improve) and p_CI (degrade). If p_IC > p_CI, majority voting converges to correct answer.

**Insight for our study**: Our Jaccard similarity metric (run-to-run consistency) is essentially measuring the stationary distribution—high similarity means the model is already near convergence. The finding that high-effort runs have ~70% similarity suggests p_IC >> p_CI for those runs.

---

### 4. Temperature Diversity Unlocks Latent Capability

**Key Paper**: [2510.02611] *On the Role of Temperature Sampling in Test-Time Scaling*

> "Different sampling temperatures solve different subsets of problems... temperature scaling yields an additional 7.3 points over single-temperature TTS."

**Key insight**: At large sample counts, single-temperature scaling plateaus—certain problems remain unsolved regardless of sample count. Multi-temperature sampling expands the "reasoning boundary."

**Insight for our study**: We used a fixed temperature across runs. This paper suggests that allocating some runs to different temperatures could discover papers that the model systematically misses at default temperature. Could explain why consensus sometimes surfaces unexpected papers.

---

### 5. Distribution-Calibrated Voting

**Key Paper**: [2512.03019] *Distribution-Calibrated Inference for Thinking LLM-as-a-Judge*

> "Common aggregation rules (majority vote, soft self-consistency) are inconsistent when ties are allowed... our approach models three-way preferences with a Bradley-Terry-Davidson formulation."

**Key insight**: Majority voting loses information. Better to model the full vote distribution, extracting both "decisiveness" (margin) and "tie propensity" as separate signals.

**Insight for our study**: Our >50% threshold for consensus is crude. Papers at 47% vs 53% are treated very differently despite nearly identical signal. A calibrated aggregation could provide more nuanced ranking.

---

### 6. Test-Time Compute: No Universal Winner

**Key Paper**: [2512.02008] *The Art of Scaling Test-Time Compute*

> "No single TTS strategy universally dominates... reasoning models exhibit distinct trace-quality patterns across problem difficulty."

**Key insight**: Short-horizon models (like reasoning models) benefit from short traces + fast search. Long-horizon models need longer traces + majority voting. The optimal strategy depends on model family and task difficulty.

**Insight for our study**: Our task (paper selection from ~200 candidates) is a "subjective reasoning" task, not a verifiable math problem. The optimal strategy may differ from math benchmarks—our finding that single-shot works for high effort may be task-specific.

---

### 7. Reproducibility and Precision

**Key Paper**: [2506.09501] *Give Me FP32 or Give Me Death?*

> "Under bfloat16 precision with greedy decoding, a reasoning model can exhibit up to 9% variation in accuracy due to differences in GPU count, type, and batch size."

**Key insight**: Non-associative floating-point arithmetic causes reasoning chains to diverge across hardware configurations. FP32 is needed for reproducibility.

**Insight for our study**: Our run-to-run variation may include hardware-induced noise, not just sampling stochasticity. This suggests our consistency metrics (Jaccard similarity) underestimate true model consistency.

---

### 8. Controllable Reasoning Effort

**Key Paper**: [2508.18773] *ThinkDial: An Open Recipe for Controlling Reasoning Effort in Large Language Models*

> "ThinkDial enables seamless switching between three distinct reasoning regimes: High mode (full reasoning), Medium mode (50% token reduction with <10% performance degradation), and Low mode (75% token reduction with <15% performance degradation)."

**Key insight**: Reasoning effort can be explicitly controlled via system prompts after training with mode-labeled data. A single model can produce short, medium, or long reasoning traces on demand.

**Insight for our study**: This validates our experimental design—reasoning effort is a meaningful, controllable parameter. Our finding that "high effort suffices for single-shot" aligns with their finding that High mode preserves full capability while lower modes trade off accuracy for efficiency.

**Connection**: Our "reasoning_effort" parameter maps directly to their mode concept. Future work could train a model to select effort level adaptively based on task difficulty.

---

### 9. LLM-as-a-Judge Reliability Metrics

**Key Paper**: [2512.16041] *Are We on the Right Way to Assessing LLM-as-a-Judge?*

> "Even top-performing models fail to maintain consistent preferences in nearly a quarter of difficult cases... We attribute this to situational preference."

**Key metrics**:
- **Intra-Pair Instability (IPI)**: Do you get the same answer if you ask the same question twice?
- **Total Order Violation (TOV)**: If A > B and B > C, is A > C?

**Insight for our study**: Our paper selection task is essentially LLM-as-a-Judge (ranking papers by interestingness). The ~30% run-to-run variation we see in low-effort mode reflects IPI. Our finding that high-effort reduces variation aligns with their finding that "deep reasoning enhances judging consistency."

---

### 10. Bias Correction for LLM Judgments

**Key Paper**: [2511.21140] *How to Correctly Report LLM-as-a-Judge Evaluations*

> "Apply a Rogan-Gladen-style plug-in estimator to debias the raw pass-rate... derive confidence intervals that account for variability in both test and calibration samples."

**Key insight**: Raw LLM judgment rates are biased. Need to estimate true-positive and true-negative rates from calibration data, then correct.

**Insight for our study**: Our consensus threshold (>50%) is a raw judgment rate. If the LLM has systematic biases (e.g., prefers papers with certain keywords), our consensus may amplify rather than correct those biases. Calibration against human preferences could help.

---

### 11. Peer-Review Style Ensemble

**Key Paper**: [2512.23213] *LLM-PeerReview: Ensembling via Peer-Review Process*

> "Multiple LLMs score each candidate response... scores are aggregated via Dawid-Skene EM model that learns judge reliabilities."

**Key insight**: Rather than having one model vote 30 times, use multiple diverse models as judges. Weight their votes by learned reliability.

**Insight for our study**: Our experiment used a single model family (Gemini) with varying reasoning effort. Using diverse model families as judges could provide more robust consensus—each model may have different blind spots.

---

## Papers for Appendix / Further Reading

### Tier 1: Directly Relevant (strong candidates for citation)

| arxiv_code | Title | Key Insight |
|------------|-------|-------------|
| 2511.02309 | The Sequential Edge | Sequential refinement beats parallel voting at matched compute |
| 2510.15444 | Bridging Internal Probability and Self-Consistency | Perplexity-weighted aggregation reduces samples by 50% |
| 2510.02611 | Temperature Sampling in Test-Time Scaling | Multi-temperature solves different problem subsets |
| 2512.02008 | The Art of Scaling Test-Time Compute | No universal TTS winner; strategy depends on model/task |
| 2510.17498 | Deep Self-Evolving Reasoning | Markov chain framing: p_IC > p_CI → convergence |
| 2508.18773 | ThinkDial: Controlling Reasoning Effort | Validates reasoning effort as controllable parameter |
| 2512.16041 | Assessing LLM-as-a-Judge (Sage) | IPI and TOV metrics for self-consistency |

### Tier 2: Useful Context

| arxiv_code | Title | Key Insight |
|------------|-------|-------------|
| 2512.03019 | Distribution-Calibrated Inference | Bradley-Terry for calibrated vote aggregation |
| 2506.09501 | Give Me FP32 or Give Me Death | Hardware precision affects reproducibility |
| 2511.21140 | How to Report LLM-as-a-Judge | Rogan-Gladen bias correction for judgments |
| 2512.23213 | LLM-PeerReview | Dawid-Skene EM for multi-judge aggregation |
| 2510.14913 | Budget-aware Test-time Scaling | Cheap discriminative verifiers beat expensive generative ones |
| 2511.02303 | Unlocking Multi-Agent LLM Reasoning | Lazy agent bias, Shapley-based credit assignment |

### Tier 3: Extended Reading

| arxiv_code | Title | Key Insight |
|------------|-------|-------------|
| 2502.05234 | Optimizing Temperature for LLMs | TURN: entropy-based auto temperature selection |
| 2510.24801 | Fortytwo: Swarm Inference | Reputation-weighted Bradley-Terry consensus |
| 2510.01581 | Think Right (TRAAC) | Adaptive reasoning budget based on difficulty |
| 2507.14958 | MUR: Momentum Uncertainty Reasoning | 50% token reduction via selective compute |
| 2511.21581 | Learning When to Stop | RL for adaptive latent reasoning depth |

---

## Open Questions / Future Directions

1. **Inverse-entropy voting**: Would weighting runs by trace perplexity improve our consensus?
2. **Multi-temperature**: What if we ran 10 runs at each of 3 temperatures instead of 30 at one?
3. **Sequential refinement**: Instead of parallel runs, let the model iteratively refine its selection?
4. **Diverse judges**: Use Claude + GPT + Gemini as a panel instead of Gemini 30x?
5. **Calibrated aggregation**: Replace >50% threshold with Bradley-Terry ranking?

---

## Session Log

### Searches Completed
1. Self-consistency and voting methods
2. LLM reasoning (chain-of-thought, reasoning)
3. Model consistency and reliability
4. Ensemble and multi-agent methods
5. Test-time compute scaling
6. Temperature effects
7. Calibration and confidence
8. Thinking/reasoning models
9. Variability and reproducibility
10. Selection and ranking

### Database Stats
- Total papers in database: 12,920
- Papers examined in detail: ~40
- Papers selected for appendix: 18

---

## Synthesis: What the Literature Tells Us

### Our Study in Context

Our experiment—comparing single-shot vs 30-run consensus at varying reasoning effort levels—sits at the intersection of three active research areas:

1. **Test-Time Scaling (TTS)**: The literature shows no universal winner among TTS strategies. Our finding that "high reasoning effort + single-shot suffices" is consistent with this—the optimal strategy depends on model capability and task type.

2. **Self-Consistency**: Parallel majority voting (our consensus approach) is a well-studied baseline. The literature suggests several improvements:
   - Perplexity-weighted aggregation (RPC) could reduce needed samples by 50%
   - Multi-temperature sampling could expand the "reasoning boundary"
   - Sequential refinement might outperform parallel at matched compute

3. **LLM-as-a-Judge**: Paper selection is fundamentally a judgment task. The literature shows even top models have ~25% inconsistency on hard judgments. Our run-to-run variation reflects this phenomenon.

### Key Validation

The literature validates our core finding: **reasoning effort is a meaningful, controllable parameter** (ThinkDial). High-effort reasoning produces lower-entropy, more confident traces—which explains why single-shot works when reasoning effort is high.

### Potential Improvements

If extending this work, the literature suggests:

1. **Inverse-entropy voting**: Weight runs by trace confidence, not equally
2. **Calibrated aggregation**: Replace >50% threshold with Bradley-Terry ranking
3. **Multi-temperature**: Allocate runs across temperatures to expand coverage
4. **Diverse judges**: Use multiple model families instead of one model 30x
5. **Bias correction**: Calibrate against human preferences to correct systematic biases

### Limitations to Acknowledge

1. **Subjective task**: Most TTS literature focuses on math/code with verifiable answers. Paper selection is subjective—different ground truth.
2. **Single model family**: Using Gemini variants only. Multi-family validation would strengthen conclusions.
3. **Fixed temperature**: We didn't explore temperature diversity, which literature suggests matters.

---

## Final Recommendation

**For the published report**, I recommend citing the Tier 1 papers in a "Related Work" or "Discussion" section to contextualize our findings within the broader TTS and self-consistency literature. The key framing:

> "Our finding that high reasoning effort enables reliable single-shot selection aligns with recent work showing that test-time compute strategies are task- and model-dependent [2512.02008], and that controllable reasoning effort is an emerging paradigm [2508.18773]. The theoretical foundation for why consensus voting helps at lower effort levels is provided by Markov chain models of iterative refinement [2510.17498] and self-consistency theory [2510.15444]."

