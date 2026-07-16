import io, os, sys
from pathlib import Path

# ---- GUI helpers --------------------------------------------------------------
try:
    from tkinter import Tk, filedialog
except Exception:
    print("tkinter is required for the file dialog.")
    sys.exit(1)

# ---- Pillow (needs AVIF plugin) -----------------------------------------------
try:
    from PIL import Image
except Exception as e:
    print(f"Could not import Pillow: {e}")
    sys.exit(1)

# Register the AVIF plug‑in – must be done **before** any image is used.
try:
    import pillow_avif        # registers AVIF support with Pillow
except ImportError as e:
    print("pillow-avif-plugin not found. Install it with:")
    print("   pip install pillow-avif-plugin")
    sys.exit(1)

# ---- libimagequant (colour‑reduction) -----------------------------------------
try:
    import imagequant
except Exception as e:
    print("libimagequant is required for palette reduction. Install via 'pip install imagequant'")
    sys.exit(1)

# ---- Settings ---------------------------------------------------------------
import settings   # module generated from the file "settings.py"

def print_current_settings() -> None:
    """Show all options that the script will use."""
    print("\n=== Current Settings ===")
    for name in [
        "resolution",
        "target_size_kb",
        "remove_metadata",
        "minimum_passes",
        "maximum_passes",
        "grayscale",
        "num_colours_MAX",
        "num_colours_MIN",
        "save_path",
    ]:
        print(f" {name:18s} : {getattr(settings, name)}")
    print("========================\n")

def update_save_path_in_settings(new_path: str) -> None:
    """Write the chosen folder back into settings.py."""
    file = Path(__file__).parent / "settings.py"
    lines = file.read_text().splitlines()
    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith("save_path"):
            parts = line.split("#", 1)
            new_line = f'save_path = "{new_path}"'
            if len(parts) == 2:
                new_line += f" #{parts[1].strip()}"
            lines[i] = new_line
            found = True
            break
    if not found:          # append a new line
        lines.append(f"\n# The folder where compressed images are saved")
        lines.append(f'save_path = "{new_path}"')
    file.write_text("\n".join(lines) + "\n")

def parse_resolution(res_str: str):
    """Parse 'WxH' into (w, h); empty string → None."""
    if not res_str:
        return None
    try:
        w, h = map(int, res_str.lower().split("x"))
        return w, h
    except Exception:
        return None

# ---- Core compression --------------------------------------------------------
def compress_to_avif(
    img: Image.Image,
    target_bytes: int,
    num_min: int,
    num_max: int,
    min_passes: int,
    max_passes: int,
) -> tuple[bytes | None, int]:
    """
    Compress an image to AVIF.

    Returns (data, passes_used).  If the target size can’t be reached,
    the best result found during the passes is returned.
    """
    # ---------- helper to encode with a given quality ----------
    def _encode(img_to_encode: Image.Image, qual: int) -> bytes | None:
        out_buf = io.BytesIO()
        try:
            img_to_encode.save(out_buf, format="AVIF", quality=qual,
                               speed=1, subsampling="4:2:0",
                               range_="full")
            return out_buf.getvalue()
        except Exception:
            return None

    best_overall_data = None
    best_overall_size = float("inf")
    passes_used = 0
    colors = num_max          # start with the maximum palette size
    scale_factor = 1.0         # full resolution at first pass
    prev_best_size = None     # size from previous pass

    base_img = img.copy()   # keep an untouched copy for each new pass

    for _ in range(max_passes):
        passes_used += 1

        # ----- resize if we are scaling down ---------------------------------
        cur_w, cur_h = int(base_img.width * scale_factor), int(base_img.height * scale_factor)
        cur_img = base_img.resize((cur_w, cur_h), Image.LANCZOS)

        # ----- colour‑reduction (if in colour mode) ---------------------------
        if cur_img.mode != "L" and colors < 256:
            cur_img = imagequant.quantize_pil_image(
                cur_img,
                max_colors=colors,
                dithering_level=1.0,
                min_quality=0,
                max_quality=100,
            )
            # libimagequant returns a palettised image – convert to RGB for AVIF
            if cur_img.mode != "RGB":
                cur_img = cur_img.convert("RGB")

        # ----- strip all metadata --------------------------------------------
        for key in ("exif", "icc_profile", "xmp"):
            cur_img.info.pop(key, None)

        # --------------------------------------------------------------------
        # Binary search on quality (5‑90) to get the largest file <= target_bytes
        # --------------------------------------------------------------------
        low, high = 5, 90                     # safe bounds for AVIF quality
        best_q_for_pass = None
        best_data_for_pass = None

        while low <= high:
            mid = (low + high) // 2
            data = _encode(cur_img, mid)
            if data is None:                  # encode failed – try lower quality
                high = mid - 1
                continue

            size = len(data)

            if size <= target_bytes:
                best_q_for_pass = mid
                best_data_for_pass = data
                low = mid + 1                 # maybe a higher quality still fits
            else:
                high = mid - 1

        if best_data_for_pass is None:         # nothing fitted – try the lowest we tried
            data = _encode(cur_img, low)
            if data is not None:
                best_data_for_pass = data
                best_q_for_pass = low

        if best_data_for_pass is None:
            break                              # cannot encode even at lowest quality

        cur_size = len(best_data_for_pass)

        # If we hit the target exactly or better than previous passes.
        if cur_size <= target_bytes:
            return best_data_for_pass, passes_used

        # Keep the smallest file found so far (might be > target).
        if cur_size < best_overall_size:
            best_overall_size = cur_size
            best_overall_data = best_data_for_pass

        # --------------------------------------------------------------------
        # Stop early if improvement is <3 % and we have at least min_passes.
        # --------------------------------------------------------------------
        if prev_best_size is not None:
            improvement = (prev_best_size - cur_size) / prev_best_size
            if improvement < 0.03 and passes_used >= min_passes:
                return best_overall_data, passes_used

        prev_best_size = cur_size

        # ----- prepare for next pass: reduce colours or shrink resolution -----
        if colors > num_min:
            new_colors = max(num_min, int(colors * 0.8))
            if new_colors == colors:          # avoid infinite loop
                new_colors -= 1
            colors = new_colors
        else:
            if scale_factor > 0.5:
                scale_factor *= 0.95           # shrink a bit each pass
            else:
                break                          # cannot improve further

    # No pass satisfied the target – return best result found.
    return best_overall_data, passes_used
# ---- Main entry point --------------------------------------------------------
def main() -> None:
    print_current_settings()

    # 1️⃣ Pick source image -----------------------------------------------
    root = Tk()
    root.withdraw()
    src_path = filedialog.askopenfilename(
        title="Select an image to compress",
        filetypes=[
            ("Images", "*.jpg *.jpeg *.png *.bmp *.gif *.tif *.tiff *.webp *.avif"),
            ("All files", "*.*")
        ]
    )
    if not src_path:
        print("No source file chosen – exiting.")
        sys.exit(0)

    # 2️⃣ Load image -----------------------------------------------
    try:
        img = Image.open(src_path)
    except Exception as e:
        print(f"Could not open image: {e}")
        sys.exit(1)

    # 3️⃣ Apply user options -----------------------------------------
    if getattr(settings, "grayscale", False):
        img = img.convert("L")          # greyscale
    else:
        img = img.convert("RGB")         # keep full colour

    res_target = parse_resolution(getattr(settings, "resolution", ""))
    if res_target:
        max_w, max_h = res_target
        img.thumbnail((max_w, max_h), Image.LANCZOS)
        print(f"Resized to: {img.width}x{img.height}")

    # 4️⃣ Target size in bytes -----------------------------------------
    try:
        target_kb = float(getattr(settings, "target_size_kb", 5))
        if target_kb <= 0:
            raise ValueError()
    except Exception:
        print("Invalid target_size_kb in settings – using default 5 KB.")
        target_kb = 5
    target_bytes = int(target_kb * 1024)

    # 5️⃣ Run compression passes ---------------------------------------
    num_min = getattr(settings, "num_colours_MIN", 32)
    num_max = getattr(settings, "num_colours_MAX", 192)
    min_passes = getattr(settings, "minimum_passes", 3)
    max_passes = getattr(settings, "maximum_passes", 10)

    data, passes_used = compress_to_avif(
        img,
        target_bytes,
        num_min,
        num_max,
        min_passes,
        max_passes
    )

    if data is None:
        print("Compression failed – no output produced.")
        sys.exit(1)

    final_kb = len(data) / 1024
    print(f"\nFinished – {passes_used} pass{'es'[:passes_used==1]}")
    print(f"Output size : {final_kb:.2f} KB (target was {target_kb:.2f} KB)\n")

    # 6️⃣ Determine output folder ---------------------------------------
    save_dir = getattr(settings, "save_path", "").strip()
    if not save_dir or not Path(save_dir).exists():
        chosen_dir = filedialog.askdirectory(
            title="Select folder for compressed images",
            initialdir=os.path.dirname(src_path)
        )
        if not chosen_dir:
            print("No folder chosen – exiting.")
            sys.exit(1)
        save_dir = chosen_dir
        update_save_path_in_settings(save_dir)   # persist for next run

    # 7️⃣ Write the AVIF file -----------------------------------------
    original_name = Path(src_path).stem
    out_path = Path(save_dir) / f"{original_name}.avif"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "wb") as f:
        f.write(data)

    print(f"File saved: {out_path}")


# ------------------------------------------------------------------
if __name__ == "__main__":
    main()
