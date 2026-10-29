"use strict";

const form = document.querySelector("#analysis-form");
const studentRows = document.querySelector("#student-rows");
const thresholdInput = document.querySelector("#pass-mark");
const formStatus = document.querySelector("#form-status");
const saveButton = document.querySelector("#save-analysis");
const invalidWarning = document.querySelector("#invalid-warning");
const historyRows = document.querySelector("#history-rows");
const historyStatus = document.querySelector("#history-status");
const resultsStatus = document.querySelector("#results-status");
const studentSearchInput = document.querySelector("#student-search");
const studentSearchStatus = document.querySelector("#student-search-status");
const nearPassFilter = document.querySelector("#near-pass-filter");
let nextStudentNumber = studentRows.querySelectorAll("[data-student-row]").length + 1;
let isSaving = false;
let selectedAnalysisRequest = 0;
let selectedPassMark = null;

function createStudentRow(studentNumber) {
	const row = document.createElement("tr");
	row.dataset.studentRow = "";

	const nameCell = document.createElement("td");
	const nameInput = document.createElement("input");
	nameInput.className = "student-input";
	nameInput.name = "student-name";
	nameInput.type = "text";
	nameInput.setAttribute("aria-label", `Student ${studentNumber} name`);
	nameCell.append(nameInput);

	const marksCell = document.createElement("td");
	const marksInput = document.createElement("input");
	marksInput.className = "student-input";
	marksInput.name = "student-marks";
	marksInput.type = "text";
	marksInput.inputMode = "decimal";
	marksInput.setAttribute("aria-label", `Student ${studentNumber} marks`);
	marksCell.append(marksInput);

	const actionCell = document.createElement("td");
	const removeButton = document.createElement("button");
	removeButton.className = "remove-button";
	removeButton.type = "button";
	removeButton.textContent = "Remove";
	removeButton.setAttribute("aria-label", `Remove student ${studentNumber}`);
	actionCell.append(removeButton);

	row.append(nameCell, marksCell, actionCell);
	return row;
}

function collectFormData() {
	const thresholdText = thresholdInput.value.trim();
	if (thresholdText === "") {
		formStatus.textContent = "Enter a passing threshold from 0 to 100.";
		thresholdInput.focus();
		return null;
	}

	const passMark = Number(thresholdText);
	if (!Number.isFinite(passMark) || passMark < 0 || passMark > 100) {
		formStatus.textContent = "Passing threshold must be a finite number from 0 to 100.";
		thresholdInput.focus();
		return null;
	}

	const students = Array.from(studentRows.querySelectorAll("[data-student-row]"), (row) => ({
		name: row.querySelector('[name="student-name"]').value,
		marks: row.querySelector('[name="student-marks"]').value,
	}));

	return { pass_mark: passMark, students };
}

function setFormBusy(isBusy) {
	form.querySelectorAll("input, button:not(#save-analysis)").forEach((control) => {
		control.disabled = isBusy;
	});
	saveButton.disabled = isBusy;
	saveButton.textContent = isBusy ? "Saving…" : "Save analysis";
}

function resetForm() {
	form.reset();
	studentRows.replaceChildren();
	for (let studentNumber = 1; studentNumber <= 3; studentNumber += 1) {
		studentRows.append(createStudentRow(studentNumber));
	}
	nextStudentNumber = 4;
}

function appendCell(row, value) {
	const cell = document.createElement("td");
	cell.textContent = value;
	row.append(cell);
	return cell;
}

async function refreshHistory() {
	historyStatus.textContent = "Loading saved analyses…";
	try {
		const response = await fetch("/analyses");
		const payload = await response.json();
		if (!response.ok) {
			throw new Error(payload?.error?.message || `Request failed with HTTP ${response.status}.`);
		}

		const analyses = payload.analyses;
		historyRows.replaceChildren();
		if (analyses.length === 0) {
			const row = document.createElement("tr");
			const cell = appendCell(row, "No saved analyses yet. Add student names and marks above, then choose Save analysis to see the results here.");
			cell.colSpan = 6;
			cell.className = "empty-state";
			historyRows.append(row);
			historyStatus.textContent = "No saved analyses yet. Add student names and marks above, then choose Save analysis to see the results here.";
			return;
		}

		analyses.forEach((analysis) => {
			const row = document.createElement("tr");
			appendCell(row, String(analysis.id));
			appendCell(row, analysis.created_at ?? "N/A");
			appendCell(row, String(analysis.pass_mark));
			appendCell(row, String(analysis.valid_count));
			appendCell(row, String(analysis.invalid_count));
			const actionCell = document.createElement("td");
			const viewButton = document.createElement("button");
			viewButton.className = "button button-secondary view-button";
			viewButton.type = "button";
			viewButton.textContent = "View";
			viewButton.addEventListener("click", () => loadAnalysis(analysis.id));
			actionCell.append(viewButton);
			row.append(actionCell);
			historyRows.append(row);
		});
		historyStatus.textContent = `${analyses.length} saved ${analyses.length === 1 ? "analysis" : "analyses"}.`;
	} catch (error) {
		historyStatus.textContent = `Could not load saved analyses: ${error.message}`;
	}
}

function renderAnalysis(analysis) {
	document.querySelector("#selected-analysis-id").textContent = String(analysis.id);
	document.querySelector("#selected-pass-mark").textContent = String(analysis.pass_mark);

	const resultRows = document.querySelector("#result-students");
	resultRows.replaceChildren();
	studentSearchInput.value = "";
	nearPassFilter.checked = false;
	studentSearchInput.disabled = analysis.students.length === 0;
	nearPassFilter.disabled = analysis.students.length === 0;
	selectedPassMark = Number(analysis.pass_mark);
	studentSearchStatus.textContent = "";
	studentSearchStatus.hidden = true;
	if (analysis.students.length === 0) {
		const row = document.createElement("tr");
		const cell = appendCell(row, "No valid student records.");
		cell.colSpan = 3;
		cell.className = "empty-state";
		resultRows.append(row);
	} else {
		analysis.students.forEach((student) => {
			const row = document.createElement("tr");
			row.dataset.resultStudent = "";
			appendCell(row, student.name);
			appendCell(row, String(student.marks));
			appendCell(row, student.status);
			resultRows.append(row);
		});
	}

	const summary = analysis.summary;
	document.querySelector("#result-average").textContent = summary.average === null
		? "N/A"
		: Number(summary.average).toFixed(2);
	document.querySelector("#result-highest").textContent = summary.highest_scorer === null
		? "N/A"
		: `${summary.highest_scorer.name} (${summary.highest_scorer.marks})`;
	document.querySelector("#result-valid-count").textContent = String(summary.valid_count);
	document.querySelector("#result-invalid-count").textContent = String(summary.invalid_count);
	document.querySelector("#result-pass-count").textContent = String(summary.pass_count);
	document.querySelector("#result-fail-count").textContent = String(summary.fail_count);
}

function filterResultStudents() {
	const query = studentSearchInput.value.trim();
	const rows = Array.from(document.querySelectorAll("#result-students [data-result-student]"));
	let visibleCount = 0;

	rows.forEach((row) => {
		const matches = matchesStudentFilters({
			name: row.cells[0].textContent,
			marks: row.cells[1].textContent,
		}, query, nearPassFilter.checked, selectedPassMark);
		row.hidden = !matches;
		if (matches) {
			visibleCount += 1;
		}
	});

	const filterMessage = studentFilterStatus(query, nearPassFilter.checked, visibleCount, rows.length);
	studentSearchStatus.textContent = filterMessage;
	studentSearchStatus.hidden = filterMessage === "";
}

async function loadAnalysis(analysisId) {
	const requestNumber = ++selectedAnalysisRequest;
	resultsStatus.textContent = `Loading analysis ${analysisId}…`;
	try {
		const response = await fetch(`/analyses/${encodeURIComponent(analysisId)}`);
		const payload = await response.json();
		if (!response.ok) {
			throw new Error(payload?.error?.message || `Request failed with HTTP ${response.status}.`);
		}
		if (requestNumber !== selectedAnalysisRequest) {
			return true;
		}

		renderAnalysis(payload);
		resultsStatus.textContent = `Showing saved analysis ${analysisId}.`;
		return true;
	} catch (error) {
		if (requestNumber === selectedAnalysisRequest) {
			resultsStatus.textContent = `Could not load analysis ${analysisId}: ${error.message}`;
		}
		return false;
	}
}

async function submitAnalysis() {
	if (isSaving) {
		return;
	}

	const formData = collectFormData();
	if (!formData) {
		return;
	}

	isSaving = true;
	setFormBusy(true);
	formStatus.textContent = "Saving…";
	invalidWarning.hidden = true;
	try {
		let response;
		try {
			response = await fetch("/analyses", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(formData),
			});
		} catch {
			formStatus.textContent = "The connection failed before the server confirmed the save. The outcome is unknown. Check saved history before retrying; this page will not repeat the request.";
			return;
		}

		let payload;
		try {
			payload = await response.json();
		} catch {
			payload = null;
		}
		if (!response.ok) {
			const message = payload?.error?.message || "The server rejected the analysis.";
			formStatus.textContent = `Could not save the analysis (HTTP ${response.status}): ${message}`;
			return;
		}
		if (!payload || !Number.isInteger(payload.id)) {
			formStatus.textContent = "The server responded, but did not provide a usable save confirmation. The outcome is unknown. Check saved history before retrying.";
			return;
		}

		const invalidCount = Number(payload.invalid_count) || 0;
		const validCount = Number(payload.valid_count) || 0;
		formStatus.textContent = `Analysis ${payload.id} saved. ${validCount} valid and ${invalidCount} invalid records.`;
		if (invalidCount > 0) {
			invalidWarning.textContent = `${invalidCount} invalid student ${invalidCount === 1 ? "record was" : "records were"} skipped.`;
			invalidWarning.hidden = false;
		}

		resetForm();
		const [analysisLoaded] = await Promise.all([
			loadAnalysis(payload.id),
			refreshHistory(),
		]);
		if (!analysisLoaded) {
			formStatus.textContent = `Analysis ${payload.id} was saved, but its results could not be displayed. The saved analysis is still in history.`;
		}
	} finally {
		isSaving = false;
		setFormBusy(false);
	}
}

document.querySelector("#add-student").addEventListener("click", () => {
	const row = createStudentRow(nextStudentNumber);
	studentRows.append(row);
	nextStudentNumber += 1;
	row.querySelector('[name="student-name"]').focus();
});

studentSearchInput.addEventListener("input", filterResultStudents);
nearPassFilter.addEventListener("change", filterResultStudents);

form.addEventListener("click", (event) => {
	const removeButton = event.target.closest(".remove-button");
	if (removeButton) {
		removeButton.closest("[data-student-row]").remove();
	}
});

form.addEventListener("submit", (event) => {
	event.preventDefault();
	submitAnalysis();
});

refreshHistory();
