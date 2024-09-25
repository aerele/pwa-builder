import frappe
import json
import requests
import os
from urllib.parse import urlparse
from frappe import ValidationError, _, qb, scrub, throw
from pwa_builder.rename_template_app import rename_template_app
from frappe.model.meta import Meta

@frappe.whitelist(allow_guest=True)
def add_site(data, update=False):
	if isinstance(data, str):
		data = json.loads(data)
	url = urlparse(data.get("site_url"))
	login_url = url.scheme + "://" + url.netloc + "/api/method/login"

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
def get_meta(doctype, project,with_parent=False,cached=True) -> "Meta":
	doc = frappe.get_doc("PWA-Project", project)
	url = urlparse(doc.site_url)
	site_url = url.scheme + "://" + url.netloc
	end_point = "/api/method/frappe.desk.form.load.getdoctype?doctype={0}&with_parent=1".format(doctype)

	response = call(site_url, end_point, doc.user_id, doc.get_password("password"), doc.project_title)
	if response.ok:
		meta = response.json()
		if with_parent == True:
			return meta
		else:
			for doc in meta["docs"]:
				if doc["name"] == doctype:
					return doc
	else:
		response.raise_for_status()

def call(url, end_point, username, password, project, force=False, count=1):
	cookies = get_cookies(url, username, password, project, force=force)
	response = requests.get(url+end_point, cookies=cookies)
	if response.status_code == 403 and count <= 3:
		response = call(url, end_point, username, password, project, force=True, count=count+1)

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
	frappe.enqueue(
		method="pwa_builder.api.schedule_export_project",
		project_name=project_name,
		queue="short",
		job_name=frappe.utils.get_job_name("export_app_for", "PWA-Project", project_name)
	)

def schedule_export_project(project_name):
	from pwa_builder.pwa_builder.doctype.pwa_github_integration import pwa_github_integration
	
	#project doc
	project_doc = frappe.get_doc("PWA-Project",project_name)
	
	git_clone_response=pwa_github_integration.clone_pwa_template(project_name)
	if git_clone_response.get('success') and git_clone_response.get('public_folder_path'):
		file_path = git_clone_response.get('public_folder_path')
		if pwa_doctype := frappe.get_list("PWA DocType", {"project_name": project_doc.name}):
			for doctype in pwa_doctype:
				doc = frappe.get_doc("PWA DocType", doctype.name)
				json_data = doc.field_list
				file_name = doc.title + ".json"
				path = file_path+"/pwa_build/pwa_build/pwa_form/"+file_name.lower()
				os.makedirs(os.path.dirname(path), exist_ok=True)
				with open(path, 'w') as json_file:
					json_file.write(json_data)
			# rename the app
			if renaming_result := rename_template_app(
				app_path=file_path,
				new_app_name=project_doc.project_title,
				new_url="frontend"
			):
				if renaming_result.get("success"):
					if push_repo_result := pwa_github_integration.push_to_github(
						path=git_clone_response.get('project_folder_path')+"/"+scrub(project_doc.project_title),
						repo_name=project_doc.project_title,
						current_default_branch=project_doc.github_default_branch,
						last_push_commit=project_doc.last_push_commit
					):
						if push_repo_result.get('success'):
							project_doc.github_repository_url = push_repo_result.get("message",{}).get('clone_url',None)
							project_doc.github_default_branch = push_repo_result.get("message",{}).get('default_branch',None)
							project_doc.last_push_commit = push_repo_result.get('commit_msg')
							project_doc.save(ignore_permissions=True)
							return {"success":True, "message":"Project exported successfully"}
						else:
							return {"success" : False, "error" : push_repo_result.get('error')}
					else:
						return {"success":False, "error":"Error while pushing to github"}
				else:
					return {"success" : False, "error" : renaming_result.get('error')}
			else:
				return {"success":False, "error": "Error while renaming app"}
		else:
			return {"success" : False, "error" : "No PWA DocType found for this project"}
	else:
		return {"success":False, "error": git_clone_response.get('error')}


# validate form mandatory fields
@frappe.whitelist()
def validate_form_fields(project_name):
	result={
		"success":True,
		"forms_with_missing_fields":{}
	}
	if form_list := frappe.get_all(
		"PWA DocType", {"project_name": project_name, "disable": 0},["name","doctype_name"]
	):
		for form in form_list:
			mandatory_fields_parent = {}
			mandatory_fields_child = {}
			child_table_list=[]
			field_meta = frappe.db.get_value("PWA DocType", form.get("name"), "field_list") or {}
			field_meta = json.loads(field_meta)
			for field in field_meta.get('pwa_form_fields',[]):
				if field.get("reqd") and field.get("fieldtype") not in ["Column Break","Section Break","Tab Break"]:
					mandatory_fields_parent[field.get("fieldname")] = field.get("label")
				if field.get("fieldtype") == "Table":
					if field.get("options") and isinstance(field.get("options"),list):
						for row in field.get("options"):
							if row.get("reqd"):
								mandatory_fields_child[row.get('parent')] = {}
								mandatory_fields_child[row.get('parent')][row.get("fieldname")]=row.get("label")
								if row.get('parent') not in child_table_list:
									child_table_list.append(row.get('parent'))
					else:
						child_table_list.append(field.get("options"))
			if actual_field_meta := get_meta(doctype=form.get("doctype_name"), project=project_name,with_parent=True,cached=False):
				missing_fields_parent, missing_fields_child = process_mandatory_fields(
					form=form.get("doctype_name"),
					actual_field_meta=actual_field_meta,
					mandatory_fields_parent=mandatory_fields_parent,
					mandatory_fields_child=mandatory_fields_child,
					child_table_list=child_table_list
				)
				if missing_fields_parent.values() or missing_fields_child.values():
					result['success']=False
					result['forms_with_missing_fields'][form.get("doctype_name")]={}
					result['forms_with_missing_fields'][form.get("doctype_name")].update(missing_fields_parent)
					result['forms_with_missing_fields'][form.get("doctype_name")].update(missing_fields_child)
		if not result.get('success'):
			result['message']='Mandatory fields missing in the form/forms'
	else:
		result['success']=False
		result['message']='No PWA DocType found for this project'
	return result
				
def process_mandatory_fields(form, actual_field_meta, mandatory_fields_parent={}, mandatory_fields_child={},child_table_list=[]):
	missing_fields_parent={}
	missing_fields_child={}
	child_table_list = child_table_list or []
	if not isinstance(actual_field_meta, dict):
		actual_field_meta = json.loads(actual_field_meta)
	for doctype_field in actual_field_meta.get('docs'):
		if doctype_field.get('name') == form:
			child_table_list = [child_table.get('options') for child_table in doctype_field.get('fields') if child_table.get('fieldtype') == 'Table' and child_table.get('reqd')]
			if missing_fields:= validate_mandatory_fields(
				actual_field_meta=doctype_field.get('fields'),
				mandatory_fields=mandatory_fields_parent
			):
				missing_fields_parent[form] = list(missing_fields.values())
		elif doctype_field.get('name') in child_table_list:
			if missing_fields := validate_mandatory_fields(
				actual_field_meta=doctype_field.get('fields'),
				mandatory_fields=mandatory_fields_child.get(doctype_field.get('doctype'))
			):
				missing_fields_child[doctype_field.get('name')] = list(missing_fields.values())

	return missing_fields_parent, missing_fields_child

def validate_mandatory_fields(actual_field_meta, mandatory_fields):
	missing_fields = {}
	for field in actual_field_meta:
		if field.get("reqd"):
			if mandatory_fields:
				if field.get("fieldname") not in mandatory_fields.keys():
					missing_fields[field.get("fieldname")] = field.get("label")
			else:
				missing_fields[field.get("fieldname")] = field.get("label")
	return missing_fields