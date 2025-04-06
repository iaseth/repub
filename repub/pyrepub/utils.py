import os
from typing import List

from PIL import Image



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


def get_filepaths_in_directory(dirpath):
	filepaths = []
	for root, _, files in os.walk(dirpath):
		for file in files:
			filepath = os.path.join(root, file)
			filepaths.append(filepath)
	return filepaths


def get_epub_file_paths(directory: str, recursive: bool = False) -> List[str]:
	if recursive:
		return [os.path.join(root, file)
				for root, _, files in os.walk(directory)
				for file in files if file.lower().endswith('.epub')]
	else:
		return [os.path.join(directory, file)
				for file in os.listdir(directory)
				if os.path.isfile(os.path.join(directory, file)) and file.lower().endswith('.epub')]

