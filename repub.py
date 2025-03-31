#!/usr/bin/env python3
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


def process_epub(epub_path, replace=False):
	print(f"Processing EPUB: {green(epub_path)}")


def main():
	args = sys.argv[1:]
	if len(args) == 0:
		print("Usage:\n\tpython3 repub.py <ebook1.epub> <ebook2.epub> . . ."); return

	for epub_path in args:
		process_epub(epub_path, replace=True)


if __name__ == "__main__":
	main()
