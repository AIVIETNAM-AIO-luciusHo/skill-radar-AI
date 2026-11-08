<!-- Quy trình: Issue → nhánh + code → PR → ci-ok xanh → review & approve → merge. Chi tiết: CONTRIBUTING.md -->

## 1. Issue liên quan

Closes #

**Task trong spec:** <!-- ví dụ T007 trong specs/001-mvp-data-pipeline/tasks.md; ghi "Không có" nếu ngoài spec -->

## 2. Mục tiêu và thay đổi

**Mục tiêu:**
<!-- Vấn đề cần giải quyết, một hai câu. -->

**Thay đổi đã thực hiện:**
-
-

**Ngoài phạm vi (cố ý không làm):**
-

## 3. Bằng chứng kiểm thử

- **Lệnh:** `make ci`
- **Kết quả:** <!-- số liệu thật, ví dụ "27 passed"; "F1 = 0.xx trên gold dev" -->
- **Link CI:**

## 4. Checklist chất lượng

### Đặc tả và triển khai
- [ ] Đáp ứng toàn bộ Acceptance Criteria của Issue
- [ ] Không làm ngoài phạm vi Issue
- [ ] Tuân thủ `docs/data_contract.md` và `ports/schemas.py` (đổi schema thì cập nhật cả hai trong PR này)
- [ ] Đã xử lý lỗi và dữ liệu biên
- [ ] Nếu chạm logic dữ liệu: test viết trước, mã QA liên quan đều có test
- [ ] Mọi con số/mention mới truy ngược được về `job_id` và vị trí ký tự
- [ ] Không commit dữ liệu thô, khóa API, `.env`, PII hay mô hình nặng

### Kiểm thử và CI
- [ ] CI trên GitHub xanh, gồm check bắt buộc `ci-ok`
- [ ] `ruff check .` và `ruff format --check .` thành công
- [ ] `pytest` thành công
- [ ] Có test cho hành vi mới hoặc thay đổi
- [ ] Không làm hỏng chức năng hiện có

### Quy trình và tài liệu
- [ ] Nhánh đặt tên `feat|fix|docs|chore/<số-issue>-<slug>`
- [ ] Đã tự review ở tab Files changed
- [ ] Tài liệu cập nhật nếu cần (README, `docs/`, `specs/*/tasks.md`: tick task, `docs/decisions.md`)
- [ ] PR không chứa thay đổi không liên quan
- [ ] Các thảo luận review đã được giải quyết

## 5. Xác nhận trước merge

- [ ] `ci-ok` xanh, không còn lỗi CI chưa xử lý
- [ ] Đã được review và approve theo quy định hiện hành (xem CONTRIBUTING.md)
- [ ] Sẵn sàng merge vào `main`

## 6. Ghi chú cho reviewer

- **Điểm cần kiểm tra kỹ:**
- **Giới hạn, rủi ro còn lại:** <!-- ghi "Không có" nếu thật sự không -->
- **Bước tiếp theo:**
