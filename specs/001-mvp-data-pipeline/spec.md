# Feature Specification: MVP Data Pipeline & Dashboard (Giai đoạn 1)

**Feature Branch**: `001-mvp-data-pipeline`

**Created**: 2026-11-07

**Status**: Draft

**Input**: Giai đoạn 1 của `docs/technical-report.md` (§0.4, §10): pipeline `bronze → silver → gold` cho ngành IT/Data & AI, thị trường Global; trích xuất kỹ năng bằng từ điển + luật polarity; Mention Rate + Wilson CI; phân vị lương; dashboard 3 tab. Mốc `v0.1.0` ở cuối Tuần 6.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Xu hướng kỹ năng đáng tin (Priority: P1)

Người phân tích muốn biết tỷ lệ JD IT yêu cầu một kỹ năng thay đổi thế nào theo kỳ (nửa năm/quý), kèm khoảng tin cậy, và bấm vào bất kỳ con số nào để xem các đoạn JD làm bằng chứng.

**Why this priority**: Đây là giá trị cốt lõi của sản phẩm và là phần mọi thứ khác (cụm, vòng đời, role drift) dựa vào. Nó cũng buộc phải giải quyết dedup, ghost filter, polarity và offset đúng.

**Independent Test**: Chạy `make all` trên fixture tổng hợp, mở Tab 1, chọn kỹ năng `Kubernetes`: thấy chuỗi Mention Rate + Wilson CI; chọn một điểm, thấy danh sách `job_id` + đoạn văn bản.

**Acceptance Scenarios**:

1. **Given** 50.000 JD cũ và 2.000 JD mới, **When** tính xu hướng, **Then** hệ thống dùng tỷ lệ trên JD đã khử trùng lặp, không dùng số đếm (QA-TIME-01).
2. **Given** một JD đăng lặp 8 tuần hoặc đăng chéo nhiều nguồn, **When** thống kê, **Then** chúng cùng một `dedup_group_id` và chỉ tính 1 lần mỗi quý (QA-INGEST-01).
3. **Given** câu "No experience with Kubernetes required; migrating from PHP to Go", **When** trích xuất, **Then** `Go=REQUIRED`, `Kubernetes=NEGATED`, `PHP=NEGATED`, và `NEGATED` không vào tử số (QA-NLP-02).
4. **Given** kỹ năng `C++`, `C#`, `.NET Core`, `Node.js`, `CI/CD`, **When** trích xuất, **Then** `text[char_start:char_end]` khớp chuỗi gốc (QA-NLP-01).

---

### User Story 2 - Phân vị lương theo nhóm (Priority: P2)

Ứng viên muốn xem P25/P50/P75 lương theo nhóm nghề và cấp bậc, biết bao nhiêu phần trăm tin có công bố lương và cỡ mẫu.

**Why this priority**: Câu hỏi thứ hai của người dùng, nhưng cần pipeline lương riêng nên độc lập với US1 về mặt kiểm thử.

**Independent Test**: Mở Tab 2, chọn nhóm nghề + cấp bậc: thấy boxplot P25–P75, `Disclosure Rate`, `N_salary`; nhóm `N_salary < 30` hiện thông báo thay vì biểu đồ.

**Acceptance Scenarios**:

1. **Given** lương trộn `$40/hr`, `35 triệu VND/tháng`, `$120,000/yr`, **When** parse, **Then** quy đổi đúng về `Annualized USD` (Global) hoặc `Triệu VND/tháng` (VN) (QA-SAL-02).
2. **Given** "Thỏa thuận", "Competitive" hoặc `$1/yr`, **When** parse, **Then** `salary_disclosed=False`, không điền giá trị (QA-SAL-01).
3. **Given** "Up to $3,000", **When** parse, **Then** `salary_bound_type="UPPER_ONLY"` và không vào phân vị chính.

---

### User Story 3 - Kiểm tra vệ sinh dữ liệu và chất lượng baseline (Priority: P3)

Chủ dự án muốn biết đã loại bao nhiêu tin trùng và tin ảo, và baseline từ điển đạt Precision/Recall/F1 bao nhiêu trên gold set.

**Why this priority**: Làm cho các tuyên bố ở US1–US2 kiểm chứng được; cũng là mốc để Giai đoạn 2 chứng minh NER vượt baseline.

**Independent Test**: Mở Tab 3: thấy tỷ lệ trùng, tỷ lệ ghost, bảng P/R/F1 trên gold dev, cỡ gold set và Cohen's κ.

**Acceptance Scenarios**:

1. **Given** tin mở > 90 ngày nội dung không đổi (nguồn có `first_seen/last_seen`), **When** lọc, **Then** gắn `is_ghost_job` và loại khỏi mẫu số (QA-INGEST-02).
2. **Given** gold set ≥ 100 đoạn do một người gán nhãn hai lượt cách nhau ≥ 3 ngày (nhóm 1 người), **When** tính đồng thuận, **Then** báo cáo Cohen's κ giữa hai lượt (mục tiêu ≥ 0.7).

---

### Edge Cases

- JD HTML lồng nhiều tầng, thực thể HTML (`&amp;`), Unicode: offset phải trỏ về chuỗi gốc.
- JD thiếu cả phần yêu cầu hoặc < 100 ký tự mô tả chuyên môn: loại, đếm vào thống kê vệ sinh.
- Nguồn không có ngày đăng: không đưa vào phép tính theo kỳ, không đoán ngày.
- Nhóm lương `N_salary < 30`: không vẽ.
- Cùng JD (hoặc bản trùng) rơi vào cả dev và held-out: bị test từ chối (QA-LEAK-01).
- Kỹ năng đa dụng (`Git`, `English`, `Agile`): không ảnh hưởng thống kê MVP nhưng phải có trong fixture để GĐ2 dùng lại.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Hệ thống MUST nạp dữ liệu lịch sử (Kaggle) và API công khai (Greenhouse/Lever, Adzuna) vào `data/bronze/` dạng Parquet bất biến, ghi `source_dataset`, `ingested_at`, và `first_seen/last_seen` khi nguồn có.
- **FR-002**: Hệ thống MUST kiểm kê dữ liệu và ghi `docs/data_inventory.md` (kích thước, giấy phép, tỷ lệ có lương, phân bố theo năm) trước khi khóa trục thời gian (cổng G0).
- **FR-003**: Hệ thống MUST làm sạch HTML và tách vùng Requirements/Responsibilities/Compensation, giữ `char_offset` trên chuỗi gốc.
- **FR-004**: Hệ thống MUST khử trùng lặp bằng MinHash LSH (128 hàm, Jaccard ≥ 0.85) kèm khóa `(company, title, quarter)` và gán `dedup_group_id`.
- **FR-005**: Hệ thống MUST gắn cờ ghost job (> 90 ngày không đổi, chỉ với nguồn có `first_seen/last_seen`) và loại JD rỗng (< 100 ký tự mô tả chuyên môn).
- **FR-006**: Hệ thống MUST bóc tách và chuẩn hóa lương theo mục 2.4 báo cáo kỹ thuật, gồm cờ `salary_disclosed`, `salary_bound_type` và loại lương dự đoán.
- **FR-007**: Hệ thống MUST trích xuất kỹ năng bằng từ điển ESCO + alias và gán `polarity ∈ {REQUIRED, PREFERRED, NEGATED}` bằng luật cửa sổ; mỗi mention có `char_start, char_end, evidence_span, model_version`.
- **FR-008**: Hệ thống MUST tính `Mention Rate` + Wilson CI 95% theo (ngành, kỹ năng, kỳ) trên JD hợp lệ đã khử trùng lặp, chỉ đếm `REQUIRED`.
- **FR-009**: Hệ thống MUST tính P25/P50/P75/IQR lương theo (nhóm nghề, cấp bậc, khu vực, kỳ), chỉ cho nhóm `N_salary ≥ 30`, kèm `Disclosure Rate`.
- **FR-010**: Hệ thống MUST cung cấp `make all` tái tạo `silver/` và `gold/` từ `bronze/`.
- **FR-011**: Dashboard Streamlit MUST có Tab 1 (Market Radar), Tab 2 (Salary Quantiles), Tab 3 (Hygiene & Baseline QA), đọc trực tiếp DuckDB gold, và cho xem đoạn bằng chứng của mỗi con số.
- **FR-012**: Hệ thống MUST kiểm schema bằng Pandera tại mỗi ranh giới lớp.
- **FR-013**: Gold set (≥ 100 đoạn) MUST được lưu trong `data/gold_labels/` và chia dev/held-out theo `dedup_group_id`.

### Key Entities

- **RawJD**: tin tuyển dụng thô (nguồn, ngày, tiêu đề, công ty, mô tả HTML/text, lương thô).
- **FACT_JOB_POSTING**: một JD hợp lệ (`job_id`, `sector_id`, `job_family`, `listed_year/quarter`, `experience_level`, lương chuẩn hóa, `dedup_group_id`, `is_ghost_filtered`, `source_dataset`, `market_region`).
- **FACT_SKILL_MENTION**: một lần nhắc kỹ năng với offset, `polarity`, bằng chứng, `model_version`.
- **DIM_SKILL_TAXONOMY**: kỹ năng chuẩn (ESCO + alias công nghệ).
- **MART_SKILL_TREND_PERIOD / MART_SALARY_QUANTILES**: bảng tổng hợp phục vụ dashboard.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `uv sync --locked && make all` trên máy sạch tạo lại toàn bộ `gold/` từ `bronze/`; chạy hai lần cho kết quả giống nhau.
- **SC-002**: Mọi test QA-TIME-01, QA-INGEST-01/02, QA-SAL-01/02, QA-NLP-01/02, QA-LEAK-01 xanh trong CI.
- **SC-003**: 100% mention trong `FACT_SKILL_MENTION` thỏa `text[char_start:char_end] == evidence_span` trên fixture và trên mẫu 1.000 mention thật.
- **SC-004**: Baseline có P/R/F1 báo cáo trên gold dev; polarity accuracy ≥ 0.9 trên gold (mục tiêu, chỉnh theo thực tế).
- **SC-005**: Truy vấn dashboard p95 < 200 ms trên `gold/`.
- **SC-006**: Tag `v0.1.0` phát hành với 3 tab chạy thông suốt và README hướng dẫn chạy nhanh.

## Assumptions

- Dự án một người, 15–20 giờ/tuần; kế hoạch tuần trong báo cáo kỹ thuật giữ nguyên nhưng không còn tách DA / ML+QA.
- Các giả định ở mục 12.2 báo cáo kỹ thuật (bộ Kaggle 2017–2022, phạm vi Adzuna, ngưỡng số) chưa kiểm chứng; kết quả G0 có thể thu hẹp trục thời gian thành 2023–24 so với 2025–26.
- Chỉ ngành IT/Data & AI, thị trường Global; JD tiếng Anh. Việt Nam và đa ngành thuộc Giai đoạn 3.
- Không dùng LLM, GPU hay dịch vụ trả phí trong Giai đoạn 1.
