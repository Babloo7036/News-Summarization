import streamlit as st
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from gtts import gTTS
from translate import Translator as TransLateTranslator
from keybert import KeyBERT
from io import BytesIO
import pandas as pd

# Initialize models
kw_model = KeyBERT()
translator = TransLateTranslator(to_lang="hi")  # Hindi translation

# App configuration
st.set_page_config(page_title="News Sentiment Analyzer", layout="wide")
st.title("📰 News Sentiment Analyzer")
st.caption("Analyze news sentiment and get audio translations in Hindi")

def fetch_news(company_name):
    """Fetch news articles from BBC Search"""
    articles = []
    for page in range(3):  # Check first 3 pages
        try:
            url = f"https://www.bbc.com/search?q={company_name}&page={page}"
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.select('div.sc-c6f6255e-0.eGcloy'):
                title = item.find('h2').get_text() if item.find('h2') else None
                summary = item.select_one('div.sc-4ea10043-3.kMizuB').get_text() if item.select_one('div.sc-4ea10043-3.kMizuB') else None
                
                if title and summary:
                    articles.append({
                        "title": title,
                        "summary": summary,
                        "sentiment": "",
                        "keywords": [],
                        "audio": None
                    })
        except Exception as e:
            st.warning(f"Couldn't fetch page {page}: {str(e)}")
    
    return articles[:10]  # Return max 10 articles

def analyze_sentiment(text):
    """Classify sentiment using TextBlob"""
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.1:
        return "😊 Positive"
    elif analysis.sentiment.polarity < -0.1:
        return "😠 Negative"
    return "😐 Neutral"

def get_keywords(text):
    """Extract keywords using KeyBERT"""
    return [kw[0] for kw in kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), top_n=3)]

def create_audio(text):
    """Generate Hindi audio from text"""
    try:
        translated = translator.translate(text)
        audio = BytesIO()
        tts = gTTS(translated, lang='hi')
        tts.write_to_fp(audio)
        audio.seek(0)
        return audio
    except Exception as e:
        st.error(f"Translation/Audio error: {str(e)}")
        return None

# Main UI
company = st.text_input("Enter company name", "Microsoft")
if st.button("Analyze News"):
    if not company.strip():
        st.error("Please enter a company name")
        st.stop()
    
    with st.spinner("Searching for news articles..."):
        articles = fetch_news(company)
        
        if not articles:
            st.warning("No articles found. Try a different company name.")
            st.stop()
        
        # Process articles
        progress_bar = st.progress(0)
        for i, article in enumerate(articles):
            article["sentiment"] = analyze_sentiment(article["summary"])
            article["keywords"] = get_keywords(article["summary"])
            article["audio"] = create_audio(article["summary"])
            progress_bar.progress((i + 1) / len(articles))
        
        # Show results
        st.success(f"Analysis complete for {company}")
        
        # Sentiment distribution
        st.subheader("Sentiment Overview")
        sentiment_df = pd.DataFrame([a["sentiment"] for a in articles]).value_counts().reset_index()
        sentiment_df.columns = ["Sentiment", "Count"]
        st.bar_chart(sentiment_df.set_index("Sentiment"))
        
        # Articles display
        st.subheader("News Articles")
        for i, article in enumerate(articles, 1):
            with st.expander(f"{i}. {article['title']} ({article['sentiment']})"):
                st.write(article["summary"])
                st.write(f"**Keywords:** {', '.join(article['keywords'])}")
                
                if article["audio"]:
                    st.audio(article["audio"], format="audio/mp3")
                else:
                    st.warning("Audio translation unavailable")