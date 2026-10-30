"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
const {
	isWithinFivePointsBelow,
	matchesStudentFilters,
	matchesStudentName,
	studentFilterStatus,
} = require("./static/student-search.js");

test("student name search is case-insensitive, partial, and ignores surrounding spaces", () => {
	assert.equal(matchesStudentName("Asha Patel", "  ASH "), true);
	assert.equal(matchesStudentName("Ben", "maya"), false);
	assert.equal(matchesStudentName("Asha", "   "), true);
});

test("near-pass filter includes the lower bound and excludes passers", () => {
	assert.equal(isWithinFivePointsBelow(54.9, 60), false);
	assert.equal(isWithinFivePointsBelow(55, 60), true);
	assert.equal(isWithinFivePointsBelow(58, 60), true);
	assert.equal(isWithinFivePointsBelow(59.9, 60), true);
	assert.equal(isWithinFivePointsBelow(60, 60), false);
});

test("name search and near-pass filter combine with AND", () => {
	const students = [
		{ name: "Asha Patel", marks: 58 },
		{ name: "Asha Rao", marks: 54.9 },
		{ name: "Ben Shah", marks: 59.9 },
	];
	assert.deepEqual(
		students.filter((student) => matchesStudentFilters(student, "asha", true, 60)),
		[{ name: "Asha Patel", marks: 58 }],
	);
	assert.deepEqual(
		students.filter((student) => matchesStudentFilters(student, "", true, 60)),
		[{ name: "Asha Patel", marks: 58 }, { name: "Ben Shah", marks: 59.9 }],
	);
	assert.deepEqual(
		students.filter((student) => matchesStudentFilters(student, "", true, 90)),
		[],
		"a different selected analysis threshold can leave nobody qualifying",
	);
});

test("an empty near-pass result set is reported as no qualifying students", () => {
	const students = [{ name: "Passer", marks: 60 }, { name: "Far below", marks: 40 }];
	const visible = students.filter((student) => matchesStudentFilters(student, "", true, 60));
	assert.deepEqual(visible, []);
	assert.equal(
		studentFilterStatus("", true, visible.length, students.length),
		"No students are within 5 points below passing.",
	);
	assert.equal(
		studentFilterStatus("far", true, 0, students.length),
		'No students match "far" within 5 points below passing.',
	);
});
