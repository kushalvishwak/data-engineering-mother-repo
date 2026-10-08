---
id: behavioral-project-story
title: Project Story and Behavioural Round
tier: 3
priority: must-know
sources: [cookbook, obenner/data-quality.md, obenner/system-design.md, obenner/observability.md, devinterview]
---

# Project Story and Behavioural Round

## Say it in one line
Your project story is a rehearsed three-minute narrative — problem, data, decisions, trade-offs, result, what you would change — built so that every claim inside it survives the follow-up question.

## Must be able to recite
The three sources carry no behavioural questions; this node is standard interview practice plus the follow-ups a machine-learning student project always attracts, so treat every unmarked item here as `(not in sources, but standard)`.
- **The three-minute shape** — 20 seconds on the problem and why it mattered, 30 on the data (source, size, shape), 60 on what you built and the two decisions you made, 30 on trade-offs, 20 on the result with a number, 10 on what you would change.
- **Lead with the problem, not the stack** — "loan applications were scored by hand, about four hours each" earns a follow-up; "I used pandas and scikit-learn" ends the conversation.
- **Quantify everything you can** — rows, megabytes, number of sources, runtime before and after, F1, hours saved; a number proves you measured and it steers the interviewer to ground you are ready for.
- **Name exactly two decisions** — one architecture or modelling choice and one trade-off where you knowingly gave something up; more than two and the listener loses the thread.
- **Have a real "what I would change"** — tests, orchestration, incremental loads, monitoring, a proper temporal split; "more data" and "more tuning" both read as no reflection.
- **Dataset provenance** — where the data came from, how it was collected, whether you were allowed to use it, its size, and what you did about missing, duplicate and outlier rows.
- **Split by time when the data has time** — train on the earlier period and test on the later one; a random split on time-ordered rows leaks the future into training and inflates the score you are quoting.
- **State the class balance** — give the positive rate; at two percent positives, accuracy is just the majority-class baseline, so you report precision, recall and F1 at a chosen threshold, and PR-AUC rather than ROC-AUC when positives are rare.
- **Precision versus recall in business terms** — precision is "of the ones I flagged, how many were real", recall is "of the real ones, how many did I catch"; in fraud or credit you pick the operating point from the cost of a missed case against the cost of an investigator's time.
- **F1 and the confusion matrix** — precision is TP/(TP+FP), recall is TP/(TP+FN), F1 is their harmonic mean 2PR/(P+R); be able to compute all of it from four numbers on paper.
- **Leakage is the flaw they hunt for** — any feature that uses information unavailable at prediction time, including post-outcome fields, target encoding fitted on the full dataset, and a scaler or imputer fitted before the split.
- **Be honest about deployment** — say exactly what shipped: a notebook, a Streamlit demo, a scheduled scoring job, or a real endpoint; "it stayed a notebook, and here is how I would ship it" beats a production claim that collapses in one question.
- **Have one real failure ready** — a leaky feature, a join that fanned out, a memory blow-up, a schema change — with how you spotted it and what you did, because "nothing went wrong" means you did not look.
- **STAR for the soft questions** — Situation in one sentence, Task as your specific responsibility, Action as what you personally did, Result as something measurable plus the lesson; say "I" for actions and "we" only for context.
- **Bring three questions back** — one on the team's stack and data volumes, one on how work arrives and gets reviewed, one on what a good first six months looks like; leave pay and perks out of a technical round.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it. Only the process and productionisation questions below trace to the sources; the rest is the standard round for this role, marked once here rather than on every line `(not in sources, but standard)`.
- Walk me through your project. — Three minutes in the fixed shape, problem first, ending on the result and the one thing you would change.
- Why this dataset, where did it come from, and how was it collected? — Name the source, the collection method, the licence or permission, and the period it covers.
- How big was the dataset? — Rows, columns and size on disk; if it was small, say so plainly and say what would change at a hundred times the volume.
- How did you split train and test, and was there a time dimension? — If rows are time-ordered, split by time and say why; if you split randomly on temporal data, call it out as the mistake it was.
- Was the data balanced? — Give the positive rate, then the technique (class weights or resampling applied inside the training folds only) and the metric you judged it by.
- Why not accuracy? — With rare positives, accuracy is the majority baseline; precision, recall, F1 and PR-AUC say something about the minority class you actually care about.
- Define precision, recall and F1, and compute them from this confusion matrix. — TP/(TP+FP), TP/(TP+FN), and the harmonic mean; practise it on paper because it is asked cold.
- How did you handle missing values, duplicates and outliers? — Say the rule and the reason (median imputation, drop above a null threshold, dedup on the business key), not just the function name.
- Which features mattered and how do you know? — Importances or coefficients plus an ablation, and a sanity check that no important feature is leaking the label.
- Did you deploy it, and what would a real deployment look like? — Be exact about what shipped, then describe the batch scoring job or endpoint, the schedule, and where predictions would land.
- ★ How would you turn that notebook into a production pipeline? — Extract into idempotent steps, orchestrate with dependencies and retries, land raw immutably, version the model and the code, add tests and logging, and alert on the freshness of the output table.
- ★ How did you make sure the data was correct? — Name the checks: row counts against the source, not-null and range checks on key fields, uniqueness on the identifier, and a spot reconciliation against the raw file.
- If it were retrained monthly, how would you know it had degraded? — Monitor input distribution drift and the prediction mix, then the realised outcome metric once labels arrive, and alert on a shift rather than waiting for a complaint.
- What was the hardest bug and how did you find it? — One concrete bug, the symptom, the way you narrowed it down, and the fix.
- What would you do with three more months? — An engineering answer: proper temporal validation, a pipeline, monitoring, a simpler baseline to compare against.
- Why did you choose that model over a simpler baseline? — Give the baseline's number and the gain; if the gain was small, say the simpler model was the right choice.
- What was your specific contribution in a group project? — Your part in one sentence, then the interfaces you owned; do not narrate the whole team's work.
- Tell me about a disagreement with a teammate. — STAR: the technical substance, how you resolved it with evidence, and what you would do earlier next time.
- Tell me about a time you failed or missed a deadline. — Own the cause, describe the recovery, end on the process change; never blame a teammate.
- Tell me about a time you had to learn something quickly. — Name the thing, the resource, the timebox, and what you shipped with it.
- How do you prioritise when several things are urgent? — Ask which consumer breaks first and what the cost of delay is, then confirm the order with whoever owns it rather than guessing silently.
- What do you do when requirements are unclear? — Write down your interpretation with the assumptions listed, get it confirmed in one message, then build the smallest version that can be shown.
- Why data engineering rather than data science? — Say you prefer building the systems the analysis depends on, and point at the part of your project that was actually pipeline work.
- Why this company or this bank? — One concrete thing about the domain or the scale, plus what you want to learn there; nothing that is only true of every employer.
- What are your strengths and weaknesses? — One strength backed by an example from the project, one real weakness with the concrete correction in progress.
- Have you worked in Agile — what is Scrum, a sprint, a stand-up, an OKR, and what is Jira used for? — Scrum is timeboxed sprints with stand-ups, review and retro; OKRs are objectives with measurable key results; Jira is where the tickets and the board live.
- Do you use Git — what are branches, commits and pull requests, and what is CI/CD? — Branch per change, small commits, pull request for review, continuous integration builds and tests every push, continuous deployment releases the passing build automatically.
- How do you handle feedback on your code? — Treat review comments as the cheapest bug-fix available, ask when a comment is unclear, and say what you changed.
- Explain something technical to a non-technical stakeholder. — Pick one from your project, lead with the business consequence, and use no tool names.
- Do you have any questions for us? — Ask the three you prepared; having none reads as no interest.

## Traps
- Reciting the tech stack instead of the problem and the decisions — the interviewer cannot ask a good follow-up about a list of libraries.
- Saying "we" for everything in a group project — if your specific contribution never surfaces, it is assumed to be small.
- Defending a random train/test split on time-ordered data — say it leaks future information and that you would split by time; owning the flaw scores better than arguing.
- Quoting accuracy on an imbalanced dataset — 98 percent accuracy at a 2 percent positive rate is the do-nothing baseline, and the interviewer knows it.
- Overclaiming scale or deployment — "millions of records" for a 50,000-row CSV, or "in production" for a local notebook, collapses on one question and costs you the rest of the round.
- Turning a failure question into a humblebrag — "I work too hard" is a non-answer; give a real mistake with the correction attached.

## Graph
- **Needs first:** [[system-design-scenarios]]
- **Leads to:** —
- **Asked together with:** —
