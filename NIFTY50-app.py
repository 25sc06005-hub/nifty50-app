import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="ReviewShield", page_icon="⭐", layout="centered")

st.title("⭐ ReviewShield")
st.caption("AI Customer Review & Reputation Manager for Small Businesses")

# 1. API Key Setup
st.sidebar.header("⚙️ Configuration")
api_key = st.sidebar.text_input("Enter Free Gemini API Key", type="password")
st.sidebar.caption("Get a free key at [aistudio.google.com](https://aistudio.google.com)")

# 2. Business Details & Input
st.subheader("1. Business Context")
col_a, col_b = st.columns(2)
with col_a:
    biz_name = st.text_input("Business Name", value="Bella's Italian Bistro")
with col_b:
    biz_type = st.selectbox("Business Type", ["Restaurant / Cafe", "Automotive / Repair", "Dental / Healthcare", "Retail Store"])

tone = st.selectbox("Desired Response Tone", ["Professional & Empathetic", "Friendly & Casual", "Formal & Direct"])

st.subheader("2. Customer Review Details")
stars = st.slider("Star Rating Received", 1, 5, 2)
review_text = st.text_area(
    "Paste Customer Review:",
    height=100,
    placeholder="e.g., The food took 45 minutes to arrive and was cold. Terrible service!"
)

# 3. AI Generation Engine
if st.button("Generate Professional Reply", type="primary"):
    if not api_key:
        st.error("Please enter your free Gemini API key in the sidebar.")
    elif not review_text.strip():
        st.warning("Please paste a review first.")
    else:
        with st.spinner("Analyzing sentiment and crafting response..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')

                prompt = f"""
                You are an expert customer relations manager for "{biz_name}", a {biz_type}.
                Customer Rating: {stars} / 5 stars.
                Customer Review: "{review_text}"
                Desired Tone: {tone}

                Analyze the review and return raw JSON ONLY with these keys:
                {{
                    "sentiment": "Positive" | "Neutral" | "Negative",
                    "core_issue": "1 sentence identifying the main issue or compliment",
                    "generated_reply": "A polished, professional response directly addresssing the customer. If negative, apologize politely and offer an offline contact email for resolution.",
                    "internal_action_tip": "1 practical action item for the staff/manager to fix this internally."
                }}
                """

                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                
                result = json.loads(response.text)

                st.divider()
                st.subheader("3. AI Generated Reply & Insights")

                # Metrics Display
                sentiment = result.get("sentiment", "Neutral")
                c1, c2 = st.columns(2)
                with c1:
                    if sentiment == "Positive":
                        st.success(f"Sentiment: {sentiment}")
                    elif sentiment == "Negative":
                        st.error(f"Sentiment: {sentiment}")
                    else:
                        st.warning(f"Sentiment: {sentiment}")
                with c2:
                    st.info(f"Issue: {result.get('core_issue', 'N/A')}")

                # Output Response
                st.markdown("**Copy-Paste Response for Google/Yelp:**")
                st.code(result.get("generated_reply", ""), language="text")

                # Staff Action Tip
                with st.expander("💡 Recommended Internal Staff Action"):
                    st.write(result.get("internal_action_tip", "N/A"))

            except Exception as e:
                st.error(f"Error generating response: {str(e)}")