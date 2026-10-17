import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from api import create_app


SAMPLE_STUDENTS = [
	{"name": "Asha", "marks": 39},
	{"name": "Ben", "marks": 40},
	{"name": "Cara", "marks": 82.5},
]


class TestAnalysisAPI(unittest.TestCase):
	def setUp(self):
		self.temp_dir = tempfile.TemporaryDirectory()
		self.database = Path(self.temp_dir.name) / "analyses.db"
		self.app = create_app(
			{"TESTING": True, "DATABASE": str(self.database)}
		)
		self.client = self.app.test_client()

	def tearDown(self):
		self.temp_dir.cleanup()

	def post_analysis(self, payload):
		return self.client.post("/analyses", json=payload)

	def saved_count(self):
		if not self.database.exists():
			return 0
		with sqlite3.connect(self.database) as connection:
			return connection.execute(
				"SELECT COUNT(*) FROM analyses"
			).fetchone()[0]

	def test_health_and_empty_history(self):
		health = self.client.get("/health")
		history = self.client.get("/analyses")

		self.assertEqual(health.status_code, 200)
		self.assertEqual(health.get_json(), {"status": "ok"})
		self.assertEqual(history.status_code, 200)
		self.assertEqual(history.get_json(), {"analyses": []})

	def test_importing_api_does_not_create_database(self):
		result = subprocess.run(
			[
				sys.executable,
				"-c",
				"import sqlite3; "
				"sqlite3.connect = lambda *args, **kwargs: "
				"(_ for _ in ()).throw(AssertionError('database opened')); "
				"import api",
			],
			cwd=Path(__file__).parent,
			capture_output=True,
			text=True,
		)
		self.assertEqual(result.returncode, 0, result.stderr)
		self.assertFalse(self.database.exists())

	def test_valid_creation_and_retrieval_summary(self):
		created = self.post_analysis(
			{"pass_mark": 50, "students": SAMPLE_STUDENTS}
		)
		self.assertEqual(created.status_code, 201)
		result = created.get_json()
		self.assertEqual(
			{key: result[key] for key in ("valid_count", "invalid_count", "pass_mark")},
			{"valid_count": 3, "invalid_count": 0, "pass_mark": 50.0},
		)
		self.assertIsInstance(result["id"], int)

		response = self.client.get(f"/analyses/{result['id']}")
		self.assertEqual(response.status_code, 200)
		analysis = response.get_json()
		self.assertEqual(analysis["source_file"], "api")
		self.assertEqual(analysis["pass_mark"], 50)
		self.assertEqual(
			analysis["students"],
			[
				{"name": "Asha", "marks": 39.0, "status": "Fail"},
				{"name": "Ben", "marks": 40.0, "status": "Fail"},
				{"name": "Cara", "marks": 82.5, "status": "Pass"},
			],
		)
		self.assertEqual(
			analysis["summary"],
			{
				"valid_count": 3,
				"invalid_count": 0,
				"pass_count": 1,
				"fail_count": 2,
				"average": 53.833333333333336,
				"highest_scorer": {"name": "Cara", "marks": 82.5},
			},
		)

	def test_saved_thresholds_are_independent(self):
		response_40 = self.post_analysis(
			{"pass_mark": 40, "students": SAMPLE_STUDENTS}
		)
		response_50 = self.post_analysis(
			{"pass_mark": 50, "students": SAMPLE_STUDENTS}
		)
		self.assertEqual(response_40.status_code, 201)
		self.assertEqual(response_50.status_code, 201)

		analysis_40 = self.client.get(
			f"/analyses/{response_40.get_json()['id']}"
		)
		analysis_50 = self.client.get(
			f"/analyses/{response_50.get_json()['id']}"
		)
		self.assertEqual(analysis_40.status_code, 200)
		self.assertEqual(analysis_50.status_code, 200)
		self.assertEqual(analysis_40.get_json()["pass_mark"], 40)
		self.assertEqual(analysis_50.get_json()["pass_mark"], 50)
		self.assertEqual(analysis_40.get_json()["summary"]["pass_count"], 2)
		self.assertEqual(analysis_50.get_json()["summary"]["pass_count"], 1)
		self.assertEqual(
			[row["status"] for row in analysis_40.get_json()["students"]],
			["Fail", "Pass", "Pass"],
		)
		self.assertEqual(
			[row["status"] for row in analysis_50.get_json()["students"]],
			["Fail", "Fail", "Pass"],
		)

	def test_invalid_student_records_count_once(self):
		response = self.post_analysis(
			{
				"students": [
					{"name": "  ", "marks": 10},
					{"name": "Mina", "marks": "abc"},
					{"name": "Sam", "marks": True},
					{"name": "Lee", "marks": 101},
					{"name": "Ari", "marks": "75.5"},
				]
			}
		)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.get_json()["valid_count"], 1)
		self.assertEqual(response.get_json()["invalid_count"], 4)
		analysis = self.client.get(
			f"/analyses/{response.get_json()['id']}"
		)
		self.assertEqual(analysis.status_code, 200)
		self.assertEqual(analysis.get_json()["students"][0]["marks"], 75.5)
		self.assertEqual(analysis.get_json()["summary"]["invalid_count"], 4)

		empty_result = self.post_analysis(
			{"students": [{"name": "No mark"}]}
		)
		self.assertEqual(empty_result.status_code, 201)
		self.assertEqual(empty_result.get_json()["valid_count"], 0)
		self.assertEqual(empty_result.get_json()["invalid_count"], 1)

	def test_empty_analysis_has_null_average_and_highest_scorer(self):
		response = self.post_analysis({"students": []})
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.get_json()["pass_mark"], 40.0)
		self.assertEqual(response.get_json()["valid_count"], 0)
		self.assertEqual(response.get_json()["invalid_count"], 0)
		analysis = self.client.get(
			f"/analyses/{response.get_json()['id']}"
		)
		self.assertEqual(analysis.status_code, 200)
		self.assertEqual(analysis.get_json()["students"], [])
		self.assertIsNone(analysis.get_json()["summary"]["average"])
		self.assertIsNone(
			analysis.get_json()["summary"]["highest_scorer"]
		)

	def test_duplicate_names_and_original_order_are_preserved(self):
		response = self.post_analysis(
			{
				"students": [
					{"name": "Kai", "marks": 10},
					{"name": "Mia", "marks": 20},
					{"name": "Kai", "marks": 30},
				]
			}
		)
		self.assertEqual(response.status_code, 201)
		analysis = self.client.get(
			f"/analyses/{response.get_json()['id']}"
		)
		self.assertEqual(analysis.status_code, 200)
		self.assertEqual(
			[(row["name"], row["marks"]) for row in analysis.get_json()["students"]],
			[("Kai", 10.0), ("Mia", 20.0), ("Kai", 30.0)],
		)

	def test_invalid_thresholds_are_rejected_without_saving(self):
		for value in (True, "50", -1, 101, 10**1000):
			with self.subTest(pass_mark=value):
				before = self.saved_count()
				response = self.post_analysis(
					{"pass_mark": value, "students": SAMPLE_STUDENTS}
				)
				self.assertEqual(response.status_code, 400)
				self.assertEqual(
					response.get_json()["error"]["code"],
					"invalid_pass_mark",
				)
				self.assertEqual(self.saved_count(), before)

		response = self.client.post(
			"/analyses",
			data='{"pass_mark": NaN, "students": []}',
			content_type="application/json",
		)
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.get_json()["error"]["code"], "invalid_pass_mark")
		self.assertEqual(self.saved_count(), 0)

	def test_malformed_json_content_type_and_structure_errors(self):
		cases = [
			self.client.post(
				"/analyses", data="{", content_type="application/json"
			),
			self.client.post("/analyses", data="{}", content_type="text/plain"),
			self.post_analysis({"pass_mark": 30}),
			self.post_analysis({"students": "not a list"}),
			self.post_analysis({"students": [{"name": "A"}, 5]}),
		]
		self.assertEqual(
			[response.status_code for response in cases],
			[400, 415, 400, 400, 400],
		)
		self.assertEqual(
			[response.get_json()["error"]["code"] for response in cases],
			[
				"invalid_json",
				"unsupported_media_type",
				"invalid_students",
				"invalid_students",
				"invalid_student_structure",
			],
		)
		self.assertEqual(self.saved_count(), 0)

	def test_unknown_analysis_returns_consistent_404(self):
		response = self.client.get("/analyses/999")
		self.assertEqual(response.status_code, 404)
		self.assertEqual(
			response.get_json(),
			{
				"error": {
					"code": "analysis_not_found",
					"message": "Analysis was not found.",
				}
			},
		)

	def test_history_lists_newest_first_with_required_fields(self):
		first = self.post_analysis({"students": []})
		second = self.post_analysis({"students": SAMPLE_STUDENTS})
		self.assertEqual(first.status_code, 201)
		self.assertEqual(second.status_code, 201)
		history = self.client.get("/analyses")
		self.assertEqual(history.status_code, 200)
		rows = history.get_json()["analyses"]
		self.assertEqual(
			[row["id"] for row in rows],
			[second.get_json()["id"], first.get_json()["id"]],
		)
		self.assertEqual(
			set(rows[0]),
			{
				"id", "created_at", "source_file", "pass_mark",
				"valid_count", "invalid_count",
			},
		)

	def test_second_application_instance_reads_persisted_results(self):
		created = self.post_analysis(
			{"pass_mark": 50, "students": SAMPLE_STUDENTS}
		)
		self.assertEqual(created.status_code, 201)
		second_app = create_app(
			{"TESTING": True, "DATABASE": str(self.database)}
		)
		response = second_app.test_client().get(
			f"/analyses/{created.get_json()['id']}"
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.get_json()["pass_mark"], 50)
		self.assertEqual(response.get_json()["summary"]["pass_count"], 1)

	def test_application_instances_use_separate_databases(self):
		other_database = Path(self.temp_dir.name) / "other.db"
		other_app = create_app(
			{"TESTING": True, "DATABASE": str(other_database)}
		)
		created = self.post_analysis({"students": SAMPLE_STUDENTS})
		self.assertEqual(created.status_code, 201)
		other_history = other_app.test_client().get("/analyses")
		self.assertEqual(other_history.status_code, 200)
		self.assertEqual(other_history.get_json(), {"analyses": []})
		self.assertNotEqual(self.database, other_database)


if __name__ == "__main__":
	unittest.main()
