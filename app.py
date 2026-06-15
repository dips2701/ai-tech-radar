import streamlit as st
import sqlite3
import pandas as pd
from database import DB_PATH, create_table, update_summary_fields
from summarizer import summarize_update
from summarize import parse_summary_output

create_table()

st.set_page_config(page_title="AI Tech Radar", layout="wide")

st.title("🚀 AI Tech Radar")
st.write("Daily AI news, research, tools, and updates.")

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query(
    "SELECT * FROM updates ORDER BY published DESC, id DESC",
    conn
)
conn.close()

news_count = len(df[df["category"] == "News"])
research_count = len(df[df["category"] == "Research"])
github_count = len(df[df["category"] == "GitHub"])

col1, col2, col3 = st.columns(3)
col1.metric("News", news_count)
col2.metric("Research", research_count)
col3.metric("GitHub", github_count)

categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
category = st.sidebar.selectbox("Category", categories)
search = st.sidebar.text_input("Search")

if category != "All":
    df = df[df["category"] == category]

if search:
    df = df[df["title"].str.contains(search, case=False, na=False)]

st.write(df["category"].value_counts())

if df.empty:
    st.warning("No news found. Run: python fetch_news.py")
else:
    for _, row in df.iterrows():
        st.subheader(row["title"])
        st.write(f"**Source:** {row['source']}")
        if pd.notna(row["impact"]) and row["impact"]:
            st.write(f"**Impact:** {row['impact']}/10")

        if pd.notna(row["ai_summary"]) and row["ai_summary"]:
            st.markdown(f"**AI Summary**\n---\n{row['ai_summary']}")
        if pd.notna(row["why_it_matters"]) and row["why_it_matters"]:
            st.markdown(f"**Why It Matters**\n---\n{row['why_it_matters']}")
        if pd.notna(row["action_item"]) and row["action_item"]:
            st.markdown(f"**Action Item**\n---\n{row['action_item']}")

        if st.button("Generate AI Summary", key=f"generate_{row['id']}"):
            with st.spinner("Generating AI summary..."):
                raw = summarize_update(row["title"], row["summary"])
                st.write(raw)
                fields = parse_summary_output(raw)
                update_summary_fields(
                    row["id"],
                    fields["SUMMARY"],
                    fields["WHY_IT_MATTERS"],
                    fields["ACTION"],
                    fields["IMPACT"]
                )
                st.success("Saved AI summary to database.")

        st.link_button("Read more", row["url"])
        st.divider()