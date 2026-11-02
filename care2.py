import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Medical Receipt OCR Scanner",
    page_icon="📸",
    layout="centered"
)

# --- DIRECTORY DATA (Premium Local Hospital Map) ---
DOCTOR_DIRECTORY = {
    "headache": {
        "specialty": "Neurology & Neuro-sciences",
        "doctor": "Dr. Varun Kumar Reddy",
        "hospital": "Medicover Super Specialty Hospitals",
        "location": "Near RTC Bus Stand, Kurnool, AP",
        "details": "Highly-regarded expert specializing in chronic migraine profiling and neuro-diagnostics."
    },
    "fever": {
        "specialty": "General Internal Medicine",
        "doctor": "Dr. Amala",
        "hospital": "Aarka Multispecialty Hospitals",
        "location": "Gayatri Estate, Kurnool, AP",
        "details": "Specializes in infectious clinical diseases and persistent viral pyrexia management."
    },
    "back pain": {
        "specialty": "Orthopaedics & Spine Surgery",
        "doctor": "Dr. N. Tilak Mahesh",
        "hospital": "C.N. Orthopedic Shoulder & Knee Clinic",
        "location": "Gooty Road, Shilpa Birla Compound, Kurnool, AP",
        "details": "Renowned orthopedic surgeon specializing in musculoskeletal injuries and spinal strain."
    }
}

# --- HEALTHCARE INTELLIGENCE ENGINE ---
def process_extracted_text(text_content):
    clean_text = str(text_content).lower()
    
    # Analyze text for target matching keywords
    detected_symptom = None
    if "head" in clean_text or "ache" in clean_text or "migraine" in clean_text:
        detected_symptom = "headache"
    elif "fever" in clean_text or "temp" in clean_text or "chills" in clean_text:
        detected_symptom = "fever"
    elif "back" in clean_text or "pain" in clean_text or "ortho" in clean_text:
        detected_symptom = "back pain"
        
    if detected_symptom:
        match = DOCTOR_DIRECTORY[detected_symptom]
        response = (
            f"### 🎯 AI OCR Symptom Extraction Successful!\n"
            f"**Detected Symptom from Receipt:** `{detected_symptom.upper()}`\n\n"
            f"🏥 **AI Doctor Referral:** Based on clinical department matching for **{match['specialty']}**, we have mapped your case to a premium local medical provider:\n"
            f"- **Recommended Specialist:** **{match['doctor']}**\n"
            f"- **Hospital/Facility:** **{match['hospital']}**\n"
            f"- **Location Address:** 📍 {match['location']}\n"
            f"- **Medical Focus:** {match['details']}\n\n"
            f"📋 *Action Item: Show this reference panel at the hospital registration desk to bypass the general assessment queue.*"
        )
        return response
    else:
        return (
            f"### 📋 OCR Scan Completed\n"
            f"⚠️ **Result:** We scanned the document text but could not identify explicit matching keyword references for *headache*, *fever*, or *back pain*.\n\n"
            f"🩺 **AI Direction:** Please visit a triage desk or consult a **General Physician** for an official manual diagnosis script evaluation."
        )

# --- USER INTERFACE DESIGN ---
st.title("📸 AI Medical Receipt OCR Chatbot")
st.markdown("Upload or drop an image of an old medical receipt, bill, or prescription slip below. Our system will extract the clinical parameters and route you to the appropriate specialist facility.")

if "ocr_messages" not in st.session_state:
    st.session_state.ocr_messages = [
        {"role": "assistant", "content": "Hello! I am your AI Medical Scanner. Please upload an image of your previous hospital receipt or document below, and I will instantly analyze it to route you to the correct specialist."}
    ]

# Display history logs
for message in st.session_state.ocr_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- UI CONTROL PANEL (File Upload Element) ---
st.markdown("---")
uploaded_file = st.file_uploader("📁 Choose a medical receipt image (PNG, JPG, JPEG)...", type=["png", "jpg", "jpeg"])

# Backup TextInput Option in case user doesn't have local system Tesseract setup running
manual_text = st.text_area("✍️ Backup Option: If you don't have an image, paste your receipt text here instead:")

if st.button("🚀 Process & Analyze Document", type="primary"):
    extracted_text = ""
    
    # Route 1: Handle Image OCR Scanning
    if uploaded_file is not None:
        try:
            with st.spinner("Analyzing document layers via OCR..."):
                img = Image.open(uploaded_file)
                extracted_text = pytesseract.image_to_string(img)
                
                # Show text snippet to user inside chat block
                with st.chat_message("user"):
                    st.image(img, caption="Uploaded Document Snapshot", width=250)
                    st.markdown(f"**[System Parsed Text]:** \n```text\n{extracted_text[:300]}...\n```")
                st.session_state.ocr_messages.append({"role": "user", "content": f"Uploaded receipt image. OCR text found: {extracted_text[:100]}..."})
        except Exception as e:
            st.warning("⚠️ Local OCR engine not fully initialized. Switching seamlessly to manual input processing mode.")
            
    # Route 2: Handle Manual Text Area Input if Image is blank/errored
    if not extracted_text.strip() and manual_text.strip():
        extracted_text = manual_text
        with st.chat_message("user"):
            st.markdown(f"**Submitted Prescription Text:**\n*{extracted_text}*")
        st.session_state.ocr_messages.append({"role": "user", "content": extracted_text})
        
    # Process findings if any text was collected
    if extracted_text.strip():
        bot_reply = process_extracted_text(extracted_text)
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
        st.session_state.ocr_messages.append({"role": "assistant", "content": bot_reply})
    else:
        st.error("Please upload a valid receipt image file or fill out the text block space first before executing calculations.")

st.markdown("---")
st.caption("⚠️ **Medical Disclaimer:** This system provides automated document parsing and mock administrative reference data based on user input. It does not replace professional emergency clinical oversight or manual visual inspections by licensed practitioners.")
