import streamlit as st
import pandas as pd
import plotly.express as px
import json

# ================= CONFIG =================
st.set_page_config(
    page_title="PolicyPulse AI | Multi-Scheme Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= STYLING =================
def apply_custom_design():
    # Removed the buggy selectbox CSS to fix the sidebar gap
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; }
        
        /* Metric Cards */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 20px; 
            border-radius: 15px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        [data-testid="stMetric"] label { color: #94a3b8 !important; font-weight: bold; }
        
        /* Sidebar */
        [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 { color: #2dd4bf !important; font-size: 1.8rem !important; }
        section[data-testid="stSidebar"] label p { color: #f8fafc !important; font-size: 1.1rem !important; font-weight: 600;}
        
        /* Tabs */
        .stTabs [data-baseweb="tab"] { height: 50px; background-color: transparent; color: #94a3b8; font-size: 1.1rem; }
        .stTabs [aria-selected="true"] { color: #2dd4bf !important; border-bottom-color: #2dd4bf !important; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

# ================= FUNCTIONS =================
@st.cache_data
def load_and_prep_data():
    try:
        df = pd.read_csv("governance_master_final.csv")
        # Calculate Utilization (Capped at 100% for visual sanity if data has slight errors)
        df["Utilization"] = ((df["Funds_Spent"] / (df["Funds_Allocated"] + 1e-8)) * 100).round(2)
        df["Utilization"] = df["Utilization"].apply(lambda x: min(x, 100.0))
        return df
    except:
        return pd.DataFrame()

def generate_ai_policy_brief(state_row, scheme):
    """Simulates an AI engine analyzing the state's performance"""
    utilization = state_row['Utilization']
    allocated = state_row['Funds_Allocated']
    
    brief = f"**🤖 AI Automated Policy Brief for {state_row['State']} ({scheme})**\n\n"
    
    # Logic 1: Utilization
    if utilization < 60:
        brief += f"🔴 **Critical Alert:** Fund utilization is severely low at **{utilization}%**. Recommend immediate audit of administrative bottlenecks delaying fund disbursement.\n"
    elif utilization < 85:
        brief += f"🟠 **Optimization Opportunity:** Moderate utilization (**{utilization}%**). Streamlining beneficiary verification could accelerate the remaining ₹{(allocated - state_row['Funds_Spent']):,.0f} Cr deployment.\n"
    else:
        brief += f"🟢 **High Efficiency:** Excellent utilization (**{utilization}%**). State is ready for Phase 2 expansion or budget increments.\n"
        
    # Logic 2: Scale
    if state_row['Beneficiaries'] > 1000000:
        brief += f"📈 **Massive Scale:** Managing over **{state_row['Beneficiaries']:,.0f}** beneficiaries indicates robust digital infrastructure. Model can be exported to struggling states.\n"
    else:
        brief += f"🎯 **Targeted Reach:** Current reach is **{state_row['Beneficiaries']:,.0f}** beneficiaries. Recommend local awareness campaigns to increase scheme penetration.\n"
        
    # Logic 3: Scheme Specific Context
    if scheme == "Ayushman Bharat":
        insurance_cov = state_row.get('Insurance_Coverage_Percent', 0)
        brief += f"🏥 **Socio-Economic Context:** NFHS-5 data shows general health insurance coverage is at **{insurance_cov}%**. Ayushman Bharat is critical to bridge this gap."
    elif scheme == "PM Awas Yojana":
        brief += f"🏠 **Infrastructure Impact:** Rapid house completion directly correlates with local employment generation and rural economic upliftment."
        
    return brief

# ================= MAIN APP =================
def main():
    apply_custom_design()
    df = load_and_prep_data()

    if df.empty:
        st.error("❌ Master Data not found. Please ensure 'governance_master_final.csv' is in the folder.")
        return

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚡ PolicyPulse AI")
        st.markdown("<p style='color:#94a3b8; font-size:1.2rem;'>Multi-Scheme Governance Intelligence Platform</p>", unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1141/1141971.png", width=70)
    st.sidebar.title("System Control")
    
    selected_scheme = st.sidebar.selectbox("📂 Select Scheme", df["Scheme"].unique())
    
    # 1. Filter by Scheme
    scheme_df = df[df["Scheme"] == selected_scheme].copy() 
    
    # 2. 🔥 THE ULTIMATE GEOJSON MATCH FIX 🔥
    scheme_df['State'] = scheme_df['State'].replace({
        "Jammu and Kashmir": "Jammu & Kashmir",
        "Andaman & Nicobar Islands": "Andaman & Nicobar Island",
        "Dadra & Nagar Haveli and Daman & Diu": "Daman & Diu"
    })
    
    # 3. Target State Selection
    selected_state = st.sidebar.selectbox("🎯 Target State", sorted(scheme_df["State"].unique()))
    state_row = scheme_df[scheme_df["State"] == selected_state].iloc[0]

    # --- AUTOMATION: ONE-CLICK REPORT GENERATOR ---
    st.sidebar.divider() # Using native divider to prevent layout bugs
    st.sidebar.markdown("### 📄 Automated Reporting")
    
    # Added .strip() to clean up stray newlines that stretch the UI
    clean_brief = generate_ai_policy_brief(state_row, selected_scheme).replace('**', '').replace('🤖 AI Automated Policy Brief for ', '').strip()
    
    report_content = f"""
GOVERNMENT INTELLIGENCE REPORT
==============================
Scheme: {selected_scheme}
State: {selected_state}

FINANCIAL OVERVIEW:
- Allocated Budget: Rs. {state_row['Funds_Allocated']:,.2f} Cr
- Funds Utilized: Rs. {state_row['Funds_Spent']:,.2f} Cr
- Utilization Rate: {state_row['Utilization']}%

IMPACT METRICS:
- Total Beneficiaries Reached: {state_row['Beneficiaries']:,.0f}

AI DIAGNOSTIC BRIEF:
{clean_brief}

*Generated autonomously by PolicyPulse AI Engine*
"""
    
    # 2. COLORFUL HTML version for the Sidebar Display
    if state_row['Utilization'] < 60:
        status_color = "#ef4444" # Red
    elif state_row['Utilization'] < 85:
        status_color = "#f59e0b" # Orange
    else:
        status_color = "#10b981" # Green

    # BULLETPROOF HTML STRING
    colored_display = (
        f'<div style="background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border-left: 5px solid {status_color}; margin-bottom: 15px;">'
        f'<h4 style="color: #3b82f6; margin-top: 0;">{selected_state} Intelligence Brief</h4>'
        f'<p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 5px;"><b>Budget:</b> ₹{state_row["Funds_Allocated"]:,.0f} Cr</p>'
        f'<p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 10px;"><b>Utilized:</b> <span style="color: {status_color}; font-weight: bold;">{state_row["Utilization"]}%</span></p>'
        f'<hr style="border-color: rgba(255,255,255,0.1); margin: 10px 0;">'
        f'<p style="color: #f8fafc; font-size: 0.85rem; font-style: italic; margin-bottom: 0;">{clean_brief}</p>'
        f'</div>'
    )
    
    st.sidebar.markdown(colored_display, unsafe_allow_html=True)
    
    st.sidebar.download_button(
        label="📥 Download Full Text Report",
        data=report_content,
        file_name=f"{selected_state}_{selected_scheme}_Report.txt",
        mime="text/plain"
    )

    # 📌 KPI SECTION
    st.write("---")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(f"{selected_scheme} Beneficiaries", f"{state_row['Beneficiaries']:,.0f}", selected_state)
    k2.metric("Fund Utilization", f"{state_row['Utilization']:.1f}%", "Financial Health")
    k3.metric("Funds Allocated", f"₹{state_row['Funds_Allocated']:,.0f} Cr", "Total Budget")
    k4.metric("Funds Spent", f"₹{state_row['Funds_Spent']:,.0f} Cr", "Deployed")

    # TABS
    tab_map, tab_analytics, tab_comparison, tab_predictive = st.tabs(["🗺️ Geo-Intelligence", "🧠 AI Policy Engine", "📈 Cross-Scheme Analytics", "🔮 Predictive Analytics"])

    with tab_map:
        st.markdown(f"### 📍 National Utilization Heatmap: {selected_scheme}")
        try:
            with open("states_india.geojson") as f:
                india_geo = json.load(f)
            
            # Smart Tooltip Map
            fig_map = px.choropleth(
                scheme_df,
                geojson=india_geo,
                locations="State",
                featureidkey="properties.st_nm",
                color="Utilization",
                color_continuous_scale="Viridis",
                hover_name="State",
                hover_data={
                    "State": False,
                    "Beneficiaries": ":,",
                    "Funds_Allocated": ":,.1f",
                    "Funds_Spent": ":,.1f",
                    "Utilization": ":.1f%"
                },
                labels={"Funds_Allocated": "Budget (Cr)", "Funds_Spent": "Spent (Cr)"},
                template="plotly_dark"
            )
            fig_map.update_geos(visible=False, fitbounds="locations")
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', height=600)
            st.plotly_chart(fig_map, use_container_width=True)
        except Exception as e:
            st.warning("⚠️ Upload 'states_india.geojson' to view the interactive map. Error details:")
            st.error(e)

    with tab_analytics:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("### 🔬 Diagnostic Report")
            # Generate the AI Brief
            ai_brief = generate_ai_policy_brief(state_row, selected_scheme)
            st.info(ai_brief)
            
        with c2:
            st.markdown("### 🏆 Top 5 Performing States")
            top_df = scheme_df.sort_values("Utilization", ascending=False).head(5)
            fig_bar = px.bar(top_df, x="State", y="Utilization", color="Utilization",
                         color_continuous_scale="Tealgrn", template="plotly_dark",
                         text_auto='.1f')
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab_comparison:
        st.markdown("### 📊 Macro-Economic Scheme Comparison")
        st.markdown("Evaluating budget deployment across different sectors of governance.")
        comp_df = df.groupby("Scheme").agg({"Funds_Allocated": "sum", "Funds_Spent": "sum"}).reset_index()
        fig_comp = px.bar(comp_df, x="Scheme", y=["Funds_Allocated", "Funds_Spent"], 
                          barmode="group",
                          labels={"value": "Amount (in Crores)", "variable": "Financial Status"},
                          template="plotly_dark", color_discrete_sequence=['#3b82f6', '#10b981'])
        fig_comp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_comp, use_container_width=True)

    with tab_predictive:
        st.markdown(f"### 🔮 Predictive Impact Simulator for {selected_state}")
        st.markdown("Use historical state efficiency data to forecast the impact of budget increments.")
        
        c1, c2 = st.columns([1, 1.5])
        
        with c1:
            st.markdown("#### Scenario Variables")
            # Calculate State Efficiency (Beneficiaries per Crore)
            efficiency = state_row['Beneficiaries'] / (state_row['Funds_Spent'] + 1e-8)
            
            # Slider for budget injection
            simulated_budget = st.slider(
                "Inject Additional Budget (₹ Crores)", 
                min_value=0, max_value=5000, step=100, value=500
            )
            
            # Predict new beneficiaries
            projected_new_bens = simulated_budget * efficiency
            total_projected_bens = state_row['Beneficiaries'] + projected_new_bens
            
            st.info(f"**Historical Efficiency:** {efficiency:,.0f} beneficiaries per ₹1 Crore spent.")
            
        with c2:
            st.markdown("#### Projected Policy Impact")
            
            # Show the prediction in cool metrics
            p1, p2 = st.columns(2)
            p1.metric(
                label="New Beneficiaries Reached", 
                value=f"+{projected_new_bens:,.0f}", 
                delta="Projected Growth"
            )
            p2.metric(
                label="Total Projected Reach", 
                value=f"{total_projected_bens:,.0f}", 
                delta=f"{(total_projected_bens/state_row['Beneficiaries'] - 1)*100:.1f}% Increase"
            )
            
            # Visualizing the jump
            proj_df = pd.DataFrame({
                "Status": ["Current Baseline", "Projected Future"],
                "Beneficiaries": [state_row['Beneficiaries'], total_projected_bens]
            })
            fig_proj = px.bar(
                proj_df, x="Status", y="Beneficiaries", 
                color="Status", template="plotly_dark", 
                color_discrete_sequence=['#94a3b8', '#2dd4bf'],
                text_auto='.2s'
            )
            fig_proj.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300)
            st.plotly_chart(fig_proj, use_container_width=True)

    # Footer sits cleanly at the bottom
    st.markdown("<br><hr><center style='color:#64748b;'>PolicyPulse AI Engine | Powered by data.gov.in</center>", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 