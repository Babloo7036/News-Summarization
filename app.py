from utils import *

def display_results(company: str, articles: list):
    """Display analysis results in Streamlit"""
    st.success(f"Analysis complete for {company}")
    
    # Sentiment distribution
    st.subheader("📊 Sentiment Overview")
    if articles:
        sentiment_df = pd.DataFrame([a["sentiment"] for a in articles]).value_counts().reset_index()
        sentiment_df.columns = ["Sentiment", "Count"]
        st.bar_chart(sentiment_df.set_index("Sentiment"))
    
    # Articles display
    st.subheader("📰 News Articles")
    for i, article in enumerate(articles, 1):
        with st.expander(f"{i}. {article['title']} ({article['sentiment']})"):
            st.write(article["summary"])
            st.write(f"**Keywords:** {', '.join(article['keywords'])}")
            
            if article["audio"]:
                st.audio(article["audio"], format="audio/mp3")
            else:
                st.warning("Audio translation unavailable")

def main():
    """Main application function"""
    # Configure page
    st.set_page_config(
        page_title="News Sentiment Analyzer",
        page_icon="📰",
        layout="wide"
    )
    
    st.title("📰 News Sentiment Analyzer")
    st.caption("Analyze news sentiment and get audio translations in Hindi")
    
    # Input section
    company = st.text_input(
        "Enter company name", 
        placeholder="e.g., Microsoft, Tesla",
        key="company_input"
    )
    
    if st.button("Analyze News", type="primary"):
        if not company.strip():
            st.error("Please enter a company name")
            return
        
        with st.spinner("Searching for news articles..."):
            articles = fetch_news(company.strip())
            
            if not articles:
                st.warning("No articles found. Try a different company name.")
                return
            
            # Process articles with progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, article in enumerate(articles):
                status_text.text(f"Processing article {i+1}/{len(articles)}...")
                article["sentiment"] = analyze_sentiment(article["summary"])
                article["keywords"] = extract_keywords(article["summary"])
                article["audio"] = generate_audio(article["summary"])
                progress_bar.progress((i + 1) / len(articles))
            
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            display_results(company, articles)

if __name__ == "__main__":
    main()