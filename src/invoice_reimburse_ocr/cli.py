from __future__ import annotations

import argparse
from pathlib import Path

from .ocr import create_ocr_engine
from .pipeline import process_folder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="发票批量识别与报销 Excel 导出工具")
    parser.add_argument("--input", required=True, help="待识别发票图片所在文件夹")
    parser.add_argument("--output", default=".", help="输出根目录，默认项目当前目录")
    parser.add_argument(
        "--ocr-engine",
        choices=["paddle", "sidecar"],
        default="sidecar",
        help="OCR 引擎：paddle 为真实 OCR，sidecar 读取同名 .txt 便于测试",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    engine = create_ocr_engine(args.ocr_engine)
    result = process_folder(Path(args.input), Path(args.output), engine)
    print(f"处理完成：共 {result.total} 张，待复核 {result.review_count} 张")
    print(f"输出目录：{result.output_dir}")
    print(f"报销明细：{result.reimbursement_file}")
    print(f"处理日志：{result.log_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
