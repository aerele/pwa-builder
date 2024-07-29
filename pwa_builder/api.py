import frappe
import json
import requests
from urllib.parse import urlparse

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

    response = requests.post(login_url, data={"usr": data.get("user_id"), "pwd": data.get("password")})

    if response.status_code == 200:
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