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
translator = TransLateTranslator(to_lang="hi")

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
    if analysis.sentiment.polarity > 0:
        return "😊 Positive"
    elif analysis.sentiment.polarity < 0:
        return "😠 Negative"
    return "😐 Neutral"

def get_keywords(text):
    """Extract keywords using KeyBERT"""
    return [kw[0] for kw in kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), top_n=3)]

# Generate Hindi audio
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