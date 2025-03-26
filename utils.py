import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from gtts import gTTS
import pandas as pd
import os
import uuid
from googletrans import Translator
from keybert import KeyBERT
from io import BytesIO

# Initialize KeyBERT model
kw_model = KeyBERT()

# Function to fetch news articles
def fetch_news_articles(company_name):
    urls = [f"https://www.bbc.com/search?q={company_name}&page={i}" for i in range(6)]
    articles = []
    
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for item in soup.find_all('div', class_='sc-c6f6255e-0 eGcloy'):
                title_element = item.find('h2')
                summary_element = item.find('div', class_='sc-4ea10043-3 kMizuB')
                
                if title_element and summary_element:
                    articles.append({
                        "Title": title_element.text,
                        "Summary": summary_element.text,
                        "Sentiment": "",
                        "Keywords": [],
                        "Audio": None
                    })
        except Exception as e:
            st.warning(f"Error fetching {url}: {str(e)}")
            continue
    
    return articles[:15]  # Return max 15 articles

# Sentiment analysis
def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return "Positive"
    elif analysis.sentiment.polarity < 0:
        return "Negative"
    return "Neutral"

# Keyword extraction
def extract_keywords(text):
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=3)
    return [keyword[0] for keyword in keywords]

# Generate Hindi audio
def generate_hindi_audio(text):
    try:
        translator = Translator()
        translated = translator.translate(text, src='en', dest='hi').text
        tts = gTTS(translated, lang='hi')
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        st.error(f"Audio generation error: {str(e)}")
        return None    