"""Cut the background out of a photo and boost contrast -> data/portrait.png (RGBA)."""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent


def main(src):
    img = remove(Image.open(src).convert("RGB"))  # RGBA, background transparent
    rgba = np.array(img)
    gray = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)
    out = np.dstack([gray, gray, gray, rgba[:, :, 3]])
    Image.fromarray(out).save(ROOT / "data" / "portrait.png")
    print("wrote data/portrait.png")


if __name__ == "__main__":
    main(sys.argv[1])
