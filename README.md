# FCCL 材料語意問答客服

使用 Streamlit 建立線上客服介面。使用多語言 Sentence Transformers 模型將問題轉成 384 維向量，再呼叫 Supabase `match_qa` 函式搜尋 `public.qa`。

## 本機啟動

1. 確認 Supabase 已執行 `qa.sql`。
2. 在專案根目錄的 `.env` 設定 `SUPABASE_URL` 和 `SUPABASE_ANON_KEY`。
3. 執行：

   ```powershell
   uv run streamlit run main.py
   ```

第一次搜尋會下載語意模型，需要網路連線。

## 部署到 Streamlit Community Cloud

1. 將專案推送到 GitHub；不要提交 `.env`、`supabase_pw.txt` 或 `.streamlit/secrets.toml`。
2. 至少上傳 `main.py`、`requirements.txt` 和 `QA.csv`。其中 `QA.csv` 提供分類選單的常見問題。
3. 在 [Streamlit Community Cloud](https://share.streamlit.io/) 選擇 **Create app**，指定 GitHub 儲存庫、分支和入口檔 `main.py`。在 **Advanced settings** 選擇 Python 3.14，符合專案的 `.python-version` 與 `pyproject.toml` 設定。
4. 在部署設定的 **Secrets** 加入以下內容，使用 Supabase 專案的 URL 和 anon/publishable key：

   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_ANON_KEY = "your-supabase-anon-key"
   ```

5. 部署完成後開啟 Streamlit 提供的網址。

本機 `.env` 由 `python-dotenv` 載入；雲端則使用 Streamlit Secrets。資料庫搜尋使用 `qa.sql` 所建立的 `public.match_qa` RPC。查詢端與資料集嵌入使用相同的 `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` 模型。
