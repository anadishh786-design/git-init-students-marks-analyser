"use strict";

const form = document.querySelector("#analysis-form");
const studentRows = document.querySelector("#student-rows");
const thresholdInput = document.querySelector("#pass-mark");
const formStatus = document.querySelector("#form-status");
let nextStudentNumber = studentRows.querySelectorAll("[data-student-row]").length + 1;

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

document.querySelector("#add-student").addEventListener("click", () => {
	const row = createStudentRow(nextStudentNumber);
	studentRows.append(row);
	nextStudentNumber += 1;
	row.querySelector('[name="student-name"]').focus();
});

form.addEventListener("click", (event) => {
	const removeButton = event.target.closest(".remove-button");
	if (removeButton) {
		removeButton.closest("[data-student-row]").remove();
	}
});

form.addEventListener("submit", (event) => {
	event.preventDefault();
	const formData = collectFormData();
	if (formData) {
		formStatus.textContent = `Threshold is valid. ${formData.students.length} student rows ready; saving is added in Stage 4.`;
	}
});