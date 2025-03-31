# repub

`repub` is a Python script designed to optimize EPUB files by removing embedded fonts and associated styles. This process reduces the file size and allows e-readers, such as Kindle, to utilize their default fonts for a consistent reading experience.

## Features

- **Font Removal**: Deletes embedded font files (`.otf`, `.ttf`, `.woff`, `.woff2`) from the EPUB archive.
- **Style Cleanup**: Eliminates `@font-face` declarations and `font-family` properties from CSS files within the EPUB.
- **Manifest Update**: Removes references to custom fonts in the EPUB's manifest file (`.opf`).
- **File Size Reduction**: Outputs a leaner version of the original EPUB, appending `-lean` to the filename, and reports the space saved.

## Usage

1. **Ensure Python 3.x is installed** on your system.

2. **Clone the repository**:

   ```sh
   git clone https://github.com/iaseth/repub.git
   ```


3. **Navigate to the project directory**:

   ```sh
   cd repub
   ```


4. **Run the script** with the path to your EPUB file as an argument:

   ```sh
   python3 repub.py /path/to/your/book.epub
   ```


   By default, the script creates a new EPUB file with `-lean` appended to the original filename (e.g., `book-lean.epub`). To overwrite the original file, use the `--replace` flag:

   ```sh
   python3 repub.py --replace /path/to/your/book.epub
   ```


## Example Output


```
Found EPUB: Bag of Bones - Stephen King.epub
    Cleaning OPF file:
        Reduced OPF: content.opf 11350 => 7376 (35.0% saved)
    Cleaning 1 CSS files:
        Reduced CSS: style0001.css 15923 => 11536 (27.6% saved)
            Saved 4.3 KB
    Cleaning 24 Font files:
        Removed font: font00408.otf (54.3 KB)
        Removed font: font00399.otf (34.5 KB)
        Removed font: font00400.otf (26.4 KB)
        Removed font: font00406.otf (78.1 KB)
        Removed font: font00417.otf (182.9 KB)
        Removed font: font00418.otf (49.6 KB)
        Removed font: font00404.otf (26.9 KB)
        Removed font: font00398.otf (34.4 KB)
        Removed font: font00403.otf (26.5 KB)
        Removed font: font00412.otf (116.2 KB)
        Removed font: font00405.otf (28.1 KB)
        Removed font: font00410.otf (41.6 KB)
        Removed font: font00419.otf (37.7 KB)
        Removed font: font00420.otf (34.6 KB)
        Removed font: font00415.otf (73.2 KB)
        Removed font: font00397.otf (55.1 KB)
        Removed font: font00416.otf (180.1 KB)
        Removed font: font00411.otf (29.5 KB)
        Removed font: font00413.otf (87.5 KB)
        Removed font: font00402.otf (25.5 KB)
        Removed font: font00414.otf (71.7 KB)
        Removed font: font00407.otf (30.0 KB)
        Removed font: font00409.otf (39.9 KB)
        Removed font: font00401.otf (25.1 KB)
            Saved 1389.3 KB
Saved: Bag of Bones - Stephen King-lean.epub
    Original EPUB size: 1844.67 KB
        Lean EPUB size: 872.49 KB
     Total space saved: 972.18 KB (52.7%)
```


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

By using `repub`, you can ensure that your EPUB files are optimized for size and display, leveraging your e-reader's default fonts for a uniform reading experience. 
