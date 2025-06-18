import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from TrustLab.ishwar.news_authenticity_detector import NewsAuthenticitySystem

# Page configuration
st.set_page_config(
    page_title="News Authenticity Detector",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize system
@st.cache_resource
def load_system():
    return NewsAuthenticitySystem()

system = load_system()

# Sidebar
st.sidebar.title("News Authenticity Detector")
st.sidebar.markdown("#### Detect fake news with AI")
st.sidebar.markdown("---")
st.sidebar.markdown("This tool uses multiple AI agents to analyze news articles:")
st.sidebar.markdown("1. NLP Classifier")
st.sidebar.markdown("2. Fact Checker")
st.sidebar.markdown("3. Source Credibility Evaluator")
st.sidebar.markdown("4. Result Aggregator")
st.sidebar.markdown("---")
st.sidebar.markdown("ℹ️ Enter a news headline or article text and optional source URL to get an authenticity analysis.")

# Main content
st.title("📰 News Authenticity Analysis")
st.markdown("Enter a news headline or article to analyze its authenticity")

# Input form
with st.form("news_form"):
    news_text = st.text_area("News text or headline", height=150)
    source_url = st.text_input("Source URL (optional)")
    submitted = st.form_submit_button("Analyze")

# Process and display results
if submitted and news_text:
    with st.spinner('Analyzing news authenticity...'):
        result = system.analyze(news_text, source_url)
    
    # Display verdict with color
    verdict_color = {
        "Highly Authentic": "green",
        "Likely Authentic": "lightgreen",
        "Uncertain": "orange",
        "Suspicious": "orangered",
        "Likely Fake": "red"
    }
    
    color = verdict_color.get(result["verdict"], "orange")
    
    # Display main verdict
    st.markdown(f"## Verdict: <span style='color:{color}'>{result['verdict']}</span>", unsafe_allow_html=True)
    
    # Create columns for the dashboard
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Overall score
        st.metric("Authenticity Score", f"{result['authenticity_score']:.2f}/1.00")
        
        # Explanation
        st.subheader("Analysis Breakdown")
        
        # Create data for breakdown chart
        components = {
            "NLP Analysis": result['explanation']['nlp_classification']['contribution'],
            "Fact Check": result['explanation']['fact_check']['contribution'],
            "Source Credibility": result['explanation']['source_credibility']['contribution']
        }
        
        # Create a DataFrame for the components
        df = pd.DataFrame({
            'Component': list(components.keys()),
            'Score': list(components.values())
        })
        
        # Create a horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, 3))
        sns.barplot(x='Score', y='Component', data=df, palette='viridis', ax=ax)
        ax.set_xlim(0, 0.5)  # Maximum possible score for a component would be 0.5
        ax.set_title('Component Contributions')
        st.pyplot(fig)
        
        # Display component details
        st.markdown("#### Component Details")
        
        # NLP Classification
        nlp_color = "green" if result['explanation']['nlp_classification']['real_probability'] >= 0.5 else "red"
        st.markdown(f"**NLP Analysis**: <span style='color:{nlp_color}'>{result['explanation']['nlp_classification']['real_probability']:.2f}</span> probability of being real", unsafe_allow_html=True)
        
        # Fact Check
        matches_count = result['explanation']['fact_check']['matches_found']
        fact_check_color = "green" if result['explanation']['fact_check']['match_score'] >= 0.5 else "orange"
        st.markdown(f"**Fact Check**: <span style='color:{fact_check_color}'>{result['explanation']['fact_check']['match_score']:.2f}</span> match score ({matches_count} {'matches' if matches_count != 1 else 'match'} found)", unsafe_allow_html=True)
        
        # Source Credibility
        source_level = result['explanation']['source_credibility']['credibility_level']
        source_color = {"High": "green", "Medium": "orange", "Low": "red"}.get(source_level, "gray")
        st.markdown(f"**Source Credibility**: <span style='color:{source_color}'>{source_level}</span> ({result['explanation']['source_credibility']['credibility_score']:.2f})", unsafe_allow_html=True)
        
    with col2:
        # Detailed information
        st.subheader("Detailed Information")
        
        # Show the claims extracted
        st.markdown("#### Extracted Claims")
        for i, claim in enumerate(result['details']['fact_check']['claims']):
            st.markdown(f"{i+1}. {claim}")
        
        # Show matches if any
        if result['details']['fact_check']['matches']:
            st.markdown("#### Matching Sources")
            for match in result['details']['fact_check']['matches']:
                st.markdown(f"- [{match['title']}]({match['url']}) ({match['source']})")
        else:
            st.info("No matching sources found in fact check databases.")
        
        # Show source information if provided
        if source_url:
            st.markdown("#### Source Information")
            source_name = result['details']['source_credibility']['source_name']
            st.markdown(f"Domain: **{source_name}**")
            st.markdown(f"Credibility: **{result['details']['source_credibility']['credibility_level']}**")
    
    # Show raw data expandable
    with st.expander("Show raw analysis data"):
        st.json(result)

else:
    if submitted:
        st.warning("Please enter some news text to analyze.")
    else:
        # Display some example news for testing
        st.info("👈 Enter a news article or headline and click 'Analyze' to get started.")
        
        with st.expander("Try with an example"):
            examples = [
                "Scientists discover new vaccine that is 100% effective against all variants of COVID-19.",
                "Local politician caught taking bribes in undercover FBI operation.",
                "Studies show chocolate is healthier than vegetables, doctors recommend eating it daily."
            ]
            
            for i, example in enumerate(examples):
                if st.button(f"Example {i+1}", key=f"example_{i}"):
                    # Set the example text in the session state
                    st.session_state['example_text'] = example
                    st.experimental_rerun()

# If an example was selected
if 'example_text' in st.session_state:
    # Use the example text
    example_text = st.session_state['example_text']
    # Clear it from session state so it doesn't persist
    del st.session_state['example_text']
    # Process the example
    with st.spinner('Analyzing example news...'):
        result = system.analyze(example_text, None)
    
    # Display results (same code as above)
    verdict_color = {
        "Highly Authentic": "green",
        "Likely Authentic": "lightgreen",
        "Uncertain": "orange",
        "Suspicious": "orangered",
        "Likely Fake": "red"
    }
    
    color = verdict_color.get(result["verdict"], "orange")
    
    # Display main verdict
    st.markdown(f"## Verdict: <span style='color:{color}'>{result['verdict']}</span>", unsafe_allow_html=True)
    
    # Create columns for the dashboard
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Overall score
        st.metric("Authenticity Score", f"{result['authenticity_score']:.2f}/1.00")
        
        # Explanation
        st.subheader("Analysis Breakdown")
        
        # Create data for breakdown chart
        components = {
            "NLP Analysis": result['explanation']['nlp_classification']['contribution'],
            "Fact Check": result['explanation']['fact_check']['contribution'],
            "Source Credibility": result['explanation']['source_credibility']['contribution']
        }
        
        # Create a DataFrame for the components
        df = pd.DataFrame({
            'Component': list(components.keys()),
            'Score': list(components.values())
        })
        
        # Create a horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, 3))
        sns.barplot(x='Score', y='Component', data=df, palette='viridis', ax=ax)
        ax.set_xlim(0, 0.5)  # Maximum possible score for a component would be 0.5
        ax.set_title('Component Contributions')
        st.pyplot(fig)
        
        # Display component details
        st.markdown("#### Component Details")
        
        # NLP Classification
        nlp_color = "green" if result['explanation']['nlp_classification']['real_probability'] >= 0.5 else "red"
        st.markdown(f"**NLP Analysis**: <span style='color:{nlp_color}'>{result['explanation']['nlp_classification']['real_probability']:.2f}</span> probability of being real", unsafe_allow_html=True)
        
        # Fact Check
        matches_count = result['explanation']['fact_check']['matches_found']
        fact_check_color = "green" if result['explanation']['fact_check']['match_score'] >= 0.5 else "orange"
        st.markdown(f"**Fact Check**: <span style='color:{fact_check_color}'>{result['explanation']['fact_check']['match_score']:.2f}</span> match score ({matches_count} {'matches' if matches_count != 1 else 'match'} found)", unsafe_allow_html=True)
        
        # Source Credibility
        source_level = result['explanation']['source_credibility']['credibility_level']
        source_color = {"High": "green", "Medium": "orange", "Low": "red"}.get(source_level, "gray")
        st.markdown(f"**Source Credibility**: <span style='color:{source_color}'>{source_level}</span> ({result['explanation']['source_credibility']['credibility_score']:.2f})", unsafe_allow_html=True)
        
    with col2:
        # Detailed information
        st.subheader("Detailed Information")
        
        # Show the claims extracted
        st.markdown("#### Extracted Claims")
        for i, claim in enumerate(result['details']['fact_check']['claims']):
            st.markdown(f"{i+1}. {claim}")
        
        # Show matches if any
        if result['details']['fact_check']['matches']:
            st.markdown("#### Matching Sources")
            for match in result['details']['fact_check']['matches']:
                st.markdown(f"- [{match['title']}]({match['url']}) ({match['source']})")
        else:
            st.info("No matching sources found in fact check databases.")
        
    # Show raw data expandable
    with st.expander("Show raw analysis data"):
        st.json(result)

# Footer
st.markdown("---")
st.markdown("*Disclaimer: This is a demo system with simulated AI responses. In a production system, it would use actual NLP models, fact-checking APIs, and credibility databases.*")
