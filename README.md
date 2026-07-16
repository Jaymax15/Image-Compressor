# Extreme Image Compressor

Extreme Image Compressor is a lightweight Python-based command-line utility designed for aggressive image compression while preserving as much visual quality as possible. The application has no GUI and is intended to be fast, simple, and highly configurable.

Using modern AVIF encoding techniques, the compressor is capable of reducing images from several hundred kilobytes down to extremely small file sizes. In testing, images as large as 500 KB have been compressed to approximately 20 KB or less with surprisingly minimal visible quality loss, depending on the target size selected.

## Features

* Command-line interface (CLI)
* Extremely aggressive compression
* Configurable target file size (KB)
* Optional image resizing
* Metadata removal
* Multi-pass compression support
* Optional grayscale conversion
* Adjustable color palette limits
* Outputs exclusively to AVIF format
* Supports compressing existing AVIF files

## How It Works

The compressor attempts to achieve a user-defined target size in kilobytes. Once the image reaches the requested size (or the closest possible approximation), the process stops automatically.

Example results:

| Original Size | Target Size | Typical Quality                               |
| ------------- | ----------- | --------------------------------------------- |
| 500 KB        | 20 KB       | Heavy compression, visible artifacts possible |
| 300 KB        | 100 KB      | Minimal visible loss                          |
| 300 KB        | 50 KB       | Good quality with excellent compression       |

Smaller target sizes will naturally result in greater image degradation. More conservative targets generally produce excellent results while still providing significant reductions in file size.

## Configuration

### Resolution

You may optionally specify a maximum resolution.

* If an image exceeds the configured dimensions, it will be resized.
* Leaving this value blank preserves the original resolution.

### Target Size (KB)

Determines the desired output size.

Examples:

* `100` → Attempts to produce a ~100 KB image.
* `50` → Higher compression with good quality.
* `20` → Extreme compression; artifacts are likely.

### Remove Metadata

Recommended: `True`

This removes EXIF and other metadata from the image, reducing file size without affecting visual quality.

### Compression Passes

The compressor supports multiple passes over an image.

Recommended values:

* `1` – Fastest
* `2` – Recommended
* `3` – Maximum recommended

Using additional passes can improve compression efficiency but may increase compression artifacts during aggressive reductions.

### Grayscale

Recommended: `False`

For smaller images, grayscale typically saves very little space. It may only become useful for extremely large, high-resolution images where every kilobyte matters.

### Color Quality

Controls the minimum color palette used during compression.

Recommended values:

* Minimum: `64`
* Maximum: `256`

While lower values can produce additional compression, they can significantly reduce image quality. Values below `64` are generally not recommended unless extreme compression is required.

## Output

* Input: Most common image formats.
* Output: Always `.avif`

All compressed images are exported as AVIF files regardless of the original format.

An added benefit of this approach is that AVIF files can be recompressed multiple times if desired, allowing for even more aggressive size reductions.

## Recommendations

For the best balance between quality and compression:

```text
Target Size: 50–100 KB
Passes: 2
Metadata Removal: True
Grayscale: False
Minimum Colors: 64
Maximum Colors: 256
```

Windows (PowerShell) Installation

Open PowerShell and run the following command:
```powershell
py -3.11 -m pip install --upgrade pip Pillow pillow-avif-plugin imagequant
```

# Requirements

This project was developed and tested using **Python 3.11** and is recommended for the best compatibility.

### Required Python Packages

* Pillow
* pillow-avif-plugin
* imagequant

> **Note:** `tkinter` is required for the file selection dialogs. It is included with most standard Python installations on Windows. Linux users may need to install it separately.

The program also requires a `settings.py` file to be present in the same directory as `Image_Compressor.py`.

## Running the Program

```bash
python Image_Compressor.py
```

The application will:

1. Open a file selection dialog.
2. Allow you to choose an image.
3. Compress the image using AVIF encoding.
4. Reduce colors intelligently using `libimagequant`.
5. Save the compressed image as `.avif`.

---

## Supported Input Formats

* JPG / JPEG
* PNG
* BMP
* GIF
* TIFF
* WEBP
* AVIF

---

## Notes

* Recommended Python Version: **3.11**
* `tkinter` must be available on your system.
* The script automatically removes image metadata during compression.
* Compression settings such as target size, color limits, and output location are configured through `settings.py`.
* AVIF output provides extremely high compression ratios while maintaining impressive image quality.

Despite its simplicity, the compressor is capable of producing remarkably small images while maintaining surprisingly good visual fidelity.

Contributions, optimizations, and additional encoding techniques are always welcome.
