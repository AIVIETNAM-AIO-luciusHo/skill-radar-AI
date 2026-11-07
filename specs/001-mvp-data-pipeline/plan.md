# Implementation Plan: MVP Data Pipeline & Dashboard

**Branch**: `001-mvp-data-pipeline` | **Date**: 2026-11-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-mvp-data-pipeline/spec.md`

## Summary

Pipeline Medallion `bronze → silver → gold` bằng Polars + DuckDB + Parquet; trích xuất kỹ năng bằng từ điển ESCO + alias và luật polarity; thống kê Mention Rate + Wilson và phân vị lương; dashboard Streamlit đọc DuckDB. Chi tiết toán và schema ở `docs/technical-report.md` §2.5, §3, §4.1.

## Technical Context

**Language/Version**: Python ≥ 3.11 (`uv`, `uv.lock` commit)

**Primary Dependencies**: polars, duckdb, pandera, pydantic v2, httpx, datasketch, rapidfuzz, scipy, pyyaml; extras `nlp` (spaCy PhraseMatcher), `app` (streamlit, plotly)

**Storage**: Parquet theo lớp `data/{bronze,silver,gold}/`; DuckDB đọc trực tiếp (không server)

**Testing**: pytest trên fixture tổng hợp (không mạng/GPU/dữ liệu thật); CI giới hạn < 60 s

**Target Platform**: Linux / WSL2, máy cá nhân

**Project Type**: thư viện Python + CLI qua `make` + ứng dụng Streamlit

**Performance Goals**: truy vấn dashboard p95 < 200 ms trên `gold/`

**Constraints**: chi phí 0 VND; ~6 GiB VRAM (GĐ1 không dùng GPU); nguồn hợp quy (API/JSON công khai)

**Scale/Scope**: vài chục nghìn đến vài trăm nghìn JD IT; 3 tab dashboard; ≥ 100 đoạn gold set

## Constitution Check

| Nguyên tắc | Đạt? | Cách đáp ứng |
|---|---|---|
| I. Bằng chứng truy ngược | ✅ | `FACT_SKILL_MENTION` lưu offset + `evidence_span`; test SC-003 |
| II. Thống kê chặt chẽ | ✅ | FR-008/009, QA-TIME/SAL; nguồn tách theo `source_dataset` |
| III. Baseline trước | ✅ | GĐ1 không có mô hình học máy |
| IV. Test-first | ✅ | Mỗi task logic dữ liệu có task test đứng trước |
| V. Medallion + Ports/Adapters | ✅ | Cấu trúc dưới đây; Pandera ở ranh giới |
| VI. YAGNI | ✅ | Không tạo file GĐ2/GĐ3; `[GĐ2]` chỉ nằm trong tài liệu |

## Project Structure

### Documentation (this feature)

```text
specs/001-mvp-data-pipeline/
├── spec.md
├── plan.md
└── tasks.md
```

### Source Code (repository root)

```text
src/skillradar/
├── ports/        schemas.py (RawJD, SkillMention, SalaryBand), interfaces.py
├── ingestion/    historical_loaders.py, api_connectors.py
├── hygiene/      dedup.py, ghost_filter.py, salary_parser.py
├── nlp/          section_splitter.py, baseline_dict.py, negation_context.py
├── analytics/    trends.py, salary.py
└── pipeline.py   # ghép bước: bronze -> silver -> gold (điểm vào của `make all`)
app/streamlit_app.py
configs/          sources.yaml, taxonomy.yaml, scraping_rate_limits.yaml
tests/            test_offsets_negation.py, test_dedup_ghost.py, test_salary.py, test_trend_math.py
```

**Structure Decision**: dự án đơn (single project), một package `skillradar`. Thư mục con chỉ được tạo khi task cần file đầu tiên trong đó.

## Quyết định thiết kế cho GĐ1

- **Mention Rate theo kỳ** dùng bucket nửa năm hoặc quý (chọn sau G0 theo mật độ dữ liệu); kỳ có ít JD hợp lệ hơn ngưỡng tối thiểu (đặt trong `configs/sources.yaml`) bị ẩn, không làm tròn lên.
- **Dedup** chạy trên văn bản đã chuẩn hóa sau `section_splitter`; `dedup_group_id` ổn định giữa các lần chạy (hash của khóa nhóm, không phải số thứ tự).
- **Polarity** bằng luật cửa sổ ± N token quanh span, danh sách tín hiệu trong `configs/taxonomy.yaml` để chỉnh theo lỗi trên gold dev mà không sửa code.
- **Gold set** do một người gán hai lượt cách nhau ≥ 3 ngày để tính κ; nếu κ < 0.7 thì sửa `labeling_guidelines.md` rồi gán lại các ca bất đồng.
- **Dashboard** chỉ đọc `data/gold/*.parquet` qua DuckDB; mọi logic thống kê ở `analytics/`, không ở Streamlit.

## Complexity Tracking

Không có vi phạm Constitution cần biện minh.
