# RUNLOG

## Run 1 – Baseline

**Hypothesis**

Establish the baseline performance before making any modifications.

**Changes**

- Used the provided baseline implementation without any modifications.

**Result**

| Metric | Value |
|--------|------|
| BPB | **2.3718** |
| Parameters | 1,339,840 |
| Steps | 2000 |

**Conclusion**

This serves as the reference point for all future experiments.

---

## Run 2 – Standard Transformer Optimizations

**Hypothesis**

Applying common transformer training improvements should improve optimization stability and generalization.

**Changes**

- Enabled weight tying
- Switched Adam to AdamW
- Added weight decay
- Added cosine learning rate schedule
- Added warmup
- Added gradient clipping
- Reduced initialization standard deviation
- Enabled dropout

**Result**

| Metric | Value |
|--------|------|
| BPB | **2.7798** |
| Parameters | 1,298,880 |

**Observation**

Performance became significantly worse than the baseline.

Training loss also increased (approximately 2.05 compared to the baseline loss of 1.73), indicating that the model underfit within the limited training budget.

**Conclusion**

The standard optimization techniques that are normally effective for long training runs are counterproductive when only 2000 optimization steps are available.

---

## Run 3 – Minimal Optimizer Changes

**Hypothesis**

AdamW and gradient clipping alone may provide benefits without the overhead introduced by learning-rate schedules and regularization.

**Changes**

- Kept weight tying
- Kept AdamW
- Kept gradient clipping
- Removed:
  - Warmup
  - Cosine scheduler
  - Weight decay
  - Dropout

**Result**

| Metric | Value |
|--------|------|
| BPB | **2.3954** |
| Parameters | 1,298,880 |

**Observation**

Performance remained slightly worse than the original baseline.

**Conclusion**

Optimizer changes alone provide little benefit under such a small optimization budget.

---

## Run 4 – Context Length Experiment

**Hypothesis**

Increasing the context window should allow the model to capture longer dependencies.

**Changes**

- Restored baseline optimizer
- Retained weight tying
- Retained gradient clipping
- Increased block size from 128 to 256

**Result**

| Metric | Value |
|--------|------|
| BPB | **2.4541** |
| Parameters | 1,319,360 |

**Observation**

Performance degraded further.

**Analysis**

Increasing block size spreads the fixed number of updates over longer sequences without sufficient optimization time.

**Conclusion**

Simply increasing sequence length does not improve performance within the strict 2000-step constraint.

---

## Run 5 – Larger Model Capacity

**Hypothesis**

A larger transformer should model the training distribution more effectively.

**Changes**

- Increased embedding dimension to **192**
- Increased attention heads to **6**
- Used block size **256**

**Result**

| Metric | Value |
|--------|------|
| BPB | **2.4055** |
| Parameters | 1,878,144 |

**Observation**

Although the model remained under the 2M parameter limit, the larger architecture did not improve dev performance.

**Conclusion**

Increasing model capacity alone is ineffective when optimization steps are severely limited.

---

## Run 6 – Character + Byte Fallback Tokenizer

**Hypothesis**

The baseline byte-level tokenizer wastes context on UTF-8 encoded Devanagari characters. Replacing it with a tokenizer that assigns dedicated IDs to common multi-byte characters should improve effective context utilization.

**Changes**

Implemented a new tokenizer with:

- Byte fallback for arbitrary UTF-8 text
- Dedicated vocabulary entries for frequently occurring multi-byte characters
- Character vocabulary trained only on the provided corpus
- Vocabulary size increased from 256 to 816 tokens

No architectural or optimizer changes were introduced.

**Result**

| Metric | Value |
|--------|------|
| BPB | **2.3136** |
| Parameters | 1,388,480 |

**Observation**

Corpus size effectively reduced from approximately **7.3 million bytes** to **5.7 million tokens**, allowing the model to observe substantially more meaningful text within the same context window.

This reduced the evaluation BPB by approximately **2.5%** compared to the baseline.

**Conclusion**

Tokenizer efficiency had a significantly larger impact than optimizer tuning.

This experiment demonstrated that sequence efficiency, rather than optimization strategy, was the true bottleneck.

---

## Run 7 – Batch Size Experiment

**Hypothesis**

Changing batch size may improve optimization dynamics while using the new tokenizer.

**Changes**

- Retained the new tokenizer
- Increased batch size to 32

**Result**

| Metric | Value |
|--------|------|
| BPB | **2.3136** |

**Observation**

Training loss decreased slightly, but the evaluation BPB remained unchanged.

Training time also increased.

**Conclusion**

Batch size had negligible impact on generalization under the fixed optimization budget.

---

## Run 8 – Improved Tokenizer Refinements

**Hypothesis**

Minor refinements to the character-byte tokenizer may further improve compression efficiency.

**Changes**

Refined tokenizer implementation while preserving:

- Character vocabulary
- Byte fallback mechanism
- UTF-8 reversibility
- Automatic vocabulary loading

**Result**

| Metric | Value |
|--------|------|
| BPB | **2.3136** |

**Observation**

Evaluation performance remained identical.

The tokenizer implementation became cleaner and more robust without affecting model quality.

**Conclusion**

The primary gain had already been achieved by replacing byte-level tokenization. Further tokenizer engineering produced no measurable improvement within the given constraints.

---

# Final Configuration

- Character + Byte Fallback Tokenizer
- Vocabulary Size: 816
- Baseline GPT Architecture
- Parameter Count: 1,388,480
- Optimizer: Adam
- Steps: 2000
- Context Length: 128
- Final Dev BPB: **2.3136**

## Overall Findings

The experiments consistently showed that optimization tricks and architectural scaling provide limited benefit under a strict 2000-step training budget. The dominant bottleneck was inefficient byte-level tokenization of multilingual text. Replacing the tokenizer with a character-aware byte fallback tokenizer substantially improved sequence efficiency and produced the best overall performance while remaining comfortably within all competition constraints.