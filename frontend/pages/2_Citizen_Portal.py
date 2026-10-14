import streamlit as st
import requests

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Citizen Portal | SIH26043",
    page_icon="📢",
    layout="centered",
    initial_sidebar_state="collapsed",
)

API_URL = "http://127.0.0.1:8000/api/v1/submissions"

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Hide default Streamlit chrome for a cleaner "portal" feel */
    #MainMenu, footer, header {visibility: hidden;}

    .stApp {
        background: radial-gradient(circle at top left, #0f172a 0%, #0b1120 45%, #05070d 100%);
    }

    .block-container {
        padding-top: 1.5rem;
        max-width: 760px;
    }

    /* ---------- Header ---------- */
    .portal-header {
        text-align: center;
        margin-bottom: 1.25rem;
    }
    .portal-badge {
        display: inline-block;
        padding: 0.3rem 0.9rem;
        border-radius: 999px;
        background: rgba(31, 162, 255, 0.12);
        border: 1px solid rgba(31, 162, 255, 0.35);
        color: #7dd3fc;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.9rem;
    }
    .portal-title {
        background: linear-gradient(90deg, #1fa2ff, #12d8fa, #a6ffcb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.6rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.15;
    }
    .portal-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        max-width: 650px;
        margin: 0.8rem auto 0 auto;
        line-height: 1.5;
        text-align: center;
    }

    /* ---------- Trust strip ---------- */
    .trust-strip {
        display: flex;
        justify-content: center;
        gap: 1.6rem;
        flex-wrap: wrap;
        margin: 1.6rem 0 2rem 0;
    }
    .trust-item {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        color: #cbd5e1;
        font-size: 0.85rem;
    }

    /* ---------- Card wrapper for the form ---------- */
    .form-card {
        background: rgba(255, 255, 255, 0.035);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 1.8rem 1.8rem 0.6rem 1.8rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
        margin-bottom: 1.5rem;
    }

    .section-label {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #e2e8f0;
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 0.4rem;
    }
    .section-hint {
        color: #64748b;
        font-size: 0.82rem;
        margin-bottom: 0.8rem;
    }

    /* ---------- Inputs ---------- */
    .stTextArea textarea, .stTextInput input {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border: 1px solid #1fa2ff !important;
        box-shadow: 0 0 0 1px #1fa2ff !important;
    }

    /* ---------- Submit button ---------- */
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(90deg, #1fa2ff, #12d8fa);
        color: #05070d;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 0;
        font-size: 1.05rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(31, 162, 255, 0.35);
        color: #05070d;
    }

    .footer-note {
        text-align: center;
        color: #475569;
        font-size: 0.78rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Navigation Switch
# ---------------------------------------------------------------------------
nav_c1, nav_c2 = st.columns([3, 1])
with nav_c2:
    st.page_link("pages/1_Officer_Dashboard.py", label="Officer View", icon="🏛️")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="portal-header">
    <span class="portal-badge">SIH26043 &nbsp;•&nbsp; AI-Routed Grievance System</span>
    <h1 class="portal-title">📢 Public Grievance Portal</h1>
    <p class="portal-subtitle">
        Report civic challenges in your community. Our AI reads your report and routes it to the right department instantly — no forms to navigate, no waiting in line.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="trust-strip">
    <div class="trust-item">🔒 Secure submission</div>
    <div class="trust-item">⚡ Instant AI routing</div>
    <div class="trust-item">🏛️ Reaches the right department</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Citizen Input Form
# ---------------------------------------------------------------------------
st.markdown('<div class="form-card">', unsafe_allow_html=True)

with st.form("citizen_report_form", clear_on_submit=True):

    st.markdown('<div class="section-label">📝 What is the issue?</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-hint">Be as specific as possible — the more detail, the faster and more accurate the routing.</div>', unsafe_allow_html=True)
    description = st.text_area(
        "Describe the problem in detail",
        placeholder="Example: The main drinking water pipeline in our village has burst, and we have been without clean water for 3 days...",
        height=150,
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">📍 Location Details</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-hint">This helps us connect you with the correct regional office.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        district = st.text_input("District / City", placeholder="e.g., Ranchi")
    with col2:
        village = st.text_input("Village / Locality (Optional)", placeholder="e.g., Tamar")

    pincode = st.text_input("Pincode", placeholder="e.g., 834001")

    st.markdown("<br>", unsafe_allow_html=True)

    submitted = st.form_submit_button("🚀 Submit Report", type="primary", use_container_width=True)

    if submitted:
        if len(description.strip()) < 10:
            st.error("⚠️ Please provide a more detailed description of the issue (at least 10 characters).")
        elif not district or not pincode:
            st.error("⚠️ District and Pincode are required to route your report accurately.")
        else:
            with st.spinner("Analyzing and routing your report securely..."):
                payload = {
                    "text": description,
                    "district": district.strip(),
                    "village": village.strip() if village else None,
                    "pincode": pincode.strip(),
                }

                try:
                    response = requests.post(API_URL, json=payload)

                    if response.status_code == 200:
                        st.balloons()
                        st.success("✅ Report successfully submitted!")
                        st.info("Your report has been analyzed by the system and forwarded to the appropriate regional command center.")
                    else:
                        st.error(f"❌ Failed to submit report. Server returned: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Could not connect to the server. Is the backend running? Error: {e}")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<p class="footer-note">Your report is reviewed by an AI classification pipeline before reaching human officials. False reports may delay genuine grievances.</p>', unsafe_allow_html=True)