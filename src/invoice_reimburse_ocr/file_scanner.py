from __future__ import annotations

from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
PDF_EXTENSIONS = {".pdf"}


def discover_input_files(input_dir: Path, include_pdf: bool = True) -> list[Path]:
    if not input_dir.exists():
        raise FileNotFoundError(f"输入目录不存在：{input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"输入路径不是目录：{input_dir}")

    extensions = set(IMAGE_EXTENSIONS)
    if include_pdf:
        extensions.update(PDF_EXTENSIONS)

    files = [
        path
        for path in input_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in extensions
    ]
    return sorted(files)
