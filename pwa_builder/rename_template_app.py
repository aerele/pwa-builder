import os
import shutil
from frappe import _, scrub


def rename_template_app(app_path,new_app_name="Aerele",old_app_name="PWA Template",old_url="pwa",new_url="new_pwa"):
	new_module_name = new_app_name
	new_app_name = scrub(new_app_name)
	old_module_name = old_app_name
	old_app_name = scrub(old_app_name)

	# Step 1: Rename the app directory and all subdirectories/files
	new_app_path = os.path.join(os.path.dirname(app_path), new_app_name)
	
	if os.path.exists(new_app_path):
		print(f"Error: Directory '{new_app_name}' already exists.")
		return

	print(f"Renaming app directory from '{old_app_name}' to '{new_app_name}'")
	shutil.move(app_path, new_app_path)

	# Step 2: Recursively rename all subdirectories and files containing the old app name
	print("Renaming all subdirectories and files")
	rename_subdirectories_and_files(new_app_path, old_app_name, new_app_name,old_url,new_url)

	# Step 3: Update all references in code files (including module names)
	print("Updating all references in code files")
	update_import_paths(new_app_path, old_app_name, new_app_name,old_module_name,new_module_name, old_url, new_url)

	print("Renaming completed successfully!")

def rename_subdirectories_and_files(root_path, old_app_name, new_app_name, old_url, new_url):
	"""Recursively rename all subdirectories and files containing the old app name."""
	for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
		# Skip .git directories and their contents
		if '.git' in dirnames:
			dirnames.remove('.git')

		# Rename directories
		for dirname in dirnames:
			if old_app_name in dirname:
				old_dir_path = os.path.join(dirpath, dirname)
				new_dir_path = os.path.join(dirpath, dirname.replace(old_app_name, new_app_name))
				print(f"Renaming directory '{old_dir_path}' to '{new_dir_path}'")
				shutil.move(old_dir_path, new_dir_path)
			elif old_url in dirname:
				old_dir_path = os.path.join(dirpath, dirname)
				new_dir_path = os.path.join(dirpath, dirname.replace(old_url, new_url))
				print(f"Renaming URL directory '{old_url}' to '{new_url}'")
				shutil.move(old_dir_path, new_dir_path)
		
		# Rename files
		for filename in filenames:
			if old_app_name in filename:
				old_file_path = os.path.join(dirpath, filename)
				new_file_path = os.path.join(dirpath, filename.replace(old_app_name, new_app_name))
				print(f"Renaming file '{old_file_path}' to '{new_file_path}'")
				shutil.move(old_file_path, new_file_path)

def replace_in_file(file_path, old_string, new_string, old_module_name, new_module_name, old_url, new_url):
	"""Replace old_string and old_module_name with new_string and new_module_name in a file."""
	try:
		with open(file_path, 'r', encoding='utf-8') as file:
			file_data = file.read()
	except (UnicodeDecodeError, PermissionError):
		print(f"Skipping file due to encoding or permission issues: {file_path}")
		return
	
	# Replace app name and module name
	new_data = file_data.replace(old_string, new_string).replace(old_module_name, new_module_name).replace(old_url,new_url)
	try:
		with open(file_path, 'w', encoding='utf-8') as file:
			file.write(new_data)
	except PermissionError:
		print(f"Skipping file due to write permission issues: {file_path}")

def update_import_paths(root_path, old_app_name, new_app_name,old_module_name, new_module_name, old_url, new_url):
	"""Recursively update import paths and module names in all files."""

	for dirpath, _, filenames in os.walk(root_path):
		# Skip .git directories and their contents
		if '.git' in dirpath:
			continue
		for filename in filenames:
			file_path = os.path.join(dirpath, filename)
			replace_in_file(file_path, old_app_name, new_app_name, old_module_name, new_module_name, old_url, new_url)
