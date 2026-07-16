
# ── General options ---------------------------------------------
resolution          = ""           # e.g. "500x500"  – empty means no resizing
target_size_kb      = 3            # desired maximum size in kilobytes
remove_metadata     = True         # strip EXIF / ICC / XMP data
minimum_passes      = 1            # minimum number of compression passes
maximum_passes      = 2           # stop after this many attempts

# ── Colour handling -----------------------------------------------
grayscale           = False        # keep full colour if False, else greyscale

num_colours_MAX     = 256          # colours to start with (2–256)
num_colours_MIN     = 64           # minimum allowed colours

# ── File output ----------------------------------------------------
save_path = "C:/Users/Jason/Downloads"  # automatically updated by Image_Tools.py
