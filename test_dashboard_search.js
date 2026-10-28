"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
const { matchesStudentName } = require("./static/student-search.js");

test("student name search is case-insensitive, partial, and ignores surrounding spaces", () => {
	assert.equal(matchesStudentName("Asha Patel", "  ASH "), true);
	assert.equal(matchesStudentName("Ben", "maya"), false);
	assert.equal(matchesStudentName("Asha", "   "), true);
});
