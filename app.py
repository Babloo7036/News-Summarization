from utils import *

# App configuration
st.set_page_config(page_title="News Sentiment Analyzer", layout="wide")
st.title("📰 News Sentiment Analyzer")
st.caption("Analyze news sentiment and get audio translations in Hindi")


# Main app function
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
