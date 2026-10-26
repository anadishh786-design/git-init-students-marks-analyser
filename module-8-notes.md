# Module 8: One Small, Smart Improvement

## Problem

A teacher struggles to get started when the dashboard has no saved analyses because the empty history only says that it is empty and does not explain what to do next.

## Two possible solutions

1. Explain how to create the first analysis in the empty history state.
2. Add a search field to help locate a student in saved results.

I chose the empty-state guidance because it helps every teacher who opens the dashboard before saving anything. It is a small copy change that leaves saved marks and thresholds untouched.

## Example

When a teacher opens the dashboard and there are no saved analyses, the dashboard should explain how to create the first one.

## Implementation

The empty history row and its live status now say: “No saved analyses yet. Add student names and marks above, then choose Save analysis to see the results here.” The initial HTML placeholder and the message rendered after the API responds use the same guidance.

## Demo

1. Open the dashboard with an empty analysis history.
2. The history area explains that the teacher should add student names and marks in the form above and choose **Save analysis**.
3. Save an analysis. The history row and its empty-state guidance are replaced by the saved analysis, while its results appear below.

## Checks

| Check | Expected | Actual |
| --- | --- | --- |
| No saved analyses | The history row and status explain how to create the first analysis. | The initial HTML and the JavaScript empty-history branch contain the same instruction. Browser execution could not be verified in this environment because Python is unavailable. |
| One or more saved analyses | Saved rows and View buttons appear; the empty-state guidance is removed. | The existing non-empty branch replaces the history rows before rendering saved records. This path was inspected, but browser execution could not be verified in this environment. |

No focused automated test was added: this change only replaces static UI copy and introduces no new logic. The existing tests were attempted with `.venv\Scripts\python.exe -m unittest discover -v`, but could not start because `.venv` references a Python installation that no longer exists. The project currently has no Python executable available on PATH.

## Limitation and deliberate omission

The guidance only appears in the empty history state; it does not provide sample data or an interactive shortcut to the form. Student search was deliberately left out because it solves a separate problem.

## AI assistance and personal verification

AI assistance was used to identify the empty-state problem, choose the smaller solution, and edit the history messages and this note. I checked that the initial HTML and the JavaScript empty-history branch show matching guidance, and reviewed the existing non-empty history branch. I could not personally verify the live browser rendering or run the Python suite because Python is unavailable in this environment.

## If simplified further

Keep one short sentence in the empty history row telling the teacher to add student names and marks, then choose **Save analysis**.
