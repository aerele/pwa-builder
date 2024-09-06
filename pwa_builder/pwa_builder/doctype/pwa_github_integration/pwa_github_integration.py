# Copyright (c) 2024, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

import os
import git
import frappe
import requests
import shutil
from git import Repo, InvalidGitRepositoryError
from time import sleep
from frappe import ValidationError, _, qb, scrub, throw
from frappe.utils import get_site_path, scheduler, touch_file
from frappe.model.document import Document


class PWAGitHubIntegration(Document):
	pass


frappe.whitelist()
def push_to_github(path, repo_name, current_default_branch=None, last_push_commit=None):
	pwa_github_integration = frappe.get_single('PWA GitHub Integration')
	github_token = pwa_github_integration.get_password('access_token')
	github_username = pwa_github_integration.github_username
	push_to_org = pwa_github_integration.push_repository_to_an_organization
	organization_name = pwa_github_integration.organization_name
	is_private = pwa_github_integration.is_private
	get_exports_on = pwa_github_integration.get_exports_on


	branch_name = get_branch_name(get_exports_on=get_exports_on,current_default_branch=current_default_branch)
	commit_msg = get_commit_message(get_exports_on=get_exports_on,last_push_commit=last_push_commit)

	repo_name = scrub(repo_name)

	repo_path = path
	if not os.path.exists(path):
		return {'success': False, 'error': 'The provided path does not exist.'}

	headers = {
		'Authorization': f'token {github_token}',
		'Accept': 'application/vnd.github.v3+json'
	}

	# Define repository URL
	if push_to_org and organization_name:
		repo_url = f'https://api.github.com/orgs/{organization_name}/repos'
		repo_full_name = f'{organization_name}/{repo_name}'
	else:
		repo_url = f'https://api.github.com/user/repos'
		repo_full_name = f'{github_username}/{repo_name}'

	repo_data = {
		'name': repo_name,
		'private': is_private,  # Change this if you need a private repository
		'auto_init': False  # Initialize with a README
	}

	try:
		# Check if the repository exists
		response = requests.get(f'https://api.github.com/repos/{repo_full_name}', headers=headers)
		if response.status_code == 404:
			# Repository does not exist, create it
			response = requests.post(repo_url, json=repo_data, headers=headers)
			if response.status_code == 201:
				print(f"Repository '{repo_name}' created successfully.")
				sleep(10)  # Wait for a short period to ensure the repository is fully initialized
			else:
				return {'success': False, 'error': f"Failed to create repository: {response.json().get('message')}"}
		elif response.status_code == 200:
			print(f"Repository '{repo_name}' already exists.")
		else:
			return {'success': False, 'error': f"Failed to check repository existence: {response.json().get('message')}"}

		# Initialize a new Git repository in the directory
		repo = git.Repo.init(repo_path)
		repo.git.add(A=True)
		repo.index.commit('Initial commit')
		correct_url = f"https://{github_token}@github.com/{repo_full_name}.git"

		try:
			origin = repo.remote(name='origin')
			current_url = origin.url
		except ValueError:
			origin = repo.create_remote('origin', correct_url)
		else:
			if current_url != correct_url:
				origin.set_url(correct_url)

		if branch_name not in repo.branches:
			new_branch = repo.create_head(branch_name)
		else:
			new_branch = repo.heads[branch_name]
		new_branch.checkout()

		repo.git.add(A=True)  # Stage all files
		repo.index.commit(commit_msg)  # Commit changes

		# Force Push
		try:
			origin.push(refspec=f'{branch_name}:{branch_name}', force=True)
			print("Force push successful.")
		except git.exc.GitCommandError as e:
			frappe.log_error(frappe.get_traceback(), "Git Force Push Failed")
			return {'success': False, 'error': f"Force push failed: {str(e)}"}

		# Set the last pushed branch as default
		repo_api_url = f'https://api.github.com/repos/{repo_full_name}'
		repo_settings = {
			'default_branch': branch_name
		}

		try:
			response = requests.patch(repo_api_url, json=repo_settings, headers=headers)
			if response.status_code == 200:
				print(f"Default branch set to '{branch_name}'.")
				return {'success': True, "message":response.json(), "commit_msg":commit_msg}
			else:
				return {'success': False, 'error': f"Failed to set default branch: {response.json().get('message')}"}
		except Exception as e:
			frappe.log_error(frappe.get_traceback(), "Failed to set default branch")
			return {'success': False, 'error': str(e)}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Git Push Failed")
		return {'success': False, 'error': str(e)}


def clone_pwa_template(project_name,repo_url="https://github.com/aerele/pwa_build.git"):
	project_name = scrub(project_name)
	public_folder = os.path.join(get_site_path("public/files/"), project_name,"pwa_build")
	project_folder = os.path.join(get_site_path("public/files/"), project_name)
	result = {'success': False, 'error': 'An error occurred.'}
	# If the directory exists and is not empty, remove it
	if os.path.exists(project_folder) and os.listdir(project_folder):
		shutil.rmtree(project_folder)
		print(f"Removed existing directory: {public_folder}")
	
	# Clone the repository into the public folder
	try:
		Repo.clone_from(repo_url, public_folder)
		result['public_folder_path'] = public_folder
		result['project_folder_path'] = project_folder
		result['success'] = True
		result['message'] = "Repository cloned successfully."
	except InvalidGitRepositoryError:
		result['public_folder_path'] = None
		result['project_folder_path'] = None
		result['success'] = False
		result['error'] = f"Directory {public_folder} exists but is not a valid Git repository."
	except Exception as e:
		result['public_folder_path'] = None
		result['project_folder_path'] = None
		result['success'] = False
		result['error'] = f"{e}"
	return result

def get_branch_name(get_exports_on,current_default_branch):
	branch_name=current_default_branch
	if get_exports_on == "New Commit":
		if not current_default_branch:
			branch_name = "version-1"
	elif get_exports_on == "New Branch":
		if not current_default_branch:
			branch_name = "version-1"
		else:
			branch_name = f'''version-{eval(branch_name.split("-")[-1])+1}'''
	return branch_name

def get_commit_message(get_exports_on,last_push_commit):
	commit_msg=last_push_commit
	if get_exports_on == "New Commit":
		if not last_push_commit:
			commit_msg = "version-1"
		else:
			commit_msg = f'''version-{eval(commit_msg.split("-")[-1])+1}'''
	elif get_exports_on == "New Branch":
		if not last_push_commit:
			commit_msg = "version-1"
	return commit_msg