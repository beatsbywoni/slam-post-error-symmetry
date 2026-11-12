# Additional file 1. Supplementary methods and results

Failed exercises mark error-prone periods: error rates before and after errors in app-based language practice

All values are percentage points with 95% learner-bootstrap intervals unless marked. All quantities are observational contrasts between periods around error clusters and periods around matched comparison exercises; none is an identified causal effect. Columns are the English course for Spanish speakers, the Spanish course for English speakers and the French course for English speakers.

## Supplementary methods

**Corpus and inclusion.** Duolingo SLAM version 4.0 training partitions (file stamp 20190204). Tokens were lower-cased surface forms. Learner records with at least 200 tokens and 20 token errors were retained. Token frequency is the count of a surface form in the course's training partition, cut into quartiles over tokens.

**Matching (planned).** Comparison anchors were exercises of the same learner with fewer than two token errors, matched exactly on day band of use (0–7, 7–14, 14–30 days since first use), exercise format, exercise-length band (1–2, 3–4, 5–7, 8 or more tokens) and the exercise median of the token-frequency quartile. Both anchor types required 20 tokens before the first token and 20 tokens after the last token of the exercise within the learner's record. Up to three comparison anchors were drawn per event without replacement (seed 20260923); anchors could be reused across events. Events with no eligible comparison were dropped (16%, 17% and 18% of eligible events).

**Item-difficulty adjustment (planned).** For each token, the error rate of the same surface form among all other retained learners of the course was subtracted from the response (0 or 1). Forms with fewer than 20 occurrences by other learners (0.2%, 0.4% and 0.7% of tokens) used the leave-one-learner-out error rate of the token's part of speech.

**Inference (planned).** Per-event quantities were averaged within learner; learner means were averaged with equal weight. Intervals are 2.5th and 97.5th percentiles of 2,000 bootstrap resamples of learners (seed 20260923) with matched sets held fixed. The reduction of the excess after item-difficulty adjustment (H4) is 1 minus the ratio of adjusted to raw excess, computed within each resample. It describes how much the excess shrinks when average word-form error rates are subtracted; it does not partition the excess into causes, and sentence-level or learner-specific difficulty is not removed.

**History rules (planned sensitivity).** Prior rule: comparison anchors ending within 20 tokens after the end of a previous cluster were excluded. Symmetric rule: the same exclusion was also applied to events. An earlier draft of the plan used the prior rule as the main rule; a code test on the first 150 learners of the French course showed that it selects comparison pre windows free of clusters, and the rule of no history conditioning was fixed before any full-course analysis. The plan records this sequence.

**Dose contrast (planned, with a post hoc within-learner version).** The planned contrast is the mean DiD of learners who had clusters of four or more errors minus the mean DiD of learners who had clusters of two errors; the two means come from overlapping but different sets of learners (Table S1 gives the numbers), and the interval is from the same bootstrap resamples. The post hoc version computes, for each learner with clusters of both sizes, the DiD for four or more errors minus the DiD for two errors, and averages these differences.

**Exploratory splits (planned).** Item difficulty of the cluster: tertiles of the mean leave-one-learner-out error rate of the cluster exercise's tokens. Break: whether the first exercise of the post window began 30 minutes or more after the cluster.

**Adjacent exercises (post hoc).** For each anchor, the proportion of wrong tokens in the exercise immediately before and immediately after it in the learner's record (and the mean over the three exercises on each side) was computed for events and for the same matched comparison anchors as in the planned analysis.

**Overlapping comparisons (post hoc).** A comparison anchor was classed as overlapping if its pre or post window contained any token of the cluster exercise it was matched to. Under the planned matching this applied to 8.8%, 10.8%, 11.8% of drawn comparison anchors, and 21%, 24%, 26% of clusters had at least one. In the re-analysis such anchors were removed from the pool before drawing.

**Practice bouts and alternative matching keys (post hoc).** Practice bouts were separated at gaps of 30 minutes or more between successive recorded exercises. They are defined by the analyst and are not the application's own sessions, whose identifiers were not retained at extraction; no claim is made about position within an application session. Three keys were added to the planned matching one at a time: the corpus field for session type (lesson, practice, test); a band for the number of exercises in the bout (1–8, 9–15, 16–28, 29 or more); and a band for the anchor's ordinal position in its bout (1–3, 4–8, 9–15, 16–28, 29 or more). These keys increase the share of comparison anchors drawn from the cluster's own bout and therefore the share of overlapping comparisons, so they are reported with overlapping comparisons excluded. Without that exclusion, matching on position within the bout appeared to remove most of the excess (pre excess 0.32, 0.04 and 0.22); with it the excess was the same as under the planned matching (Table S2). Rest of bout: error rate over tokens of the anchor's bout that lay more than 20 tokens from the anchor exercise, event minus comparison. Comparison bouts may themselves contain clusters, including the matched one, so this contrast is biased against finding elevation.

**Matching seeds (post hoc).** The planned matching was repeated with 20 seeds; the table gives the mean and range of the point estimates.

**Repeated word forms (post hoc).** A window token was classed as repeated if its surface form occurred in the anchor exercise, and as new otherwise.

**Exercise durations (post hoc).** Durations that were missing or not positive (2.6%, 5.1% and 7.1% of exercises) were dropped, and the remainder were winsorised at the course 99th percentile (99, 69 and 68 s). Log durations were centred on the course mean for exercises of the same format and token count (capped at 12). For event anchors and for comparison anchors separately, the available adjusted log durations at each of the three exercises before and the three after the anchor were first averaged within learner, lag by lag; the pre value is the mean of the available lag means at −3 to −1 and the post value the mean of those at +1 to +3. A learner contributes to a quantity if that quantity can be computed, so the numbers of learners differ slightly between rows of Table S4. The complete-case rows use the learners for whom both pre and post excess could be computed; they do not require every individual duration to be present. The table reports differences in log duration multiplied by 100, which approximate percentages.

**Time reversal (post hoc).** Each learner's token sequence was reversed, exercise boundaries were mapped accordingly, day bands were recomputed on the reversed record, and the same estimator was applied. In reversed records the window labelled post precedes the cluster in real time. With no history conditioning the reversed difference in differences is, apart from re-matching, the negative of the forward one by construction, so reversal is informative only for the history rules.

**Code.** The estimator script was frozen and hashed on 23 September 2026 (SHA-256 be418183335ad136dbeb89bd6e2532f4339d2215cf818312310823753a219540). It was later extended with options used only by post hoc analyses; the frozen file is archived and reproduces the planned results.

## Table S1. Planned sensitivity and exploratory analyses

| Analysis | English | Spanish | French |
|---|---|---|---|
| Window of 10 tokens: pre excess | 1.67 [1.45, 1.88] | 1.43 [1.17, 1.69] | 2.04 [1.72, 2.36] |
| Window of 10 tokens: post excess | 1.87 [1.66, 2.09] | 1.54 [1.27, 1.79] | 1.82 [1.51, 2.14] |
| Window of 10 tokens: DiD | 0.21 [−0.05, 0.46] | 0.10 [−0.17, 0.36] | −0.22 [−0.60, 0.15] |
| Window of 30 tokens: pre excess | 0.72 [0.57, 0.87] | 0.47 [0.28, 0.64] | 0.56 [0.36, 0.77] |
| Window of 30 tokens: post excess | 1.11 [0.96, 1.27] | 0.48 [0.30, 0.66] | 0.21 [−0.00, 0.43] |
| Window of 30 tokens: DiD | 0.39 [0.22, 0.57] | 0.02 [−0.17, 0.21] | −0.34 [−0.61, −0.09] |
| Threshold of three errors: pre excess | 1.60 [1.27, 1.91] | 1.41 [0.97, 1.81] | 0.61 [0.07, 1.17] |
| Threshold of three errors: post excess | 1.93 [1.61, 2.26] | 1.22 [0.82, 1.62] | 0.19 [−0.33, 0.76] |
| Threshold of three errors: DiD | 0.34 [−0.07, 0.77] | −0.19 [−0.67, 0.29] | −0.42 [−1.10, 0.31] |
| Clusters of 2 errors: pre excess | 0.66 [0.47, 0.84] | 0.61 [0.39, 0.82] | 1.05 [0.80, 1.31] |
| Clusters of 2 errors: post excess | 1.17 [0.99, 1.35] | 0.68 [0.48, 0.88] | 0.85 [0.57, 1.12] |
| Clusters of 2 errors: DiD | 0.51 [0.27, 0.76] | 0.08 [−0.18, 0.31] | −0.20 [−0.57, 0.14] |
| Clusters of 3 errors: pre excess | 1.66 [1.28, 2.05] | 1.49 [1.01, 1.96] | 0.55 [−0.12, 1.18] |
| Clusters of 3 errors: post excess | 2.15 [1.79, 2.53] | 1.59 [1.14, 2.05] | −0.06 [−0.70, 0.62] |
| Clusters of 3 errors: DiD | 0.49 [−0.02, 0.99] | 0.10 [−0.45, 0.68] | −0.60 [−1.49, 0.30] |
| Clusters of 4+ errors: pre excess | 2.86 [2.27, 3.44] | 3.09 [2.31, 3.91] | 1.33 [0.25, 2.45] |
| Clusters of 4+ errors: post excess | 3.02 [2.41, 3.62] | 2.30 [1.48, 3.11] | 2.24 [1.22, 3.26] |
| Clusters of 4+ errors: DiD | 0.15 [−0.62, 0.93] | −0.78 [−1.76, 0.17] | 0.91 [−0.56, 2.32] |
| Planned dose contrast: DiD, learners with 4+ errors minus learners with 2 errors | −0.36 [−1.18, 0.45] | −0.86 [−1.85, 0.15] | 1.12 [−0.41, 2.62] |
| Learners with clusters of 2 errors | 2,487 | 2,456 | 1,158 |
| Learners with clusters of 4+ errors | 1,472 | 1,063 | 620 |
| Learners with both | 1,463 | 1,058 | 618 |
| Clusters of 2 / 3 / 4+ errors | 36,647 / 9,892 / 5,770 | 34,264 / 7,700 / 2,922 | 20,493 / 4,710 / 2,307 |
| Post hoc, within learners with both: DiD 4+ minus DiD 2 | −0.35 [−1.21, 0.50] | −0.79 [−1.87, 0.24] | 1.02 [−0.50, 2.56] |
| Post hoc, within learners with both: adjusted DiD 4+ minus DiD 2 | −0.11 [−0.90, 0.72] | −0.74 [−1.73, 0.22] | 1.32 [−0.05, 2.68] |
| Adjusted excess, tokens −5 to −1 | 1.53 [1.23, 1.84] | 1.52 [1.19, 1.86] | 1.38 [0.99, 1.75] |
| Adjusted excess, token +1 | 1.20 [0.75, 1.64] | 1.77 [1.17, 2.38] | 0.98 [0.32, 1.63] |
| Adjusted excess, tokens +2 to +5 | 1.71 [1.41, 2.02] | 1.52 [1.14, 1.89] | 1.24 [0.83, 1.67] |
| Adjusted excess, tokens +6 to +20 | 0.89 [0.71, 1.07] | 0.44 [0.24, 0.64] | 0.35 [0.10, 0.60] |
| Raw excess, tokens −5 to −1 | 2.11 [1.81, 2.43] | 1.83 [1.48, 2.18] | 3.28 [2.82, 3.72] |
| Raw excess, token +1 | 1.46 [0.99, 1.91] | 1.95 [1.34, 2.56] | 3.51 [2.76, 4.33] |
| Reduction of pre excess after item-difficulty adjustment (%) | 31 [26, 37] | 16 [10, 24] | 32 [23, 41] |
| Reduction of post excess after item-difficulty adjustment (%) | 25 [22, 29] | 12 [6, 18] | 29 [19, 42] |
| Exploratory, clusters on the easiest third of items: adjusted DiD | 0.15 [−0.16, 0.43] | 0.02 [−0.28, 0.34] | 0.09 [−0.37, 0.57] |
| Exploratory, clusters on the middle third of items: adjusted DiD | 0.57 [0.26, 0.90] | −0.04 [−0.42, 0.33] | −0.16 [−0.73, 0.42] |
| Exploratory, clusters on the hardest third of items: adjusted DiD | 0.42 [0.04, 0.79] | 0.30 [−0.10, 0.70] | −0.46 [−0.96, 0.04] |
| Exploratory, practice continued within 30 min: DiD | 0.53 [0.34, 0.74] | 0.26 [0.05, 0.47] | −0.09 [−0.41, 0.23] |
| Exploratory, break of 30 min or more: DiD | −1.74 [−2.50, −0.93] | −2.77 [−3.68, −1.94] | −2.09 [−3.33, −0.86] |
| Exploratory, practice continued: post excess | 1.48 [1.30, 1.66] | 0.91 [0.70, 1.10] | 0.93 [0.68, 1.19] |
| Exploratory, break: post excess | 0.98 [0.41, 1.53] | 0.00 [−0.68, 0.66] | −0.60 [−1.53, 0.31] |
| Post hoc: P(break of 30 min or more) after cluster (%) | 6.95 [6.63, 7.29] | 6.50 [6.17, 6.86] | 6.12 [5.75, 6.48] |
| Post hoc: P(break) after comparison exercise (%) | 6.07 [5.94, 6.20] | 5.84 [5.72, 5.96] | 6.26 [6.07, 6.44] |
| Post hoc: difference | 0.88 [0.57, 1.20] | 0.66 [0.34, 0.99] | −0.14 [−0.50, 0.22] |

## Table S2. Post hoc analyses of the comparison set

| Analysis | English | Spanish | French |
|---|---|---|---|
| Matching seeds, pre excess: mean (range) | 1.00 (0.97 to 1.03) | 0.73 (0.67 to 0.78) | 1.08 (1.03 to 1.11) |
| Matching seeds, post excess: mean (range) | 1.45 (1.41 to 1.50) | 0.81 (0.76 to 0.84) | 0.75 (0.69 to 0.83) |
| Matching seeds, DiD: mean (range) | 0.45 (0.41 to 0.49) | 0.08 (0.01 to 0.16) | −0.33 (−0.38 to −0.23) |
| Adjacent exercises: excess before | 2.32 [1.93, 2.71] | 2.30 [1.79, 2.80] | 4.04 [3.41, 4.67] |
| Adjacent exercises: excess after | 2.38 [2.02, 2.76] | 1.87 [1.39, 2.33] | 4.10 [3.47, 4.75] |
| Adjacent exercises: DiD | 0.06 [−0.39, 0.53] | −0.43 [−1.00, 0.15] | 0.06 [−0.68, 0.82] |
| Three exercises on each side: DiD | 0.34 [0.07, 0.61] | −0.13 [−0.46, 0.20] | 0.03 [−0.38, 0.46] |
| Error-free comparison exercises only: DiD (token windows) | 0.40 [0.21, 0.59] | 0.07 [−0.17, 0.30] | −0.32 [−0.64, 0.02] |
| Error-free comparison exercises only: DiD (adjacent exercises) | 0.16 [−0.30, 0.61] | −0.09 [−0.71, 0.55] | 0.36 [−0.49, 1.20] |
| Share of comparison anchors from the cluster's bout (%) | 22.0 [21.4, 22.6] | 24.5 [23.8, 25.2] | 26.3 [25.4, 27.3] |
| Overlapping comparisons excluded. Planned keys: clusters | 51,149 | 43,300 | 26,422 |
| Overlapping comparisons excluded. Planned keys: pre excess | 1.71 [1.53, 1.90] | 1.72 [1.50, 1.94] | 2.17 [1.91, 2.44] |
| Overlapping comparisons excluded. Planned keys: post excess | 2.14 [1.96, 2.34] | 1.63 [1.41, 1.86] | 1.79 [1.52, 2.07] |
| Overlapping comparisons excluded. Planned keys: DiD | 0.42 [0.21, 0.63] | −0.09 [−0.33, 0.14] | −0.38 [−0.71, −0.05] |
| Overlapping comparisons excluded. Planned keys: DiD, adjacent exercises | 0.20 [−0.25, 0.66] | −0.37 [−0.89, 0.17] | −0.12 [−0.84, 0.57] |
| Overlapping comparisons excluded. Plus session type: clusters | 46,213 | 38,755 | 23,549 |
| Overlapping comparisons excluded. Plus session type: pre excess | 1.37 [1.18, 1.57] | 1.54 [1.30, 1.78] | 1.98 [1.70, 2.27] |
| Overlapping comparisons excluded. Plus session type: post excess | 1.81 [1.62, 2.00] | 1.44 [1.20, 1.69] | 1.74 [1.42, 2.05] |
| Overlapping comparisons excluded. Plus session type: DiD | 0.44 [0.22, 0.66] | −0.10 [−0.34, 0.15] | −0.24 [−0.61, 0.14] |
| Overlapping comparisons excluded. Plus session type: DiD, adjacent exercises | 0.05 [−0.43, 0.56] | −0.39 [−1.02, 0.23] | −0.16 [−1.02, 0.68] |
| Overlapping comparisons excluded. Plus bout-length band: clusters | 39,579 | 32,851 | 19,911 |
| Overlapping comparisons excluded. Plus bout-length band: pre excess | 1.55 [1.34, 1.79] | 1.65 [1.40, 1.94] | 2.25 [1.89, 2.59] |
| Overlapping comparisons excluded. Plus bout-length band: post excess | 1.91 [1.71, 2.10] | 1.41 [1.14, 1.68] | 2.11 [1.76, 2.45] |
| Overlapping comparisons excluded. Plus bout-length band: DiD | 0.35 [0.09, 0.60] | −0.24 [−0.54, 0.05] | −0.14 [−0.59, 0.35] |
| Overlapping comparisons excluded. Plus bout-length band: DiD, adjacent exercises | −0.02 [−0.58, 0.53] | −0.06 [−0.73, 0.62] | −0.15 [−1.11, 0.85] |
| Overlapping comparisons excluded. Plus position within bout: clusters | 34,988 | 28,404 | 16,851 |
| Overlapping comparisons excluded. Plus position within bout: pre excess | 1.68 [1.46, 1.90] | 1.70 [1.41, 2.01] | 2.13 [1.77, 2.51] |
| Overlapping comparisons excluded. Plus position within bout: post excess | 2.16 [1.94, 2.39] | 1.81 [1.52, 2.10] | 2.18 [1.78, 2.55] |
| Overlapping comparisons excluded. Plus position within bout: DiD | 0.47 [0.21, 0.77] | 0.10 [−0.22, 0.43] | 0.05 [−0.44, 0.54] |
| Overlapping comparisons excluded. Plus position within bout: DiD, adjacent exercises | 0.75 [0.16, 1.36] | −0.20 [−1.01, 0.61] | −0.04 [−1.28, 1.16] |
| Position within bout, overlap allowed, same clusters: pre excess | 1.01 [0.80, 1.23] | 0.98 [0.71, 1.26] | 1.14 [0.79, 1.50] |
| Position within bout, overlap allowed, same clusters: post excess | 1.52 [1.31, 1.74] | 1.22 [0.94, 1.50] | 1.17 [0.81, 1.52] |
| Position within bout, overlap allowed, same clusters: DiD | 0.51 [0.26, 0.78] | 0.23 [−0.07, 0.55] | 0.03 [−0.44, 0.52] |
| Rest-of-bout analysis: clusters | 34,083 | 27,474 | 17,262 |
| Rest of bout: excess | −0.15 [−0.32, 0.03] | −0.34 [−0.54, −0.12] | −1.06 [−1.36, −0.76] |
| Same clusters: pre excess | 0.81 [0.56, 1.05] | 0.37 [0.10, 0.65] | 0.91 [0.53, 1.30] |
| Same clusters: post excess | 1.16 [0.94, 1.42] | 0.41 [0.12, 0.69] | 0.59 [0.19, 0.98] |

Note. Intervals that exclude a rise of one point need not lie within ±1 point: for the three-error threshold the French interval extends below −1 (Table S1). With position within the bout added to the matching, the adjacent-exercise intervals for the English and French courses do not exclude a rise of one point, and with error-free comparison exercises the French adjacent-exercise interval does not. Under the planned symmetric history rule the English and French token-window intervals reach 1.12 and 1.14 (Table S5).

## Table S3. Repeated and new word forms (post hoc)

| Quantity | English | Spanish | French |
|---|---|---|---|
| Share of repeated forms, event pre window (%) | 11.2 [11.1, 11.4] | 7.7 [7.5, 7.8] | 8.9 [8.7, 9.0] |
| Share of repeated forms, event post window (%) | 12.9 [12.7, 13.1] | 9.8 [9.6, 10.0] | 10.1 [9.9, 10.3] |
| Share of repeated forms, comparison pre window (%) | 13.8 [13.6, 14.0] | 10.1 [10.0, 10.3] | 10.4 [10.2, 10.6] |
| Share of repeated forms, comparison post window (%) | 13.5 [13.3, 13.7] | 9.3 [9.2, 9.4] | 9.3 [9.1, 9.5] |
| New word forms: adjusted pre excess | 0.51 [0.34, 0.68] | 0.40 [0.20, 0.61] | 0.51 [0.28, 0.74] |
| New word forms: adjusted post excess | 0.82 [0.65, 0.98] | 0.52 [0.33, 0.71] | 0.15 [−0.07, 0.39] |
| New word forms: adjusted DiD | 0.31 [0.12, 0.50] | 0.12 [−0.09, 0.32] | −0.35 [−0.64, −0.06] |
| Repeated word forms: adjusted pre excess | 2.73 [2.28, 3.20] | 3.16 [2.51, 3.77] | 2.35 [1.67, 3.06] |
| Repeated word forms: adjusted post excess | 2.90 [2.47, 3.30] | 3.68 [3.10, 4.23] | 4.79 [4.09, 5.43] |
| Repeated word forms: adjusted DiD | 0.16 [−0.42, 0.70] | 0.59 [−0.12, 1.33] | 2.54 [1.69, 3.33] |

## Table S4. Exercise durations around clusters (post hoc; differences in adjusted log duration × 100)

| Quantity | English | Spanish | French |
|---|---|---|---|
| Cluster exercise minus comparison exercise | 7.71 [6.40, 9.07], n = 2,498 | 6.41 [5.13, 7.66], n = 2,462 | −3.55 [−5.11, −2.02], n = 1,151 |
| Pre excess (three exercises before) | 0.66 [0.01, 1.31], n = 2,497 | 0.36 [−0.36, 1.07], n = 2,459 | −2.06 [−2.99, −1.19], n = 1,148 |
| Post excess (three exercises after) | 1.76 [1.12, 2.40], n = 2,495 | 0.99 [0.26, 1.69], n = 2,463 | −0.87 [−1.75, −0.02], n = 1,149 |
| DiD | 1.05 [0.19, 1.86], n = 2,494 | 0.54 [−0.41, 1.49], n = 2,457 | 1.13 [−0.12, 2.31], n = 1,146 |
| DiD, adjacent exercises only | 1.03 [−0.24, 2.32], n = 2,493 | 0.20 [−1.36, 1.78], n = 2,444 | 0.36 [−1.52, 2.13], n = 1,145 |
| Complete cases: pre excess | 0.65 [0.01, 1.29], n = 2,494 | 0.34 [−0.39, 1.08], n = 2,457 | −2.00 [−2.86, −1.18], n = 1,146 |
| Complete cases: post excess | 1.71 [1.05, 2.36], n = 2,494 | 0.88 [0.13, 1.59], n = 2,457 | −0.87 [−1.80, 0.04], n = 1,146 |
| Complete cases: DiD | 1.05 [0.20, 1.90], n = 2,494 | 0.54 [−0.42, 1.47], n = 2,457 | 1.13 [−0.03, 2.35], n = 1,146 |

Note. n is the number of learners contributing to each quantity. Pre and post excess in the first block are computed on slightly different learners, so their difference need not equal the DiD; the complete-case block uses the same learners throughout.

## Table S5. Contrasts under three rules for conditioning on error history, forward and time-reversed

| Rule and quantity | English | Spanish | French |
|---|---|---|---|
| No conditioning (planned main analysis): pre excess | 1.00 [0.82, 1.17] | 0.74 [0.53, 0.95] | 1.04 [0.80, 1.29] |
| No conditioning (planned main analysis): post excess | 1.43 [1.26, 1.60] | 0.82 [0.62, 1.01] | 0.79 [0.54, 1.04] |
| No conditioning (planned main analysis): event windows, post − pre | 0.07 [−0.06, 0.20] | 0.09 [−0.06, 0.24] | 0.15 [−0.05, 0.33] |
| No conditioning (planned main analysis): comparison windows, post − pre | −0.37 [−0.50, −0.23] | 0.01 [−0.15, 0.15] | 0.40 [0.16, 0.62] |
| No conditioning (planned main analysis): DiD | 0.43 [0.24, 0.62] | 0.08 [−0.11, 0.28] | −0.25 [−0.57, 0.05] |
| No conditioning (planned main analysis): DiD, learners with clusters of 4+ errors minus learners with clusters of 2 | −0.36 [−1.18, 0.45] | −0.86 [−1.85, 0.15] | 1.12 [−0.41, 2.62] |
| No conditioning (planned main analysis), time-reversed (post hoc): DiD, 4+ minus 2 | 0.55 [−0.23, 1.34] | 0.33 [−0.75, 1.35] | −1.28 [−2.78, 0.24] |
| No conditioning (planned main analysis), time-reversed (post hoc): pre excess | 1.42 [1.25, 1.60] | 0.77 [0.57, 0.97] | 0.73 [0.49, 0.98] |
| No conditioning (planned main analysis), time-reversed (post hoc): post excess | 0.95 [0.78, 1.12] | 0.69 [0.49, 0.90] | 1.07 [0.82, 1.31] |
| No conditioning (planned main analysis), time-reversed (post hoc): DiD | −0.47 [−0.66, −0.29] | −0.08 [−0.29, 0.13] | 0.34 [0.03, 0.66] |
| Prior rule, comparisons only (planned sensitivity): pre excess | 6.45 [6.19, 6.71] | 6.93 [6.64, 7.20] | 9.18 [8.82, 9.56] |
| Prior rule, comparisons only (planned sensitivity): post excess | 1.78 [1.56, 1.99] | 0.90 [0.63, 1.15] | 0.63 [0.26, 0.99] |
| Prior rule, comparisons only (planned sensitivity): event windows, post − pre | 0.03 [−0.11, 0.18] | 0.13 [−0.05, 0.32] | 0.00 [−0.25, 0.24] |
| Prior rule, comparisons only (planned sensitivity): comparison windows, post − pre | 4.71 [4.51, 4.90] | 6.16 [5.94, 6.38] | 8.55 [8.19, 8.91] |
| Prior rule, comparisons only (planned sensitivity): DiD | −4.68 [−4.92, −4.42] | −6.03 [−6.31, −5.74] | −8.55 [−9.04, −8.10] |
| Prior rule, comparisons only (planned sensitivity): DiD, learners with clusters of 4+ errors minus learners with clusters of 2 | −2.44 [−3.31, −1.59] | −2.30 [−3.37, −1.23] | −2.15 [−3.89, −0.51] |
| Prior rule, comparisons only (planned sensitivity), time-reversed (post hoc): DiD, 4+ minus 2 | −0.90 [−1.75, −0.08] | −0.60 [−1.76, 0.47] | −3.46 [−5.11, −1.81] |
| Prior rule, comparisons only (planned sensitivity), time-reversed (post hoc): pre excess | 6.76 [6.52, 7.01] | 6.93 [6.66, 7.21] | 9.03 [8.67, 9.38] |
| Prior rule, comparisons only (planned sensitivity), time-reversed (post hoc): post excess | 1.19 [0.97, 1.40] | 0.86 [0.60, 1.14] | 1.00 [0.66, 1.34] |
| Prior rule, comparisons only (planned sensitivity), time-reversed (post hoc): DiD | −5.58 [−5.83, −5.34] | −6.07 [−6.34, −5.78] | −8.04 [−8.47, −7.60] |
| Symmetric rule, both anchor types (planned sensitivity): pre excess | 0.45 [0.32, 0.58] | 0.58 [0.42, 0.73] | 0.26 [0.04, 0.50] |
| Symmetric rule, both anchor types (planned sensitivity): post excess | 1.32 [1.10, 1.53] | 0.63 [0.36, 0.91] | 0.90 [0.45, 1.37] |
| Symmetric rule, both anchor types (planned sensitivity): event windows, post − pre | 5.51 [5.27, 5.75] | 6.09 [5.81, 6.37] | 8.88 [8.49, 9.28] |
| Symmetric rule, both anchor types (planned sensitivity): comparison windows, post − pre | 4.64 [4.44, 4.85] | 6.04 [5.80, 6.28] | 8.24 [7.84, 8.65] |
| Symmetric rule, both anchor types (planned sensitivity): DiD | 0.87 [0.63, 1.12] | 0.05 [−0.24, 0.37] | 0.63 [0.13, 1.14] |
| Symmetric rule, both anchor types (planned sensitivity): DiD, learners with clusters of 4+ errors minus learners with clusters of 2 | 1.51 [0.53, 2.49] | 0.57 [−0.76, 1.89] | 0.29 [−1.80, 2.32] |
| Symmetric rule, both anchor types (planned sensitivity), time-reversed (post hoc): DiD, 4+ minus 2 | 2.78 [1.82, 3.77] | 1.54 [0.17, 2.88] | −0.29 [−2.16, 1.63] |
| Symmetric rule, both anchor types (planned sensitivity), time-reversed (post hoc): pre excess | 0.66 [0.53, 0.78] | 0.37 [0.22, 0.54] | 0.19 [−0.03, 0.42] |
| Symmetric rule, both anchor types (planned sensitivity), time-reversed (post hoc): post excess | 1.05 [0.82, 1.28] | 0.64 [0.35, 0.92] | 1.64 [1.25, 2.03] |
| Symmetric rule, both anchor types (planned sensitivity), time-reversed (post hoc): DiD | 0.40 [0.13, 0.64] | 0.27 [−0.05, 0.58] | 1.45 [0.99, 1.91] |

Note. Under the prior rule the comparison pre window is selected to contain no recent cluster, so comparison error rates rise from before to after the anchor and the pre excess is inflated; the DiD under that rule is not interpretable as a post-error change. Under the symmetric rule the dose contrast in the English course exceeds one point, and it does so in reversed time as well, so it is not interpretable as an effect of the cluster either.

## Table S6. Flow of learner records and error clusters into the analysis

| Step | English | Spanish | French |
|---|---|---|---|
| Learner records in the training partition | 2,593 | 2,643 | 1,213 |
| Tokens in the training partition | 2,622,957 | 1,973,556 | 926,646 |
| Learner records retained (at least 200 tokens and 20 token errors) | 2,530 | 2,497 | 1,160 |
| Tokens retained | 2,594,768 | 1,930,107 | 916,000 |
| Error clusters (exercises with 2+ token errors) in retained records | 64,956 | 56,478 | 34,750 |
| Excluded: fewer than 20 tokens before or after within the record | 2,525 | 2,596 | 1,306 |
| Clusters with complete windows | 62,431 | 53,882 | 33,444 |
| Excluded: no matched comparison exercise | 10,122 | 8,996 | 5,934 |
| Clusters analysed | 52,309 | 44,886 | 27,510 |
| Learners contributing at least one analysed cluster | 2,508 | 2,475 | 1,160 |

Note. Across courses: 6,449 learner records and 5,523,159 tokens in the training partitions; 6,187 records and 5,440,875 tokens retained; 124,705 clusters from 6,143 learners analysed. The abstract's 6,187 refers to retained records. Both anchor types require complete windows, so the analysis is conditional on the learner continuing for at least 20 further tokens within the training partition; a break of 30 minutes is not a permanent exit.

## Table S7. Sequence of plans and analyses

| Date (2026) | Step | What was known afterwards |
|---|---|---|
| 3 July, 10 August, 18 September | Earlier plan, addendum and post hoc corrections for the same corpus, as cited in the present plan; they concerned individual consistency in, and prediction of, post-cluster error | By 23 September: the one-sided contrast between post-cluster and matched windows, the change from before to after for clusters alone (near zero), and the individual-consistency and predictive analyses |
| Before 23 September | Code test on the first 150 learners of the French course, under no conditioning, the earlier (prior) rule and the symmetric rule | The prior rule distorts comparison pre windows; for those 150 learners, DiD −0.21 [−0.99, 0.53] under no conditioning and 1.85 [0.43, 3.31] under the symmetric rule |
| 23 September | Present plan written; estimator, extractor and plan hashed; files placed in a private Open Science Framework project | Nothing further |
| 23 September | Full-course planned analyses, planned sensitivity analyses and exploratory splits run | Planned results |
| After the planned analyses (September) | Post hoc: position-in-bout matching, repeated word forms, time reversal, break probability | These results |
| November | Post hoc: adjacent exercises, overlapping comparisons, alternative keys, rest of bout, matching seeds, exercise durations, within-learner dose contrast, complete-case durations | These results |

Note. The earlier plans and their analyses are not reported here. The plan document mentions the 150-learner test under the prior rule only; the archived test output also contains the other two rules, as stated above. The date of the private deposit is not independently certified; the archive contains the plan, the hash record and the frozen code. The mapping of theoretical accounts onto three patterns in the Introduction was formulated after the planned results were known.
