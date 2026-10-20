import os

import streamlit as st
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from supabase import Client, create_client


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

st.set_page_config(page_title="FPC 線上客服", page_icon="💬", layout="centered")
load_dotenv()


def get_setting(name: str) -> str | None:
    """Read a setting from Streamlit secrets first, then local environment."""
    try:
        value = st.secrets.get(name)
    except (FileNotFoundError, AttributeError):
        value = None
    return value or os.getenv(name)


@st.cache_resource(show_spinner="載入語意模型中（第一次需要下載模型）…")
def load_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


@st.cache_resource
def get_supabase(url: str, key: str) -> Client:
    return create_client(url, key)


st.title("FPC 材料線上客服")
st.write("可詢問 3L-SS、3L-DS、2L-CAST、2L-SPT 與 2L-LAMI 材料。")

supabase_url = get_setting("SUPABASE_URL")
supabase_key = get_setting("SUPABASE_ANON_KEY") or get_setting("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    st.error("尚未設定 Supabase 連線資訊。請在本機 .env 或 Streamlit Secrets 設定 SUPABASE_URL 與 SUPABASE_ANON_KEY。")
    st.stop()

with st.form("qa_search"):
    user_question = st.text_input(
        "請輸入問題",
        placeholder="例如：2L-SPT 和 2L-CAST 有什麼差異？",
    )
    submitted = st.form_submit_button("搜尋答案", type="primary")

if submitted:
    if not user_question.strip():
        st.warning("請先輸入問題。")
        st.stop()

    try:
        with st.spinner("正在搜尋相近的問答…"):
            model = load_model()
            # Match the representation used when qa.sql embeddings were generated.
            query_text = f"問題：{user_question.strip()} 答案："
            vector = model.encode(query_text, normalize_embeddings=True).tolist()
            client = get_supabase(supabase_url, supabase_key)
            response = client.rpc(
                "match_qa",
                {"query_embedding": vector, "match_count": 3},
            ).execute()

        results = response.data or []
        if not results:
            st.info("目前沒有找到相近的問答，請換個方式描述或聯絡線上客服。")
        else:
            st.subheader("搜尋結果")
            for index, item in enumerate(results, start=1):
                score = item.get("similarity")
                label = f"{index}. {item['question']}"
                if score is not None:
                    label += f"（相似度 {float(score):.0%}）"
                with st.expander(label, expanded=(index == 1)):
                    st.write(item["answer"])
    except Exception:
        st.error("搜尋時發生錯誤，請確認 Supabase 設定、qa.sql 已執行，並稍後再試。")

st.caption("答案為通用材料資訊；實際規格請以供應商資料表及工程確認為準。")
