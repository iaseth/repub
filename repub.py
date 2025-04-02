#!/usr/bin/env python3
import argparse
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile
from typing import List

from PIL import Image



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


def verbose(*args, **kwargs):
	if cmd_args.verbose:
		print(*args, **kwargs)



def filesize_string(filepath=None, size=0):
	if filepath:
		size = os.path.getsize(filepath)
	return f"{size / 1024:.2f} KB"



def get_image_resolution(image_path):
	"""Returns the resolution (width, height) of a JPG/JPEG image."""
	try:
		with Image.open(image_path) as img:
			return img.size  # (width, height)
	except Exception as e:
		print(f"Error opening {image_path}: {e}")
		return None



def remove_font_styles(css_file):
	filename = os.path.basename(css_file)
	with open(css_file, 'r', encoding='utf-8') as file:
		css_content = file.read()

	old_size = len(css_content)
	# Remove @font-face declarations
	css_content = re.sub(r'@font-face\s*{.*?}', '', css_content, flags=re.DOTALL)

	# Remove font-family properties
	css_content = re.sub(r'font-family:\s*[^;]+;', '', css_content, flags=re.IGNORECASE)

	new_size = len(css_content)
	if new_size == old_size:
		verbose(f"\t\t\tSkipped CSS: {yellow(filename)} already optimized!")
		return 0

	with open(css_file, 'w', encoding='utf-8') as file:
		file.write(css_content)

	saved_bytes = old_size - new_size
	saved_percent = 100 * saved_bytes / old_size
	verbose(f"\t\t\tReduced CSS: {green(filename)} {old_size} => {new_size} ({saved_percent:.1f}% saved)")
	return saved_bytes


def remove_custom_fonts(opf_file):
	filename = os.path.basename(opf_file)
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

	saved_bytes = old_size - new_size
	if saved_bytes == 0:
		verbose(f"\t\t\tSkipped OPF: {yellow(filename)} already optimized")
		return []

	saved_percent = 100 * saved_bytes / old_size
	verbose(f"\t\t\tReduced OPF: {green(os.path.basename(opf_file))} {old_size} => {new_size} ({saved_percent:.1f}% saved)")

	return font_files


def compress_image(image_file, idx=0, max_image_pixels=720):
	"""Compresses the image to the specified size (width, height) in place."""
	filename = os.path.basename(image_file)
	size = get_image_resolution(image_file)
	width, height = size

	big_size = max(width, height)
	needs_compression = big_size > max_image_pixels

	if needs_compression:
		scale_factor = max_image_pixels / big_size
		width_after = int(width * scale_factor)
		height_after = int(height * scale_factor)
		size_after = (width_after, height_after)

		try:
			with Image.open(image_file) as img:
				img = img.resize(size_after, Image.LANCZOS)
				img.save(image_file, optimize=True, quality=85)
			verbose(f"\t\t\t{idx:3}. Compressed image {green(filename):20} => {size} to {size_after}")
		except Exception as e:
			verbose(f"\t\t\t{idx:3}. Error compressing {red(filename)}: {e}")
	else:
		verbose(f"\t\t\t{idx:3}. Skipped image {yellow(filename):20} => {size}")


def process_epub(epub_path, replace=False, max_image_pixels=720):
	if not os.path.isfile(epub_path):
		print(f"Not found: {red(epub_path)}"); return

	if not epub_path.endswith('.epub'):
		print(f"Bad path: {red(epub_path)}"); return

	print(f"\tFound EPUB: {green(epub_path)} ({filesize_string(filepath=epub_path)})")

	base_name = os.path.splitext(epub_path)[0]
	lean_epub_path = epub_path if replace else f"{base_name}-lean.epub"
	temp_dir = f"{base_name}-temp"

	# Extract EPUB
	with zipfile.ZipFile(epub_path, 'r') as zip_ref:
		zip_ref.extractall(temp_dir)

	# Identify CSS and OPF files
	opf_file = None
	image_files = []
	css_files = []
	font_files = []

	for root, _, files in os.walk(temp_dir):
		for file in files:
			path = os.path.join(root, file)
			if file.endswith('.opf'):
				opf_file = path
			elif file.endswith('.jpg') or file.endswith('.jpeg'):
				image_files.append(path)
			elif file.endswith('.css'):
				css_files.append(path)

	if opf_file:
		verbose(f"\t\tCleaning OPF file:")
		font_files = remove_custom_fonts(opf_file)

	if len(css_files) > 0:
		verbose(f"\t\tCleaning {len(css_files)} CSS files:")
		saved_bytes = 0
		for css_file in css_files:
			saved_bytes += remove_font_styles(css_file)
		verbose(f"\t\t\t\tSaved {saved_bytes/1024:.1f} KB")

	# Delete font files
	if len(font_files) > 0:
		verbose(f"\t\tCleaning {len(font_files)} Font files:")
		saved_bytes = 0

		for font_file in enumerate(font_files):
			for root, _, files in os.walk(temp_dir):
				for file in files:
					if file in font_file or any(file.endswith(ext) for ext in ['.otf', '.ttf', '.woff', '.woff2']):
						font_path = os.path.join(root, file)
						size = os.path.getsize(font_path)
						os.remove(font_path)
						verbose(f"\t\t\tRemoved font: {green(os.path.basename(font_path))} ({size/1024:.1f} KB)")
						saved_bytes += size
		verbose(f"\t\t\t\tSaved {saved_bytes/1024:.1f} KB")

	if len(image_files) > 0 and max_image_pixels is not None:
		verbose(f"\t\tCleaning {len(image_files)} Image files:")
		for idx, image_file in enumerate(image_files, start=1):
			compress_image(image_file, idx=idx, max_image_pixels=max_image_pixels)

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
	print(f"\tSaved EPUB: {green(lean_epub_path)} ({filesize_string(filepath=lean_epub_path)})")

	# Compare sizes
	new_size = os.path.getsize(lean_epub_path)
	space_saved = original_size - new_size
	percentage_saved = (space_saved / original_size) * 100

	print(f"\t\tOriginal EPUB size: {filesize_string(size=original_size)}")
	print(f"\t\t    Lean EPUB size: {filesize_string(filepath=lean_epub_path)}")
	print(f"\t\t Total space saved: {space_saved / 1024:.2f} KB ({percentage_saved:.1f}%)")


def get_epub_file_paths(directory: str, recursive: bool = False) -> List[str]:
	if recursive:
		return [os.path.join(root, file)
				for root, _, files in os.walk(directory)
				for file in files if file.lower().endswith('.epub')]
	else:
		return [os.path.join(directory, file)
				for file in os.listdir(directory)
				if os.path.isfile(os.path.join(directory, file)) and file.lower().endswith('.epub')]



def main():
	parser = argparse.ArgumentParser(description="repub.py - remove custom fonts from EPUB ebooks")

	# Positional argument: Path
	parser.add_argument("path", type=str, help="Path to the file or directory")

	# Boolean flags with short and long options
	parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
	parser.add_argument("-D", "--directory", action="store_true", help="Process directories as well")
	parser.add_argument("-R", "--recursive", action="store_true", help="Process directories recursively")
	parser.add_argument("-r", "--replace", action="store_true", help="Replace original files")

	global cmd_args
	cmd_args = parser.parse_args()
	verbose(cmd_args)

	if os.path.isfile(cmd_args.path):
		process_epub(cmd_args.path, replace=cmd_args.replace)
	elif os.path.isdir(cmd_args.path):
		if cmd_args.directory:
			if cmd_args.recursive:
				print(f"Processing directory recursively: {cmd_args.path}")
				epub_paths = get_epub_file_paths(cmd_args.path, recursive=True)
			else:
				print(f"Processing directory: {cmd_args.path}")
				epub_paths = get_epub_file_paths(cmd_args.path)

			print(f"\tFound {len(epub_paths)} epub files inside directory!")
			for i, epub_path in enumerate(epub_paths, start=1):
				print(f"\tEpub {i}/{len(epub_paths)}: {green(epub_path)}")
				process_epub(epub_path, replace=cmd_args.replace)
		else:
			print(f"Ignored directory: {cmd_args.path}")
	else:
		print(f"Not found: {cmd_args.path}")


if __name__ == "__main__":
	main()
