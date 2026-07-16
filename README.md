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

## Example Usage

```bash
python compressor.py input.jpg output.avif --target-size 50 --passes 2 --remove-metadata
```

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

## Notes

This project was built as a lightweight utility for situations where bandwidth and storage are limited. It pairs particularly well with low-bandwidth communication systems and can dramatically reduce the size of images intended for transmission over constrained networks.

Despite its simplicity, the compressor is capable of producing remarkably small images while maintaining surprisingly good visual fidelity.

Contributions, optimizations, and additional encoding techniques are always welcome.
