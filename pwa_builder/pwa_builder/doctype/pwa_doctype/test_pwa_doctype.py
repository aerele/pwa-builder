# Copyright (c) 2024, Aerele Technologies Private Limited and Contributors
# See license.txt

import json

import frappe
from frappe.tests.utils import FrappeTestCase

from pwa_builder.api import set_value, with_nav_order


def make_project(title="_Test PWA Project"):
	return frappe.get_doc({
		"doctype": "PWA-Project",
		"project_title": title,
		"connection_type": "This Site",
		"site_url": frappe.utils.get_url(),
	}).insert()


def make_screen(project, doctype_name="ToDo", fields=None, nav_order=0):
	return frappe.get_doc({
		"doctype": "PWA DocType",
		"title": f"_Test {doctype_name} Screen",
		"doctype_name": doctype_name,
		"project_name": project,
		"nav_order": nav_order,
		"field_list": json.dumps({"pwa_form_fields": fields or []}),
	}).insert()


class TestPWADocType(FrappeTestCase):
	def setUp(self):
		self.project = make_project()

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def test_set_value_saves_field_list(self):
		screen = make_screen(self.project.name)
		value = {"form_name": "ToDo", "pwa_form_fields": [{"fieldname": "description"}]}

		set_value("PWA DocType", screen.name, "field_list", value)

		saved = json.loads(frappe.db.get_value("PWA DocType", screen.name, "field_list"))
		self.assertEqual(saved, value)

	def test_set_value_rejects_other_doctypes(self):
		self.assertRaises(
			frappe.PermissionError,
			set_value, "User", "Administrator", "first_name", "Hacked",
		)
		self.assertNotEqual(frappe.db.get_value("User", "Administrator", "first_name"), "Hacked")

	def test_set_value_rejects_other_fields(self):
		screen = make_screen(self.project.name)
		self.assertRaises(
			frappe.PermissionError,
			set_value, "PWA DocType", screen.name, "project_name", "x",
		)

	def test_set_value_denied_for_guest(self):
		screen = make_screen(self.project.name)
		with self.set_user("Guest"):
			self.assertRaises(
				frappe.PermissionError,
				set_value, "PWA DocType", screen.name, "field_list", {},
			)

	def test_with_nav_order_stamps_order(self):
		screen = make_screen(self.project.name, nav_order=3)
		self.assertEqual(json.loads(with_nav_order(screen))["nav_order"], 3)

	def test_with_nav_order_defaults_to_zero(self):
		screen = make_screen(self.project.name)
		screen.nav_order = None
		self.assertEqual(json.loads(with_nav_order(screen))["nav_order"], 0)

	def test_with_nav_order_keeps_invalid_json(self):
		screen = frappe._dict(field_list="not json", nav_order=1)
		self.assertEqual(with_nav_order(screen), "not json")
