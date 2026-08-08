import streamlit as st
import requests
import json

st.set_page_config(page_title="ReviewShield API Engine", page_icon="⚙️", layout="centered")

# ==========================================
# 1. CUSTOM REST API CLIENT MODULE
# ==========================================
class GeminiRESTClient:
    """Custom REST API client handling direct HTTP requests to Google's Gemini API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Direct REST API endpoint
        self.endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={self.api_key}"
        )
        self.headers = {"Content-Type": "application/json"}

    def analyze_and_respond(self, business_name: str, star_rating: int, review_text: str) -> dict:
        """Constructs raw HTTP payload, handles POST request, and parses JSON output."""
        prompt = f"""
        You are an expert customer relations manager for '{business_name}'.
        Customer Rating: {star_rating} / 5 stars.
        Customer Review: "{review_text}"

        Analyze the review and return raw JSON ONLY with these exact keys:
        {{
            "sentiment": "Positive" | "Neutral" | "Negative",
            "core_issue": "1 sentence identifying the main issue or compliment",
            "generated_reply": "A polished, professional response directly addressing the customer on Google Maps.",
            "staff_action_tip": "1 practical action item for internal staff."
        }}
        """

        # Structuring the raw JSON HTTP POST body
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }

        # Making direct HTTP POST request using Python `requests`
        response = requests.post(
            self.endpoint, 
            headers=self.headers, 
            data=json.dumps(payload),
            timeout=10
        )

        # Handling API status codes explicitly
        if response.status_code == 200:
            response_json = response.json()
            # Extracting content text from REST payload structure
            raw_content = response_json["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw_content)
        else:
            raise Exception(f"HTTP Error {response.status_code}: {response.text}")


# ==========================================
# 2. STREAMLIT FRONTEND DASHBOARD
# ==========================================
st.title("⚙️ ReviewShield (Custom API Client)")
st.caption("Direct HTTP/REST API Integration Engine for Google Reviews")

# Sidebar Configuration
st.sidebar.header("🔑 Authentication")
api_key = st.sidebar.text_input("Enter Free Gemini API Key", type="password")
st.sidebar.caption("Get a free key at [aistudio.google.com](https://aistudio.google.com)")

# Input Controls
st.subheader("1. Request Payload Parameters")
biz_name = st.text_input("Business Name", value="Bella's Italian Bistro")
stars = st.slider("Customer Star Rating", 1, 5, 1)
review = st.text_area(
    "Customer Review Text:",
    value="The table was dirty when we sat down, and our pasta took almost an hour to come out."
)

# API Trigger Button
if st.button("Execute Custom REST API Call", type="primary"):
    if not api_key:
        st.error("Please enter your API Key in the sidebar.")
    elif not review.strip():
        st.warning("Please enter a customer review.")
    else:
        with st.spinner("Dispatching HTTP POST request to Gemini REST Endpoint..."):
            try:
                # Instantiate custom REST client
                client = GeminiRESTClient(api_key=api_key)
                
                # Execute API call
                result = client.analyze_and_respond(
                    business_name=biz_name,
                    star_rating=stars,
                    review_text=review
                )

                # Render Response
                st.divider()
                st.subheader("2. HTTP Response Data")

                col1, col2 = st.columns(2)
                with col1:
                    sentiment = result.get("sentiment", "Neutral")
                    if sentiment == "Negative":
                        st.error(f"Sentiment: {sentiment}")
                    elif sentiment == "Positive":
                        st.success(f"Sentiment: {sentiment}")
                    else:
                        st.warning(f"Sentiment: {sentiment}")
                
                with col2:
                    st.info(f"Core Issue: {result.get('core_issue')}")

                st.markdown("**Generated Google Maps Reply:**")
                st.code(result.get("generated_reply"), language="text")

                with st.expander("💡 Staff Action Recommendation"):
                    st.write(result.get("staff_action_tip"))

            except Exception as e:
                st.error(f"API Request Failed: {str(e)}")