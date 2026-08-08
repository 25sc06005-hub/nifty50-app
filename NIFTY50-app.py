import streamlit as st
import google.generativeai as genai
import json
import time

st.set_page_config(page_title="AutoShield for Google", page_icon="🌐", layout="centered")

st.title("🌐 AutoShield: Google Reviews Automation")
st.caption("Auto-sync Google Maps reviews and publish AI replies with 1 click.")

# 1. API Configuration
st.sidebar.header("⚙️ Configuration")
api_key = st.sidebar.text_input("Enter Free Gemini API Key", type="password")

# 2. Simulated Google Business Profile Connection
st.sidebar.markdown("---")
st.sidebar.subheader("Google Business Account")
if "connected" not in st.session_state:
    st.session_state.connected = False

if not st.session_state.connected:
    if st.sidebar.button("🔗 Connect Google Business"):
        st.session_state.connected = True
        st.sidebar.success("Connected to 'Bella's Italian Bistro'!")
        st.rerun()
else:
    st.sidebar.success("🟢 Connected: Bella's Italian Bistro")

# Mock Incoming Google Reviews (Simulating Google API)
MOCK_GOOGLE_REVIEWS = [
    {
        "id": "rev_01",
        "author": "Rahul Sharma",
        "stars": 1,
        "date": "10 mins ago",
        "review": "The food took 50 minutes to arrive and was completely cold. Poor service."
    },
    {
        "id": "rev_02",
        "author": "Ananya Patel",
        "stars": 5,
        "date": "2 hours ago",
        "review": "Best pasta in town! The staff was super warm and hospitable. Will come again!"
    }
]

# 3. Main Dashboard
if not st.session_state.connected:
    st.info("Click 'Connect Google Business' in the sidebar to sync incoming Google Maps reviews.")
else:
    st.subheader("📥 Incoming Unreplied Google Reviews")
    
    # Select a review pulled from "Google"
    review_options = [f"{r['stars']}⭐ from {r['author']} ({r['date']})" for r in MOCK_GOOGLE_REVIEWS]
    selected_idx = st.selectbox("Select Review to Process:", range(len(review_options)), format_func=lambda x: review_options[x])
    
    selected_review = MOCK_GOOGLE_REVIEWS[selected_idx]
    
    st.card = st.container(border=True)
    st.card.write(f"**Author:** {selected_review['author']}")
    st.card.write(f"**Rating:** {'⭐' * selected_review['stars']}")
    st.card.write(f"**Review:** \"{selected_review['review']}\"")
    
    if st.button("Generate & Publish to Google", type="primary"):
        if not api_key:
            st.error("Please enter your free Gemini API key in the sidebar.")
        else:
            with st.spinner("Analyzing review and communicating with Google API..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')

                    prompt = f"""
                    You are responding on behalf of Bella's Italian Bistro on Google Maps.
                    Customer Rating: {selected_review['stars']} stars.
                    Customer Review: "{selected_review['review']}"

                    Return raw JSON ONLY:
                    {{
                        "sentiment": "Positive" | "Negative",
                        "reply": "A polite, short response to post publicly on Google Maps."
                    }}
                    """

                    response = model.generate_content(
                        prompt,
                        generation_config={"response_mime_type": "application/json"}
                    )
                    
                    result = json.loads(response.text)

                    st.divider()
                    st.subheader("🚀 Google Reply Status")
                    
                    st.write(f"**Sentiment Analysis:** `{result.get('sentiment')}`")
                    st.code(result.get("reply"), language="text")
                    
                    # Simulating the API POST call back to Google
                    with st.spinner("Posting reply directly to Google Maps..."):
                        time.sleep(1.5) # Fake network delay for demo
                    
                    st.success("✅ Reply published directly to Google Business Profile!")

                except Exception as e:
                    st.error(f"Error: {str(e)}")