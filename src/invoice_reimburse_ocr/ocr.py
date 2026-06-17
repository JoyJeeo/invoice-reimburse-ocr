from __future__ import annotations

from pathlib import Path
from typing import Protocol


class OCREngine(Protocol):
    def extract_text(self, file_path: Path) -> str:
        ...


class SidecarTextOCREngine:
    """Development/test OCR engine that reads text from an adjacent .txt file."""

    def extract_text(self, file_path: Path) -> str:
        sidecar = file_path.with_suffix(".txt")
        if not sidecar.exists():
            raise RuntimeError(f"未找到旁路文本文件，且未启用真实 OCR：{sidecar}")
        return sidecar.read_text(encoding="utf-8")


class PaddleOCREngine:
    def __init__(self) -> None:
        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise RuntimeError("未安装 PaddleOCR，请安装可选 OCR 依赖或使用 --ocr-engine sidecar") from exc
        self._ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)

    def extract_text(self, file_path: Path) -> str:
        result = self._ocr.ocr(str(file_path), cls=True)
        lines: list[str] = []
        for page in result or []:
            for item in page or []:
                if len(item) >= 2 and item[1]:
                    lines.append(str(item[1][0]))
        if not lines:
            raise RuntimeError("OCR 未识别到文本")
        return "\n".join(lines)


def create_ocr_engine(name: str) -> OCREngine:
    if name == "paddle":
        return PaddleOCREngine()
    if name == "sidecar":
        return SidecarTextOCREngine()
    raise ValueError(f"不支持的 OCR 引擎：{name}")
