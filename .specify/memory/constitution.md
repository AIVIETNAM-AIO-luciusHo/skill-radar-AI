# SkillRadar AI Constitution

## Core Principles

### I. Dữ liệu là bằng chứng, truy ngược được (NON-NEGOTIABLE)
Mọi con số trên dashboard hoặc trong báo cáo phải truy ngược được về `job_id` và đoạn văn bản gốc
`[char_start, char_end)`. Bước làm sạch HTML giữ offset trên chuỗi gốc. Mỗi `SkillMention` lưu
`evidence_span`, `polarity`, `link_confidence` và `model_version`. Không có bằng chứng thì không có con số.

### II. Thống kê chặt chẽ trước khi trình bày
- Xu hướng dùng **tỷ lệ chuẩn hóa** (`Mention Rate` trên JD đã khử trùng lặp) kèm khoảng tin cậy Wilson 95%, không bao giờ dùng số đếm tuyệt đối.
- Chỉ JD `REQUIRED` vào tử số; `NEGATED` không bao giờ vào.
- Lương: chỉ dùng lương **công bố**; không điền trung bình; lương dự đoán của nền tảng và `UPPER_ONLY` không vào phân vị chính; chỉ vẽ nhóm có `N_salary ≥ 30` và luôn hiển thị `Disclosure Rate`.
- Không so sánh xu hướng giữa các nguồn khác phân phối nếu chưa kiểm trong từng nguồn (`source_dataset`, `market_region`).
- Kiểm định nhiều kỹ năng phải hiệu chỉnh Benjamini–Hochberg.

### III. Baseline trước, mô hình sau
Giai đoạn 1 chạy trọn pipeline bằng từ điển + luật. Mô hình học máy (NER, linking, phân cụm) chỉ được
nhận khi **thắng baseline trên gold set giữ kín** và kết quả được báo cáo kèm khoảng tin cậy. Mô hình không
thắng vẫn là kết quả hợp lệ, không phải lý do trì hoãn MVP.

### IV. Test-first cho logic dữ liệu
Phần có công thức, ngưỡng hoặc biến đổi dữ liệu (dedup, ghost filter, salary parser, offset, polarity,
Mention Rate/Wilson, quantile) viết test **trước**, trên fixture tổng hợp nhỏ, không cần mạng, GPU hay dữ liệu thật.
Mỗi mã QA trong báo cáo kỹ thuật (QA-TIME, QA-INGEST, QA-SAL, QA-NLP, QA-CLUST, QA-LEAK, QA-PERF) tương ứng ít nhất một test.
Gold set được chia theo `dedup_group_id` và theo thời gian để chống rò rỉ.

### V. Tái lập và kiến trúc Medallion
Dữ liệu chảy `bronze → silver → gold` (Parquet + DuckDB). Bronze bất biến; silver và gold sinh lại được
bằng `uv sync && make all`. Mỗi lớp có schema kiểm bằng Pandera ở ranh giới. Ranh giới mô-đun theo Ports/Adapters
(`ports/schemas.py`, `ports/interfaces.py`); không có logic nghiệp vụ trong notebook hay Streamlit.

### VI. Đơn giản, đúng giai đoạn (YAGNI)
Không tạo file, phụ thuộc hay trừu tượng của giai đoạn sau khi giai đoạn hiện tại chưa xong. Không thêm thư
viện cho vài dòng code. Cắt giảm theo đúng thứ tự cut-line trong báo cáo kỹ thuật; **không bao giờ cắt**: dedup,
mẫu số chuẩn hóa + Wilson, quy tắc lương, offset/bằng chứng, gold set, CI.

## Ràng buộc kỹ thuật và pháp lý

- **Chi phí 0 VND, chạy cục bộ:** Python ≥ 3.11 quản lý bằng `uv` (`uv.lock` luôn được commit), WSL2, ~6 GiB VRAM. Huấn luyện nặng chạy trên Kaggle/Colab; suy luận cục bộ dùng ONNX INT8 hoặc fp16.
- **Ưu tiên nguồn hợp quy:** API và JSON công khai (Greenhouse/Lever, Adzuna) trước; scraping chỉ sau khi đọc `robots.txt` và điều khoản, delay ≥ 2.5 s kèm jitter, không thu PII của nhà tuyển dụng, không tái xuất bản nguyên văn hàng loạt.
- **Không commit** dữ liệu thô, khóa API, `.env`, mô hình nặng. Chỉ `data/gold_labels/` và fixture nhỏ được phép.
- **Ngôn ngữ:** tài liệu và nội dung giao diện bằng tiếng Việt; mã, tên cột, commit message bằng tiếng Anh. Tên kỹ năng giữ nguyên bản (`C++`, `Node.js`).
- Giả định chưa kiểm chứng phải được ghi là giả định (mục 12.2 báo cáo kỹ thuật) cho đến khi có thực nghiệm.

## Quy trình phát triển

- Quy trình chuẩn, không ngoại lệ: **Issue → nhánh + code → PR → `ci-ok` xanh → review & approve → merge** (chi tiết và Definition of Done ở `CONTRIBUTING.md`). `main` được bảo vệ bằng Ruleset: chỉ merge qua PR, cần check `ci-ok` (`ruff check`, `ruff format --check`, `pytest`), phải giải quyết hết hội thoại.
- Approval: bắt buộc 1 approval từ người thứ hai ngay khi người đó có quyền Write; trước đó (một người có quyền ghi) bước review là tự review kỹ vì GitHub không cho tự approve, và cổng cứng duy nhất là `ci-ok`.
- Quy trình mỗi tính năng lớn: `speckit-specify → plan → tasks → implement`, mỗi task thành một GitHub Issue, nhánh `feat/<issue#>-<slug>`, PR ghi `Closes #n`, lệnh kiểm chứng và số liệu thật.
- Tiến độ nằm ở GitHub Projects (trường Status/Phase/Week/Size/Priority); không ghi trạng thái ở hai nơi. Ô tick trong `tasks.md` được tick trong chính PR đóng task.
- Quyết định kiến trúc ghi vào `docs/decisions.md` (D-xx, trạng thái proposed/approved).
- Mỗi cổng G0–G4 kết thúc bằng một dòng quyết định trong `docs/decisions.md`.

## Governance

Constitution này ưu tiên hơn mọi thói quen làm việc khác; mâu thuẫn với báo cáo kỹ thuật
(`docs/technical-report.md`) thì sửa một trong hai trong cùng PR. Mọi PR tự kiểm tra tuân thủ qua
`.github/pull_request_template.md`. Sửa đổi nguyên tắc cần ghi lý do vào `docs/decisions.md` và tăng phiên bản:
MAJOR khi bỏ/đổi nghĩa nguyên tắc, MINOR khi thêm nguyên tắc hoặc mục, PATCH khi sửa câu chữ.

**Version**: 1.1.0 | **Ratified**: 2026-11-07 | **Last Amended**: 2026-11-08
