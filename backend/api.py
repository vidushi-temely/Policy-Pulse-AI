import os
import json
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="PolicyPulse AI API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base Path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "governance_master_final.csv")
GEOJSON_PATH = os.path.join(BASE_DIR, "states_india.geojson")

def load_and_prep_data():
    try:
        df = pd.read_csv(CSV_PATH)
        # Calculate Utilization (Capped at 100% for visual sanity if data has slight errors)
        df["Utilization"] = ((df["Funds_Spent"] / (df["Funds_Allocated"] + 1e-8)) * 100).round(2)
        df["Utilization"] = df["Utilization"].apply(lambda x: min(x, 100.0))
        
        # GEOJSON MATCH FIX
        df['State'] = df['State'].replace({
            "Jammu and Kashmir": "Jammu & Kashmir",
            "Andaman & Nicobar Islands": "Andaman & Nicobar Island",
            "Dadra & Nagar Haveli and Daman & Diu": "Daman & Diu"
        })
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return pd.DataFrame()

df = load_and_prep_data()

class ChatRequest(BaseModel):
    message: str

class OptimizeRequest(BaseModel):
    scheme: str
    additional_budget: float

def generate_ai_policy_brief(state_row, scheme):
    """Simulates an AI engine analyzing the state's performance"""
    utilization = float(state_row['Utilization'])
    allocated = float(state_row['Funds_Allocated'])
    spent = float(state_row['Funds_Spent'])
    beneficiaries = float(state_row['Beneficiaries'])
    state_name = str(state_row['State'])
    
    brief = f"**🤖 AI Automated Policy Brief for {state_name} ({scheme})**\n\n"
    
    # Logic 1: Utilization
    if utilization < 60:
        brief += f"🔴 **Critical Alert:** Fund utilization is severely low at **{utilization}%**. Recommend immediate audit of administrative bottlenecks delaying fund disbursement.\n"
    elif utilization < 85:
        brief += f"🟠 **Optimization Opportunity:** Moderate utilization (**{utilization}%**). Streamlining beneficiary verification could accelerate the remaining ₹{(allocated - spent):,.0f} Cr deployment.\n"
    else:
        brief += f"🟢 **High Efficiency:** Excellent utilization (**{utilization}%**). State is ready for Phase 2 expansion or budget increments.\n"
        
    # Logic 2: Scale
    if beneficiaries > 1000000:
        brief += f"📈 **Massive Scale:** Managing over **{beneficiaries:,.0f}** beneficiaries indicates robust digital infrastructure. Model can be exported to struggling states.\n"
    else:
        brief += f"🎯 **Targeted Reach:** Current reach is **{beneficiaries:,.0f}** beneficiaries. Recommend local awareness campaigns to increase scheme penetration.\n"
        
    # Logic 3: Scheme Specific Context
    if scheme == "Ayushman Bharat":
        insurance_cov = float(state_row.get('Insurance_Coverage_Percent', 0))
        brief += f"🏥 **Socio-Economic Context:** NFHS-5 data shows general health insurance coverage is at **{insurance_cov}%**. Ayushman Bharat is critical to bridge this gap."
    elif scheme == "PM Awas Yojana":
        brief += f"🏠 **Infrastructure Impact:** Rapid house completion directly correlates with local employment generation and rural economic upliftment."
    elif scheme == "PM Kisan":
        brief += f"🌾 **Agricultural Support:** Direct Income Support under PM Kisan provides safety nets and capital liquidity for small and marginal farmers."
    elif scheme == "Jal Jeevan Mission":
        brief += f"💧 **Clean Water Impact:** Safe drinking water tap connections drastically reduce water-borne illnesses and improve rural public health."
    elif scheme == "MGNREGA":
        brief += f"👷 **Rural Employment Guarantee:** Providing guaranteed wage employment is a powerful social safety net and supports sustainable local asset creation."
        
    return brief

def run_integrity_audit(scheme: str):
    scheme_df = df[df["Scheme"] == scheme].copy()
    if scheme_df.empty:
        return {
            "scheme": scheme,
            "national_median_cost_per_beneficiary_rupees": 0.0,
            "state_risks": [],
            "findings": []
        }
        
    # Cost per beneficiary (spent * 10,000,000 / beneficiaries)
    scheme_df["cost_per_ben"] = (scheme_df["Funds_Spent"] * 1e7) / (scheme_df["Beneficiaries"] + 1e-8)
    
    valid_records = scheme_df[(scheme_df["Funds_Spent"] > 0.5) & (scheme_df["Beneficiaries"] > 10)]
    if not valid_records.empty:
        median_cost = float(valid_records["cost_per_ben"].median())
    else:
        median_cost = 5000.0
        
    state_risks = []
    findings = []
    
    for _, row in scheme_df.iterrows():
        state_name = row["State"]
        spent = float(row["Funds_Spent"])
        allocated = float(row["Funds_Allocated"])
        bens = int(row["Beneficiaries"])
        cost_per_ben = float(row["cost_per_ben"])
        
        risk_score = 8.0
        anomaly_type = "Standard Integrity Signature"
        
        # 1. Phantom Beneficiary Check (extreme cost per beneficiary relative to national median)
        if spent > 2.0 and bens > 0:
            inflation = cost_per_ben / (median_cost + 1e-8)
            if inflation > 3.0:
                risk_score += 65.0
                anomaly_type = "Extreme Cost Discrepancy"
                findings.append({
                    "type": "danger",
                    "state": state_name,
                    "title": "Severe Phantom Beneficiary Risk",
                    "description": f"State spent ₹{spent:.2f} Cr but reached only {bens:,} citizens. Cost per citizen is ₹{cost_per_ben:,.0f}, which is {inflation:.1f}x higher than the national median of ₹{median_cost:,.0f}.",
                    "remedy": "Bypass intermediate state departments using automated Direct Benefit Transfer (DBT) channels."
                })
            elif inflation > 1.8:
                risk_score += 35.0
                anomaly_type = "Elevated Reach Deficit"
                findings.append({
                    "type": "warning",
                    "state": state_name,
                    "title": "Suspicious Spending Deficit",
                    "description": f"State operational expenditure equals ₹{cost_per_ben:,.0f} per verified citizen, which is {inflation:.1f}x the national median baseline.",
                    "remedy": "Enforce mandatory biometric e-KYC claimant verification."
                })
                
        # 2. Ghost Spending Check (Non-zero spending, near zero reach)
        if spent > 5.0 and bens < 10:
            risk_score += 75.0
            anomaly_type = "Ghost Spending"
            findings.append({
                "type": "danger",
                "state": state_name,
                "title": "Critical Ghost Disbursal Alert",
                "description": f"State has disbursed ₹{spent:.2f} Cr but recorded only {bens} active beneficiaries, indicating high potential for paper projects and phantom contractors.",
                "remedy": "Suspend active central pipelines and mandate geo-tagged drone photographic audits of physical assets."
            })
            
        # 3. Reporting Inflation Check (Ayushman Bharat specific NFHS discrepancy)
        if scheme == "Ayushman Bharat" and bens > 100000:
            coverage = float(row.get("Insurance_Coverage_Percent", 0))
            if coverage < 18.0:
                risk_score += 45.0
                anomaly_type = "Reporting Discrepancy Profile"
                findings.append({
                    "type": "warning",
                    "state": state_name,
                    "title": "Reporting Discrepancy Flagged",
                    "description": f"State claims over {bens:,} active Ayushman Bharat beneficiaries, but independent NFHS-5 surveys show general health coverage is under {coverage}%.",
                    "remedy": "Verify registries against central tax registries to clear ghost duplicate records."
                })
                
        risk_score = min(risk_score, 100.0)
        category = "Low"
        if risk_score > 60:
            category = "High"
        elif risk_score > 30:
            category = "Medium"
            
        state_risks.append({
            "state": state_name,
            "risk_score": round(risk_score, 1),
            "category": category,
            "spending_per_ben_rupees": round(cost_per_ben, 0),
            "anomaly_type": anomaly_type
        })
        
    state_risks = sorted(state_risks, key=lambda x: x["risk_score"], reverse=True)
    
    return {
        "scheme": scheme,
        "national_median_cost_per_beneficiary_rupees": round(median_cost, 0),
        "state_risks": state_risks,
        "findings": findings
    }

@app.get("/api/schemes")
def get_schemes():
    if df.empty:
        raise HTTPException(status_code=500, detail="Data not available")
    return {"schemes": df["Scheme"].unique().tolist()}

@app.get("/api/states")
def get_states(scheme: str):
    if df.empty:
        raise HTTPException(status_code=500, detail="Data not available")
    scheme_df = df[df["Scheme"] == scheme]
    if scheme_df.empty:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return {"states": sorted(scheme_df["State"].unique().tolist())}

@app.get("/api/data")
def get_data(scheme: str, state: str):
    if df.empty:
        raise HTTPException(status_code=500, detail="Data not available")
    
    scheme_df = df[df["Scheme"] == scheme]
    state_data = scheme_df[scheme_df["State"] == state]
    
    if state_data.empty:
        raise HTTPException(status_code=404, detail="Data not found for scheme and state")
        
    row = state_data.iloc[0]
    brief = generate_ai_policy_brief(row, scheme)
    
    clean_brief = brief.replace('**', '').replace('🤖 AI Automated Policy Brief for ', '').strip()
    
    return {
        "scheme": scheme,
        "state": state,
        "metrics": {
            "beneficiaries": int(row["Beneficiaries"]),
            "utilization": float(row["Utilization"]),
            "funds_allocated": float(row["Funds_Allocated"]),
            "funds_spent": float(row["Funds_Spent"])
        },
        "ai_brief": brief,
        "clean_brief": clean_brief
    }

@app.get("/api/map-data")
def get_map_data(scheme: str):
    if df.empty:
        raise HTTPException(status_code=500, detail="Data not available")
    scheme_df = df[df["Scheme"] == scheme]
    return scheme_df.to_dict(orient="records")

@app.get("/api/geojson")
def get_geojson():
    if not os.path.exists(GEOJSON_PATH):
        raise HTTPException(status_code=404, detail="GeoJSON not found")
    with open(GEOJSON_PATH, "r") as f:
        return json.load(f)

@app.get("/api/analytics/top-states")
def get_top_states(scheme: str):
    scheme_df = df[df["Scheme"] == scheme]
    top_df = scheme_df.sort_values("Utilization", ascending=False).head(5)
    return top_df[["State", "Utilization"]].to_dict(orient="records")

@app.get("/api/analytics/comparison")
def get_comparison():
    comp_df = df.groupby("Scheme").agg({"Funds_Allocated": "sum", "Funds_Spent": "sum"}).reset_index()
    return comp_df.to_dict(orient="records")

@app.get("/api/predictive")
def get_predictive(scheme: str, state: str, additional_budget: float):
    scheme_df = df[df["Scheme"] == scheme]
    state_data = scheme_df[scheme_df["State"] == state]
    
    if state_data.empty:
        raise HTTPException(status_code=404, detail="Data not found")
        
    row = state_data.iloc[0]
    efficiency = row['Beneficiaries'] / (row['Funds_Spent'] + 1e-8)
    
    projected_new_bens = additional_budget * efficiency
    total_projected_bens = row['Beneficiaries'] + projected_new_bens
    
    return {
        "efficiency": efficiency,
        "additional_budget": additional_budget,
        "projected_new_beneficiaries": projected_new_bens,
        "total_projected_beneficiaries": total_projected_bens,
        "current_beneficiaries": row['Beneficiaries']
    }

@app.get("/api/ai/alerts")
def get_ai_alerts():
    if df.empty:
        raise HTTPException(status_code=500, detail="Data not available")
    
    alerts = []
    
    # 1. Underutilization Alert
    underutilized = df[(df["Utilization"] < 50.0) & (df["Funds_Allocated"] > 20.0)]
    for _, row in underutilized.iterrows():
        alerts.append({
            "type": "warning",
            "title": "Severe Budget Underutilization",
            "message": f"{row['State']} has spent only {row['Utilization']}% of its ₹{row['Funds_Allocated']:.1f} Cr budget for {row['Scheme']}.",
            "state": row["State"],
            "scheme": row["Scheme"],
            "metric": "utilization",
            "value": f"{row['Utilization']}%"
        })
        
    # 2. Over-budget Stress Alert
    overspent = df[df["Funds_Spent"] > (df["Funds_Allocated"] * 1.15)]
    for _, row in overspent.iterrows():
        if row["Funds_Allocated"] > 1.0:
            alerts.append({
                "type": "danger",
                "title": "Financial Stress / High Demand",
                "message": f"{row['State']} has spent ₹{row['Funds_Spent']:.1f} Cr, exceeding its allocated budget of ₹{row['Funds_Allocated']:.1f} Cr for {row['Scheme']}.",
                "state": row["State"],
                "scheme": row["Scheme"],
                "metric": "overspend",
                "value": f"+{((row['Funds_Spent']/row['Funds_Allocated'] - 1)*100):.0f}%"
            })
            
    # 3. Efficiency Champion
    df_eff = df[df["Funds_Spent"] > 5.0].copy()
    df_eff["efficiency"] = df_eff["Beneficiaries"] / df_eff["Funds_Spent"]
    top_eff = df_eff[df_eff["Utilization"] > 90.0].sort_values("efficiency", ascending=False).head(5)
    for _, row in top_eff.iterrows():
        alerts.append({
            "type": "success",
            "title": "High-Efficiency Governance Model",
            "message": f"{row['State']} achieved high efficiency under {row['Scheme']}, reaching {int(row['Beneficiaries']):,} citizens with {row['Utilization']}% utilization.",
            "state": row["State"],
            "scheme": row["Scheme"],
            "metric": "efficiency",
            "value": "Top Performer"
        })

    priority = {"danger": 0, "warning": 1, "success": 2}
    alerts = sorted(alerts, key=lambda x: priority.get(x["type"], 3))
    
    return {"alerts": alerts[:12]}

@app.get("/api/integrity/audit")
def get_integrity_audit(scheme: str):
    if df.empty:
        raise HTTPException(status_code=500, detail="Data not available")
    return run_integrity_audit(scheme)

@app.post("/api/ai/chat")
def post_ai_chat(request: ChatRequest):
    if df.empty:
        raise HTTPException(status_code=500, detail="Data not available")
        
    user_msg = request.message.lower()
    
    # 1. ENTITY EXTRACTION
    found_states = []
    all_states = df["State"].unique()
    for s in all_states:
        if s.lower() in user_msg:
            found_states.append(s)
            
    found_schemes = []
    all_schemes = df["Scheme"].unique()
    for sch in all_schemes:
        if sch.lower() in user_msg:
            found_schemes.append(sch)
            
    # 2. SEMANTIC INTENT PARSER
    wants_utilization = any(w in user_msg for w in ["utiliz", "percent", "disburs", "speed", "fast", "slow", "deploy"])
    wants_budget = any(w in user_msg for w in ["budget", "allocat", "fund", "money", "grant", "rupee", "cr"])
    wants_spent = any(w in user_msg for w in ["spent", "spend", "expend", "outflow"])
    wants_reach = any(w in user_msg for w in ["reach", "beneficiar", "people", "citizen", "outreach", "impact", "target"])
    wants_efficiency = any(w in user_msg for w in ["efficien", "perform", "ratio", "per cr", "output"])
    wants_cost = any(w in user_msg for w in ["cost per", "cost of", "expenditure per", "average cost"])
    wants_leakage = any(w in user_msg for w in ["leakage", "corruption", "ghost", "phantom", "fraud", "integrity", "red flag", "audit"])
    
    is_best = any(w in user_msg for w in ["best", "top", "highest", "leader", "champion", "max", "most", "highest"])
    is_worst = any(w in user_msg for w in ["worst", "lowest", "lagging", "struggl", "fail", "min", "least", "bottleneck"])
    is_compare = any(w in user_msg for w in ["compare", "vs", "versus", "difference", "differ", "contrast"])
    is_average = any(w in user_msg for w in ["average", "mean", "median", "overall"])
    is_list = any(w in user_msg for w in ["list", "show", "rank", "give me", "display"])

    response_text = ""
    
    # 3. CONTEXT FILTERING
    if found_states and found_schemes:
        sub_df = df[df["State"].isin(found_states) & df["Scheme"].isin(found_schemes)]
        scope_desc = f"for **{', '.join(found_states)}** under **{', '.join(found_schemes)}**"
    elif found_states:
        sub_df = df[df["State"].isin(found_states)]
        scope_desc = f"across all schemes in **{', '.join(found_states)}**"
    elif found_schemes:
        sub_df = df[df["Scheme"].isin(found_schemes)]
        scope_desc = f"nationally under **{', '.join(found_schemes)}**"
    else:
        sub_df = df.copy()
        scope_desc = "across the entire national ledger"

    if sub_df.empty:
        active_schemes = df["Scheme"].unique().tolist()
        return {
            "reply": (
                f"### 🔍 Context Search Completed\n\n"
                f"I searched the active ledger for your specified combination but found no matching entries.\n"
                f"**Active Schemes in DB:** {', '.join(active_schemes)}\n"
                f"Please refine your query with these active names!"
            )
        }

    # 4. DECISION TREE RESOLVER
    
    # CASE 1: Comparison between multiple states or schemes
    if is_compare or len(found_states) > 1 or len(found_schemes) > 1:
        response_text = f"### 📊 Live Comparative Intelligence Report\n\nAnalyzed metrics {scope_desc}:\n\n"
        
        if len(found_schemes) > 1:
            comp_grp = sub_df.groupby("Scheme").agg({
                "Funds_Allocated": "sum",
                "Funds_Spent": "sum",
                "Beneficiaries": "sum"
            }).reset_index()
            comp_grp["Utilization"] = (comp_grp["Funds_Spent"] / (comp_grp["Funds_Allocated"] + 1e-8)) * 100
            
            for _, row in comp_grp.iterrows():
                response_text += (
                    f"- **{row['Scheme']}**:\n"
                    f"  - Financial Status: ₹{row['Funds_Allocated']:,.1f} Cr Allocated | ₹{row['Funds_Spent']:,.1f} Cr Spent (**{row['Utilization']:.1f}% Utilized**)\n"
                    f"  - Citizen Outreach: **{int(row['Beneficiaries']):,}** citizens reached\n"
                )
            best_row = comp_grp.sort_values("Utilization", ascending=False).iloc[0]
            worst_row = comp_grp.sort_values("Utilization", ascending=True).iloc[0]
            response_text += f"\n💡 **AI Verdict:** **{best_row['Scheme']}** demonstrates higher spending speed than **{worst_row['Scheme']}**."
            
        else:
            comp_grp = sub_df.groupby("State").agg({
                "Funds_Allocated": "sum",
                "Funds_Spent": "sum",
                "Beneficiaries": "sum"
            }).reset_index()
            comp_grp["Utilization"] = (comp_grp["Funds_Spent"] / (comp_grp["Funds_Allocated"] + 1e-8)) * 100
            
            for _, row in comp_grp.iterrows():
                response_text += (
                    f"- **{row['State']}**:\n"
                    f"  - Budget Status: ₹{row['Funds_Allocated']:,.1f} Cr Allocated | ₹{row['Funds_Spent']:,.1f} Cr Spent (**{row['Utilization']:.1f}% Spent**)\n"
                    f"  - Direct Outreach: **{int(row['Beneficiaries']):,}** verified citizens\n"
                )
            best_row = comp_grp.sort_values("Utilization", ascending=False).iloc[0]
            worst_row = comp_grp.sort_values("Utilization", ascending=True).iloc[0]
            response_text += f"\n💡 **AI Verdict:** **{best_row['State']}** out-performs **{worst_row['State']}** in capital deployment speed."

    # CASE 2: Best / Top Performer Search
    elif is_best:
        sort_col = "Beneficiaries" if wants_reach else "Funds_Allocated" if wants_budget else "Funds_Spent" if wants_spent else "Utilization"
        col_desc = "outreach scale" if wants_reach else "budget allocation" if wants_budget else "funds spent" if wants_spent else "spending speed"
        
        top_row = sub_df.sort_values(sort_col, ascending=False).iloc[0]
        response_text = (
            f"### 🏆 Leaderboard Search: Top Performer\n\n"
            f"Audited active performance {scope_desc} to locate the highest {col_desc}:\n\n"
            f"- **Top Performer State:** **{top_row['State']}**\n"
            f"- **Scheme Profile:** {top_row['Scheme']}\n"
            f"- **Target Metric Value:** "
        )
        if sort_col == "Utilization":
            response_text += f"**{top_row['Utilization']}% budget utilization** (Spent: ₹{top_row['Funds_Spent']:.1f} Cr)"
        elif sort_col == "Beneficiaries":
            response_text += f"**{int(top_row['Beneficiaries']):,} beneficiaries reached**"
        else:
            response_text += f"**₹{top_row[sort_col]:,.2f} Cr**"
            
        response_text += (
            f"\n\n💡 **Best Practice Recommendation:**\n"
            f"Administrative workflows, DBT pipelines, and local procurement models in **{top_row['State']}** should be studied and scaled to other districts."
        )

    # CASE 3: Worst / Lagging Performer Search
    elif is_worst:
        sort_col = "Beneficiaries" if wants_reach else "Funds_Allocated" if wants_budget else "Funds_Spent" if wants_spent else "Utilization"
        col_desc = "outreach scale" if wants_reach else "budget allocation" if wants_budget else "funds spent" if wants_spent else "spending speed"
        
        valid_sub = sub_df[sub_df["Funds_Allocated"] > 1.0]
        if valid_sub.empty:
            valid_sub = sub_df
            
        bottom_row = valid_sub.sort_values(sort_col, ascending=True).iloc[0]
        unspent = bottom_row['Funds_Allocated'] - bottom_row['Funds_Spent']
        
        response_text = (
            f"### ⚠️ Bottleneck Sweep: Lagging Performer\n\n"
            f"Analyzed administrative bottlenecks {scope_desc} to isolate the lowest {col_desc}:\n\n"
            f"- **Lowest Performer State:** **{bottom_row['State']}**\n"
            f"- **Scheme Profile:** {bottom_row['Scheme']}\n"
            f"- **Target Metric Value:** "
        )
        if sort_col == "Utilization":
            response_text += f"**{bottom_row['Utilization']}% budget utilization** (Stalled budget: ₹{unspent:.1f} Cr)"
        elif sort_col == "Beneficiaries":
            response_text += f"**{int(bottom_row['Beneficiaries']):,} reached**"
        else:
            response_text += f"**₹{bottom_row[sort_col]:,.2f} Cr**"
            
        response_text += (
            f"\n\n🛡️ **Vigilance Action Recommendation:**\n"
            f"Deploy an administrative taskforce to **{bottom_row['State']}** to inspect billing holds, clear local disputes, and accelerate fund releases."
        )

    # CASE 4: Average / Median Aggregations
    elif is_average:
        avg_alloc = sub_df["Funds_Allocated"].mean()
        avg_spent = sub_df["Funds_Spent"].mean()
        avg_util = (sub_df["Funds_Spent"].sum() / (sub_df["Funds_Allocated"].sum() + 1e-8)) * 100
        avg_bens = sub_df["Beneficiaries"].mean()
        
        response_text = (
            f"### 📊 Aggregate Analytical Summary\n\n"
            f"Calculated average governance metrics {scope_desc}:\n\n"
            f"- **Average Allocation:** ₹{avg_alloc:,.2f} Cr\n"
            f"- **Average Expenditure:** ₹{avg_spent:,.2f} Cr\n"
            f"- **Combined Allocation Speed:** **{avg_util:.1f}% combined utilization**\n"
            f"- **Average Beneficiary Scale:** **{int(avg_bens):,}** verified citizens reached per state."
        )

    # CASE 5: Rank Listing / Top N Listing
    elif is_list:
        sort_col = "Beneficiaries" if wants_reach else "Funds_Allocated" if wants_budget else "Funds_Spent" if wants_spent else "Utilization"
        col_desc = "Outreach (Citizens)" if wants_reach else "Allocation (₹ Cr)" if wants_budget else "Expenditure (₹ Cr)" if wants_spent else "Utilization %"
        
        rank_df = sub_df.sort_values(sort_col, ascending=False).head(5)
        response_text = f"### 📋 Top 5 Performance Ledger\n\nRanking results {scope_desc} sorted by **{col_desc}**:\n\n"
        
        for idx, (_, row) in enumerate(rank_df.iterrows(), 1):
            val = f"{row['Utilization']}%" if sort_col == "Utilization" else f"{int(row['Beneficiaries']):,}" if sort_col == "Beneficiaries" else f"₹{row[sort_col]:,.2f} Cr"
            response_text += f"{idx}. **{row['State']}** - {row['Scheme']} | **{val}**\n"

    # CASE 6: Leakage & Forensic Corruption Sweep
    elif wants_leakage:
        target_scheme = found_schemes[0] if found_schemes else "Ayushman Bharat"
        audit = run_integrity_audit(target_scheme)
        high_risk_states = [s for s in audit["state_risks"] if s["risk_score"] > 50]
        
        response_text = (
            f"### 🛡️ Forensic Integrity Guard: **{target_scheme}** Audit\n\n"
            f"I have executed anomaly-detection cost audits under **{target_scheme}**:\n\n"
            f"- **National Cost Baseline:** The median operational expenditure per verified citizen is **₹{audit['national_median_cost_per_beneficiary_rupees']:,.0f}**.\n"
            f"- **System Vulnerability:** Identified **{len(high_risk_states)} outliers** with anomalous cost profiles.\n\n"
            f"**Audit Findings:**\n"
        )
        for f in audit["findings"][:3]:
            response_text += f"- **{f['state']}**: ⚠️ *{f['title']}* - {f['description']}\n  *AI Remedy:* {f['remedy']}\n\n"
            
        if not audit["findings"]:
            response_text += "✅ **Clean Scan:** No phantom beneficiary spikes or duplicate contractor patterns isolated in the database.\n\n"

        response_text += (
            f"\n💡 **AI Prevention Playbook:**\n"
            f"Transition state distribution points entirely to biometric Aadhaar verification to wipe out duplicate ghost registries."
        )

    # CASE 7: Precise Lookup (1 State, 1 Scheme)
    elif len(found_states) == 1 and len(found_schemes) == 1:
        row = sub_df.iloc[0]
        cost_per_ben = (row["Funds_Spent"] * 1e7) / (row["Beneficiaries"] + 1e-8)
        
        response_text = (
            f"### 📊 Dynamic Diagnostic: {found_states[0]} ({found_schemes[0]})\n\n"
            f"Custom audit sheet derived directly from the live database:\n\n"
            f"- **Financial Utilization:** Deployed **₹{row['Funds_Spent']:,.2f} Cr** out of **₹{row['Funds_Allocated']:,.2f} Cr** allocated (**{row['Utilization']}% utilization speed**).\n"
            f"- **Outreach Footprint:** Reached **{int(row['Beneficiaries']):,}** citizens.\n"
            f"- **Administrative Cost:** Operational cost averages **₹{cost_per_ben:,.0f}** per beneficiary.\n\n"
        )
        if row["Utilization"] < 60:
            response_text += f"⚠️ **Core Bottleneck:** Utilization is critically low. Administrative friction in releasing local matching grants is delaying ₹{(row['Funds_Allocated'] - row['Funds_Spent']):,.2f} Cr. Action: Establish direct central oversight."
        elif row["Utilization"] < 85:
            response_text += f"💡 **Optimization Option:** Moderate performance. Launching community-level outreach drives could help deploy the remaining ₹{(row['Funds_Allocated'] - row['Funds_Spent']):,.2f} Cr."
        else:
            response_text += f"✅ **Strategic Recommendation:** Flawless implementation profile! Eligible for matched expansion funding."

    # CASE 8: State Portfolio Overview (1 State)
    elif len(found_states) == 1:
        total_allocated = sub_df["Funds_Allocated"].sum()
        total_spent = sub_df["Funds_Spent"].sum()
        total_bens = sub_df["Beneficiaries"].sum()
        avg_util = (total_spent / (total_allocated + 1e-8)) * 100
        
        response_text = (
            f"### 📊 Portfolio Audit: **{found_states[0]}**\n\n"
            f"Compiled performance stats across all active schemes in **{found_states[0]}**:\n\n"
            f"- **Cumulative Funding:** ₹{total_allocated:,.2f} Cr Allocated | ₹{total_spent:,.2f} Cr Spent\n"
            f"- **Average Deployment Speed:** **{avg_util:.1f}% combined utilization**\n"
            f"- **Total Direct Impact:** Reached **{int(total_bens):,}** direct citizens.\n\n"
            f"**Sectoral Report:**\n"
        )
        for _, row in sub_df.iterrows():
            status_emoji = "🟢" if row["Utilization"] >= 85 else "🟠" if row["Utilization"] >= 60 else "🔴"
            response_text += f"- **{row['Scheme']}:** {status_emoji} {row['Utilization']}% utilized (Spent: ₹{row['Funds_Spent']:.1f} Cr | Reached: {int(row['Beneficiaries']):,})\n"
            
        best_scheme = sub_df.sort_values("Utilization", ascending=False).iloc[0]
        worst_scheme = sub_df.sort_values("Utilization", ascending=True).iloc[0]
        response_text += (
            f"\n💡 **AI Verdict for {found_states[0]}:\n"
            f"1. **Primary Success:** Replicate the speed of **{best_scheme['Scheme']}** ({best_scheme['Utilization']}% utilized).\n"
            f"2. **Primary Bottleneck:** Direct local audits toward **{worst_scheme['Scheme']}** ({worst_scheme['Utilization']}% utilized)."
        )

    # CASE 9: Scheme Portfolio Overview (1 Scheme)
    elif len(found_schemes) == 1:
        total_allocated = sub_df["Funds_Allocated"].sum()
        total_spent = sub_df["Funds_Spent"].sum()
        total_bens = sub_df["Beneficiaries"].sum()
        avg_util = (total_spent / (total_allocated + 1e-8)) * 100
        
        top_states = sub_df.sort_values("Utilization", ascending=False).head(3)
        bottom_states = sub_df.sort_values("Utilization", ascending=True).head(3)
        
        response_text = (
            f"### ⚡ Macro Scheme Intelligence: **{found_schemes[0]}**\n\n"
            f"National analytics summary for **{found_schemes[0]}** across all states:\n\n"
            f"- **Macro Budget Footprint:** Cumulative allocation of **₹{total_allocated:,.2f} Cr**, with **₹{total_spent:,.2f} Cr** spent (**{avg_util:.1f}% average utilization**).\n"
            f"- **National Citizen Scale:** Reached **{int(total_bens):,}** active beneficiaries nationwide.\n\n"
            f"**Top Performing States (Highest Utilization):**\n"
        )
        for _, row in top_states.iterrows():
            response_text += f"- **{row['State']}:** {row['Utilization']}% (₹{row['Funds_Spent']:.1f} Cr spent)\n"
            
        response_text += f"\n**Lagging States (Lowest Utilization):**\n"
        for _, row in bottom_states.iterrows():
            response_text += f"- **{row['State']}:** {row['Utilization']}% (₹{row['Funds_Spent']:.1f} Cr spent)\n"

    # FALLBACK / HELP
    else:
        active_schemes = df["Scheme"].unique().tolist()
        active_states_cnt = len(df["State"].unique())
        
        response_text = (
            f"### 🤖 PulseCopilot Dynamic Policy Advisor\n\n"
            f"I am fully compiled with the live database ledger. Since your query didn't match a specific location or scheme, here is what I can compute for you in real-time:\n\n"
            f"- **Audited Database Capacity:** Managing **{len(active_schemes)} central schemes** across **{active_states_cnt} states and UTs**.\n"
            f"- **Interactive Commands I Can Run:**\n"
            f"  - **Leaderboards:** *'Who is the best state for Jal Jeevan Mission?'*\n"
            f"  - **Leakage Sweeps:** *'Run a corruption audit on PM Kisan'* or *'Leakage in Bihar'*\n"
            f"  - **Comparisons:** *'Compare Bihar vs Maharashtra'*\n"
            f"  - **Scheme Audits:** *'Tell me about Ayushman Bharat'* or *'How is Maharashtra doing?'*\n\n"
            f"What specific audit or governance recommendation can I run for you?"
        )
        
    return {"reply": response_text}
@app.post("/api/predictive/optimize")
def post_predictive_optimize(request: OptimizeRequest):
    if df.empty:
        raise HTTPException(status_code=500, detail="Data not available")
        
    scheme_df = df[df["Scheme"] == request.scheme].copy()
    if scheme_df.empty:
        raise HTTPException(status_code=404, detail="Scheme not found")
        
    scheme_df["efficiency"] = scheme_df["Beneficiaries"] / (scheme_df["Funds_Spent"] + 1e-8)
    
    valid_states = scheme_df[scheme_df["Funds_Spent"] > 0.1].copy()
    if valid_states.empty:
        valid_states = scheme_df.copy()
        
    total_eff = valid_states["efficiency"].sum()
    if total_eff == 0:
        valid_states["weight"] = 1.0 / len(valid_states)
    else:
        valid_states["weight"] = valid_states["efficiency"] / total_eff
        
    valid_states["allocated_share"] = valid_states["weight"] * request.additional_budget
    
    cap = request.additional_budget * 0.25
    over_cap = valid_states[valid_states["allocated_share"] > 4.0] # Limit slightly
    cap_value = request.additional_budget * 0.25
    
    over_cap = valid_states[valid_states["allocated_share"] > cap_value]
    
    if not over_cap.empty:
        excess = 0.0
        for idx, row in over_cap.iterrows():
            excess += row["allocated_share"] - cap_value
            valid_states.at[idx, "allocated_share"] = cap_value
            
        remaining_states = valid_states[valid_states["allocated_share"] < cap_value]
        if not remaining_states.empty:
            rem_total_weight = remaining_states["weight"].sum()
            for idx, row in remaining_states.iterrows():
                share_of_excess = (row["weight"] / (rem_total_weight + 1e-8)) * excess
                valid_states.at[idx, "allocated_share"] += share_of_excess
                
    allocations = []
    total_projected_gain = 0.0
    for _, row in valid_states.iterrows():
        allocated = float(row["allocated_share"])
        projected_new_bens = allocated * float(row["efficiency"])
        total_projected_gain += projected_new_bens
        
        allocations.append({
            "state": row["State"],
            "current_budget": float(row["Funds_Allocated"]),
            "current_spent": float(row["Funds_Spent"]),
            "current_beneficiaries": int(row["Beneficiaries"]),
            "allocated_increment": round(allocated, 2),
            "projected_new_beneficiaries": int(projected_new_bens),
            "efficiency": float(row["efficiency"])
        })
        
    allocations = sorted(allocations, key=lambda x: x["allocated_increment"], reverse=True)
    
    return {
        "scheme": request.scheme,
        "additional_budget": request.additional_budget,
        "total_projected_new_beneficiaries": int(total_projected_gain),
        "allocations": allocations[:10]
    }
