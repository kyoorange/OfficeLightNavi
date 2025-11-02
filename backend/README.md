# バックエンド起動手順

## 前提条件

- Python 3.11以上がインストールされていること
- 依存関係がインストールされていること（`pip install -r requirements.txt`）

## 起動方法

**このディレクトリ（`backend`）でコマンドを実行してください：**

```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 環境変数の設定

`backend/.env`ファイルを作成し、以下を設定してください：

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Database URL
# Supabaseの場合
# DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres?schema=public"

# CORS Origins (本番環境用)
# フロントエンドのURLをカンマ区切りで指定
# CORS_ORIGINS="https://your-frontend.vercel.app,https://your-custom-domain.com"
```

