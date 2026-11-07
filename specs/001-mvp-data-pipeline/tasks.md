---
description: "Task list: MVP Data Pipeline & Dashboard (Giai đoạn 1, Tuần 1–6)"
---

# Tasks: MVP Data Pipeline & Dashboard

**Input**: `specs/001-mvp-data-pipeline/` (spec.md, plan.md)

**Tests**: BẮT BUỘC cho logic dữ liệu (Constitution IV): viết test, thấy đỏ, rồi cài đặt.

**Mỗi task = một GitHub Issue** (`[W<tuần>] ...`); tick `[x]` trong chính PR đóng Issue. Tiến độ sống ở GitHub Projects.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: có thể song song (khác file, không phụ thuộc)
- **[Story]**: US1 xu hướng · US2 lương · US3 vệ sinh/baseline

## Phase 1: Setup — Tuần 1 (M0, cổng G0)

- [ ] T001 Tạo GitHub Project (trường Status/Phase/Week/Size/Priority), 4 milestone M0–M3, nhãn `task|bug|spike|must|should|could`
- [ ] T002 Áp Ruleset từ `.github/rulesets/main.json`; mở PR thử, xác nhận `ci-ok` chặn merge khi lint đỏ
- [ ] T003 [P] Spike G0: kiểm kê dữ liệu → `docs/data_inventory.md` (nguồn, giấy phép, số JD/năm, tỷ lệ có lương, độ dài mô tả); ghi quyết định trục thời gian vào `docs/decisions.md`
- [ ] T004 [P] Spike: đăng ký Adzuna, kiểm danh sách quốc gia, hạn mức, ý nghĩa `salary_is_predicted`; thử Greenhouse JSON 500 JD
- [ ] T005 Viết `docs/data_contract.md` v1 và `src/skillradar/ports/schemas.py` (`RawJD`, `SkillMention`, `SalaryBand`) cùng test schema

**Checkpoint G0**: trục thời gian đã chốt dựa trên dữ liệu thật; có 500 JD mới từ API.

## Phase 2: Foundational — Tuần 2–3 (Bronze → Silver, cổng G1)

**⚠️ Chặn mọi user story.**

- [ ] T006 [P] Test offset `[char_start, char_end)` cho `C++`, `C#`, `.NET Core`, `Node.js`, `CI/CD`, HTML entity, Unicode — `tests/test_offsets_negation.py` (QA-NLP-01)
- [ ] T007 Cài `src/skillradar/nlp/section_splitter.py` giữ offset trên chuỗi gốc
- [ ] T008 [P] `src/skillradar/ingestion/historical_loaders.py` → `data/bronze/` (+ Pandera) và `configs/sources.yaml`
- [ ] T009 [P] `src/skillradar/ingestion/api_connectors.py` (Greenhouse/Lever, Adzuna): rate limit, lưu `first_seen/last_seen`, không thu PII
- [ ] T010 [P] Test dedup + ghost filter — `tests/test_dedup_ghost.py` (QA-INGEST-01/02)
- [ ] T011 `src/skillradar/hygiene/dedup.py` (MinHash 128, Jaccard ≥ 0.85, khóa `(company,title,quarter)`, id ổn định) và `ghost_filter.py` (> 90 ngày, < 100 ký tự)
- [ ] T012 [P] Test lương — `tests/test_salary.py` (QA-SAL-01/02, UPPER_ONLY, predicted, ngoại lai)
- [ ] T013 `src/skillradar/hygiene/salary_parser.py` + bảng tỷ giá theo năm trong `configs/taxonomy.yaml`
- [ ] T014 [P] Soạn `docs/labeling_guidelines.md`

**Checkpoint G1**: `data/silver/` sạch, QA-INGEST/QA-SAL xanh.

## Phase 3: User Story 1 — Xu hướng kỹ năng (P1) — Tuần 3–4, 6 🎯 MVP

- [ ] T015 [P] [US1] Test polarity — mở rộng `tests/test_offsets_negation.py` (QA-NLP-02, PREFERRED, NEGATED)
- [ ] T016 [US1] `src/skillradar/nlp/baseline_dict.py` (spaCy PhraseMatcher + ESCO + alias trong `configs/taxonomy.yaml`)
- [ ] T017 [US1] `src/skillradar/nlp/negation_context.py` (luật cửa sổ; tín hiệu nằm trong config)
- [ ] T018 [P] [US1] Test Mention Rate / Wilson — `tests/test_trend_math.py` (QA-TIME-01, tính tay vài ca)
- [ ] T019 [US1] `src/skillradar/analytics/trends.py` → `MART_SKILL_TREND_PERIOD`
- [ ] T020 [US1] EDA đối chiếu Stack Overflow Developer Survey (`notebooks/`, kết luận vào `docs/`)
- [ ] T021 [US1] Streamlit Tab 1 Market Radar có xem bằng chứng (`app/streamlit_app.py`)

## Phase 4: User Story 2 — Phân vị lương (P2) — Tuần 5–6

- [ ] T022 [P] [US2] Test quantile + ngưỡng `N_salary ≥ 30` + Disclosure Rate
- [ ] T023 [US2] `src/skillradar/analytics/salary.py` → `MART_SALARY_QUANTILES`
- [ ] T024 [US2] Phân tích thiên lệch của nhóm tin có công bố lương → `docs/methodology.md`
- [ ] T025 [US2] Streamlit Tab 2 Salary Quantiles

## Phase 5: User Story 3 — Vệ sinh & baseline (P3) — Tuần 4–6

- [ ] T026 [US3] Gán nhãn gold set ≥ 100 đoạn (lượt 1), `data/gold_labels/`; chia dev/held-out theo `dedup_group_id`
- [ ] T027 [US3] Gán lượt 2 sau ≥ 3 ngày, tính Cohen's κ, cập nhật guideline nếu κ < 0.7
- [ ] T028 [P] [US3] Test rò rỉ dữ liệu (QA-LEAK-01)
- [ ] T029 [US3] Đo P/R/F1 baseline + polarity accuracy trên gold dev
- [ ] T030 [US3] Streamlit Tab 3 Hygiene & Baseline QA

## Phase 6: Polish — Tuần 6 (cổng G2 = MVP)

- [ ] T031 `src/skillradar/pipeline.py` + target `make ingest|silver|gold|all|app` trong `Makefile`
- [ ] T032 Kiểm tái lập: `uv sync --locked && make all` hai lần trên bản clone sạch, kết quả giống nhau (SC-001)
- [ ] T033 Benchmark truy vấn p95 < 200 ms (SC-005); cập nhật README (ảnh chụp dashboard, quick start)
- [ ] T034 Tag `v0.1.0`, đóng milestone M1, ghi quyết định G2 vào `docs/decisions.md`

## Dependencies & Execution Order

- Phase 1 → Phase 2 → (Phase 3, 4, 5 có thể xen kẽ vì một người) → Phase 6.
- T007 chặn T011, T016; T013 chặn T023; T016–T017 chặn T029; T026 chặn T029.
- Test (T006, T010, T012, T015, T018, T022, T028) luôn đứng trước phần cài đặt tương ứng.
- Nếu trễ: cắt theo cut-line (§11 báo cáo kỹ thuật); không cắt dedup, Wilson, quy tắc lương, offset, gold set, CI.
