import streamlit as st
import pandas as pd
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# Page setup
st.set_page_config(page_title="TikTok Trending Songs – Remix Finder", layout="wide")
st.title("🎧 TikTok Trending Songs — Remix Finder (EDM / Techno)")

# --- Fetch trending songs ---
@st.cache_data(ttl=3600)
def fetch_kworb_tiktok_top(country_code="US", top_n=25):
    """Fetch top TikTok trending songs from Kworb.net"""
    url = f"https://kworb.net/charts/tiktok/{country_code.lower()}.html"
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table")
    if table is None:
        st.error("Could not find chart table on Kworb — layout might have changed.")
        return pd.DataFrame()

    songs = []
    for row in table.find_all("tr")[1:top_n+1]:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) >= 3:
            rank, artist, title = cols[:3]
            songs.append({"rank": rank, "artist": artist, "title": title})
    df = pd.DataFrame(songs)

    # Add YouTube and Spotify search links
    df["YouTube"] = df.apply(
        lambda r: f"https://www.youtube.com/results?search_query={quote(r['artist']+' '+r['title'])}",
        axis=1,
    )
    df["Spotify"] = df.apply(
        lambda r: f"https://open.spotify.com/search/{quote(r['artist']+' '+r['title'])}",
        axis=1,
    )
    return df

# --- Sidebar filters ---
st.sidebar.header("Filters")
region = st.sidebar.selectbox("Region", ["US", "UK", "DE", "FR", "Global"])
keyword = st.sidebar.text_input("Search by artist or title", "")

# Load chart for chosen region
df = fetch_kworb_tiktok_top(region, 25)

if keyword:
    df = df[df.apply(lambda r: keyword.lower() in (r["artist"] + r["title"]).lower(), axis=1)]

# --- Show table ---
st.dataframe(df[["rank", "artist", "title", "YouTube", "Spotify"]])

# --- 🎲 Random Song Picker ---
st.markdown("### 🎲 Random Song Picker")
if st.button("Give me a random song to remix"):
    if len(df) > 0:
        random_song = df.sample(1).iloc[0]
        st.success(f"Your remix challenge: **{random_song['title']}** by **{random_song['artist']}**")
        st.markdown(f"[🎧 Listen on YouTube]({random_song['YouTube']}) | [🎵 Find on Spotify]({random_song['Spotify']})")
    else:
        st.warning("No songs available. Try changing filters or region.")

st.caption("Data from Kworb TikTok Charts • Links auto-generated • Built with ❤️ using Streamlit")
