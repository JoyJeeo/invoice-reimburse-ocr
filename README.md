# invoice-reimburse-ocr

发票批量识别与报销 Excel 导出工具。本项目按 `需求手册.md` 实现本地批量处理流程：读取文件夹中的发票图片，识别并解析核心报销字段，生成模板文件、正式报销明细和独立处理日志。

## 功能

- 递归读取 `jpg/jpeg/png/bmp/tif/tiff/pdf` 文件。
- 通过可替换 OCR 引擎提取文本：
  - `sidecar`：读取同名 `.txt` 文件，适合开发、测试和无 OCR 环境演示。
  - `paddle`：使用 PaddleOCR 做真实本地 OCR。
- 解析发票代码、号码、日期、金额、购销方名称和税号。
- 识别付款记录/支付凭证，提取付款日期、交易单号、付款金额、付款方、收款方和付款方式，并加入正式报销明细。
- 若识别到外币发票，会提示输入对应人民币汇率，也可通过 `--exchange-rate USD=7.25` 预先指定。
- 自动去重：重复发票、重复付款记录不会进入正式报销明细，但会在 `处理日志.xlsx` 中标记为“重复已去重”。
- 自动校验必填字段、金额、日期和同批次重复发票号码。
- 导出到 `outputs/YYYYMMDD_HHMMSS/`：
  - `发票报销模板.xlsx`
  - `报销明细_YYYYMMDD_HHMMSS.xlsx`
  - `处理日志.xlsx`

正式报销明细只包含需求手册规定的 10 个核心字段，不混入文件名、状态、错误信息等辅助列。

## 环境准备

推荐使用 Conda：

```bash
conda env create -f environment.yml
conda activate invoice-reimburse-ocr
pip install -e ".[test]"
```

如需真实 OCR，再根据本机系统安装 PaddleOCR 相关依赖：

```bash
pip install paddleocr paddlepaddle opencv-python
```

## 使用方式

项目根目录下已预留 `invoices/` 目录，用来放置待识别的发票图片、付款记录截图或 PDF。真实票据属于敏感数据，目录中的文件默认不会被 Git 提交。

开发/测试模式，图片旁边放一个同名 `.txt` 文件：

```bash
invoice-ocr --input ./invoices --ocr-engine sidecar
```

真实 OCR 模式：

```bash
invoice-ocr --input ./invoices --ocr-engine paddle
```

外币发票可直接传入汇率：

```bash
invoice-ocr --input ./invoices --ocr-engine sidecar --exchange-rate USD=7.25 --exchange-rate EUR=7.80
```

指定输出根目录：

```bash
invoice-ocr --input ./invoices --output .
```

## 测试

```bash
pytest
```
