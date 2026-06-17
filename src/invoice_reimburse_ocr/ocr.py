from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
from typing import Protocol

from .preprocessor import normalize_image_for_ocr, preprocess_for_ocr


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
        try:
            self._ocr = PaddleOCR(lang="ch", use_textline_orientation=True)
        except Exception:
            self._ocr = PaddleOCR(use_angle_cls=True, lang="ch")

    def extract_text(self, file_path: Path) -> str:
        with preprocess_for_ocr(file_path) as preprocessed:
            result = self._run_ocr(preprocessed.path)
        lines = _extract_paddle_text_lines(result)
        if not lines:
            raise RuntimeError("OCR 未识别到文本")
        return "\n".join(lines)

    def _run_ocr(self, image_path: Path):
        if hasattr(self._ocr, "predict"):
            return self._ocr.predict(str(image_path))
        return self._ocr.ocr(str(image_path), cls=True)


class TesseractOCREngine:
    def __init__(self, language: str | None = None) -> None:
        if not shutil.which("tesseract"):
            raise RuntimeError("未安装 tesseract 命令行工具")
        self._language = language or _detect_tesseract_language()

    def extract_text(self, file_path: Path) -> str:
        import tempfile

        with tempfile.TemporaryDirectory(prefix="invoice_tesseract_") as temp_dir:
            image_path = normalize_image_for_ocr(file_path, Path(temp_dir))
            env = os.environ.copy()
            local_tessdata = Path.cwd() / ".tessdata"
            if local_tessdata.exists():
                env["TESSDATA_PREFIX"] = str(local_tessdata)
            result = subprocess.run(
                ["tesseract", str(image_path), "stdout", "-l", self._language, "--psm", "6"],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            if result.returncode != 0:
                raise RuntimeError(f"Tesseract OCR 失败：{result.stderr.strip()}")
            text = result.stdout.strip()
            if not text:
                raise RuntimeError("Tesseract OCR 未识别到文本")
            return text


def _detect_tesseract_language() -> str:
    local_tessdata = Path.cwd() / ".tessdata"
    if (local_tessdata / "chi_sim.traineddata").exists():
        return "chi_sim+eng+snum"
    return "eng+snum"


def _extract_paddle_text_lines(result) -> list[str]:
    lines: list[str] = []
    for page in result or []:
        if isinstance(page, dict):
            rec_texts = page.get("rec_texts") or page.get("text") or []
            lines.extend(str(text) for text in rec_texts if text)
            continue
        if hasattr(page, "json"):
            page_json = page.json
            if isinstance(page_json, dict):
                rec_texts = page_json.get("res", {}).get("rec_texts") or []
                lines.extend(str(text) for text in rec_texts if text)
                continue
        for item in page or []:
            if len(item) >= 2 and item[1]:
                lines.append(str(item[1][0]))
    return lines


def create_ocr_engine(name: str) -> OCREngine:
    if name == "paddle":
        return PaddleOCREngine()
    if name == "tesseract":
        return TesseractOCREngine()
    if name == "sidecar":
        return SidecarTextOCREngine()
    raise ValueError(f"不支持的 OCR 引擎：{name}")
