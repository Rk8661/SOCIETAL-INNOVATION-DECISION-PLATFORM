import re
import streamlit as st
from utils.api_client import submit_citizen_problem

st.set_page_config(page_title="Citizen Portal", page_icon="📢")

def extract_lat_lon(url: str):
    """Extracts latitude and longitude from a standard Google Maps URL."""
    if not url:
        return None, None
    # Looks for the @latitude,longitude pattern in the URL
    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

st.title("📢 Report a Community Problem")
st.write("Describe the issue below. Your report will be processed and routed through the platform.")

# Create a form so the page doesn't reload on every keystroke
with st.form("citizen_submission_form"):
    text = st.text_area("What is the problem?", placeholder="E.g., The village well has contaminated water...")

    col1, col2, col3 = st.columns(3)
    with col1:
        district = st.text_input("District")
    with col2:
        village = st.text_input("Village / Block")
    with col3:
        pincode = st.text_input("Pincode")

    st.write("📍 Location")
    # Using the prototype location capture method for MVP
    gmaps_link = st.text_input(
        "Google Maps Link (Optional)",
        placeholder="https://www.google.com/maps/place/Dumka/@24.2683,87.2494,15z",
        help="Prototype location capture. Production will use native device GPS."
    )

    submitted = st.form_submit_button("Submit Report", type="primary")

# Handle what happens when the user clicks submit
if submitted:
    if not text.strip():
        st.error("Please describe the problem before submitting.")
    else:
        lat, lon = extract_lat_lon(gmaps_link)

        # 1. Don't silently discard an invalid Maps link
        if gmaps_link and (lat is None or lon is None):
            st.error("We couldn't read the location from this Google Maps link. Please paste a valid standard Maps link (containing @lat,lon).")
            st.stop()

        # Build the JSON payload matching our FastAPI schema
        payload = {
            "text": text,
            "district": district if district else None,
            "village": village if village else None,
            "pincode": pincode if pincode else None,
            "latitude": lat,
            "longitude": lon
        }

        try:
            # 2. More accurate status message
            with st.spinner("Submitting your report..."):
                result = submit_citizen_problem(payload)

            st.success("✅ Report successfully submitted!")
            st.info(f"**Tracking ID:** SUB-{result['id']}  \n**Status:** {result['processing_status']}")

            # 3. Safer float checking
            if lat is not None and lon is not None:
                st.caption(f"Coordinates captured: {lat}, {lon}")

        except Exception as e:
            st.error(f"Failed to connect to the backend server. Error: {e}")