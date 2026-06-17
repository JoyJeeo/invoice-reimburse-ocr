from pathlib import Path

from invoice_reimburse_ocr.cli import main


def test_cli_returns_error_for_empty_input_directory(tmp_path: Path, capsys):
    input_dir = tmp_path / "empty"
    input_dir.mkdir()

    exit_code = main(["--input", str(input_dir), "--output", str(tmp_path), "--ocr-engine", "sidecar"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "未发现支持的图片或PDF文件" in captured.out
