"""Flask HTTP API for saved student analyses."""

import math
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import BadRequest, HTTPException

from main import calculate_summary, validate_record
from tracker import (
	close_db,
	connect_db,
	fetch_analysis,
	fetch_students,
	initialise_db,
	save_analysis,
)


def _error(code, message, status):
	return jsonify({"error": {"code": code, "message": message}}), status


def create_app(test_config=None):
	app = Flask(__name__)
	app.config.from_mapping(
		DATABASE=str(Path(app.instance_path) / "analyses.db")
	)
	if test_config is not None:
		app.config.update(test_config)

	@app.errorhandler(HTTPException)
	def handle_http_error(error):
		code = error.name.lower().replace(" ", "_")
		return _error(code, error.description, error.code)

	@app.get("/")
	def dashboard():
		return render_template("index.html")

	@app.get("/health")
	def health():
		return jsonify({"status": "ok"})

	@app.get("/analyses")
	def list_analyses():
		connection = connect_db(app.config["DATABASE"])
		try:
			initialise_db(connection)
			rows = connection.execute(
				"""
				SELECT a.id, a.created_at, a.source_file, a.pass_mark,
					   COUNT(s.id) AS valid_count, a.invalid_count
				FROM analyses AS a
				LEFT JOIN student_results AS s ON s.analysis_id = a.id
				GROUP BY a.id
				ORDER BY a.created_at DESC, a.id DESC
				"""
			).fetchall()
			analyses = [
				{
					"id": row[0],
					"created_at": row[1],
					"source_file": row[2],
					"pass_mark": row[3],
					"valid_count": row[4],
					"invalid_count": row[5],
				}
				for row in rows
			]
			return jsonify({"analyses": analyses})
		finally:
			close_db(connection)

	@app.post("/analyses")
	def create_analysis():
		if not request.is_json:
			return _error(
				"unsupported_media_type",
				"Content-Type must be application/json.",
				415,
			)

		try:
			payload = request.get_json()
		except BadRequest:
			return _error("invalid_json", "Request body must contain valid JSON.", 400)

		if not isinstance(payload, dict):
			return _error("invalid_request", "Request body must be a JSON object.", 400)

		pass_mark = payload.get("pass_mark", 40)
		try:
			pass_mark_number = float(pass_mark)
		except (OverflowError, TypeError, ValueError):
			pass_mark_number = math.nan
		if (
			isinstance(pass_mark, bool)
			or not isinstance(pass_mark, (int, float))
			or not math.isfinite(pass_mark_number)
			or not 0 <= pass_mark_number <= 100
		):
			return _error(
				"invalid_pass_mark",
				"pass_mark must be a finite JSON number between 0 and 100.",
				400,
			)

		students_payload = payload.get("students")
		if not isinstance(students_payload, list):
			return _error(
				"invalid_students",
				"students must be a JSON list.",
				400,
			)
		if any(not isinstance(student, dict) for student in students_payload):
			return _error(
				"invalid_student_structure",
				"Each item in students must be a JSON object.",
				400,
			)

		students = []
		invalid_count = 0
		for student in students_payload:
			name = student.get("name")
			marks = student.get("marks")
			if (
				not isinstance(name, str)
				or isinstance(marks, bool)
				or not isinstance(marks, (int, float, str))
			):
				invalid_count += 1
				continue

			valid, result = validate_record(name, marks)
			if valid:
				students.append({"name": name.strip(), "mark": result})
			else:
				invalid_count += 1

		connection = connect_db(app.config["DATABASE"])
		try:
			initialise_db(connection)
			analysis_id = save_analysis(
				connection,
				"api",
				pass_mark_number,
				invalid_count,
				students,
			)
		except (OSError, sqlite3.Error):
			return _error("database_error", "The analysis could not be saved.", 500)
		finally:
			close_db(connection)

		return jsonify(
			{
				"id": analysis_id,
				"valid_count": len(students),
				"invalid_count": invalid_count,
				"pass_mark": pass_mark_number,
			}
		), 201

	@app.get("/analyses/<int:analysis_id>")
	def get_analysis(analysis_id):
		connection = connect_db(app.config["DATABASE"])
		try:
			initialise_db(connection)
			analysis = fetch_analysis(connection, analysis_id)
			if analysis is None:
				return _error(
					"analysis_not_found",
					"Analysis was not found.",
					404,
				)

			_, created_at, source_file, pass_mark, invalid_count, _ = analysis
			saved_students = fetch_students(connection, analysis_id)
			summary = calculate_summary(saved_students, pass_mark)
			students = [
				{
					"name": student["name"],
					"marks": student["mark"],
					"status": (
						"Pass" if student["mark"] >= pass_mark else "Fail"
					),
				}
				for student in saved_students
			]
			highest_scorer = summary["highest_scorer"]
			return jsonify(
				{
					"id": analysis_id,
					"created_at": created_at,
					"source_file": source_file,
					"pass_mark": pass_mark,
					"students": students,
					"summary": {
						"valid_count": summary["valid_count"],
						"invalid_count": invalid_count,
						"pass_count": summary["pass_count"],
						"fail_count": summary["fail_count"],
						"average": summary["average"],
						"highest_scorer": (
							{
								"name": highest_scorer["name"],
								"marks": highest_scorer["mark"],
							}
							if highest_scorer is not None
							else None
						),
					},
				}
			)
		finally:
			close_db(connection)

	return app
