import streamlit as st
from utils import *


# Set page config
st.set_page_config(page_title="News Sentiment Analyzer", layout="wide")

# App title
st.title("📰 News Sentiment Analyzer")
st.write("Enter a company name to analyze news sentiment and get insights.")


# Main app function
def main():
    company_name = st.text_input("Enter Company Name", placeholder="e.g., Apple, Tesla")
    
    if st.button("Analyze News"):
        if not company_name:
            st.error("Please enter a company name")
            return
            
        with st.spinner("Fetching and analyzing news..."):
            articles = fetch_news_articles(company_name)
            
            if not articles:
                st.warning("No articles found for this company")
                return
                
            # Process articles
            for article in articles:
                article["Sentiment"] = analyze_sentiment(article["Summary"])
                article["Keywords"] = extract_keywords(article["Summary"])
                article["Audio"] = generate_hindi_audio(article["Summary"])
            
            # Display results
            st.success(f"Found {len(articles)} articles about {company_name}")
            
            # Show sentiment distribution
            sentiment_counts = pd.DataFrame([a["Sentiment"] for a in articles]).value_counts().reset_index()
            sentiment_counts.columns = ["Sentiment", "Count"]
            st.bar_chart(sentiment_counts.set_index("Sentiment"))
            
            # Display articles
            for i, article in enumerate(articles, 1):
                with st.expander(f"Article {i}: {article['Title']}"):
                    st.write(f"**Summary:** {article['Summary']}")
                    st.write(f"**Sentiment:** {article['Sentiment']}")
                    st.write(f"**Keywords:** {', '.join(article['Keywords'])}")
                    
                    if article["Audio"]:
                        st.audio(article["Audio"], format="audio/mp3")
                    else:
                        st.warning("Audio not available")

if __name__ == "__main__":
    main()