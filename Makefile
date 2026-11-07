.PHONY: install lint fmt test ci

install:  ## Cài môi trường từ uv.lock
	uv sync --locked

lint:  ## Giống hệt job `lint` của CI
	uv run ruff check .
	uv run ruff format --check .

fmt:  ## Tự sửa định dạng
	uv run ruff check --fix .
	uv run ruff format .

test:
	uv run pytest

ci: lint test  ## Chạy cục bộ đúng những gì `ci-ok` đòi

# Sẽ thêm khi có code thật (Giai đoạn 1): ingest, silver, gold, all (Bronze -> Gold), app.
