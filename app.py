import streamlit as st
import json
from datetime import datetime
import google.generativeai as genai
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="MedWise AI - Medical Awareness Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1e40af;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-high {
        background-color: #fee2e2;
        border-left: 5px solid #dc2626;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .risk-medium {
        background-color: #fef3c7;
        border-left: 5px solid #f59e0b;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .risk-low {
        background-color: #d1fae5;
        border-left: 5px solid #10b981;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .disclaimer {
        background-color: #fef2f2;
        border: 2px solid #fca5a5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 2rem 0;
    }
    .action-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
    }
    .stButton>button {
        background-color: #1e40af;
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 0.5rem;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1e3a8a;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

def configure_gemini():
    """Configure Gemini API"""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            st.error("⚠️ Gemini API key not found. Please add it to Streamlit secrets.")
            st.stop()
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error configuring Gemini: {str(e)}")
        st.stop()

def analyze_medical_condition(user_input, model):
    """Analyze medical condition using Gemini AI"""
    
    prompt = f"""You are a medical awareness assistant helping patients understand their health conditions better. 

User's condition description: {user_input}

Provide a comprehensive analysis in the following JSON format:

{{
    "risk_level": "LOW/MEDIUM/HIGH",
    "urgency": "EMERGENCY/URGENT/CAN_WAIT/NON_URGENT",
    "condition_name": "Name of the likely condition",
    "simple_explanation": "Explain the condition in simple, easy-to-understand language (3-4 sentences)",
    "is_emergency": true/false,
    "surgery_needed": "LIKELY_NEEDED/MAYBE_NEEDED/ALTERNATIVES_AVAILABLE/NOT_NEEDED",
    "consultation_advice": "Type of specialist to consult and when",
    "action_steps": [
        "Step 1",
        "Step 2",
        "Step 3"
    ],
    "questions_for_doctor": [
        "Question 1",
        "Question 2",
        "Question 3"
    ],
    "alternative_treatments": [
        "Alternative 1",
        "Alternative 2"
    ],
    "warning_signs": [
        "Sign 1 that requires immediate attention",
        "Sign 2"
    ],
    "lifestyle_changes": [
        "Change 1",
        "Change 2"
    ],
    "estimated_recovery_time": "Recovery timeline if treatment is pursued",
    "key_message": "One key message for the patient"
}}

Important guidelines:
- Be conservative in risk assessment (safety first)
- Use simple language, avoid medical jargon
- If it sounds like an emergency, mark it clearly
- Always encourage professional medical consultation
- Provide balanced view of surgery vs alternatives
- Be empathetic and supportive in tone"""

    try:
        response = model.generate_content(prompt)
        # Extract JSON from response
        response_text = response.text
        # Remove markdown code blocks if present
        if "```
            response_text = response_text.split("```json").split("```
        elif "```" in response_text:
            response_text = response_text.split("``````")[0]
        
        result = json.loads(response_text.strip())
        return result
    except json.JSONDecodeError as e:
        st.error(f"Error parsing AI response: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error analyzing condition: {str(e)}")
        return None

def display_analysis(result):
    """Display the analysis results"""
    
    # Emergency Alert
    if result.get('is_emergency', False):
        st.error("🚨 **EMERGENCY DETECTED** 🚨")
        st.markdown("""
        ### ⚠️ This may require immediate medical attention!
        **Please call emergency services or go to the nearest hospital immediately.**
        - India Emergency: 108 / 112
        - Ambulance: 102
        """)
        st.markdown("---")
    
    # Risk Level Display
    risk_level = result.get('risk_level', 'MEDIUM')
    risk_class = f"risk-{risk_level.lower()}"
    
    risk_colors = {
        'HIGH': '🔴',
        'MEDIUM': '🟡',
        'LOW': '🟢'
    }
    
    st.markdown(f'<div class="{risk_class}">', unsafe_allow_html=True)
    st.markdown(f"## {risk_colors.get(risk_level, '🟡')} Risk Level: **{risk_level}**")
    st.markdown(f"**Urgency:** {result.get('urgency', 'N/A')}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Condition Name
    st.markdown(f"### 📋 Likely Condition: {result.get('condition_name', 'Not determined')}")
    
    # Simple Explanation
    st.markdown('<div class="action-card">', unsafe_allow_html=True)
    st.markdown("### 💡 What This Means (In Simple Words)")
    st.write(result.get('simple_explanation', 'No explanation available'))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Two Column Layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Surgery Assessment
        st.markdown('<div class="action-card">', unsafe_allow_html=True)
        st.markdown("### 🏥 Surgery Assessment")
        surgery_status = result.get('surgery_needed', 'MAYBE_NEEDED')
        surgery_icons = {
            'LIKELY_NEEDED': '⚠️',
            'MAYBE_NEEDED': '🤔',
            'ALTERNATIVES_AVAILABLE': '✅',
            'NOT_NEEDED': '✅'
        }
        st.markdown(f"{surgery_icons.get(surgery_status, '🤔')} **{surgery_status.replace('_', ' ').title()}**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Consultation Advice
        st.markdown('<div class="action-card">', unsafe_allow_html=True)
        st.markdown("### 👨‍⚕️ Who Should You Consult?")
        st.write(result.get('consultation_advice', 'Consult a general physician first'))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Warning Signs
        st.markdown('<div class="action-card">', unsafe_allow_html=True)
        st.markdown("### ⚠️ Warning Signs (Go to ER if you experience)")
        for sign in result.get('warning_signs', []):
            st.markdown(f"- 🚨 {sign}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Action Steps
        st.markdown('<div class="action-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Recommended Action Steps")
        for i, step in enumerate(result.get('action_steps', []), 1):
            st.markdown(f"**{i}.** {step}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Alternative Treatments
        if result.get('alternative_treatments'):
            st.markdown('<div class="action-card">', unsafe_allow_html=True)
            st.markdown("### 🌿 Alternative Treatment Options")
            for alt in result.get('alternative_treatments', []):
                st.markdown(f"- {alt}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Questions for Doctor
    st.markdown('<div class="action-card">', unsafe_allow_html=True)
    st.markdown("### ❓ Important Questions to Ask Your Doctor")
    questions = result.get('questions_for_doctor', [])
    for i, question in enumerate(questions, 1):
        st.markdown(f"**Q{i}:** {question}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Lifestyle Changes
    if result.get('lifestyle_changes'):
        st.markdown('<div class="action-card">', unsafe_allow_html=True)
        st.markdown("### 🏃 Lifestyle Changes That May Help")
        for change in result.get('lifestyle_changes', []):
            st.markdown(f"- ✅ {change}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recovery Time
    if result.get('estimated_recovery_time'):
        st.info(f"⏱️ **Estimated Recovery Time:** {result.get('estimated_recovery_time')}")
    
    # Key Message
    st.success(f"💚 **Key Message:** {result.get('key_message', 'Always prioritize your health and consult qualified medical professionals.')}")

def main():
    # Header
    st.markdown('<h1 class="main-header">🏥 MedWise AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your Medical Awareness Companion - Make Informed Healthcare Decisions</p>', unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown('<div class="disclaimer">', unsafe_allow_html=True)
    st.markdown("""
    **⚠️ IMPORTANT MEDICAL DISCLAIMER**
    
    MedWise AI is an **educational tool only** and NOT a substitute for professional medical advice, diagnosis, or treatment. 
    
    - Always seek the advice of qualified healthcare providers
    - Never disregard professional medical advice or delay seeking it
    - If you think you have a medical emergency, call emergency services immediately
    - This AI analysis is for awareness purposes only
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📱 About MedWise AI")
        st.write("""
        MedWise AI helps you understand your medical condition better before making decisions about surgery or treatment.
        
        **What We Do:**
        - Analyze your symptoms or medical reports
        - Provide risk assessment
        - Suggest when to seek immediate care
        - Offer questions to ask your doctor
        - Explain alternatives to surgery
        
        **What We DON'T Do:**
        - Replace your doctor
        - Provide definitive diagnosis
        - Prescribe medication
        - Guarantee medical outcomes
        """)
        
        st.markdown("---")
        st.markdown("### 🌐 Language Support")
        language = st.selectbox(
            "Select Language",
            ["English", "हिंदी (Hindi)", "தமிழ் (Tamil)", "తెలుగు (Telugu)", "বাংলা (Bengali)"],
            help="More languages coming soon!"
        )
        
        st.markdown("---")
        st.markdown("### 🆘 Emergency Numbers")
        st.markdown("""
        - **Emergency:** 112
        - **Ambulance:** 102
        - **Medical Helpline:** 108
        """)
    
    # Main Content
    st.markdown("## 📋 Tell Us About Your Condition")
    
    # Input Method Selection
    input_method = st.radio(
        "How would you like to share your information?",
        ["📝 Type Your Symptoms/Condition", "📄 Upload Medical Report (Coming Soon)"],
        help="Choose the most convenient way to share your medical information"
    )
    
    if input_method == "📝 Type Your Symptoms/Condition":
        st.markdown("### Describe your condition in your own words")
        st.write("Include details like: symptoms, duration, pain level, previous treatments, etc.")
        
        # Example conditions
        with st.expander("💡 See Example Descriptions"):
            st.markdown("""
            **Example 1:** "I have severe stomach pain on the right side for 3 days. Doctor said it might be appendix and suggested surgery immediately."
            
            **Example 2:** "Small hole in heart detected in my child. Doctor recommends surgery within a month. Child is active and playing normally."
            
            **Example 3:** "Cataract in left eye. Vision is blurry. Eye doctor suggested surgery. I'm 65 years old with diabetes."
            
            **Example 4:** "Tooth pain for 2 weeks. Dentist says root canal needed. Pain comes and goes."
            """)
        
        user_input = st.text_area(
            "Your Condition Description",
            height=200,
            placeholder="Example: I have been experiencing chest pain for the last 2 days, especially when breathing deeply. The doctor mentioned possible heart issues and suggested immediate surgery. I'm 45 years old with no previous heart problems...",
            help="Be as detailed as possible. Include all symptoms, duration, and what doctors have told you."
        )
        
        # Common conditions quick select
        st.markdown("#### Or select a common condition to learn more:")
        common_conditions = st.multiselect(
            "Quick Select (Optional)",
            ["Appendicitis", "Heart Hole (VSD/ASD)", "Cataract", "Gallstones", "Hernia", 
             "Kidney Stones", "Tonsillitis", "Dental Issues", "Joint Pain/Arthritis"],
            help="Select if your condition matches any of these"
        )
        
        if common_conditions:
            user_input += f"\n\nRelated conditions: {', '.join(common_conditions)}"
        
        # Analyze Button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            analyze_button = st.button("🔍 Analyze My Condition", use_container_width=True)
        
        if analyze_button:
            if not user_input or len(user_input.strip()) < 20:
                st.warning("⚠️ Please provide more details about your condition (at least 20 characters)")
            else:
                with st.spinner("🤖 AI is analyzing your condition... This may take 10-15 seconds..."):
                    model = configure_gemini()
                    result = analyze_medical_condition(user_input, model)
                    
                    if result:
                        st.session_state.analysis_complete = True
                        st.session_state.analysis_result = result
                        st.success("✅ Analysis Complete!")
    
    else:
        st.info("📄 **Upload Medical Report feature is coming soon!** For now, please use the text description option.")
    
    # Display Results
    if st.session_state.analysis_complete and st.session_state.analysis_result:
        st.markdown("---")
        st.markdown("## 📊 Your Personalized Analysis")
        display_analysis(st.session_state.analysis_result)
        
        # Download Report Button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📥 Download Analysis Report (PDF)", use_container_width=True):
                st.info("📄 PDF download feature coming soon! For now, you can screenshot this page.")
        
        # Reset Button
        if st.button("🔄 Analyze Another Condition"):
            st.session_state.analysis_complete = False
            st.session_state.analysis_result = None
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #64748b; padding: 2rem 0;'>
        <p><strong>MedWise AI</strong> - Empowering Patients with Knowledge</p>
        <p>Made with ❤️ for better healthcare decisions | © 2025</p>
        <p style='font-size: 0.8rem;'>This is an educational tool. Always consult qualified medical professionals for health decisions.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
