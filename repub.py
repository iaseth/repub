#!/usr/bin/env python3
import zipfile
import os
import shutil
import re
import xml.etree.ElementTree as ET
import sys



def _colorize(color_code, *args, sep=' '):
	"""
	Returns a colored string using ANSI escape codes.
	"""
	text = sep.join(map(str, args))
	return f"\033[{color_code}m{text}\033[0m"

def red(*args, sep=' '):
	return _colorize(31, *args, sep=sep)

def green(*args, sep=' '):
	return _colorize(32, *args, sep=sep)

def yellow(*args, sep=' '):
	return _colorize(33, *args, sep=sep)

def blue(*args, sep=' '):
	return _colorize(34, *args, sep=sep)

def magenta(*args, sep=' '):
	return _colorize(35, *args, sep=sep)

def cyan(*args, sep=' '):
	return _colorize(36, *args, sep=sep)

def white(*args, sep=' '):
	return _colorize(37, *args, sep=sep)

def normal(*args, sep=' '):
	return sep.join(map(str, args))



def remove_font_styles(css_file):
	with open(css_file, 'r', encoding='utf-8') as file:
		css_content = file.read()

	old_size = len(css_content)
	# Remove @font-face declarations
	css_content = re.sub(r'@font-face\s*{.*?}', '', css_content, flags=re.DOTALL)

	# Remove font-family properties
	css_content = re.sub(r'font-family:\s*[^;]+;', '', css_content, flags=re.IGNORECASE)

	new_size = len(css_content)
	with open(css_file, 'w', encoding='utf-8') as file:
		file.write(css_content)

	saved_bytes = old_size - new_size
	saved_percent = 100 * saved_bytes / old_size
	print(f"\t\tReduced CSS: {green(os.path.basename(css_file))} {old_size} => {new_size} ({saved_percent:.1f}% saved)")
	return saved_bytes


def remove_custom_fonts(opf_file):
	old_size = os.path.getsize(opf_file)
	tree = ET.parse(opf_file)
	root = tree.getroot()
	namespace = {'opf': 'http://www.idpf.org/2007/opf'}

	manifest = root.find('opf:manifest', namespace)
	if manifest is None:
		return []

	items = manifest.findall('opf:item', namespace)
	font_files = []

	for item in items:
		href = item.get('href', '')
		media_type = item.get('media-type', '')
		if media_type.startswith('font/') or any(href.endswith(ext) for ext in ['.otf', '.ttf', '.woff', '.woff2']):
			manifest.remove(item)
			font_files.append(href)

	tree.write(opf_file, encoding='utf-8', xml_declaration=True)
	new_size = os.path.getsize(opf_file)

	saved = old_size - new_size
	saved_percent = 100 * saved / old_size
	print(f"\t\tReduced OPF: {green(os.path.basename(opf_file))} {old_size} => {new_size} ({saved_percent:.1f}% saved)")

	return font_files


def process_epub(epub_path, replace=False):
	if not os.path.isfile(epub_path):
		print(f"Not found: {red(epub_path)}"); return

	if not epub_path.endswith('.epub'):
		print(f"Bad path: {red(epub_path)}"); return

	print(f"Found EPUB: {green(epub_path)}")

	base_name = os.path.splitext(epub_path)[0]
	lean_epub_path = epub_path if replace else f"{base_name}-lean.epub"
	temp_dir = f"{base_name}-temp"

	# Extract EPUB
	with zipfile.ZipFile(epub_path, 'r') as zip_ref:
		zip_ref.extractall(temp_dir)

	# Identify CSS and OPF files
	opf_file = None
	css_files = []
	font_files = []

	for root, _, files in os.walk(temp_dir):
		for file in files:
			path = os.path.join(root, file)
			if file.endswith('.opf'):
				opf_file = path
			elif file.endswith('.css'):
				css_files.append(path)

	if opf_file:
		print(f"\tCleaning OPF file:")
		font_files = remove_custom_fonts(opf_file)

	if len(css_files) > 0:
		print(f"\tCleaning {len(css_files)} CSS files:")
		saved_bytes = 0
		for css_file in css_files:
			saved_bytes += remove_font_styles(css_file)
		print(f"\t\t\tSaved {saved_bytes/1024:.1f} KB")

	# Delete font files
	if len(font_files) > 0:
		print(f"\tCleaning {len(font_files)} Font files:")
		saved_bytes = 0

		for font_file in enumerate(font_files):
			for root, _, files in os.walk(temp_dir):
				for file in files:
					if file in font_file or any(file.endswith(ext) for ext in ['.otf', '.ttf', '.woff', '.woff2']):
						font_path = os.path.join(root, file)
						size = os.path.getsize(font_path)
						os.remove(font_path)
						print(f"\t\tRemoved font: {green(os.path.basename(font_path))} ({size/1024:.1f} KB)")
						saved_bytes += size
		print(f"\t\t\tSaved {saved_bytes/1024:.1f} KB")

	original_size = os.path.getsize(epub_path)
	# Create new EPUB
	with zipfile.ZipFile(lean_epub_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
		for root, _, files in os.walk(temp_dir):
			for file in files:
				file_path = os.path.join(root, file)
				archive_name = os.path.relpath(file_path, temp_dir)
				zipf.write(file_path, archive_name)

	# Clean up
	shutil.rmtree(temp_dir)
	print(f"Saved: {green(lean_epub_path)}")

	# Compare sizes
	new_size = os.path.getsize(lean_epub_path)
	space_saved = original_size - new_size
	percentage_saved = (space_saved / original_size) * 100

	print(f"\tOriginal EPUB size: {original_size / 1024:.2f} KB")
	print(f"\t    Lean EPUB size: {new_size / 1024:.2f} KB")
	print(f"\t Total space saved: {space_saved / 1024:.2f} KB ({percentage_saved:.1f}%)")


def main():
	args = sys.argv[1:]
	if len(args) == 0:
		print("Usage:\n\tpython3 repub.py <ebook1.epub> <ebook2.epub> . . ."); return

	replace = False
	for epub_path in args:
		process_epub(epub_path, replace=replace)


if __name__ == "__main__":
	main()
