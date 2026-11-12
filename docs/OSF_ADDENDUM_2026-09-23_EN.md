# Analysis plan addendum (23 September 2026): Do error clusters cause subsequent errors, or mark episodes that were already difficult?

Project: post-error performance in Duolingo SLAM (registered plan of 3 July 2026; addendum of 10 August 2026; post hoc corrections of 18 September 2026). This addendum specifies new analyses before they are executed. It does not alter any earlier registered quantity. Analyses run under this addendum will be labelled "specified in advance (addendum of 23 September 2026)"; everything else in the eventual report is post hoc.

Status disclosure: The author has previously computed, on these data, (a) the raw contrast between post-cluster windows and matched comparison windows, (b) a raw post-minus-pre contrast for event exercises only (near zero in all courses), and (c) individual-consistency and predictive analyses. The analyses below extend (b) with a matched-comparison pre-window, item-difficulty adjustment, dose and lag decompositions, all of which have not been computed. The author has not examined item-difficulty-adjusted contrasts, comparison-window pre-windows, dose–response or lag profiles.

## Theoretical question

Laboratory work shows that people are more error-prone immediately after an error (Adkins, Zhang & Lee, 2024) and that errors trigger monitoring and orienting responses (Notebaert et al., 2009; Wessel, 2018). In naturalistic learning records, an exercise with several errors is followed by a higher error rate than matched non-error periods. Two accounts of that observation make different predictions:

- Error-triggered account: the cluster itself induces a transient state (orienting, reduced control, frustration) that lowers subsequent accuracy. Predicts excess error AFTER the cluster relative to BEFORE it, larger with larger clusters, and concentrated in the responses immediately following.
- Difficulty-episode account: the cluster marks an episode that was already difficult (harder items, a learner state that began earlier). Predicts excess error of similar size BEFORE and AFTER the cluster, no dose asymmetry, and a substantial share of the excess attributable to item difficulty.

## Data and units

Duolingo SLAM v4.0 training partitions, three courses (en_es, es_en, fr_en); learner inclusion ≥200 tokens and ≥20 token errors (unchanged). Event: an exercise with ≥2 token errors. Anchor: the event's last token (post window) and first token (pre window). Windows: 20 tokens after the exercise end and 20 tokens before the exercise start; the event exercise's own tokens are in neither window. Events and comparisons must have complete pre and post windows within the learner's record. Comparison anchors: non-event exercises of the same learner matched on day band, format, exercise-length band and token-frequency quartile median, up to three per event without replacement within event (reuse across events permitted). Matching seed 20260923.

History conditioning (decided before the full run; see disclosure). The primary analysis imposes NO condition on the event history of either anchor type: the only difference between an event and a comparison exercise is the number of errors in that exercise. The earlier rule (comparisons excluded if a prior event ended within 20 tokens) conditions the comparison's pre window on the absence of errors and therefore cannot be used in a symmetric design; it is retained as a sensitivity analysis ("prior rule"), together with the symmetric-history rule applied to both anchor types.

Disclosure: before the full run, a code smoke test on the first 150 learners of one course (fr_en) was executed under the earlier prior-event rule; it showed that this rule produces a large pre/post asymmetry in comparison windows (comparison post minus pre ≈ +7 pp) purely by selection. The primary rule was changed to "no history conditioning" on that basis, before any full-course analysis and before any dose, lag, difficulty-share or session-gap result was examined beyond that subset. The smoke-test output is retained in the archive (`outputs/smoke_fr_en_150.txt`).

## Quantities

For each learner and window position p ∈ {−20,…,−1, +1,…,+20}: mean error in event windows E(p) and in the averaged matched comparison windows C(p). Excess(p) = E(p) − C(p). Pre excess = mean over −20…−1; post excess = mean over +1…+20.

Primary contrast (difference in differences): DiD = (E_post − E_pre) − (C_post − C_pre). Under the difficulty-episode account DiD ≈ 0; under the error-triggered account DiD > 0.

Item-difficulty adjustment: for each token surface form within a course, leave-one-learner-out error rate d(w) = (errors on w by all other learners)/(occurrences of w by all other learners); tokens with fewer than 20 other-learner occurrences use the part-of-speech leave-one-learner-out rate. Adjusted error = error − d(w). All quantities above are recomputed on adjusted errors. Share explained by item difficulty = 1 − adjusted post excess / raw post excess (reported per course with a bootstrap interval; no directional prediction).

Dose: events with exactly 2, exactly 3, and ≥4 errors. Lag: adjusted excess and DiD at position +1 alone, positions +2…+5, positions +6…+20.

Inference: learner-level percentile bootstrap, 2,000 resamples, seed 20260923, learners weighted equally, matched sets held fixed; each course reported separately (three within-platform replications). Smallest effect size of interest for DiD: 1.0 percentage point (about one third of the raw post-cluster excess previously observed).

## Hypotheses (specified before execution)

H1 (symmetry). In each course, the 95% bootstrap interval of the raw DiD lies within ±1.0 pp, and the pre excess is positive with an interval excluding zero. Disconfirmed if DiD > 1.0 pp with an interval excluding zero in at least two courses.

H2 (dose). The DiD does not increase monotonically across cluster sizes 2, 3, ≥4; the ≥4 DiD interval includes 1.0 pp or lies below it. Disconfirmed if DiD(≥4) − DiD(2) > 1.0 pp with an interval excluding zero in at least two courses.

H3 (lag). The adjusted excess at position +1 does not exceed the adjusted excess at positions −5…−1 by more than 1.0 pp (an orienting-type transient would produce an immediate spike). Reported per course.

H4 (item difficulty; descriptive). The share of the raw post excess explained by item difficulty is reported per course with intervals. No directional prediction is registered; the result is used to characterise the episode (content-driven versus learner-state-driven), not to test H1.

Exploratory (labelled as such): moderation by the surprise of the cluster (mean leave-one-learner-out difficulty of the event exercise's tokens, tertiles); post excess split by whether the first post-window exercise begins within 30 minutes of the event (same session) or later, acknowledging that session boundaries also change content.

Sensitivities: windows of 10 and 30 tokens; threshold of 3 errors; the prior rule and the symmetric-history rule described above.

## What will not be done

No new individual-difference reliability or prediction analyses; those results are retained in the archive and summarised in one paragraph with reference to the companion reports. No new hypotheses will be added after seeing the results; any additional analysis will be labelled post hoc.

Code: `analysis/p1_symmetric.py` (frozen with SHA-256 recorded in `outputs/plan_freeze.json` at the time of registration). Software: Python 3.11, pandas, numpy, scipy.
