# Sổ quyết định kiến trúc

Trạng thái: `proposed` → `approved` → `superseded`. Mỗi cổng G0–G4 thêm một dòng.

| ID | Quyết định | Lý do | Trạng thái | Ngày |
|---|---|---|---|---|
| D-01 | Giai đoạn một người: Ruleset không đòi approval, cổng cứng là CI `ci-ok` | GitHub không cho tác giả tự duyệt PR của mình | superseded bởi D-07, D-08 | 2026-11-07 |
| D-02 | Quản lý việc bằng GitHub Issues + Projects v2 (thay Jira) | Một nơi cho code, CI và tiến độ | approved | 2026-11-07 |
| D-03 | Medallion Parquet + DuckDB, không server CSDL | Dữ liệu vừa một máy; tái lập bằng `make all` | approved | 2026-11-07 |
| D-04 | GĐ1 dùng từ điển + luật; NER Transformer ở GĐ2 và phải thắng baseline | MVP không phụ thuộc GPU | approved | 2026-11-07 |
| D-05 | Mention Rate theo nửa năm/quý, Mann-Kendall + BH | Chuỗi theo năm quá ngắn | approved | 2026-11-07 |
| D-06 | Trục thời gian cuối cùng (2017–2024 hay 2023–2026) | Chờ kết quả kiểm kê dữ liệu | proposed (G0) | — |
| D-07 | Quy trình chuẩn Issue → nhánh+code → PR → `ci-ok` → review & approve → merge; mẫu PR 6 mục; Definition of Done trong mẫu Issue và `CONTRIBUTING.md`. Ruleset giữ 0 approval, nâng lên 1 khi Hogiaan có quyền Write; CODEOWNERS giữ chỉ chủ repo | Chủ repo chọn giữ nguyên tới khi có người thứ hai | approved | 2026-11-08 |
| D-08 | Ruleset `main` đòi 1 approval từ người khác; `CODEOWNERS` vẫn chỉ chủ repo, không bật review Code Owner | Hogiaan đã chấp nhận lời mời và có quyền Write (2026-11-08) | approved | 2026-11-08 |
| D-09 | Thành viên DA đổi từ Hogiaan sang Phạm Nguyễn Thanh Sơn (`ThSonDev`, Data Engineer); nhãn vai trò giữ `DA`; D-07/D-08 giữ nguyên làm lịch sử | Đổi nhân sự (2026-11-10) | approved | 2026-11-10 |
| D-10 | CODEOWNERS review chéo theo module (phần DA → ML+QA review, phần ML+QA → DA review, phần chung → cả hai); Ruleset giữ `require_code_owner_review` tắt | Tránh kẹt khi owner chính là tác giả PR; 1 approval từ người khác đã đủ ép review chéo | approved | 2026-11-10 |
