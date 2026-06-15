# KB PDF Compressor

A lightweight Linux desktop application for compressing PDF files to a target file size.

# Use "Strict Target Size Mode" for better results.
The compressor will always try to reduce the file below your target. 
⚠️This Option don't care about quality. ⚠️

## Features

* PDF compression
* Target file size compression (KB-based)
* PDF preview
* Image to PDF conversion
* Drag and drop support
* PDF and image file selection
* Compression statistics
* Linux AppImage support
* Simple desktop interface

## Supported Formats

### Input

* PDF
* JPG
* JPEG
* PNG
* WEBP
* BMP

### Output

* Compressed PDF

---

## Screenshots
### Main Window

 <img width="1085" height="805" alt="Screenshot from 2026-06-14 21-09-37" src="https://github.com/user-attachments/assets/4bf6672d-b983-4663-aaac-df4e0b940a19" />


### PDF Preview

<img width="1023" height="750" alt="Screenshot from 2026-06-14 21-11-25" src="https://github.com/user-attachments/assets/13f39cd2-f0d4-4f4c-a24b-2a33e27df046" />
<img width="1036" height="770" alt="Screenshot from 2026-06-14 21-10-29" src="https://github.com/user-attachments/assets/de4b67fc-0d73-43c7-be67-4b3792311123" />


---

## Requirements

* Linux Mint / Ubuntu / Debian
* Python 3.10+
* Ghostscript

Install Ghostscript:

```bash
sudo apt update
sudo apt install ghostscript
```

---

## Python Dependencies

Install dependencies inside a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate

pip install pillow
pip install pymupdf
pip install tkinterdnd2
pip install pyinstaller
```

---

## Running From Source

Open a terminal:

```bash
cd ~/pdf-compressor
source venv/bin/activate
python3 pdf_compressor.py
```

---

## Usage

### Compress a PDF

1. Open the application.
2. Drag and drop a PDF.
3. Set a target file size if desired.
4. Click **Compress PDF**.
5. The compressed file will be saved.

### Convert an Image to PDF

1. Drag and drop an image.
2. The image is converted to PDF.
3. Preview the generated PDF.
4. Configure compression settings.
5. Click **Compress PDF**.

### Target File Size

Example:
Target Size: 100 KB
```

The application attempts to compress the PDF as close as possible to the requested size while preserving readability.

---

## Building the Executable

Activate the virtual environment:

```bash
cd ~/pdf-compressor
source venv/bin/activate
```

Build:

```bash
pyinstaller --onefile --windowed pdf_compressor.py
```

The executable will be created in:

```text
dist/
```

---

## Building the AppImage

Build the executable first.

Then package it as an AppImage.

Output:

```text
KB-PDF-Compressor.AppImage
```

Example location:

```text
~/Downloads/KB-PDF-Compressor.AppImage
```

Run:

```bash
chmod +x KB-PDF-Compressor.AppImage
./KB-PDF-Compressor.AppImage
```

---

## Project Structure

```text
kb-pdf-compressor/
├── pdf_compressor.py
├── README.md
├── LICENSE
├── assets/
├── screenshots/
├── venv/
└── build/
```

---

## License

MIT License

You are free to use, modify, and distribute this software.

---

## Contributing

Contributions are welcome.

Ideas for future versions:

* Batch PDF compression
* Dark mode
* Compression queue
* PDF metadata viewer
* Multi-file processing
* Advanced compression profiles

---

## Author

Amit

KB PDF Compressor was created as a Linux desktop utility for PDF compression and image-to-PDF conversion.
