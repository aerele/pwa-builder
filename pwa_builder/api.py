import frappe
import json
import requests
import os
from urllib.parse import urlparse
from frappe.model.meta import Meta

@frappe.whitelist(allow_guest=True)
def add_site(data, update=False):
	print(data, "data=========================================")
	if isinstance(data, str):
		data = json.loads(data)
	# data = frappe._dict(data)
	url = urlparse(data.get("site_url"))
	print(url, "url=========================================")
	login_url = url.scheme + "://" + url.netloc + "/api/method/login"
	print(login_url, "login_url=========================================")

	print('{"usr": data.get("user_id"), "pwd": data.get("password")}', {"usr": data.get("user_id"), "pwd": data.get("password")})
	response = requests.post(login_url, data={"usr": data.get("user_id"), "pwd": data.get("password")})

	if response.status_code == 200:
		frappe.cache().hset(data.get("user_id"), data.get("project_title"), response.cookies)
		if not update:
			frappe.get_doc({
				"doctype": "PWA-Project",
				"project_title": data.get("project_title"),
				"sub_title": data.get("sub_title"),
				"site_url": data.get("site_url"),
				"user_id": data.get("user_id"),
				"password": data.get("password"),
				"description": data.get("description"),
			}).insert(ignore_permissions=True)

			return "Created"
		else:
			doc = frappe.get_doc("PW-Project", url.scheme + "://" + url.netloc)

			doc.update({
				"doctype": "PWA-Project",
				"project_title": data.get("project_title"),
				"sub_title": data.get("sub_title"),
				"site_url": data.get("site_url"),
				"user_id": data.get("user_id"),
				"password": data.get("password"),
				"description": data.get("description"),
				})
			data.save()
			return "Updated"
	else:
		return "Invalid credentials"

@frappe.whitelist(allow_guest=True)
def get_meta(doctype, project, cached=True) -> "Meta":
	doc = frappe.get_doc("PWA-Project", project)
	url = urlparse(doc.site_url)
	site_url = url.scheme + "://" + url.netloc
	end_point = "/api/method/frappe.desk.form.load.getdoctype?doctype={0}&with_parent=1".format(doctype)

	response = call(site_url, end_point, doc.user_id, doc.get_password("password"), doc.project_title)
	if response.ok:
		meta = response.json()
		for doc in meta["docs"]:
			if doc["name"] == doctype:
				print(doc, "repons4e==================================================================================")
				return doc
	# if response.status_code == 200:
		#  response.json()

def call(url, end_point, username, password, project, force=False):
	cookies = get_cookies(url, username, password, project, force=force)
	response = requests.get(url+end_point, cookies=cookies)
	if response.status_code == 403:
		response = call(url, end_point, username, password, project, force=True)
	return response


def get_cookies(url, username, password, project,  force=False):
	cookies = frappe.cache().hget(url, project)
	if not cookies or force:
		login_url = url + "/api/method/login"
		response = requests.post(
			login_url, data={"usr": username, "pwd": password}
		)
		if response.status_code == 200:
			cookies = response.cookies
			frappe.cache().hset(url, project, cookies)
	return cookies

@frappe.whitelist(allow_guest=True)
def set_value(doctype, docname, fieldname, value):

	 frappe.set_value(doctype, docname, fieldname, json.dumps(value, indent=4))

@frappe.whitelist(allow_guest=True)
def get_doc(doctype, docname):
	 return frappe.get_doc(doctype, docname)

@frappe.whitelist(allow_guest=True)
def export_project(project_name):
	print("export_project")
	# os.mkdir("sudharsanan")
	print("export")
	pwa_doctype = frappe.get_list("PWA DocType", {"project_name": project_name})
	print(pwa_doctype)

	# /home/scott007/frappe/pwa_builder/apps/pwa_builder/pwa_builder/api.py

	cd = __file__
	i, j , k = len(cd.split('/')[-1]) , len(cd.split('/')[-2]), len(cd.split('/')[-3])
	pwd = cd[:-(i + j + k + 2)]
	print(pwd)
	for doctype in pwa_doctype:
		doc = frappe.get_doc("PWA DocType", doctype.name)
		json_data = doc.field_list
		file_name = doc.title + ".json"
		# path = os.path.join("pwa_builder", "pwa_template", "pwa_template", "pwa_template", "pwa_form", "employee.json")
		path = os.path.join(pwd, "pwa_template", "pwa_template", "pwa_template", "pwa_form", file_name.lower())
		print(path)
		os.makedirs(os.path.dirname(path), exist_ok=True)
		with open(path, 'w') as json_file:
			json_file.write(json_data)


		print("json creation done")
