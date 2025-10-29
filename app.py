import streamlit as st
import json
from datetime import datetime
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="MedWise AI - Medical Awareness Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (unchanged, omitted here for brevity, include your CSS block here)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

def configure_gemini():
    """Configure Gemini API with supported model."""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            st.error("API key not found. Please add GEMINI_API_KEY to your secrets.")
            st.stop()

        genai.configure(api_key=api_key)

        # List available models to verify supported model names
        # model_list = genai.list_models()
        # st.write(model_list)  # Optional for debugging

        # Use a supported model, e.g., 'gemini-1.0-pro-vision-001'
        model_name = 'gemini-1.0-pro-vision-001'
        model = genai.GenerativeModel(model_name)
        return model

    except Exception as e:
        st.error(f"Error configuring Gemini: {str(e)}")
        st.stop()

def clean_json_response(text):
    """Clean JSON response from Gemini."""
    text = text.strip()
    # Check for JSON code block
    if "json" in text[:20].lower():
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
    return text

def analyze_medical_condition(user_input, model):
    """Analyze medical condition with Gemini AI."""
    prompt = """You are a medical awareness assistant helping patients understand their health conditions better. 

User's condition description: """ + user_input + """

Provide a comprehensive analysis in the following JSON format:

{
    "risk_level": "LOW/MEDIUM/HIGH",
    "urgency": "EMERGENCY/URGENT/CAN_WAIT/NON_URGENT",
    "condition_name": "Name of the likely condition",
    "simple_explanation": "Explain the condition in simple, easy-to-understand language",
    "is_emergency": true/false,
    "surgery_needed": "LIKELY_NEEDED/MAYBE_NEEDED/ALTERNATIVES_AVAILABLE/NOT_NEEDED",
    "consultation_advice": "Type of specialist to consult and when",
    "action_steps": [
        "Step 1",
        "Step 2",
        "Step 3",
        "Step 4"
    ],
    "questions_for_doctor": [
        "Question 1",
        "Question 2",
        "Question 3",
        "Question 4"
    ],
    "alternative_treatments": [
        "Alternative 1",
        "Alternative 2",
        "Alternative 3"
    ],
    "warning_signs": [
        "Sign 1 that requires immediate attention",
        "Sign 2",
        "Sign 3"
    ],
    "lifestyle_changes": [
        "Change 1",
        "Change 2",
        "Change 3"
    ],
    "estimated_recovery_time": "Recovery timeline if treatment is pursued",
    "key_message": "One important message for the patient"
}

Important guidelines:
- Be conservative in risk assessment
- Use simple language
- If emergency, mark clearly
- Always encourage professional medical consultation
- Provide balanced view of surgery vs alternatives
- Be empathetic and supportive"""

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
        )
        response_text = clean_json_response(response.text)
        result = json.loads(response_text)
        return result
    except json.JSONDecodeError:
        st.error("Could not parse the AI response. Please try again.")
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
    return None

def display_analysis(result):
    """Display the analysis results in a clean, professional format."""
    if not result:
        return

    # Emergency Alert
    if result.get('is_emergency', False):
        st.markdown('<div class="emergency-alert">', unsafe_allow_html=True)
        st.markdown("### EMERGENCY DETECTED")
        st.markdown("""**This may require immediate medical attention. Please:**<br>
        - Call emergency services (108 / 112)<br>
        - Go to the nearest hospital emergency room<br>
        - Do not delay seeking immediate care""")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
    # Risk level
    risk_level = result.get('risk_level', 'MEDIUM')
    risk_class = "risk-" + risk_level.lower()

    st.markdown('<div class="' + risk_class + '">', unsafe_allow_html=True)
    st.markdown("## Risk Assessment: " + risk_level)
    st.markdown("**Urgency Level:** " + result.get('urgency', 'Not determined'))
    st.markdown('</div>', unsafe_allow_html=True)

    # Condition name
    st.markdown("### Likely Condition: " + result.get('condition_name', 'Assessment in progress'))

    # Understanding
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### Understanding Your Condition")
    st.write(result.get('simple_explanation', 'Please consult a medical professional for detailed diagnosis.'))
    st.markdown('</div>', unsafe_allow_html=True)

    # Two columns for detailed info
    col1, col2 = st.columns(2)
    with col1:
        # Surgery assessment
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### Surgery Assessment")
        surgery_status = result.get('surgery_needed', 'MAYBE_NEEDED')
        st.markdown("**Status:** " + surgery_status.replace('_', ' ').title())
        st.markdown('</div>')

        # Consultation advice
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### Recommended Consultation")
        st.write(result.get('consultation_advice', 'Consult a general physician for initial evaluation'))
        st.markdown('</div>')

        # Warning signs
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### Warning Signs (Seek Immediate Care)")
        for sign in result.get('warning_signs', []):
            st.markdown("- " + sign)
        st.markdown('</div>')

    with col2:
        # Action steps
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### Recommended Action Steps")
        for i, step in enumerate(result.get('action_steps', []), 1):
            st.markdown(f"**{i}.** {step}")
        st.markdown('</div>')

        # Alternatives
        if result.get('alternative_treatments'):
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("### Alternative Treatment Options")
            for alt in result.get('alternative_treatments', []):
                st.markdown("- " + alt)
            st.markdown('</div>')

    # Questions for doctor
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### Important Questions to Ask Your Doctor")
    for i, question in enumerate(result.get('questions_for_doctor', []), 1):
        st.markdown(f"**Question {i}:** {question}")
    st.markdown('</div>')

    # Lifestyle changes
    if result.get('lifestyle_changes'):
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### Recommended Lifestyle Changes")
        for change in result.get('lifestyle_changes', []):
            st.markdown("- " + change)
        st.markdown('</div>')

    # Recovery time
    if result.get('estimated_recovery_time'):
        st.info("**Estimated Recovery Time:** " + result.get('estimated_recovery_time'))

    # Key message
    key_msg = result.get('key_message', 'Always prioritize consulting qualified medical professionals for proper diagnosis and treatment.')
    st.success("**Key Takeaway:** " + key_msg)

def main():
    # Header
    st.markdown('<h1 class="main-header">MedWise AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Medical Awareness Platform - Make Informed Healthcare Decisions</p>', unsafe_allow_html=True)
    # Disclaimer
    st.markdown('<div class="disclaimer-box">', unsafe_allow_html=True)
    st.markdown("""**IMPORTANT MEDICAL DISCLAIMER**<br>
    MedWise AI is an educational tool and NOT a substitute for professional medical advice, diagnosis, or treatment.<br>
    - Always consult qualified healthcare providers for medical decisions<br>
    - Never disregard professional medical advice<br>
    - Call emergency services immediately if you have a medical emergency<br>
    - This analysis is for informational and awareness purposes only""")
    st.markdown('</div>', unsafe_allow_html=True)

    # Sidebar content omitted for brevity — use your existing code

    # Main Content: Input, Analysis, Output
    # ... (your existing code)

if __name__ == "__main__":
    main()


