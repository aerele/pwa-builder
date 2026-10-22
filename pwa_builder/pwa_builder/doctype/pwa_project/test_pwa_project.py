# Copyright (c) 2024, Aerele Technologies Private Limited and Contributors
# See license.txt

import json
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import frappe
from frappe import scrub
from frappe.tests.utils import FrappeTestCase

from pwa_builder import api
from pwa_builder.pwa_builder.doctype.pwa_doctype.test_pwa_doctype import make_project, make_screen

GITHUB_MODULE = "pwa_builder.pwa_builder.doctype.pwa_github_integration.pwa_github_integration"


def login_response(status_code):
	return MagicMock(status_code=status_code, cookies={"sid": "_test"})


class TestPWAProject(FrappeTestCase):
	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def test_api_methods_not_open_to_guest(self):
		methods = [
			api.add_site,
			api.get_meta,
			api.set_value,
			api.export_status,
			api.export_project,
			api.validate_form_fields,
		]
		with self.set_user("Guest"):
			for method in methods:
				with self.subTest(method=method.__name__):
					self.assertRaises(frappe.PermissionError, frappe.is_whitelisted, method)

	def test_guest_cannot_use_project_endpoints(self):
		project = make_project()
		with self.set_user("Guest"):
			self.assertRaises(frappe.PermissionError, api.add_site, {"connection_type": "This Site"})
			self.assertRaises(frappe.PermissionError, api.get_meta, "ToDo", project.name)
			self.assertRaises(frappe.PermissionError, api.export_status, project.name)
			self.assertRaises(frappe.PermissionError, api.export_project, project.name)

	@patch("pwa_builder.api.requests.post")
	def test_add_site_this_site(self, mock_post):
		result = api.add_site({"project_title": "_Test Local", "connection_type": "This Site"})

		self.assertEqual(result, "Created")
		mock_post.assert_not_called()
		project = frappe.get_last_doc("PWA-Project", {"project_title": "_Test Local"})
		self.assertEqual(project.site_url, frappe.utils.get_url())
		self.assertFalse(project.user_id)

	@patch("pwa_builder.api.requests.post", return_value=login_response(200))
	def test_add_site_another_site(self, mock_post):
		data = {
			"project_title": "_Test Remote",
			"connection_type": "Another Site",
			"site_url": "https://remote.example.com/app",
			"user_id": "_test@example.com",
			"password": "_test_pwd",
		}
		self.assertEqual(api.add_site(json.dumps(data)), "Created")

		self.assertEqual(mock_post.call_args.args[0], "https://remote.example.com/api/method/login")
		project = frappe.get_last_doc("PWA-Project", {"project_title": "_Test Remote"})
		self.assertEqual(project.connection_type, "Another Site")
		self.assertEqual(project.get_password("password"), "_test_pwd")

	@patch("pwa_builder.api.requests.post", return_value=login_response(401))
	def test_add_site_invalid_credentials(self, mock_post):
		data = {"project_title": "_Test Bad Login", "site_url": "https://remote.example.com"}
		self.assertEqual(api.add_site(data), "Invalid credentials")
		self.assertFalse(frappe.db.exists("PWA-Project", {"project_title": "_Test Bad Login"}))

	@patch("pwa_builder.api.requests.post", return_value=login_response(200))
	def test_add_site_update(self, mock_post):
		project = make_project("_Test Before Update")
		data = {
			"name": project.name,
			"project_title": "_Test After Update",
			"site_url": "https://remote.example.com",
			"user_id": "_test@example.com",
			"password": "_test_pwd",
		}
		self.assertEqual(api.add_site(data, update=True), "Updated")
		self.assertEqual(
			frappe.db.get_value("PWA-Project", project.name, "project_title"), "_Test After Update"
		)

	def test_get_meta_this_site(self):
		project = make_project()

		meta = api.get_meta("ToDo", project.name, with_parent=True)
		self.assertIn("ToDo", [d.get("name") for d in meta["docs"]])

		todo = api.get_meta("ToDo", project.name)
		self.assertEqual(todo.get("name"), "ToDo")
		self.assertIn("description", [f.get("fieldname") for f in todo.get("fields")])

	def test_export_status_without_job(self):
		project = make_project()
		project.db_set(
			{"github_repository_url": "https://github.com/_test/repo.git", "last_push_commit": "version-2"}
		)

		status = api.export_status(project.name)
		self.assertIsNone(status["job_status"])
		self.assertEqual(status["repository_url"], "https://github.com/_test/repo.git")
		self.assertEqual(status["last_commit"], "version-2")

	@patch("pwa_builder.api.frappe.enqueue")
	def test_export_project_enqueues_job(self, mock_enqueue):
		project = make_project()
		api.export_project(project.name)

		kwargs = mock_enqueue.call_args.kwargs
		self.assertEqual(kwargs["method"], "pwa_builder.api.schedule_export_project")
		self.assertEqual(kwargs["project_name"], project.name)
		self.assertEqual(
			kwargs["job_id"], frappe.utils.get_job_name("export_app_for", "PWA-Project", project.name)
		)

	def test_validate_needs_github_setup(self):
		project = make_project()
		result = api.validate_form_fields(project.name)
		self.assertFalse(result["success"])
		self.assertEqual(result["message"], "Setup PWA GitHub integration First")

	def test_validate_reports_missing_mandatory_fields(self):
		set_github_credentials()
		project = make_project()
		make_screen(project.name, fields=[{"fieldname": "status", "label": "Status", "fieldtype": "Select"}])

		result = api.validate_form_fields(project.name)
		self.assertFalse(result["success"])
		self.assertEqual(result["forms_with_missing_fields"]["ToDo"], {"ToDo": ["Description"]})

	def test_validate_fails_for_empty_screen(self):
		set_github_credentials()
		project = make_project()
		make_screen(project.name)

		result = api.validate_form_fields(project.name)
		self.assertFalse(result["success"])
		self.assertEqual(result["message"], "Mandatory fields missing in the form/forms")
		self.assertEqual(result["forms_with_missing_fields"]["ToDo"], {"ToDo": ["Description"]})

	def test_validate_passes_with_mandatory_fields(self):
		set_github_credentials()
		project = make_project()
		make_screen(
			project.name,
			fields=[
				{"fieldname": "description", "label": "Description", "fieldtype": "Text Editor", "reqd": 1}
			],
		)

		result = api.validate_form_fields(project.name)
		self.assertTrue(result["success"])
		self.assertEqual(result["forms_with_missing_fields"], {})


def set_github_credentials():
	settings = frappe.get_single("PWA GitHub Integration")
	settings.update(
		{"github_username": "_test-user", "access_token": "_test-token", "get_exports_on": "New Commit"}
	)
	settings.save()


class TestPWAProjectExport(FrappeTestCase):
	def setUp(self):
		self.workdir = tempfile.mkdtemp()
		self.project = make_project("_Test Export App")
		self.project.db_set({"theme_color": "#112233", "background_color": "#ffffff"})
		make_screen(self.project.name, fields=[{"fieldname": "description"}], nav_order=2)
		self.template = self.make_template()

	def tearDown(self):
		shutil.rmtree(self.workdir, ignore_errors=True)
		frappe.db.rollback()

	def make_template(self):
		app_dir = os.path.join(self.workdir, "pwa_build")
		os.makedirs(os.path.join(app_dir, "pwa_build", "public", "pwa"))
		os.makedirs(os.path.join(app_dir, "pwa_build", "www"))
		with open(os.path.join(app_dir, "pwa_build", "public", "pwa", "manifest.webmanifest"), "w") as f:
			json.dump({"name": "Frappe UI App", "short_name": "App", "theme_color": "#000000"}, f)
		with open(os.path.join(app_dir, "pwa_build", "www", "pwa.html"), "w") as f:
			f.write("<html><head><title>Frappe UI App</title></head></html>")
		return {"success": True, "public_folder_path": app_dir, "project_folder_path": self.workdir}

	def export(self, push_result):
		with (
			patch(f"{GITHUB_MODULE}.clone_pwa_template", return_value=self.template),
			patch("pwa_builder.api.rename_template_app", return_value={"success": True}),
			patch(f"{GITHUB_MODULE}.push_to_github", return_value=push_result) as mock_push,
		):
			return api.schedule_export_project(self.project.name), mock_push

	def test_export_writes_screens_and_branding(self):
		push_result = {
			"success": True,
			"message": {"clone_url": "https://github.com/_test/export.git", "default_branch": "version-1"},
			"commit_msg": "version-1",
		}
		result, mock_push = self.export(push_result)
		self.assertTrue(result["success"])

		app_dir = self.template["public_folder_path"]
		with open(os.path.join(app_dir, "pwa_build", "pwa_build", "pwa_form", "_test todo screen.json")) as f:
			form = json.load(f)
		self.assertEqual(form["nav_order"], 2)
		self.assertEqual(form["pwa_form_fields"], [{"fieldname": "description"}])

		with open(os.path.join(app_dir, "pwa_build", "public", "pwa", "manifest.webmanifest")) as f:
			manifest = json.load(f)
		self.assertEqual(manifest["name"], "_Test Export App")
		self.assertEqual(manifest["theme_color"], "#112233")
		self.assertEqual(manifest["background_color"], "#ffffff")

		with open(os.path.join(app_dir, "pwa_build", "www", "pwa.html")) as f:
			self.assertIn("<title>_Test Export App</title>", f.read())

		self.assertEqual(mock_push.call_args.kwargs["path"], self.workdir + "/" + scrub("_Test Export App"))
		self.project.reload()
		self.assertEqual(self.project.github_repository_url, "https://github.com/_test/export.git")
		self.assertEqual(self.project.github_default_branch, "version-1")
		self.assertEqual(self.project.last_push_commit, "version-1")

	def test_export_push_failure_keeps_project(self):
		result, _ = self.export({"success": False, "error": "Bad credentials"})

		self.assertEqual(result, {"success": False, "error": "Bad credentials"})
		self.project.reload()
		self.assertFalse(self.project.github_repository_url)
