# Sổ quyết định kiến trúc

Trạng thái: `proposed` → `approved` → `superseded`. Mỗi cổng G0–G4 thêm một dòng.

| ID | Quyết định | Lý do | Trạng thái | Ngày |
|---|---|---|---|---|
| D-01 | Giai đoạn một người: Ruleset không đòi approval, cổng cứng là CI `ci-ok` | GitHub không cho tác giả tự duyệt PR của mình | superseded một phần bởi D-07 | 2026-11-07 |
| D-02 | Quản lý việc bằng GitHub Issues + Projects v2 (thay Jira) | Một nơi cho code, CI và tiến độ | approved | 2026-11-07 |
| D-03 | Medallion Parquet + DuckDB, không server CSDL | Dữ liệu vừa một máy; tái lập bằng `make all` | approved | 2026-11-07 |
| D-04 | GĐ1 dùng từ điển + luật; NER Transformer ở GĐ2 và phải thắng baseline | MVP không phụ thuộc GPU | approved | 2026-11-07 |
| D-05 | Mention Rate theo nửa năm/quý, Mann-Kendall + BH | Chuỗi theo năm quá ngắn | approved | 2026-11-07 |
| D-06 | Trục thời gian cuối cùng (2017–2024 hay 2023–2026) | Chờ kết quả kiểm kê dữ liệu | proposed (G0) | — |
| D-07 | Quy trình chuẩn Issue → nhánh+code → PR → `ci-ok` → review & approve → merge; mẫu PR 6 mục; Definition of Done trong mẫu Issue và `CONTRIBUTING.md`. Ruleset giữ 0 approval, nâng lên 1 khi Hogiaan có quyền Write; CODEOWNERS giữ chỉ chủ repo | Chủ repo chọn giữ nguyên tới khi có người thứ hai | approved | 2026-11-08 |
