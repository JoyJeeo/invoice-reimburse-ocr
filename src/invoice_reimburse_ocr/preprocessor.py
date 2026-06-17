from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator

from PIL import Image, ImageFilter


@dataclass(frozen=True)
class PreprocessResult:
    path: Path
    warnings: list[str] = field(default_factory=list)


@contextmanager
def preprocess_for_ocr(file_path: Path) -> Iterator[PreprocessResult]:
    if file_path.suffix.lower() == ".pdf":
        yield PreprocessResult(path=file_path)
        return

    with TemporaryDirectory(prefix="invoice_ocr_") as temp_dir:
        output_path = Path(temp_dir) / f"{file_path.stem}_preprocessed.png"
        warnings = preprocess_image(file_path, output_path)
        yield PreprocessResult(path=output_path, warnings=warnings)


def preprocess_image(input_path: Path, output_path: Path) -> list[str]:
    warnings: list[str] = []
    with Image.open(input_path) as image:
        dpi = image.info.get("dpi")
        if dpi and (dpi[0] < 300 or dpi[1] < 300):
            warnings.append(f"图片分辨率低于300dpi：{input_path.name}")

        processed = image.convert("L")
        processed = processed.filter(ImageFilter.MedianFilter(size=3))
        processed = processed.point(lambda pixel: 255 if pixel > 170 else 0, mode="1")
        processed = _deskew_with_opencv_if_available(processed)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        processed.save(output_path)
    return warnings


def _deskew_with_opencv_if_available(image: Image.Image) -> Image.Image:
    try:
        import cv2
        import numpy as np
    except ImportError:
        return image

    array = np.array(image.convert("L"))
    coords = np.column_stack(np.where(array < 255))
    if len(coords) < 20:
        return image

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    if abs(angle) < 0.5 or abs(angle) > 10:
        return image

    height, width = array.shape[:2]
    center = (width // 2, height // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        array,
        matrix,
        (width, height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return Image.fromarray(rotated)
