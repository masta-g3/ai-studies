# Q001: Embedding Concept Granularity

## Question
What level of semantic granularity can text embeddings reliably capture and distinguish?

Examples of granularity levels:
- **Coarse**: "Machine Learning papers" vs "Biology papers"
- **Medium**: "LLM papers" vs "Computer Vision papers"
- **Fine**: "LLM training papers" vs "LLM inference papers"
- **Very Fine**: "Genetic algorithm optimization for LLM RL tuning" vs "Gradient-based RL tuning"

## Hypothesis
Embeddings can distinguish coarse and medium granularity well, but performance degrades at finer levels where domain-specific vocabulary overlaps significantly.

## Method

### Data Sources
1. MCP paper archive - query for LLM and ML papers
2. ArXiv abstracts via web search
3. Blog posts on specific techniques

### Analysis Approach
1. Collect paper abstracts across granularity spectrum
2. Generate embeddings (multiple models to compare)
3. Compute similarity matrices within and across categories
4. Measure cluster separation at each granularity level
5. Identify threshold where distinction breaks down

### Success Criteria
- Quantify similarity distributions per granularity level
- Identify which embedding models perform best at fine granularity
- Produce actionable guidance for practitioners

## Status
- [ ] Resources collected
- [ ] Data processed
- [ ] Analysis complete
- [ ] Findings written
