# OfficeLightNavi（施設照明ナビ）

施設照明器具の選定経験が少ない担当者が、対話的に機種選定を行うことを支援するアプリケーションです。

## 機能

- 物件情報（物件名、部屋名、天井高など）をもとに機種選定を支援
- 対話的なインターフェースで質問・回答を繰り返し、最適な機種を提案
- 思考プロセスを可視化
- 候補機種の一覧表示

## 技術スタック

- **フロントエンド**: Next.js 14, Tailwind CSS
- **バックエンド**: FastAPI, Python
- **AI**: OpenAI API, Langchain
- **データ**: PostgreSQL + Supabase（pgvector対応）
- **デプロイ**: Vercel（フロント）

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/kyoorange/OfficeLightNavi.git
cd officelightnavi
```

### 2. バックエンドのセットアップ

```bash
cd backend

# 仮想環境を作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt

# 環境変数を設定
cp .env.example .env
# .envファイルを編集してOPENAI_API_KEYを設定
```

### 3. フロントエンドのセットアップ

```bash
cd frontend

# 依存関係をインストール
npm install

# 環境変数を設定（オプション）
# .env.localファイルを作成
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. 環境変数の設定

#### バックエンド

`backend/.env`ファイルを作成し、OpenAI APIキーを設定してください：

```env
OPENAI_API_KEY=your_openai_api_key_here
```

#### フロントエンド（オプション）

`frontend/.env.local`ファイルを作成し、API URLを設定できます：

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5. アプリケーションの起動

#### バックエンド

Windowsの場合：

まず、`backend`ディレクトリに移動してから実行してください：

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Linux/Macの場合：

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```


**注意**: `backend`ディレクトリに移動してからコマンドを実行してください。

バックエンドAPIが http://localhost:8000 で起動します。

#### フロントエンド

```bash
cd frontend
npm run dev
```

ブラウザで http://localhost:3000 にアクセスしてください。

## 使用方法

1. 物件情報を入力します（例: 物件名：横浜小学校、部屋名：体育館、天井高：15m）
2. エージェントが追加の質問（案件タイプ、特殊環境、調光・調色など）を行います
3. 回答すると、エージェントが思考プロセスを表示し、候補機種を提示します

## デプロイメント

SupabaseとVercelへのデプロイ手順は、[docs/supabase-vercel-deployment.md](docs/supabase-vercel-deployment.md)を参照してください。

## サンプルデータ

ベクトルデータベースに保存する機種カテゴリのデータサンプルは、`data/product_categories.json`に格納しています。

現時点（2025/11/02）でのサンプルは、以下です：

- 三菱電機LED照明器具（オプション品などは含まない）

## 開発

### ディレクトリ構造

```
officelightnavi/
├── frontend/          # Next.jsアプリ
│   ├── app/           # App Router
│   └── components/    # Reactコンポーネント
├── backend/           # FastAPIアプリ
│   ├── app/
│   │   ├── agents/    # エージェント実装
│   │   ├── routes/    # APIルート
│   │   ├── models/    # データモデル
│   │   ├── utils/     # ユーティリティ
│   │   └── data/      # モックデータ
│   └── requirements.txt
└── docs/              # ドキュメント
```

## ライセンス

未設定
