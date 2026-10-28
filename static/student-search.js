"use strict";

function matchesStudentName(name, query) {
	const normalizedQuery = String(query).trim().toLocaleLowerCase();
	return String(name).toLocaleLowerCase().includes(normalizedQuery);
}

if (typeof module !== "undefined" && module.exports) {
	module.exports = { matchesStudentName };
}
