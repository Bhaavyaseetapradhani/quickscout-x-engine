import streamlit as st
import google.generativeai as genai
from google.cloud import firestore
import json
from datetime import datetime

# Configure Gemini API
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "your-api-key-here")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Firestore (GCP Database)
db = firestore.client()

st.set_page_config(page_title="QuickScout X", layout="wide")
st.title("QuickScout X - AI Tactical Match Engine")
st.markdown("Instant tactical intelligence for athletes and coaches powered by Google Gemini AI")

# Store analysis in Firestore
def save_analysis(opponent, role, situation, analysis):
    try:
        db.collection("analyses").add({
            "opponent": opponent,
            "role": role,
            "situation": situation,
            "analysis": analysis,
            "timestamp": datetime.now()
        })
    except:
        st.warning("Could not save to database (Firestore not configured)")

# Get AI analysis from Gemini
def get_ai_analysis(opponent, role, situation, field_type):
    prompt = f"""
    You are an expert cricket tactical coach. Analyze this cricket match scenario:
    
    Opponent: {opponent}
    Your Role: {role}
    Match Situation: {situation}
    Field Type: {field_type}
    
    Provide a detailed JSON response with the following structure:
    {{
        "tendencies": "Key playing tendencies of the opponent",
        "weaknesses": "Main weaknesses to exploit",
        "strategy": "Recommended strategy for this match situation",
        "counter": "Counter-strategy against their likely moves",
        "execution_tips": "Practical tips for execution",
        "win_probability": {{
            "base": "Base win probability %",
            "with_plan": "Win probability with recommended plan %",
            "confidence": "Your confidence level %"
        }}
    }}
    
    Be specific and tactical."""
    
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        st.error(f"AI Error: {e}")
    
    return None

st.header("Enter Match Details")
col1, col2 = st.columns(2)

with col1:
    sport = st.selectbox("Sport", ["Cricket"])
    players = {
        "Men": ["Virat Kohli", "Rohit Sharma", "MS Dhoni", "Jasprit Bumrah", "Bhuvneshwar Kumar"],
        "Women": ["Smriti Mandana", "Mithali Raj", "Harmanpreet Kaur", "Shafali Verma", "Radha Yadav"]
    }
    gender = st.selectbox("Player Gender", ["Men", "Women"])
    opponent_name = st.selectbox("Select Opponent", players[gender])
    opponent_profile = st.text_area("Additional Profile Info", "Elite player", height=80)

with col2:
    match_situation = st.text_area("Match Situation", "ODI, score tied", height=80)
    your_role = st.selectbox("Your Role", ["Batsman", "Bowler", "All-rounder"])
    field_type = st.selectbox("Field Type", ["Standard", "Indoor", "Outdoor"])

st.markdown("---")

if st.button("Generate Tactical Intelligence with AI"):
    with st.spinner("Analyzing with Gemini AI..."):
        analysis = get_ai_analysis(opponent_name, your_role, match_situation, field_type)
        
        if analysis:
            st.success(f"AI Analysis Complete for {opponent_name}")
            
            # Save to database
            save_analysis(opponent_name, your_role, match_situation, analysis)
            
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Tendencies", "Weaknesses", "Strategy", "Counter", "Skills", "Impact"])
            
            with tab1:
                st.subheader(f"{opponent_name} Tendencies")
                st.write(analysis.get("tendencies", "Loading..."))
            
            with tab2:
                st.subheader("When They Struggle")
                st.write(analysis.get("weaknesses", "Loading..."))
            
            with tab3:
                st.subheader("Expected Strategy")
                st.write(analysis.get("strategy", "Loading..."))
            
            with tab4:
                st.subheader("Counter Strategy")
                st.write(analysis.get("counter", "Loading..."))
            
            with tab5:
                st.subheader("Execution Tips")
                st.write(analysis.get("execution_tips", "Loading..."))
            
            with tab6:
                st.subheader("Win Probability")
                probs = analysis.get("win_probability", {})
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Base", probs.get("base", "N/A"))
                with col2:
                    st.metric("With Plan", probs.get("with_plan", "N/A"))
                with col3:
                    st.metric("Confidence", probs.get("confidence", "N/A"))
        else:
            st.error("Could not generate analysis. Check API key and try again.")

st.markdown("---")
st.markdown("QuickScout X - Build and Blog Marathon 2025 | Powered by Google Cloud & Gemini AI")

