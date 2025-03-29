import os
import warnings
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from gtts import gTTS
from translate import Translator
from keybert import KeyBERT
from io import BytesIO
import pandas as pd
import streamlit as st

# Suppress unnecessary warnings
warnings.filterwarnings("ignore", message="missing ScriptRunContext")

# Initialize models (outside main for better performance)
kw_model = KeyBERT()
translator = Translator(to_lang="hi")  # Hindi translation

def fetch_news(company_name: str, max_pages: int = 3) -> list:
    """Fetch news articles from BBC Search with error handling"""
    articles = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for page in range(max_pages):
        try:
            url = f"https://www.bbc.com/search?q={company_name}&page={page}"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.select('div[class*="sc-c6f6255e-0"]')
            
            for item in news_items:
                try:
                    title = item.find('h2').get_text(strip=True) if item.find('h2') else None
                    summary = item.select_one('div[class*="sc-4ea10043-3"]').get_text(strip=True) if item.select_one('div[class*="sc-4ea10043-3"]') else None
                    
                    if title and summary:
                        articles.append({
                            "title": title,
                            "summary": summary,
                            "sentiment": "",
                            "keywords": [],
                            "audio": None
                        })
                except Exception as e:
                    continue
                    
        except requests.exceptions.RequestException as e:
            continue
    
    return articles[:10]  # Return max 10 articles

def analyze_sentiment(text: str) -> str:
    """Classify sentiment with emoji indicators"""
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    
    if polarity > 0:
        return "😊 Positive"
    elif polarity < 0:
        return "😠 Negative"
    return "😐 Neutral"

def extract_keywords(text: str) -> list:
    """Extract keywords with fallback"""
    try:
        return [kw[0] for kw in kw_model.extract_keywords(
            text, 
            keyphrase_ngram_range=(1, 2), 
            top_n=3
        )]
    except:
        return []

def generate_audio(text: str) -> BytesIO:
    """Generate Hindi audio with error handling"""
    try:
        translated = translator.translate(text[:500])  # Limit text length
        audio = BytesIO()
        tts = gTTS(translated, lang='hi')
        tts.write_to_fp(audio)
        audio.seek(0)
        return audio
    except Exception as e:
        return None

