# MedWise AI - Medical Awareness Platform

A web-based platform that helps patients understand their medical conditions and make informed decisions about surgeries and treatments.

## Overview

MedWise AI addresses the critical issue of rushed medical decisions that often lead to unnecessary surgeries and patient trauma. By providing AI-powered analysis in simple language, we empower patients to ask the right questions and explore all available options before proceeding with invasive treatments.

## Features

- **Symptom Analysis** - Describe your condition in plain language
- **Risk Assessment** - Get clear LOW/MEDIUM/HIGH risk evaluation
- **Surgery Necessity Check** - Understand if surgery is truly required
- **Plain Language Explanations** - Medical information without jargon
- **Doctor Questions** - Prepared questions to ask your physician
- **Alternative Options** - Explore non-surgical treatment possibilities
- **Emergency Detection** - Identifies conditions requiring immediate care
- **Multi-language Support** - English, Hindi, Tamil, Telugu, Bengali

## Technology Stack

- **Frontend:** Streamlit
- **AI Engine:** Google Gemini 1.5 Flash
- **Language:** Python 3.9+
- **Deployment:** Streamlit Community Cloud

## Installation

### Prerequisites
- Python 3.9 or higher
- Google Gemini API key

### Local Setup

1. Clone the repository


2. Install dependencies

3. Create `.streamlit/secrets.toml` and add your API key

4. Run the application

5. Open browser and navigate to `http://localhost:8501`

## Deployment on Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" and connect your repository
4. Add your Gemini API key in the Secrets section
5. Deploy

## Use Cases

This platform helps in scenarios such as:

- Patients advised for immediate appendix surgery who might benefit from antibiotic treatment first
- Parents of children with small heart holes (VSD) who are pressured for surgery when many close naturally
- Elderly patients with cataracts being told surgery is urgent when it can often wait
- Dental patients recommended extractions who could explore root canal alternatives

## Disclaimer

**IMPORTANT:** MedWise AI is an educational tool only. It does NOT:
- Provide medical diagnosis
- Replace professional medical advice
- Prescribe treatments
- Guarantee medical outcomes

Always consult licensed medical professionals for health-related decisions. In case of emergency, call emergency services immediately.

## Emergency Contacts (India)

- Emergency: 112
- Ambulance: 102
- Medical Helpline: 108

## Roadmap

- [x] Text-based condition analysis
- [x] Risk assessment system
- [x] Emergency detection
- [ ] PDF medical report upload
- [ ] OCR for scanned documents
- [ ] Full multi-language AI responses
- [ ] Doctor directory integration
- [ ] Treatment cost estimator
- [ ] Patient community forum

## Contributing

Contributions are welcome. This project aims to improve healthcare accessibility and patient awareness.

## License

MIT License

## Contact

For questions or suggestions, please open an issue on GitHub.

---

**Developed to prevent unnecessary medical trauma and empower informed healthcare decisions**
