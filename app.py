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
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e40af;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-high {
        background-color: #fee2e2;
        border-left: 5px solid #dc2626;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .risk-medium {
        background-color: #fef3c7;
        border-left: 5px solid #f59e0b;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .risk-low {
        background-color: #d1fae5;
        border-left: 5px solid #10b981;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .disclaimer-box {
        background-color: #fef2f2;
        border: 2px solid #fca5a5;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 2rem 0;
    }
    .info-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
    }
    .emergency-alert {
        background-color: #fee2e2;
        border: 3px solid #dc2626;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1.5rem 0;
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
            st.error("API key not found. Please add GEMINI_API_KEY to your Streamlit secrets.")
            st.stop()
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error configuring API: {str(e)}")
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
        response_text = response.text
        
        # Clean up response text
        if "```
            response_text = response_text.split("```json").split("```
        elif "```" in response_text:
            response_text = response_text.split("``````")[0]
        
        result = json.loads(response_text.strip())
        return result
    except json.JSONDecodeError as e:
        st.error(f"Error parsing response: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error analyzing condition: {str(e)}")
        return None

def display_analysis(result):
    """Display the analysis results in a clean, professional format"""
    
    # Emergency Alert
    if result.get('is_emergency', False):
        st.markdown('<div class="emergency-alert">', unsafe_allow_html=True)
        st.markdown("### EMERGENCY DETECTED")
        st.markdown("""
        **This may require immediate medical attention. Please:**
        - Call emergency services (108 / 112)
        - Go to the nearest hospital emergency room
        - Do not delay seeking immediate care
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
    
    # Risk Level Display
    risk_level = result.get('risk_level', 'MEDIUM')
    risk_class = f"risk-{risk_level.lower()}"
    
    st.markdown(f'<div class="{risk_class}">', unsafe_allow_html=True)
    st.markdown(f"## Risk Assessment: {risk_level}")
    st.markdown(f"**Urgency Level:** {result.get('urgency', 'Not determined')}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Condition Name
    st.markdown(f"### Likely Condition: {result.get('condition_name', 'Assessment in progress')}")
    
    # Simple Explanation
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### Understanding Your Condition")
    st.write(result.get('simple_explanation', 'Please consult a medical professional for detailed diagnosis.'))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Two Column Layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Surgery Assessment
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### Surgery Assessment")
        surgery_status = result.get('surgery_needed', 'MAYBE_NEEDED')
        st.markdown(f"**Status:** {surgery_status.replace('_', ' ').title()}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Consultation Advice
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### Recommended Consultation")
        st.write(result.get('consultation_advice', 'Consult a general physician for initial evaluation'))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Warning Signs
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### Warning Signs (Seek Immediate Care)")
        warning_signs = result.get('warning_signs', [])
        for sign in warning_signs:
            st.markdown(f"- {sign}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Action Steps
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### Recommended Action Steps")
        action_steps = result.get('action_steps', [])
        for i, step in enumerate(action_steps, 1):
            st.markdown(f"**{i}.** {step}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Alternative Treatments
        if result.get('alternative_treatments'):
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("### Alternative Treatment Options")
            alternatives = result.get('alternative_treatments', [])
            for alt in alternatives:
                st.markdown(f"- {alt}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Questions for Doctor
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### Important Questions to Ask Your Doctor")
    questions = result.get('questions_for_doctor', [])
    for i, question in enumerate(questions, 1):
        st.markdown(f"**Question {i}:** {question}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Lifestyle Changes
    if result.get('lifestyle_changes'):
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### Recommended Lifestyle Changes")
        lifestyle = result.get('lifestyle_changes', [])
        for change in lifestyle:
            st.markdown(f"- {change}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recovery Time
    if result.get('estimated_recovery_time'):
        st.info(f"**Estimated Recovery Time:** {result.get('estimated_recovery_time')}")
    
    # Key Message
    st.success(f"**Key Takeaway:** {result.get('key_message', 'Always prioritize consulting qualified medical professionals for proper diagnosis and treatment.')}")

def main():
    # Header
    st.markdown('<h1 class="main-header">MedWise AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Medical Awareness Platform - Make Informed Healthcare Decisions</p>', unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown('<div class="disclaimer-box">', unsafe_allow_html=True)
    st.markdown("""
    **IMPORTANT MEDICAL DISCLAIMER**
    
    MedWise AI is an educational tool and NOT a substitute for professional medical advice, diagnosis, or treatment.
    
    - Always consult qualified healthcare providers for medical decisions
    - Never disregard professional medical advice
    - Call emergency services immediately if you have a medical emergency
    - This analysis is for informational and awareness purposes only
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## About MedWise AI")
        st.write("""
        MedWise AI helps you understand your medical condition and make informed decisions about treatment options.
        
        **What We Provide:**
        - Risk assessment analysis
        - Treatment urgency evaluation
        - Questions to ask your doctor
        - Alternative treatment information
        - Warning signs to watch for
        
        **What We Do NOT Do:**
        - Replace medical professionals
        - Provide medical diagnosis
        - Prescribe treatments
        - Guarantee outcomes
        """)
        
        st.markdown("---")
        st.markdown("### Language Options")
        language = st.selectbox(
            "Select Language",
            ["English", "हिंदी (Hindi)", "தமிழ் (Tamil)", "తెలుగు (Telugu)", "বাংলা (Bengali)"]
        )
        
        st.markdown("---")
        st.markdown("### Emergency Contacts")
        st.markdown("""
        **India Emergency Numbers:**
        - Emergency: 112
        - Ambulance: 102
        - Medical Helpline: 108
        """)
    
    # Main Content
    st.markdown("## Share Your Medical Concern")
    
    # Input Method Selection
    input_method = st.radio(
        "Choose input method:",
        ["Type your symptoms or condition", "Upload medical report (Coming Soon)"]
    )
    
    if input_method == "Type your symptoms or condition":
        st.markdown("### Describe Your Condition")
        st.write("Please provide details about your symptoms, duration, severity, and any diagnosis you've received.")
        
        # Example conditions
        with st.expander("View example descriptions"):
            st.markdown("""
            **Example 1:** Severe stomach pain on right side for 3 days. Doctor mentioned possible appendicitis and recommended surgery. Pain is constant and gets worse with movement.
            
            **Example 2:** Small hole detected in child's heart during routine checkup. Doctor suggests surgery within a month. Child is 5 years old, active, and shows no symptoms.
            
            **Example 3:** Blurry vision in left eye diagnosed as cataract. Age 65 with diabetes. Ophthalmologist recommended surgery soon.
            
            **Example 4:** Persistent tooth pain for 2 weeks. Dentist said root canal treatment needed. Pain is intermittent and worsens with cold drinks.
            """)
        
        user_input = st.text_area(
            "Your Medical Concern",
            height=200,
            placeholder="Example: I have been experiencing chest pain for the past 2 days, especially when taking deep breaths. The doctor mentioned possible heart issues and suggested immediate surgery. I am 45 years old with no previous cardiac history. The pain is sharp and localized on the left side...",
            help="Be as detailed as possible for better analysis"
        )
        
        # Common conditions
        st.markdown("#### Select related conditions (optional):")
        common_conditions = st.multiselect(
            "Common Medical Conditions",
            ["Appendicitis", "Heart Conditions (VSD/ASD)", "Cataract", "Gallstones", 
             "Hernia", "Kidney Stones", "Tonsillitis", "Dental Problems", "Joint Pain"]
        )
        
        if common_conditions:
            user_input += f"\n\nRelated conditions: {', '.join(common_conditions)}"
        
        # Analyze Button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            analyze_button = st.button("Analyze Condition", use_container_width=True)
        
        if analyze_button:
            if not user_input or len(user_input.strip()) < 20:
                st.warning("Please provide more details about your condition (minimum 20 characters required)")
            else:
                with st.spinner("Analyzing your condition... Please wait..."):
                    model = configure_gemini()
                    result = analyze_medical_condition(user_input, model)
                    
                    if result:
                        st.session_state.analysis_complete = True
                        st.session_state.analysis_result = result
                        st.success("Analysis completed successfully")
    
    else:
        st.info("Medical report upload feature is currently under development. Please use the text description option for now.")
    
    # Display Results
    if st.session_state.analysis_complete and st.session_state.analysis_result:
        st.markdown("---")
        st.markdown("## Your Medical Analysis Report")
        display_analysis(st.session_state.analysis_result)
        
        # Action buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Download Report (PDF)", use_container_width=True):
                st.info("PDF download feature will be available soon. You can screenshot this page for now.")
        
        with col2:
            if st.button("Analyze Another Condition", use_container_width=True):
                st.session_state.analysis_complete = False
                st.session_state.analysis_result = None
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #64748b; padding: 2rem 0;'>
        <p><strong>MedWise AI</strong> - Empowering Patients Through Knowledge</p>
        <p>© 2025 MedWise AI | For Educational Purposes Only</p>
        <p style='font-size: 0.85rem; margin-top: 1rem;'>
            Always consult qualified medical professionals for health-related decisions.<br>
            This platform does not provide medical advice, diagnosis, or treatment.
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
