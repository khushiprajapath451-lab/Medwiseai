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

# Custom CSS
# Custom CSS
st.markdown("""
<style>
 /* Main app background - light blue */
.stApp {
    background-color: #cde6f7;
}

/* Main content area - light blue, black text */
.main {
    background-color: #cde6f7;
    padding: 2rem;
    color: #000000;
}

/* Ensure ALL text below header is black */
.main, .main * {
    color: #000000 !important;
}

.main p, .main span, .main div, .main li {
    color: #000000 !important;
}

.main h1 {
    color: #000000 !important;
}
.main h2, .main h3, .main h4, .main h5, .main h6 {
    color: #03045E !important;
}

.main strong, .main b {
    color: #000000 !important;
}

/* Sidebar background - blue gradient, white text */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #03045E 0%, #0077B6 100%);
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* Header and subheader styling - blue gradient, black text */
.main-header, .sub-header {
    color: #000000 !important;
    background: linear-gradient(135deg, #03045E, #0077B6);
    padding: 2rem;
    border-radius: 1rem 1rem 0 0;
    font-weight: 700;
    text-align: center;
}

/* Remove disclaimer box if present */
.disclaimer-box {
    display: none !important;
}

/* Remove backgrounds, borders, shadows from output sections */
.info-card, .risk-high, .risk-medium, .risk-low, .emergency-alert {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    color: #000000 !important; /* Ensure output text is black */
}

/* Output headings in dark blue for contrast */
.risk-high h2, .risk-medium h2, .risk-low h2,
.info-card h3, .emergency-alert h3 {
    color: #03045E !important;
}

/* Buttons with blue gradient, white text */
.stButton>button {
    background: linear-gradient(135deg, #03045E, #0077B6);
    color: #ffffff !important;
    font-weight: 600;
    padding: 0.75rem 2rem;
    border-radius: 0.75rem;
    border: none !important;
    width: 100%;
    box-shadow: none !important;
    transition: all 0.3s;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #0077B6, #03045E);
}

/* Text input areas - white background, blue border, black text */
.stTextArea textarea {
    border: 2px solid #0077B6;
    border-radius: 0.5rem;
    background-color: #ffffff;
    color: #000000 !important;
}
.stTextArea textarea::placeholder {
    color: #999999;
}
.stTextArea textarea:focus {
    border-color: #03045E;
    box-shadow: 0 0 0 3px rgba(3, 4, 94, 0.3);
}
.stTextArea label {
    color: #000000 !important;
}

/* Expander styling */
.streamlit-expanderHeader {
    background: transparent !important;
    border: 1px solid #0077B6;
    color: #000000 !important;
    border-radius: 0.5rem;
}

/* Multiselect tags - dark blue background with white text */
.stMultiSelect [data-baseweb="tag"] {
    background-color: #03045E !important;
    color: #ffffff !important;
}
.stMultiSelect label {
    color: #000000 !important;
}

/* Horizontal line - blue */
.main hr {
    border: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #03045E, transparent);
    margin: 2rem 0;
}

/* Footer text in black */
.main div[style*="text-align: center"] p {
    color: #000000 !important;
}



</style>
""", unsafe_allow_html=True)










# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

def configure_gemini():
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            st.error("API key not found. Please add GEMINI_API_KEY to your Streamlit secrets.")
            st.stop()

        genai.configure(api_key=api_key)

        models = genai.list_models()
        st.write("Available models:", [model.name for model in models])

        # Select a generative model by name pattern
        for model_obj in models:
            model_name = model_obj.name
            if ('flash' in model_name or 'pro' in model_name) and 'gemini' in model_name:
                st.info(f"Using model: {model_name}")
                return genai.GenerativeModel(model_name)
        
        # Fallback: use a hardcoded model from your earlier list
        fallback_model = 'gemini-2.5-flash'
        st.info(f"Using fallback model: {fallback_model}")
        return genai.GenerativeModel(fallback_model)

    except Exception as e:
        st.error(f"Error configuring Gemini: {str(e)}")
        st.error("Please create a NEW API key at: https://aistudio.google.com/app/apikey")
        st.stop()


    
def n_response(text):
    """Clean JSON response from Gemini"""
    # Remove markdown code blocks
    text = text.strip()
    
    # Check for json code block
    if "json" in text[:20].lower():
        # Find first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
    
    return text

def clean_json_response(text):
    """Clean JSON response from Gemini"""
    text = text.strip()
    if "json" in text[:20].lower():
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
    return text


def analyze_medical_condition(user_input, model):
    # ... your existing code ...

    prompt = """You are a medical awareness assistant helping patients understand their health conditions better. 

    User's condition description: """ + user_input + """

    Provide a comprehensive analysis in the following JSON format:

    {
        "risk_level": "LOW/MEDIUM/HIGH",
        ...
    }
    ... rest of prompt ...
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )

        raw_text = response.text
        st.text_area("Raw AI Response (for debugging)", raw_text, height=200)

        response_text = clean_json_response(raw_text)
        result = json.loads(response_text)
        return result
    except json.JSONDecodeError as e:
        st.error("Error parsing AI response. Please try again.")
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
    risk_class = "risk-" + risk_level.lower()
    
    st.markdown('<div class="' + risk_class + '">', unsafe_allow_html=True)
    st.markdown("## Risk Assessment: " + risk_level)
    st.markdown("**Urgency Level:** " + result.get('urgency', 'Not determined'))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Condition Name
    st.markdown("### Likely Condition: " + result.get('condition_name', 'Assessment in progress'))
    
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
        st.markdown("**Status:** " + surgery_status.replace('_', ' ').title())
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
            st.markdown("- " + sign)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Action Steps
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### Recommended Action Steps")
        action_steps = result.get('action_steps', [])
        for i, step in enumerate(action_steps, 1):
            st.markdown("**" + str(i) + ".** " + step)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Alternative Treatments
        if result.get('alternative_treatments'):
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("### Alternative Treatment Options")
            alternatives = result.get('alternative_treatments', [])
            for alt in alternatives:
                st.markdown("- " + alt)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Questions for Doctor
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### Important Questions to Ask Your Doctor")
    questions = result.get('questions_for_doctor', [])
    for i, question in enumerate(questions, 1):
        st.markdown("**Question " + str(i) + ":** " + question)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Lifestyle Changes
    if result.get('lifestyle_changes'):
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### Recommended Lifestyle Changes")
        lifestyle = result.get('lifestyle_changes', [])
        for change in lifestyle:
            st.markdown("- " + change)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recovery Time
    if result.get('estimated_recovery_time'):
        st.info("**Estimated Recovery Time:** " + result.get('estimated_recovery_time'))
    
    # Key Message
    key_msg = result.get('key_message', 'Always prioritize consulting qualified medical professionals for proper diagnosis and treatment.')
    st.success("**Key Takeaway:** " + key_msg)

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
            ["English", "Hindi", "Tamil", "Telugu", "Bengali"]
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
        st.write("Please provide details about your symptoms, duration, severity, and any diagnosis you have received.")
        
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
            ["Appendicitis", "Heart Conditions", "Cataract", "Gallstones", 
             "Hernia", "Kidney Stones", "Tonsillitis", "Dental Problems", "Joint Pain"]
        )
        
        if common_conditions:
            user_input = user_input + "\n\nRelated conditions: " + ", ".join(common_conditions)
        
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



