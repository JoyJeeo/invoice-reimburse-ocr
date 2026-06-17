from pathlib import Path

from invoice_reimburse_ocr.file_scanner import discover_input_files


def test_discover_input_files_recursively_scans_supported_files(tmp_path: Path):
    nested = tmp_path / "nested"
    nested.mkdir()
    supported = [
        tmp_path / "invoice.jpg",
        tmp_path / "invoice.png",
        nested / "invoice.bmp",
        nested / "invoice.tiff",
        nested / "invoice.pdf",
    ]
    for path in supported:
        path.write_bytes(b"demo")
    (tmp_path / "notes.txt").write_text("not an input", encoding="utf-8")

    files = discover_input_files(tmp_path)

    assert files == sorted(supported)
