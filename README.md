# invoice-reimburse-ocr

发票批量识别与报销 Excel 导出工具。本项目按 `需求手册.md` 实现本地批量处理流程：读取文件夹中的发票图片，识别并解析核心报销字段，生成模板文件、正式报销明细和独立处理日志。

## 功能

- 递归读取 `jpg/jpeg/png/bmp/tif/tiff/pdf` 文件。
- 通过可替换 OCR 引擎提取文本：
  - `sidecar`：读取同名 `.txt` 文件，适合开发、测试和无 OCR 环境演示。
  - `paddle`：使用 PaddleOCR 做真实本地 OCR。
- 真实 OCR 前会执行基础图像预处理：灰度化、二值化、去噪，并在安装 OpenCV 时尝试倾斜校正；低于 300dpi 的图片会记录警告。
- 解析发票代码、号码、日期、金额、购销方名称和税号。
- 识别付款记录/支付凭证，提取付款日期、交易单号、付款金额、付款方、收款方和付款方式，并加入正式报销明细。
- 若识别到外币发票，会提示输入对应人民币汇率，也可通过 `--exchange-rate USD=7.25` 预先指定。
- 自动去重：重复发票、重复付款记录不会进入正式报销明细，但会在 `处理日志.xlsx` 中标记为“重复已去重”。
- 自动校验必填字段、金额、日期和同批次重复发票号码。
- 导出到 `outputs/YYYYMMDD_HHMMSS/`：
  - `发票报销模板.xlsx`
  - `报销明细_YYYYMMDD_HHMMSS.xlsx`
  - `处理日志.xlsx`

正式报销明细只包含报销相关字段，不混入文件名、识别状态、错误信息等辅助列；外币和付款记录字段按后续业务需求追加到同一张报销明细中。

## 环境准备

推荐使用 Conda：

```bash
conda create -n invoice-reimburse-ocr python=3.9 -y
conda activate invoice-reimburse-ocr
pip install -r requirements.txt
pip install -e ".[test]"
```

也可以直接从环境文件创建：

```bash
conda env create -f environment.yml
conda activate invoice-reimburse-ocr
pip install -e ".[test]"
```

如果本机 Conda 的全局缓存或 `~/.conda` 没有写权限，可将环境和包缓存放在项目本地：

```bash
mkdir -p .conda-envs .conda-pkgs
CONDA_PKGS_DIRS="$PWD/.conda-pkgs" CONDA_ENVS_DIRS="$PWD/.conda-envs" conda --no-plugins env create --solver classic -f environment.yml
.conda-envs/invoice-reimburse-ocr/bin/python -m pip install -e ".[test]"
.conda-envs/invoice-reimburse-ocr/bin/python -m pytest
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

也可以使用手册约定的根入口：

```bash
python main.py --input ./invoices --ocr-engine sidecar
```

输出示例：

```text
outputs/20260618_143022/
├── 发票报销模板.xlsx
├── 报销明细_20260618_143022.xlsx
└── 处理日志.xlsx
```

## 测试

```bash
pytest
```

当前测试覆盖文件扫描、图像预处理、字段解析、外币换算、付款记录、去重、Excel 导出、输出目录结构和空目录错误处理。

`tests/fixtures/` 目录已预留给脱敏样本图片。当前自动化测试使用轻量生成样本和 sidecar 文本，避免真实票据进入仓库。

## FAQ

**为什么 PaddleOCR 依赖没有默认安装？**

PaddlePaddle 需要按 CPU/GPU、系统和芯片选择安装包。基础环境先保证解析、导出和测试可运行，真实 OCR 环境再按本机情况安装 `paddleocr paddlepaddle opencv-python`。

**真实发票会被提交到 Git 吗？**

不会。`invoices/` 目录下除 `.gitkeep` 外默认被忽略。
