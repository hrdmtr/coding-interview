# coding-interview

Django REST Framework を使用したカテゴリ管理 API

## 機能

- カテゴリの CRUD 操作（作成・読取・更新・削除）
- 階層構造のサポート（親カテゴリの設定）
- 企業ごとのカテゴリ管理
- バリデーション機能
  - 同一企業内でのカテゴリ名重複防止
  - 親カテゴリの同一企業チェック
  - 自己参照の禁止

## 技術スタック

- Python 3.11+
- Django 5.0+
- Django REST Framework 3.15+
- PostgreSQL (Docker Compose)
- uv (パッケージ管理)
- Ruff (linter + formatter)
- mypy (型チェック)

## セットアップ

### 前提条件

- Python 3.11 以上
- [uv](https://github.com/astral-sh/uv) がインストールされていること
- Docker & Docker Compose (PostgreSQL 用)

### インストール

```bash
# 1. 依存関係のインストール
uv pip install -e ".[dev]"

# または make を使用
make dev-install

# 2. PostgreSQL の起動 (Docker Compose 使用)
make docker-up

# 3. データベースマイグレーション
python manage.py migrate
```

### Docker Compose コマンド

```bash
# PostgreSQL を起動
make docker-up

# PostgreSQL を停止
make docker-down

# ログを確認
make docker-logs
```

### 環境変数

PostgreSQL 接続用の環境変数は `.env.sample` に記載されています。

**開発環境（Docker Compose 使用時）:**
- 環境変数の設定は不要です
- `docker-compose.yml` にデフォルト値が設定されています

**Docker を使わない場合:**
```bash
cp .env.sample .env
# 必要に応じて .env ファイルを編集
```

**検証環境・本番環境:**
- `.env` ファイルは使用せず、**AWS Secrets Manager** や **環境変数** など、適切なセキュリティ管理方法で設定してください
- 本番環境では必ず強力なパスワードを設定してください

`.env.sample` に記載されている環境変数：
```bash
POSTGRES_DB=coding-test        # データベース名
POSTGRES_USER=root             # ユーザー名
POSTGRES_PASSWORD=password     # パスワード（本番環境では必ず変更）
DB_HOST_NAME=localhost         # ホスト名
DB_PORT=5432                   # ポート番号
```

## 開発

### テストの実行

```bash
# テスト実行
make test

# カバレッジ付きテスト
make coverage

# または直接実行
python manage.py test
```

### コード品質チェック

```bash
# すべてのチェックを実行
make check

# リンターのみ実行
make lint

# フォーマット
make format

# 型チェック
make type-check
```

### 開発サーバーの起動

```bash
make run

# または
python manage.py runserver
```

### pre-commit フックの設定

```bash
uv pip install pre-commit
pre-commit install
```

## API エンドポイント

### カテゴリ API

ベース URL: `/api/categories/`

#### エンドポイント一覧

| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| GET | `/api/categories/` | カテゴリ一覧取得 |
| POST | `/api/categories/` | カテゴリ作成 |
| GET | `/api/categories/{id}/` | カテゴリ詳細取得 |
| PUT | `/api/categories/{id}/` | カテゴリ更新 |
| PATCH | `/api/categories/{id}/` | カテゴリ部分更新 |
| DELETE | `/api/categories/{id}/` | カテゴリ削除 |

#### リクエスト/レスポンス例

**カテゴリ作成**

```bash
POST /api/categories/
Content-Type: application/json

{
  "company": "uuid-of-company",
  "name": "カテゴリ名",
  "parent_category": "uuid-of-parent-category"  # オプション
}
```

**レスポンス**

```json
{
  "id": "uuid",
  "company": "uuid-of-company",
  "name": "カテゴリ名",
  "parent_category": "uuid-of-parent-category",
  "created_at": "2025-12-26T00:00:00Z",
  "updated_at": "2025-12-26T00:00:00Z"
}
```

## プロジェクト構造

```
.
├── api/                        # メインアプリケーション
│   ├── migrations/             # データベースマイグレーションファイル
│   ├── models/                 # データモデル定義
│   │   ├── __init__.py        # モデルのエクスポート設定
│   │   ├── category.py        # カテゴリモデル（階層構造、企業ごとの管理）
│   │   └── company.py         # 企業モデル（カテゴリの親エンティティ）
│   ├── serializers/           # Django REST Framework シリアライザ
│   │   └── category.py        # カテゴリシリアライザ（バリデーションロジック含む）
│   ├── views/                 # API ビュー（エンドポイントハンドラ）
│   │   └── category.py        # カテゴリビューセット（CRUD 操作）
│   ├── tests/                 # テストコード
│   │   └── test_views.py      # カテゴリ API の統合テスト（14 テストケース）
│   ├── urls.py                # API URL ルーティング設定
│   └── apps.py                # アプリケーション設定
├── config/                     # Django プロジェクト設定
│   ├── settings.py            # Django メイン設定（DB、アプリ、ミドルウェア）
│   ├── urls.py                # プロジェクトルートの URL 設定
│   ├── wsgi.py                # WSGI アプリケーション
│   └── asgi.py                # ASGI アプリケーション
├── docker-compose.yml         # PostgreSQL コンテナ設定
├── pyproject.toml             # プロジェクトメタデータ・依存関係（uv 用）
├── Makefile                   # 開発タスクコマンド集
├── manage.py                  # Django 管理コマンド
├── .env.sample                # 環境変数テンプレート
├── .gitignore                 # Git 除外設定
└── README.md                  # プロジェクトドキュメント（このファイル）
```

### ディレクトリ詳細

#### `api/` - メインアプリケーション
Django アプリケーションの本体。カテゴリ管理 API のすべてのロジックがここに含まれます。

- **`models/`**: データベーステーブルの定義
  - UUIDを主キーとして使用
  - 型ヒント（Type Hints）を完全実装
  - `__str__` メソッドによる可読性の向上

- **`serializers/`**: JSON ⇔ モデル変換とバリデーション
  - 親カテゴリの自己参照禁止
  - 企業間の整合性チェック

- **`views/`**: API エンドポイントのハンドラ
  - ModelViewSet による CRUD 自動生成
  - 型付き QuerySet

- **`tests/`**: 自動テスト
  - 14 個の包括的なテストケース
  - 正常系・異常系の両方をカバー

#### `config/` - Django プロジェクト設定
プロジェクト全体の設定ファイル群。データベース接続、ミドルウェア、インストールされたアプリケーションなどを管理。

#### ルートレベルファイル
- **`pyproject.toml`**: モダンな Python プロジェクト設定（PEP 518）
  - 依存関係管理（uv 使用）
  - Ruff、mypy の設定
  - カバレッジ設定

- **`Makefile`**: 開発タスクの簡易化
  - `make test`: テスト実行
  - `make lint`: コード品質チェック
  - `make docker-up`: PostgreSQL 起動

- **`docker-compose.yml`**: ローカル開発用 PostgreSQL 環境

## テスト

14個の包括的なテストケースを実装：

- カテゴリの CRUD 操作
- 親カテゴリの設定・更新
- バリデーションチェック
- エラーハンドリング

```bash
# テスト実行
make test

# カバレッジレポート生成
make coverage
```

## ライセンス

This project is part of a coding interview assessment.
