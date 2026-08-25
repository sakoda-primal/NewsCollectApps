#ライブラリのインストール ※ターミナル実行の方が良い？
#pip install streamlit
#pip install notion-client
#pip install newspaper3k
#pip install openai

from newspaper import Article
from notion_client import Client
import streamlit as st
from datetime import datetime

token = st.secrets["TOKEN"]
database_id = st.secrets["DATABASE_ID"]


#Notion接続
notion = Client(auth= token)

response = notion.databases.retrieve(
    database_id=database_id
)


#Notionへ保存
def save_news(title, url, article_text):

    page = notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "記事タイトル": {"title": [{"text": {"content": title}}]},
            "URL": {"url": url},
            "登録日": {"date": {"start": datetime.today().strftime("%Y-%m-%d")}}
        })
    page_id = page["id"]

    #1900文字単位で分割
    chunks = [article_text[i:i + 1900]
              for i in range(0, len(article_text), 1900)
             ]

    #パラグラフブロック作成
    children = []

    for chunk in chunks:
        children.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": chunk}}]}})

    #本文追加
    notion.blocks.children.append(page_id, children=children)



#Stremalit
st.title("ニュース収集アプリ")
url = st.text_input("ニュースURL")

if st.button("取得して保存"):

    try:
        #記事取得
        article = Article(url)

        article.download()
        article.parse()

        title = article.title
        article_text = article.text

        st.subheader("タイトル")
        st.write(title)

        st.subheader("本文プレビュー")
        st.write(article_text[:100])


        #Notion保存
        save_news(title, url, article_text)
        st.success("Notionへ保存しました")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")