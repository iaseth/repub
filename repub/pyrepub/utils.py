import os

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

