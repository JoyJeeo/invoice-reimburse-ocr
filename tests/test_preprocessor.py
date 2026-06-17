from pathlib import Path

from PIL import Image

from invoice_reimburse_ocr.preprocessor import preprocess_image


def test_preprocess_image_creates_binary_grayscale_output(tmp_path: Path):
    input_path = tmp_path / "invoice.png"
    output_path = tmp_path / "processed.png"
    image = Image.new("RGB", (40, 20), color="white")
    image.save(input_path, dpi=(200, 200))

    warnings = preprocess_image(input_path, output_path)

    assert output_path.exists()
    assert warnings == ["图片分辨率低于300dpi：invoice.png"]
    with Image.open(output_path) as processed:
        assert processed.mode in {"1", "L"}
