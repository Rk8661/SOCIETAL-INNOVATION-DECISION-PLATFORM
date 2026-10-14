import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Command Center | SIH26043", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

API_URL_BASE = "http://127.0.0.1:8000/api/v1/submissions"
API_URL_DOSSIERS = f"{API_URL_BASE}/dossiers"

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}

    .stApp { background: radial-gradient(circle at top left, #0f172a 0%, #0b1120 45%, #05070d 100%); }
    .block-container { padding-top: 1.5rem; max-width: 1300px; }

    /* ---------- Header ---------- */
    .cc-badge { display: inline-block; padding: 0.3rem 0.9rem; border-radius: 999px; background: rgba(31, 162, 255, 0.12); border: 1px solid rgba(31, 162, 255, 0.35); color: #7dd3fc; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.6rem; }
    .cc-title { background: linear-gradient(90deg, #1fa2ff, #12d8fa, #a6ffcb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 2.2rem; font-weight: 800; margin: 0; }
    .cc-subtitle { color: #94a3b8; font-size: 1rem; margin-top: 0.3rem; }

    /* ---------- KPI cards ---------- */
    div[data-testid="stMetric"] { background: rgba(255, 255, 255, 0.035); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 1rem 1.1rem; box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25); }
    div[data-testid="stMetricLabel"] { color: #94a3b8; } div[data-testid="stMetricValue"] { color: #f1f5f9; }

    /* ---------- Section headers ---------- */
    h3, h4 { color: #e2e8f0 !important; }

    /* ---------- Chart containers ---------- */
    div[data-testid="stPlotlyChart"] { background: rgba(255, 255, 255, 0.035); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 0.6rem; }

    /* ---------- Dossier cards ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] { background: rgba(255, 255, 255, 0.035) !important; border: 1px solid rgba(255, 255, 255, 0.08) !important; border-radius: 14px !important; transition: border-color 0.15s ease, transform 0.15s ease; }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: rgba(31, 162, 255, 0.4) !important; }

    /* ---------- Buttons ---------- */
    .stButton button { background: rgba(31, 162, 255, 0.12); border: 1px solid rgba(31, 162, 255, 0.4); color: #7dd3fc; border-radius: 8px; font-weight: 600; }
    .stButton button:hover { background: linear-gradient(90deg, #1fa2ff, #12d8fa); color: #05070d; border: 1px solid transparent; }

    /* ---------- Priority chips ---------- */
    .chip { display: inline-block; padding: 0.15rem 0.6rem; border-radius: 999px; font-size: 0.78rem; font-weight: 700; }
    .chip-high { background: rgba(255, 75, 75, 0.15); color: #ff6b6b; border: 1px solid rgba(255, 75, 75, 0.4); }
    .chip-medium { background: rgba(255, 164, 33, 0.15); color: #ffb84d; border: 1px solid rgba(255, 164, 33, 0.4); }
    .chip-low { background: rgba(9, 171, 59, 0.15); color: #4ade80; border: 1px solid rgba(9, 171, 59, 0.4); }

    .dossier-meta { color: #94a3b8; font-size: 0.85rem; } .dossier-meta b { color: #cbd5e1; }
    .report-card { background: rgba(0,0,0,0.2); border-left: 3px solid #1fa2ff; padding: 1rem; margin-bottom: 1rem; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

if "selected_dossier" not in st.session_state:
    st.session_state.selected_dossier = None

@st.cache_data(ttl=5)
def fetch_dossiers():
    try:
        response = requests.get(API_URL_DOSSIERS)
        return response.json() if response.status_code == 200 else []
    except Exception:
        return []

def change_status(dossier_id, new_status):
    requests.patch(f"{API_URL_DOSSIERS}/{dossier_id}/status", json={"status": new_status})
    st.session_state.selected_dossier = None
    fetch_dossiers.clear()
    st.rerun()

# ---------------------------------------------------------------------------
# VIEW 1: MAIN DASHBOARD
# ---------------------------------------------------------------------------
if st.session_state.selected_dossier is None:
    col_header1, col_header2 = st.columns([4, 1])
    with col_header1:
        st.markdown('<span class="cc-badge">SIH26043 &nbsp;•&nbsp; Live Operations</span>', unsafe_allow_html=True)
        st.markdown('<h1 class="cc-title">🏛️ Regional Command Center</h1>', unsafe_allow_html=True)
        st.markdown('<p class="cc-subtitle">Monitor and manage AI-clustered societal challenges in real time.</p>', unsafe_allow_html=True)
    with col_header2:
        st.page_link("pages/2_Citizen_Portal.py", label="Citizen Portal", icon="📢")
        st.page_link("pages/3_University_Portal.py", label="Academic Portal", icon="🎓")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", use_container_width=True):
            fetch_dossiers.clear()

    st.markdown("<br>", unsafe_allow_html=True)
    dossiers = fetch_dossiers()

    # Split the data into Active vs Processed
    active_dossiers = [d for d in dossiers if d.get("status") in ["PROCESSING", "READY_FOR_REVIEW"]]
    processed_dossiers = [d for d in dossiers if d.get("status") not in ["PROCESSING", "READY_FOR_REVIEW"]]

    # Create Tabs
    tab1, tab2 = st.tabs(["📥 Inbox (Requires Action)", "🗄️ Processed History"])

    # --- TAB 1: ACTIVE INBOX ---
    with tab1:
        if not active_dossiers:
            st.info("🎉 Inbox Zero! No active dossiers available for review.")
        else:
            df = pd.DataFrame(active_dossiers)

            # KPIs
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Pending Reviews", len(df))
            k2.metric("🚨 High Priority", len(df[df["priority"] == "High"]))
            k3.metric("⚠️ Medium Priority", len(df[df["priority"] == "Medium"]))
            k4.metric("✅ Low Priority", len(df[df["priority"] == "Low"]))

            st.markdown("<br>", unsafe_allow_html=True)

            # Charts
            st.subheader("📊 Active Queue Overview")
            chart_col1, chart_col2 = st.columns(2)
            plot_template = "plotly_dark"

            with chart_col1:
                fig_priority = px.pie(
                    df, names="priority", title="Queue by Priority", hole=0.55,
                    color="priority", color_discrete_map={"High": "#ff4b4b", "Medium": "#ffa421", "Low": "#09ab3b"},
                    template=plot_template,
                )
                fig_priority.update_traces(textfont_size=13, marker=dict(line=dict(color="#0b1120", width=2)))
                fig_priority.update_layout(margin=dict(t=50, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h", y=-0.1))
                st.plotly_chart(fig_priority, use_container_width=True)

            with chart_col2:
                domain_counts = df["domain"].value_counts().reset_index()
                domain_counts.columns = ["Domain", "Count"]
                fig_domain = px.bar(
                    domain_counts, x="Count", y="Domain", orientation="h", title="Queue by Domain",
                    color="Domain", template=plot_template, color_discrete_sequence=px.colors.sequential.Teal,
                )
                fig_domain.update_layout(showlegend=False, margin=dict(t=50, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_domain, use_container_width=True)

            st.divider()

            # --- ANOMALY ALERT ENGINE ---

            anomalies = [d for d in active_dossiers if d.get("anomaly") and d["anomaly"]["is_anomaly"]]

            if anomalies:
                for a in anomalies:
                    anom = a["anomaly"]

                    # Bulletproof HTML string: Zero empty lines and zero indentation inside the quotes
                    html_content = f"""<div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.5); padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; border-left: 6px solid #ef4444;">
<h3 style="color: #f87171; margin-top: 0;">🚨 POTENTIAL ANOMALY DETECTED</h3>
<p style="color: #e2e8f0; font-size: 1.1rem;"><b>Dossier:</b> {a['title']} &nbsp;|&nbsp; <b>Location:</b> {a['district']} ({a['pincode']})</p>
<div style="display: flex; gap: 2rem; margin-top: 1rem; margin-bottom: 1rem;">
<div><span style="color: #94a3b8; font-size: 0.85rem; text-transform: uppercase;">Reports in 24h</span><br><span style="color: #ffffff; font-size: 1.5rem; font-weight: 800;">{anom['reports_24h']}</span></div>
<div><span style="color: #94a3b8; font-size: 0.85rem; text-transform: uppercase;">Historical Baseline</span><br><span style="color: #ffffff; font-size: 1.5rem; font-weight: 800;">{anom['baseline_24h']} / 24h</span></div>
<div><span style="color: #94a3b8; font-size: 0.85rem; text-transform: uppercase;">Detection Spike</span><br><span style="color: #f87171; font-size: 1.5rem; font-weight: 800;">{anom['spike_multiplier']}x</span></div>
<div><span style="color: #94a3b8; font-size: 0.85rem; text-transform: uppercase;">Temporal Signal</span><br><span style="color: #f87171; font-size: 1.2rem; font-weight: 800;">{anom['temporal_signal']}</span></div>
<div><span style="color: #94a3b8; font-size: 0.85rem; text-transform: uppercase;">Geo-Concentration</span><br><span style="color: #f87171; font-size: 1.2rem; font-weight: 800;">{anom['geographic_concentration']}</span></div>
</div>
<p style="color: #fca5a5; font-weight: 700; margin-bottom: 0;">Recommendation: Immediate administrative review</p>
</div>"""
                    st.markdown(html_content, unsafe_allow_html=True)

                    if st.button("Review Anomaly →", key=f"btn_anom_{a['dossier_id']}", type="primary"):
                        st.session_state.selected_dossier = a['dossier_id']
                        st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)
                st.divider()

            # --- STANDARD QUEUE ---
            st.subheader("🗂️ Actionable Intelligence")
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            df = df.assign(_order=df["priority"].map(priority_order)).sort_values("_order")

            for _, d in df.iterrows():
                chip_class = f"chip-{d['priority'].lower()}"
                emoji = "🚨" if d['priority'] == "High" else "⚠️" if d['priority'] == "Medium" else "✅"

                with st.container(border=True):
                    st.markdown(f"#### {emoji} {d['title']}")
                    st.markdown(
                        f'<span class="chip {chip_class}">{d["priority"].upper()}</span>'
                        f'&nbsp;&nbsp;<span class="dossier-meta">Dossier ID: <b>{d["dossier_id"]}</b></span>'
                        f'&nbsp;&nbsp;|&nbsp;&nbsp;<span class="dossier-meta">Reports Merged: <b>{d["report_count"]}</b></span>'
                        f'&nbsp;&nbsp;|&nbsp;&nbsp;<span class="dossier-meta">📍 <b>{d["district"].title()} ({d["pincode"]})</b></span>',
                        unsafe_allow_html=True,
                    )

                    st.markdown("<br>", unsafe_allow_html=True)
                    c5, c6 = st.columns([3, 1])
                    c5.markdown(f'<span class="dossier-meta">🧭 Classification: <b>{d["domain"].title()} ➔ {d["subdomain"].title()}</b></span>', unsafe_allow_html=True)

                    with c6:
                        if st.button("Review Dossier →", key=f"btn_active_{d['dossier_id']}", use_container_width=True):
                            st.session_state.selected_dossier = d['dossier_id']
                            st.rerun()

    # --- TAB 2: PROCESSED HISTORY & ALLOCATIONS ---
    with tab2:
        if not processed_dossiers:
            st.info("No dossiers have been processed yet.")
        else:
            for d in processed_dossiers:
                with st.container(border=True):
                    if d['status'] == "VALIDATED":
                        status_color = "#3b82f6"
                        display_status = "PUBLISHED TO UNIVERSITIES"
                    elif d['status'] == "PROPOSALS_RECEIVED":
                        status_color = "#a855f7"
                        display_status = "UNIVERSITY PROPOSALS RECEIVED"
                    elif d['status'] == "ALLOCATED":
                        status_color = "#10b981"
                        display_status = "PROJECT ALLOCATED"
                    else:
                        status_color = "#64748b"
                        display_status = d['status'].replace("_", " ")

                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"#### {d['title']}")
                        st.markdown(
                            f'<span class="chip" style="border: 1px solid {status_color}; color: {status_color}; background: transparent;">{display_status}</span>'
                            f'&nbsp;&nbsp;<span class="dossier-meta">Dossier ID: <b>{d["dossier_id"]}</b></span>'
                            f'&nbsp;&nbsp;|&nbsp;&nbsp;<span class="dossier-meta">📍 <b>{d["district"].title()}</b></span>',
                            unsafe_allow_html=True,
                        )

                    with c2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if d['status'] == "PROPOSALS_RECEIVED":
                            if st.button("Award Project", key=f"award_{d['dossier_id']}", use_container_width=True):
                                change_status(d['dossier_id'], "ALLOCATED")
                        else:
                            if st.button("View Details", key=f"btn_hist_{d['dossier_id']}", use_container_width=True):
                                st.session_state.selected_dossier = d['dossier_id']
                                st.rerun()

# ---------------------------------------------------------------------------
# VIEW 2: DOSSIER DEEP DIVE
# ---------------------------------------------------------------------------
else:
    dossier_id = st.session_state.selected_dossier

    if st.button("⬅ Back to Dashboard"):
        st.session_state.selected_dossier = None
        st.rerun()

    try:
        dossier = requests.get(f"{API_URL_DOSSIERS}/{dossier_id}").json()

        st.markdown(f"<h1 class='cc-title'>{dossier['title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p class='dossier-meta'>Dossier ID: {dossier['dossier_id']} | Status: <b>{dossier['status']}</b></p>", unsafe_allow_html=True)
        st.divider()

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### AI Classification")
            st.markdown(f"**Domain:** {dossier['domain'].title()} <br> **Subdomain:** {dossier['subdomain'].title()} <br> **Priority:** {dossier['priority']}", unsafe_allow_html=True)
        with col2:
            st.markdown("### Location")
            st.markdown(f"**District:** {dossier['district'].title()} <br> **Pincode:** {dossier['pincode']}", unsafe_allow_html=True)

        st.divider()

        # --- INNOVATION MEMORY: Contextual Intervention ---
        st.markdown("### 🧠 Innovation Memory Search")

        if dossier.get("contextual_intervention"):
            ctx = dossier["contextual_intervention"]
            decision = ctx["decision"]

            if decision == "REUSE":
                bg_color = "rgba(52, 211, 153, 0.15)"
                border_color = "rgba(52, 211, 153, 0.5)"
                text_color = "#34d399"
                icon = "♻️"
            elif decision == "ADAPT":
                bg_color = "rgba(250, 204, 21, 0.15)"
                border_color = "rgba(250, 204, 21, 0.5)"
                text_color = "#facc15"
                icon = "🔧"
            else:  # INVENT
                bg_color = "rgba(168, 85, 247, 0.15)"
                border_color = "rgba(168, 85, 247, 0.5)"
                text_color = "#c084fc"
                icon = "💡"

            st.markdown(f"""
            <div style="background: {bg_color}; border: 1px solid {border_color}; padding: 1.2rem; border-radius: 12px; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="color: {text_color}; font-size: 1.2rem; font-weight: 800; letter-spacing: 0.05em;">{icon} RECOMMENDATION: {decision}</span>
                    <span style="color: {text_color}; font-size: 1.2rem; font-weight: 800;">{ctx['match_score']}% Match</span>
                </div>
                <p style="color: #e2e8f0; margin-bottom: 0.5rem;"><b>Reference:</b> {ctx['reference_project'] or 'No relevant past projects found.'}</p>
                <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 0;"><b>Reasoning:</b> {ctx['reason']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        st.markdown(f"### Community Evidence ({dossier['report_count']} merged reports)")
        for idx, report in enumerate(dossier['reports']):
            try:
                date_str = datetime.fromisoformat(report['created_at']).strftime("%Y-%m-%d %H:%M")
            except Exception:
                date_str = report['created_at']

            st.markdown(
                f"<div class='report-card'>"
                f"<span style='color:#94a3b8; font-size:0.8rem;'>Report #{idx+1} &nbsp;|&nbsp; {date_str}</span><br>"
                f"<span style='color:#e2e8f0;'>\"{report['text']}\"</span>"
                f"</div>",
                unsafe_allow_html=True
            )

        st.divider()

        if dossier['status'] in ["READY_FOR_REVIEW", "PROCESSING"]:
            st.markdown("### Government Validation")
            action_col1, action_col2, action_col3 = st.columns(3)
            with action_col1:
                if st.button("✅ Validate Challenge", use_container_width=True, type="primary"):
                    change_status(dossier_id, "VALIDATED")
            with action_col2:
                if st.button("↩ Needs Clarification", use_container_width=True):
                    change_status(dossier_id, "NEEDS_CLARIFICATION")
            with action_col3:
                if st.button("❌ Reject", use_container_width=True):
                    change_status(dossier_id, "REJECTED")

    except Exception as e:
        st.error(f"Failed to load dossier details. Make sure your FastAPI backend is running. Error: {e}")