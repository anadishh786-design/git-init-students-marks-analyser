"use strict";

function matchesStudentName(name, query) {
	const normalizedQuery = String(query).trim().toLocaleLowerCase();
	return String(name).toLocaleLowerCase().includes(normalizedQuery);
}

function isWithinFivePointsBelow(marks, passMark) {
	const score = Number(marks);
	const threshold = Number(passMark);
	return Number.isFinite(score) && Number.isFinite(threshold)
		&& score >= threshold - 5 && score < threshold;
}

function matchesStudentFilters(student, query, nearPassOnly, passMark) {
	return matchesStudentName(student.name, query)
		&& (!nearPassOnly || isWithinFivePointsBelow(student.marks, passMark));
}

function studentFilterStatus(query, nearPassOnly, visibleCount, totalCount) {
	const normalizedQuery = String(query).trim();
	if (totalCount === 0 || visibleCount > 0 || (normalizedQuery === "" && !nearPassOnly)) {
		return "";
	}
	if (normalizedQuery !== "" && nearPassOnly) {
		return `No students match "${normalizedQuery}" within 5 points below passing.`;
	}
	if (normalizedQuery !== "") {
		return `No students match "${normalizedQuery}".`;
	}
	return "No students are within 5 points below passing.";
}

if (typeof module !== "undefined" && module.exports) {
	module.exports = {
		isWithinFivePointsBelow,
		matchesStudentFilters,
		matchesStudentName,
		studentFilterStatus,
	};
}
