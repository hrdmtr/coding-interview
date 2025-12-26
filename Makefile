.PHONY: help install dev-install lint format type-check test coverage clean migrate run docker-up docker-down docker-logs

help:  ## ヘルプメッセージを表示
	@echo "使い方: make [ターゲット]"
	@echo ""
	@echo "利用可能なターゲット:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

docker-up:  ## PostgreSQL を Docker Compose で起動
	docker compose up -d
	@echo "PostgreSQL の起動を待機中..."
	@until docker compose exec db pg_isready -U root -d coding-test > /dev/null 2>&1; do sleep 1; done
	@echo "PostgreSQL の起動完了！"

docker-down:  ## Docker コンテナを停止・削除
	docker compose down

docker-logs:  ## Docker コンテナのログを表示
	docker compose logs -f

install:  ## 本番用の依存関係をインストール
	uv pip install -e .

dev-install:  ## 開発用の依存関係をインストール
	uv pip install -e ".[dev]"

lint:  ## Ruff で構文チェック
	uv run ruff check .

format:  ## Ruff でコードをフォーマット
	uv run ruff format .
	uv run ruff check --fix .

type-check:  ## mypy で型チェック
	uv run mypy .

test:  ## テストを実行 (api.tests.test_views)
	python manage.py test api.tests.test_views

test-all:  ## すべてのテストを実行
	python manage.py test

coverage:  ## カバレッジ付きでテストを実行
	uv run coverage run --source='api' manage.py test api.tests.test_views
	uv run coverage report
	uv run coverage html

migrate:  ## データベースマイグレーションを実行
	python manage.py migrate

makemigrations:  ## 新しいマイグレーションファイルを作成
	python manage.py makemigrations

run:  ## 開発サーバーを起動
	python manage.py runserver

clean:  ## 生成されたファイルをクリーンアップ
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/

check: lint type-check test  ## すべてのチェックを実行（lint, 型チェック, テスト）
