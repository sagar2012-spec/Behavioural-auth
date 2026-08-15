# Keystroke Dynamics Signal — Results Notes

Rough notes to polish into Methodology and Evaluation chapters later. Everything factual captured while fresh.

---

## 1. What this signal is

- Keystroke dynamics = identifying a user by the rhythm of how they type.
- Fixed-text type (everyone types the same password), not free-text.
- This is the strongest of the implemented signals and the one that uses real machine learning.
- It answers the earlier gap where the framework claimed ML but only used statistics (mean/stddev). This signal is genuine ML.

---

## 2. Dataset

- CMU Keystroke Dynamics Benchmark Dataset (Killourhy and Maxion).
- Source: cs.cmu.edu/~keystroke/  — free, public, standard benchmark.
- File: DSL-StrongPasswordData.csv
- Size: 20,400 rows, 34 columns.
- 51 users, each typed the password ".tie5Roanl" 400 times across 8 sessions.
- Columns:
  - subject = which user (the label, e.g. s002)
  - sessionIndex, rep = which session/repetition (not used for modelling)
  - 31 timing columns = the behavioural features:
    - H.<key> = hold time (dwell) — how long a key is held down
    - DD.<key>.<key> = down-down time — gap between pressing one key and the next
    - UD.<key>.<key> = up-down time (flight) — gap between releasing one key and pressing the next
- Why this dataset: gives 51 real users without recruiting anyone, needs no ethics approval, is the standard benchmark so results are comparable to published work.
- Justification for using benchmark instead of live volunteer typing: keystroke is the most data-hungry signal; a few volunteers typing a few times gives too little data to train well. Benchmark gives rigorous training/testing. Live capture from volunteers noted as optional/future work.

---

## 3. Model choice

- One-Class SVM (Support Vector Machine) from scikit-learn.
- Why one-class: in real enrolment you only have the genuine user's data, not the attackers'. A one-class classifier learns "normal" from just the genuine user and flags anything too different. This matches reality, so it is a defensible, honest choice.
- Features scaled with StandardScaler so all timing columns are on a comparable range (no single column dominates).

---

## 4. Method / experiment setup

- Pick one user as genuine. Everyone else = impostors.
- Shuffle the genuine user's 400 samples (random_state=42 for reproducibility), then split 50/50: train on half, test on the other half.
- Train the model on ONLY the genuine user's training half.
- Test:
  - Genuine test half → how often correctly ACCEPTED (should be high)
  - All impostor samples → how often correctly REJECTED (should be high)
- Prediction output: +1 = looks genuine, -1 = looks like impostor.

---

## 5. Tuning experiment (IMPORTANT — this is a real result showing the tradeoff)

### First attempt (too strict)
- Settings: gamma="auto", nu=0.1, trained on first 200 samples only.
- Result: genuine accepted 81/200 (~40%), impostors rejected 19514/20000 (~97.5%).
- Problem: far too strict, rejected the genuine user 60% of the time. Unusable.
- Cause: trained only on earliest samples so it learned a narrow slice; keystroke timing varies between sessions.

### Fix 1: broaden training data + retune
- Changed to shuffle + 50/50 split (sees all sessions), gamma="scale", nu=0.05.
- Result: genuine accepted 155/200 (~78%), impostors rejected 18155/20000 (~91%).
- Genuine acceptance jumped, impostor rejection dipped slightly. First clear view of the tradeoff.

### Tried varying nu (found it doesn't matter here)
- nu = 0.01, 0.02, 0.05, 0.1, 0.2 → all basically 77% genuine, 91% impostor. Almost no change.
- Finding: nu is not the lever for this data.

### Varying gamma (this IS the lever — THE TRADEOFF CURVE)
Table (nu fixed at 0.05):

| gamma  | genuine accepted | impostors rejected |
|--------|------------------|--------------------|
| 0.001  | 97.0%            | 32.0%              |
| 0.005  | 95.5%            | 37.3%              |
| 0.01   | 93.5%            | 52.5%              |
| 0.05   | 71.0%            | 97.7%              |
| 0.1    | 53.5%            | 99.9%              |
| scale  | 77.5%            | 90.8%              |

- Clear security-usability tradeoff: as gamma rises, genuine acceptance falls and impostor rejection climbs.
- Low gamma = loose boundary = accepts almost everyone (bad security).
- High gamma = tight boundary = rejects almost everyone (bad usability).
- This table is a KEY FIGURE for the evaluation chapter — it demonstrates the tradeoff empirically from my own system.
- Method note worth mentioning: tried nu first, found it flat, correctly moved to gamma. Shows real experimental method.

### Chosen operating point
- gamma="scale", nu=0.05 → 77.5% genuine, 90.8% impostor (for s002).
- Justification: most balanced point; strong impostor rejection while keeping genuine acceptance usable; any remaining weakness compensated by the multi-signal vote.

---

## 6. Cross-user validation (turns "worked for one user" into "works across users")

Ran the same test across the first 10 users, each in turn as genuine, using gamma="scale", nu=0.05.

| user | genuine accepted | impostors rejected |
|------|------------------|--------------------|
| s002 | 77.5%            | 90.8%              |
| s003 | 72.0%            | 95.6%              |
| s004 | 76.0%            | 97.7%              |
| s005 | 77.5%            | 99.6%              |
| s007 | 82.5%            | 92.9%              |
| s008 | 71.0%            | 92.4%              |
| s010 | 73.5%            | 99.9%              |
| s011 | 76.0%            | 87.1%              |
| s012 | 74.0%            | 98.6%              |
| s013 | 76.0%            | 97.2%              |
| **AVG** | **75.6%**     | **95.2%**          |

- Headline result: across 10 users, average 75.6% genuine acceptance, 95.2% impostor rejection.
- Consistency is the key point: genuine 71–82%, impostor 87–99%. Tight band = not a fluke, holds across people.
- Per-user variation is a real finding: some users more distinctive typists than others (s005, s010 >99% impostor rejection; s011 easier at 87%). Real biometric systems show this too.

---

## 7. How to FRAME this in the write-up (don't undersell it)

- 75.6% genuine acceptance is NOT disappointing — this is ONE signal alone.
- The whole framework thesis is that single signals are imperfect, which is WHY they combine in a vote.
- A keystroke signal rejecting 95% of impostors alone, combined with login timing, location, session signals via majority vote → stronger than any single signal.
- These numbers are the EVIDENCE for the multi-signal argument, not a weakness.

---

## 8. Limitations to record for this signal

- Only tested on 10 of 51 users (could extend to all 51 — quick to do).
- Fixed-text only (everyone types same password). Free-text is harder, noted as future work.
- Cold-start: needs enough samples before it authenticates reliably.
- Benchmark data, not live volunteer typing. Live capture in the app is optional/future work; if added, expect weaker numbers due to limited volunteer data.
- Password-manager / autofill / copy-paste breaks keystroke capture (same intermediary-tool limitation as login timing).

---

## 9. Reproducibility notes (for methodology chapter)

- Library: scikit-learn, OneClassSVM.
- random_state=42 on the shuffle for repeatable splits.
- StandardScaler fit on training data only, then applied to test and impostor data.
- Operating point: gamma="scale", nu=0.05.
- Script: ml/keystroke_model.py

---

## 10. What still needs doing (not part of results, just a reminder)

- Wire this model into the app as the 4th live signal in the vote.
- Decide vote logic across all signals (majority of implemented).
- Build drift-and-update loop.
- Build dashboard.
- Structured genuine-vs-impostor testing of the full system.
- Optionally extend keystroke test to all 51 users for a stronger final number.
