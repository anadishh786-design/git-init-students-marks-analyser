"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const test = require("node:test");
const vm = require("node:vm");

class Element {
	constructor(tag = "div") {
		this.tagName = tag;
	this.children = [];
	this.cells = [];
	this.listeners = {};
	this.dataset = {};
	this.attributes = {};
	this.value = "";
	this.checked = false;
	this.disabled = false;
	this.hidden = false;
	this.textContent = "";
	}
	append(...items) {
		for (const item of items) {
			this.children.push(item);
			if (this.tagName === "tr" && item.tagName === "td") this.cells.push(item);
		}
	}
	appendChild(item) { this.append(item); return item; }
	replaceChildren(...items) { this.children = []; this.cells = []; this.append(...items); }
	addEventListener(type, callback) { this.listeners[type] = callback; }
	setAttribute(name, value) { this.attributes[name] = value; }
	querySelectorAll(selector) {
		if (selector === "[data-student-row]") return this.children.filter((item) => item.dataset.studentRow !== undefined);
		if (selector === "input, button:not(#save-analysis)") return [];
		return [];
	}
	querySelector(selector) {
		if (selector === '[name="student-name"]') return this.nameInput;
		if (selector === '[name="student-marks"]') return this.marksInput;
		return null;
	}
}

function makeDashboard() {
	const ids = ["analysis-form", "student-rows", "pass-mark", "form-status", "save-analysis",
		"invalid-warning", "history-rows", "history-status", "results-status", "student-search",
		"student-search-status", "near-pass-filter", "selected-analysis-id", "selected-pass-mark",
		"result-students", "result-average", "result-highest", "result-valid-count",
		"result-invalid-count", "result-pass-count", "result-fail-count", "add-student"];
	const elements = Object.fromEntries(ids.map((id) => [id, new Element(id === "analysis-form" ? "form" : "div")]));
	elements["pass-mark"].value = "40";
	elements["student-rows"].querySelectorAll = () => [];
	elements["analysis-form"].querySelectorAll = () => [];
	elements["result-students"].querySelectorAll = (selector) => selector === "[data-result-student]"
		? elements["result-students"].children.filter((row) => row.dataset.resultStudent !== undefined) : [];
	const document = {
		querySelector(selector) { return elements[selector.slice(1)]; },
		querySelectorAll(selector) {
			if (selector === "#result-students [data-result-student]") return elements["result-students"].querySelectorAll("[data-result-student]");
			return [];
		},
		createElement(tag) { return new Element(tag); },
	};
	const savedAnalysis = {
		id: 7, pass_mark: 60,
		students: [
			{ name: "Asha", marks: 55, status: "Fail" },
			{ name: "Arjun", marks: 58, status: "Fail" },
			{ name: "Ben", marks: 60, status: "Pass" },
		],
		summary: { average: 57.67, highest_scorer: { name: "Ben", marks: 60 }, valid_count: 3,
			invalid_count: 0, pass_count: 1, fail_count: 2 },
	};
	const fetch = async (url) => ({
		ok: true,
		json: async () => url === "/analyses" ? { analyses: [{ id: 7, pass_mark: 60, valid_count: 3, invalid_count: 0 }] } : savedAnalysis,
	});
	const context = { document, fetch, console };
	vm.runInNewContext(fs.readFileSync("static/student-search.js", "utf8"), context);
	vm.runInNewContext(fs.readFileSync("static/app.js", "utf8"), context);
	return { elements, savedAnalysis };
}

test("dashboard filter keeps using the loaded analysis threshold after the form changes", async () => {
	const { elements } = makeDashboard();
	await new Promise((resolve) => setImmediate(resolve));
	const viewButton = elements["history-rows"].children[0].children[5].children[0];
	await viewButton.listeners.click();
	assert.equal(elements["selected-pass-mark"].textContent, "60");

	// This form belongs to a new analysis; changing it must not alter filtering of the saved one.
	elements["pass-mark"].value = "90";
	elements["near-pass-filter"].checked = true;
	elements["near-pass-filter"].listeners.change();
	const visible = elements["result-students"].children
		.filter((row) => row.dataset.resultStudent !== undefined && !row.hidden)
		.map((row) => row.cells[0].textContent);
	assert.deepEqual(visible, ["Asha", "Arjun"]);
});
