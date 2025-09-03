# import os
# import praw
# import pandas as pd
# import time
# from datetime import datetime, timedelta
# import requests
# from bs4 import BeautifulSoup
# import pytz
# import streamlit as st
# import re
# from io import BytesIO
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# # ----------------------------
# # Streamlit Page Config
# # ----------------------------
# st.set_page_config(page_title="Social Media Tracker", layout="wide")

# # Custom CSS
# st.markdown("""
#     <style>
#     .stDownloadButton>button {
#         background-color: #004578;
#         color: white;
#         border-radius: 8px;
#         padding: 8px 16px;
#         font-weight: 500;
#         border: none;
#     }
#     .stDownloadButton>button:hover {
#         background-color: #005a9e;
#         color: white;
#     }
#     .css-1d391kg td {
#         white-space: nowrap;
#         overflow: hidden;
#         text-overflow: ellipsis;
#         max-width: 400px;
#     }
#     </style>
# """, unsafe_allow_html=True)

# st.title("Social Media Tracker")
# st.caption("Tracking Windows-related issues from Reddit & Microsoft Learn")

# # ----------------------------
# # Sidebar Controls
# # ----------------------------
# st.sidebar.header("Fetch Settings")
# days_to_fetch = st.sidebar.slider("Number of days to look back", min_value=1, max_value=30, value=5)
# posts_per_source = st.sidebar.slider("Posts per subreddit/page", min_value=10, max_value=100, value=50)

# # ----------------------------
# # Helper Functions
# # ----------------------------
# def convert_df(df):
#     output = BytesIO()
#     df.to_excel(output, index=False, engine='openpyxl')
#     return output.getvalue()

# def clean_df(df):
#     df = df.drop_duplicates(subset=['Title'], keep='first')
#     df['Date'] = pd.to_datetime(df['Date'], errors='coerce', utc=True)
#     df['Date'] = df['Date'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
#     return df.sort_values(by='Date', ascending=False)

# def add_sentiment(df):
#     analyzer = SentimentIntensityAnalyzer()
#     df['Sentiment'] = df['Title'].apply(lambda x: analyzer.polarity_scores(x)['compound'] if pd.notnull(x) else 0)
#     return df

# # ----------------------------
# # Fetch Reddit Data
# # ----------------------------
# with st.spinner("Fetching Reddit data..."):
#     try:
#         reddit = praw.Reddit(
#             client_id='v3cuXYxt94bXX3hZmWvWtA',
#             client_secret='oAE-Hxcrv2KddpRBgzwaiToGXozxfQ',
#             user_agent='Glad-Line-2254'
#         )
#         subreddits = [
#             'windowsinsiders','WindowsHelp','Windows','Windows10','Windows11',
#             'techsupport','pcmasterrace','gaming','Steam','PCGaming','bugs',
#             'softwarebugs','TechSupport'
#         ]
#         dict_reddit = {}
#         count = 0
#         cutoff = datetime.utcnow() - timedelta(days=days_to_fetch)
#         for sub in subreddits:
#             for submission in reddit.subreddit(sub).new(limit=posts_per_source):
#                 post_date = pd.to_datetime(submission.created_utc, unit='s', errors='coerce')
#                 if post_date >= cutoff:
#                     try:
#                         submission.comments.replace_more(limit=0)
#                         comments_text = " | ".join([c.body for c in submission.comments[:3]])
#                     except Exception:
#                         comments_text = "No comments available"
#                     dict_reddit[count] = {
#                         "Date": post_date,
#                         "Title": submission.title,
#                         "Comments": comments_text,
#                         "url": submission.url,
#                         "Source": f"Reddit ({sub})",
#                         "UpVotes": submission.ups
#                     }
#                     count += 1
#             time.sleep(1)
#         df_reddit = pd.DataFrame.from_dict(dict_reddit, orient='index')
#         df_reddit = clean_df(df_reddit)
#         df_reddit = add_sentiment(df_reddit)
#     except Exception as e:
#         st.error(f"Reddit scraping failed: {e}")
#         df_reddit = pd.DataFrame()

# # ----------------------------
# # Fetch Microsoft Learn Data
# # ----------------------------
# with st.spinner("Fetching Microsoft Learn data..."):
#     try:
#         dict_learn = {}
#         cutoff = datetime.utcnow() - timedelta(days=days_to_fetch)
#         for page in range(1, 6):
#             url = f"https://learn.microsoft.com/en-us/answers/tags/60/windows?orderby=createdat&page={page}"
#             response = requests.get(url)
#             soup = BeautifulSoup(response.text, 'html.parser')
#             blocks = soup.find_all('div', class_='box margin-bottom-xxs')
#             for count, block in enumerate(blocks):
#                 title_tag = block.find('h2', class_='title is-6 margin-bottom-xxs')
#                 link_tag = block.find('a')
#                 date_tag = block.find('span', class_='display-block font-size-xs has-line-height-reset')
#                 desc_tag = block.find('p', class_='has-text-wrap')
#                 title = title_tag.get_text(strip=True) if title_tag else 'No title'
#                 link = "https://learn.microsoft.com" + link_tag.get('href') if link_tag else ''
#                 date_str = date_tag.get_text(strip=True).replace('asked', '').strip() if date_tag else None
#                 desc = desc_tag.get_text(strip=True) if desc_tag else 'No description'
#                 post_date = pd.to_datetime(date_str, errors='coerce')
#                 if post_date is not pd.NaT:
#                     post_date = post_date.replace(tzinfo=pytz.UTC)
#                 if post_date >= cutoff:
#                     dict_learn[len(dict_learn)] = {
#                         "Date": post_date,
#                         "Title": title,
#                         "Comments": desc,
#                         "url": link,
#                         "Source": "Microsoft Learn",
#                         "UpVotes": ""
#                     }
#             time.sleep(1)
#         df_learn = pd.DataFrame.from_dict(dict_learn, orient='index')
#         df_learn = clean_df(df_learn)
#         df_learn = add_sentiment(df_learn)
#     except Exception as e:
#         st.error(f"Microsoft Learn scraping failed: {e}")
#         df_learn = pd.DataFrame()

# # ----------------------------
# # Streamlit Tabs
# # ----------------------------
# tab1, tab2 = st.tabs(["Reddit", "Microsoft Learn"])

# # --- Reddit Tab ---
# with tab1:
#     st.subheader("Reddit Issues")
#     if not df_reddit.empty:
#         st.dataframe(df_reddit, use_container_width=True, hide_index=True)
#         st.download_button("Download Reddit Data", data=convert_df(df_reddit), file_name="RedditData.xlsx")

#         # Trend chart
#         trend = df_reddit.groupby(df_reddit['Date'].dt.date).size()
#         st.line_chart(trend)
#     else:
#         st.warning("No Reddit data available.")

# # --- Microsoft Learn Tab ---
# with tab2:
#     st.subheader("Microsoft Learn Issues")
#     if not df_learn.empty:
#         st.dataframe(df_learn, use_container_width=True, hide_index=True)
#         st.download_button("Download Microsoft Learn Data", data=convert_df(df_learn), file_name="LearnData.xlsx")

#         # Trend chart
#         trend = df_learn.groupby(df_learn['Date'].dt.date).size()
#         st.line_chart(trend)
#     else:
#         st.warning("No Microsoft Learn data available.")


import os
import praw
import pandas as pd
import time
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import pytz
import streamlit as st
import re
from io import BytesIO
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ----------------------------
# Streamlit Page Config
# ----------------------------
st.set_page_config(page_title="Social Media Tracker", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stDownloadButton>button {
        background-color: #004578;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
        border: none;
    }
    .stDownloadButton>button:hover {
        background-color: #005a9e;
        color: white;
    }
    .css-1d391kg td {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 400px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Social Media Tracker")
st.caption("Tracking Windows-related issues from Reddit & Microsoft Learn")

# ----------------------------
# Sidebar Controls
# ----------------------------
st.sidebar.header("Fetch Settings")
days_to_fetch = st.sidebar.slider("Number of days to look back", min_value=1, max_value=30, value=5)
posts_per_source = st.sidebar.slider("Posts per subreddit/page", min_value=10, max_value=100, value=50)
learn_pages = st.sidebar.number_input("Number of pages to scrape (Learn)", min_value=1, max_value=10, value=5)
submit = st.sidebar.button("Fetch Data")

# ----------------------------
# Helper Functions
# ----------------------------
def convert_df(df):
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    return output.getvalue()

def clean_df(df):
    df = df.drop_duplicates(subset=['Title'], keep='first')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', utc=True)
    df['Date'] = df['Date'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    return df.sort_values(by='Date', ascending=False)

def add_sentiment(df):
    analyzer = SentimentIntensityAnalyzer()
    df['Sentiment'] = df['Title'].apply(lambda x: analyzer.polarity_scores(x)['compound'] if pd.notnull(x) else 0)
    return df

# ----------------------------
# Data Fetching Trigger
# ----------------------------
if submit:
    cutoff = datetime.utcnow().replace(tzinfo=pytz.UTC) - timedelta(days=days_to_fetch)

    # ----------------------------
    # Fetch Reddit Data
    # ----------------------------
    with st.spinner("Fetching Reddit data..."):
        try:
            reddit = praw.Reddit(
                client_id='v3cuXYxt94bXX3hZmWvWtA',
                client_secret='oAE-Hxcrv2KddpRBgzwaiToGXozxfQ',
                user_agent='Glad-Line-2254'
            )
            subreddits = [
                'windowsinsiders','WindowsHelp','Windows','Windows10','Windows11',
                'techsupport','pcmasterrace','gaming','Steam','PCGaming','bugs',
                'softwarebugs','TechSupport'
            ]
            dict_reddit = {}
            count = 0
            for sub in subreddits:
                for submission in reddit.subreddit(sub).new(limit=posts_per_source):
                    post_date = pd.to_datetime(submission.created_utc, unit='s', errors='coerce').replace(tzinfo=pytz.UTC)
                    if post_date >= cutoff:
                        try:
                            submission.comments.replace_more(limit=0)
                            comments_text = " | ".join([c.body for c in submission.comments[:3]])
                        except Exception:
                            comments_text = "No comments available"
                        dict_reddit[count] = {
                            "Date": post_date,
                            "Title": submission.title,
                            "Comments": comments_text,
                            "url": submission.url,
                            "Source": f"Reddit ({sub})",
                            "UpVotes": submission.ups
                        }
                        count += 1
                time.sleep(1)
            df_reddit = pd.DataFrame.from_dict(dict_reddit, orient='index')
            df_reddit = clean_df(df_reddit)
            df_reddit = add_sentiment(df_reddit)
        except Exception as e:
            st.error(f"Reddit scraping failed: {e}")
            df_reddit = pd.DataFrame()

    # ----------------------------
    # Fetch Microsoft Learn Data
    # ----------------------------
    with st.spinner("Fetching Microsoft Learn data..."):
        try:
            dict_learn = {}
            for page in range(1, learn_pages + 1):
                url = f"https://learn.microsoft.com/en-us/answers/tags/60/windows?orderby=createdat&page={page}"
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                blocks = soup.find_all('div', class_='box margin-bottom-xxs')
                for count, block in enumerate(blocks):
                    title_tag = block.find('h2', class_='title is-6 margin-bottom-xxs')
                    link_tag = block.find('a')
                    date_tag = block.find('span', class_='display-block font-size-xs has-line-height-reset')
                    desc_tag = block.find('p', class_='has-text-wrap')
                    title = title_tag.get_text(strip=True) if title_tag else 'No title'
                    link = "https://learn.microsoft.com" + link_tag.get('href') if link_tag else ''
                    date_str = date_tag.get_text(strip=True).replace('asked', '').strip() if date_tag else None
                    desc = desc_tag.get_text(strip=True) if desc_tag else 'No description'
                    post_date = pd.to_datetime(date_str, errors='coerce')
                    if post_date is not pd.NaT:
                        post_date = post_date.replace(tzinfo=pytz.UTC)
                        if post_date >= cutoff:
                            dict_learn[len(dict_learn)] = {
                                "Date": post_date,
                                "Title": title,
                                "Comments": desc,
                                "url": link,
                                "Source": "Microsoft Learn",
                                "UpVotes": ""
                            }
                time.sleep(1)
            df_learn = pd.DataFrame.from_dict(dict_learn, orient='index')
            df_learn = clean_df(df_learn)
            df_learn = add_sentiment(df_learn)
        except Exception as e:
            st.error(f"Microsoft Learn scraping failed: {e}")
            df_learn = pd.DataFrame()

    # ----------------------------
    # Streamlit Tabs
    # ----------------------------
    tab1, tab2 = st.tabs(["Reddit", "Microsoft Learn"])

    # --- Reddit Tab ---
    with tab1:
        st.subheader("Reddit Issues")
        if not df_reddit.empty:
            st.dataframe(df_reddit, use_container_width=True, hide_index=True)
            st.download_button("Download Reddit Data", data=convert_df(df_reddit), file_name="RedditData.xlsx")
            trend = df_reddit.groupby(df_reddit['Date'].dt.date).size()
            st.line_chart(trend)
        else:
            st.warning("No Reddit data available.")

    # --- Microsoft Learn Tab ---
    with tab2:
        st.subheader("Microsoft Learn Issues")
        if not df_learn.empty:
            st.dataframe(df_learn, use_container_width=True, hide_index=True)
            st.download_button("Download Microsoft Learn Data", data=convert_df(df_learn), file_name="LearnData.xlsx")
            trend = df_learn.groupby(df_learn['Date'].dt.date).size()
            st.line_chart(trend)
        else:
            st.warning("No Microsoft Learn data available.")
