# ⚡ PolicyPulse AI | Multi-Scheme Corporate Governance Platform

PolicyPulse AI is a state-of-the-art corporate governance and decision-intelligence dashboard. It migrates a traditional public finance pipeline into an interactive, high-performance web experience. Combining a Vite-React frontend with a high-fidelity FastAPI backend, it provides real-time policy briefing, geographic intelligence maps, forensic integrity audits, and predictive impact simulations.

---

## 🚀 Key Features

### 1. 🗺️ Geo-Intelligence Command Center
* Interactive national choropleth mapping utilizing `states_india.geojson` for real-time visualization of scheme-level fund utilization across India.
* Dynamic tooltips showcasing beneficiaries reached, allocated budgets, spent amounts, and utilization ratios.

### 2. 🔬 AI Diagnostics Suite
* Formatted, card-based AI Diagnostics displaying automatically generated policy briefs.
* Emojis and border markers flagging critical underutilization (🔴), optimization opportunities (🟠), and peak performance (🟢).
* Real-time **Top 5 Performing States** bar charts to benchmark regional implementation models.

### 3. 📊 Cross-Scheme Analytics
* Comparative bar charts plotting allocated vs. spent budgets for major social security programs (e.g., Ayushman Bharat, MGNREGA, PM Kisan, PM Awas Yojana, Jal Jeevan Mission).
* Donut charts depicting the **National Budget Allocation Share** of active schemes.

### 4. 🔮 Predictive Impact Simulator
* Interactive sliders to model simulated budget injections.
* Dynamic calculations of projected beneficiary growth and total reach improvements based on historical state-level efficiency (reach per Crore spent).

### 5. 🛡️ Forensic Integrity Guard
* Automated statistical audits highlighting Phantom Beneficiary anomalies (extreme spending with minimal reach) and Ghost Spending (budget spent on near-zero active beneficiaries).
* Context-aware biometric, biometric KYC, and Aadhaar integration recommendation alerts.

### 6. 🤖 PulseCopilot AI Advisor
* Fully interactive **NLP Chatbot** using a **Semantic Intent Parser & Decision Tree Solver** to compute complex analytical queries on live data.
* Clean narration controls utilizing Google/Microsoft Text-to-Speech (TTS) engine.
* Suggestion pills for one-click contextual inquiries.

---

## 🛠️ Technology Stack

* **Frontend**: React (Vite), Plotly.js, Axios, Lucide React, CSS Variables (sleek corporate design system).
* **Backend**: FastAPI, Pandas, Pydantic, Uvicorn.
* **Data Sources**: CSV ledger (`governance_master_final.csv`), India Administrative GeoJSON boundary map (`states_india.geojson`).

---

## 📦 Project Directory Structure

```
DataScience/
├── backend/
│   ├── api.py                 # FastAPI Web Server & NLP Query Engine
│   └── requirements.txt       # Python Dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Charts.jsx          # Bar & Donut charts (Plotly)
│   │   │   ├── ForensicAudit.jsx   # Integrity ledger tables
│   │   │   ├── GeoMap.jsx          # Interactive Map container
│   │   │   ├── MetricsCard.jsx     # Reusable metrics component
│   │   │   ├── Predictive.jsx      # Sliders and projection charts
│   │   │   └── Sidebar.jsx         # Controls and download options
│   │   ├── App.jsx                 # Core Application layout & Chatbot
│   │   ├── index.css               # Premium CSS Tokens
│   │   └── main.jsx                # React Entrypoint
│   ├── index.html
│   ├── package.json
│   └── README.md
├── governance_master_final.csv # Live Data Ledger
├── states_india.geojson        # Administrative Map Layers
├── .gitignore                  # Global Git Exclusion File
└── README.md                   # Main Project Documentation
```

---

## ⚙️ Getting Started

### Prerequisites
* Python 3.9+
* Node.js 18+

### 1. Running the FastAPI Backend
Navigate to the `backend` directory, install requirements, and run the Uvicorn server:
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn api:app --reload
```
The backend API documentation will be available at `http://127.0.0.1:8000/docs`.

### 2. Running the React Frontend
Navigate to the `frontend` directory, install packages, and launch the Vite development server:
```bash
cd ../frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser to access the dashboard.
