# Copyright (c) 2024, Aerele Technologies Private Limited and Contributors
# See license.txt

import base64
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import get_site_path
from git import Repo

from pwa_builder.pwa_builder.doctype.pwa_github_integration.pwa_github_integration import (
	clone_pwa_template,
	get_branch_name,
	get_commit_message,
	next_version,
	push_to_github,
)

MODULE = "pwa_builder.pwa_builder.doctype.pwa_github_integration.pwa_github_integration"
TOKEN = "_test-token-123"


def github_response(status_code, payload=None):
	return MagicMock(status_code=status_code, json=lambda: payload or {})


class TestPWAGitHubIntegration(FrappeTestCase):
	def setUp(self):
		self.workdir = tempfile.mkdtemp()
		settings = frappe.get_single("PWA GitHub Integration")
		settings.update({"github_username": "_test-user", "access_token": TOKEN, "get_exports_on": "New Commit"})
		settings.save()

	def tearDown(self):
		shutil.rmtree(self.workdir, ignore_errors=True)
		frappe.db.rollback()

	def test_next_version(self):
		self.assertEqual(next_version("version-3"), "version-4")
		self.assertEqual(next_version(None), "version-1")
		self.assertEqual(next_version("__import__('os')"), "version-1")

	def test_branch_name(self):
		self.assertEqual(get_branch_name("New Commit", None), "version-1")
		self.assertEqual(get_branch_name("New Commit", "version-2"), "version-2")
		self.assertEqual(get_branch_name("New Branch", None), "version-1")
		self.assertEqual(get_branch_name("New Branch", "version-2"), "version-3")

	def test_commit_message(self):
		self.assertEqual(get_commit_message("New Commit", None), "version-1")
		self.assertEqual(get_commit_message("New Commit", "version-2"), "version-3")
		self.assertEqual(get_commit_message("New Branch", None), "version-1")
		self.assertEqual(get_commit_message("New Branch", "version-2"), "version-2")

	def test_push_missing_path(self):
		result = push_to_github(os.path.join(self.workdir, "missing"), "Test Repo")
		self.assertEqual(result, {"success": False, "error": "The provided path does not exist."})

	@patch(f"{MODULE}.sleep")
	@patch(f"{MODULE}.requests.post", return_value=github_response(422, {"message": "name already exists"}))
	@patch(f"{MODULE}.requests.get", return_value=github_response(404))
	def test_push_create_repo_failure(self, mock_get, mock_post, mock_sleep):
		result = push_to_github(self.workdir, "Test Repo")
		self.assertFalse(result["success"])
		self.assertIn("name already exists", result["error"])

	@patch("git.remote.Remote.push", autospec=True)
	@patch(f"{MODULE}.requests.patch", return_value=github_response(200, {"default_branch": "version-1"}))
	@patch(f"{MODULE}.requests.get", return_value=github_response(200))
	def test_push_keeps_token_out_of_git_config(self, mock_get, mock_patch, mock_push):
		push_env = {}
		mock_push.side_effect = lambda remote, **kwargs: push_env.update(remote.repo.git._environment)
		with open(os.path.join(self.workdir, "app.txt"), "w") as f:
			f.write("generated app")

		result = push_to_github(self.workdir, "Test Repo")

		self.assertTrue(result["success"])
		self.assertEqual(result["commit_msg"], "version-1")
		self.assertEqual(mock_push.call_args.kwargs["refspec"], "version-1:version-1")

		repo = Repo(self.workdir)
		self.assertEqual(repo.remote("origin").url, "https://github.com/_test-user/test_repo.git")
		with open(os.path.join(self.workdir, ".git", "config")) as f:
			self.assertNotIn(TOKEN, f.read())

		auth = base64.b64encode(f"x-access-token:{TOKEN}".encode()).decode()
		self.assertEqual(push_env["GIT_CONFIG_KEY_0"], "http.https://github.com/.extraheader")
		self.assertEqual(push_env["GIT_CONFIG_VALUE_0"], f"AUTHORIZATION: basic {auth}")


class TestClonePWATemplate(FrappeTestCase):
	project = "_Test Clone Project"

	def setUp(self):
		self.source = tempfile.mkdtemp()
		repo = Repo.init(self.source)
		with open(os.path.join(self.source, "setup.py"), "w") as f:
			f.write("# template")
		repo.index.add(["setup.py"])
		repo.index.commit("init")

	def tearDown(self):
		shutil.rmtree(self.source, ignore_errors=True)
		for folder in ("private", "public"):
			shutil.rmtree(os.path.join(get_site_path(folder, "files"), "_test_clone_project"), ignore_errors=True)

	def test_clone_into_private_files(self):
		legacy = os.path.join(get_site_path("public", "files"), "_test_clone_project")
		os.makedirs(legacy)

		result = clone_pwa_template(self.project, repo_url=self.source)

		self.assertTrue(result["success"])
		private_files = os.path.realpath(get_site_path("private", "files"))
		self.assertTrue(os.path.realpath(result["public_folder_path"]).startswith(private_files))
		self.assertTrue(os.path.exists(os.path.join(result["public_folder_path"], "setup.py")))
		self.assertFalse(os.path.exists(legacy))

	def test_clone_failure(self):
		result = clone_pwa_template(self.project, repo_url=os.path.join(self.source, "missing"))
		self.assertFalse(result["success"])
		self.assertIsNone(result["public_folder_path"])
