import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import sqlite3

# Page configuration
st.set_page_config(
    page_title="Leqembi Treatment Flowsheet",
    page_icon="💉",
    layout="wide"
)

# Initialize database
def init_db():
    conn = sqlite3.connect('leqembi_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS infusions
                 (id INTEGER PRIMARY KEY, date TEXT, weight REAL, unit TEXT, 
                  dose_mg REAL, dose_ml REAL, notes TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS mri_records
                 (id INTEGER PRIMARY KEY, date TEXT, type TEXT, 
                  aria_e TEXT, aria_h TEXT, notes TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS aria_assessments
                 (id INTEGER PRIMARY KEY, date TEXT, aria_e_status TEXT,
                  microhemorrhages TEXT, siderosis TEXT, symptoms TEXT, 
                  clinical_severity TEXT)''')
    conn.commit()
    return conn

# Initialize session state
if 'infusions' not in st.session_state:
    st.session_state.infusions = []
if 'mri_records' not in st.session_state:
    st.session_state.mri_records = []
if 'aria_assessments' not in st.session_state:
    st.session_state.aria_assessments = []

# Header
st.title("Leqembi Treatment Flowsheet")
patient_id = "12345"
st.write(f"Patient ID: {patient_id}")

# Navigation
tabs = st.tabs(["Summary", "Infusions", "MRI Tracking", "ARIA Monitoring"])

# Helper Functions
def calculate_dose(weight, unit='kg'):
    weight_kg = weight if unit == 'kg' else weight * 0.453592
    dose_mg = weight_kg * 10  # 10mg/kg dosing
    dose_ml = dose_mg / 100   # 100mg/mL concentration
    return round(dose_mg, 1), round(dose_ml, 1)

def save_infusion(data):
    conn = init_db()
    c = conn.cursor()
    c.execute('''INSERT INTO infusions (date, weight, unit, dose_mg, dose_ml, notes, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (data['date'], data['weight'], data['unit'], data['dose_mg'],
               data['dose_ml'], data['notes'], data['status']))
    conn.commit()
    conn.close()
    st.session_state.infusions.append(data)

def save_mri(data):
    conn = init_db()
    c = conn.cursor()
    c.execute('''INSERT INTO mri_records (date, type, aria_e, aria_h, notes)
                 VALUES (?, ?, ?, ?, ?)''',
              (data['date'], data['type'], data['aria_e'],
               data['aria_h'], data['notes']))
    conn.commit()
    conn.close()
    st.session_state.mri_records.append(data)

def save_aria(data):
    conn = init_db()
    c = conn.cursor()
    c.execute('''INSERT INTO aria_assessments 
                 (date, aria_e_status, microhemorrhages, siderosis, symptoms, clinical_severity)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (data['date'], data['aria_e_status'], data['microhemorrhages'],
               data['siderosis'], json.dumps(data['symptoms']), data['clinical_severity']))
    conn.commit()
    conn.close()
    st.session_state.aria_assessments.append(data)

# Summary Tab
with tabs[0]:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Treatment Status")
        if st.session_state.infusions:
            latest = st.session_state.infusions[-1]
            st.info(f"Current Infusion: #{len(st.session_state.infusions)}")
            next_date = datetime.strptime(latest['date'], '%Y-%m-%d') + timedelta(days=14)
            st.write(f"Next Due: {next_date.strftime('%Y-%m-%d')}")
    
    with col2:
        st.subheader("Last MRI Status")
        if st.session_state.mri_records:
            latest = st.session_state.mri_records[-1]
            st.write(f"Completed: {latest['date']}")
            st.write(f"Result: {latest['aria_e']} / {latest['aria_h']}")
    
    with col3:
        st.subheader("ApoE ε4 Status")
        st.write("Heterozygote")
        st.write("Moderate ARIA Risk")

# Infusions Tab
with tabs[1]:
    st.subheader("New Infusion Entry")
    with st.form("infusion_form"):
        col1, col2 = st.columns([3, 1])
        with col1:
            weight = st.number_input("Patient's Weight", min_value=0.0, max_value=500.0, value=70.0)
        with col2:
            unit = st.selectbox("Unit", ["kg", "lb"])
        
        if st.form_submit_button("Calculate Dose"):
            dose_mg, dose_ml = calculate_dose(weight, unit)
            st.session_state.calculated_dose = {'mg': dose_mg, 'ml': dose_ml}
            st.write(f"Calculated Dose: {dose_mg:.1f} mg ({dose_ml:.1f} mL)")
        
        date = st.date_input("Infusion Date")
        notes = st.text_area("Notes")
        
        if st.form_submit_button("Save Infusion"):
            if hasattr(st.session_state, 'calculated_dose'):
                infusion_data = {
                    'date': date.strftime('%Y-%m-%d'),
                    'weight': weight,
                    'unit': unit,
                    'dose_mg': st.session_state.calculated_dose['mg'],
                    'dose_ml': st.session_state.calculated_dose['ml'],
                    'notes': notes,
                    'status': 'Completed'
                }
                save_infusion(infusion_data)
                st.success("Infusion saved!")

    if st.session_state.infusions:
        st.subheader("Infusion History")
        df = pd.DataFrame(st.session_state.infusions)
        st.dataframe(df)

# MRI Tracking Tab
with tabs[2]:
    st.subheader("New MRI Entry")
    with st.form("mri_form"):
        date = st.date_input("MRI Date")
        mri_type = st.selectbox("MRI Type", [
            "Baseline",
            "Pre-infusion #5",
            "Pre-infusion #7",
            "Pre-infusion #14",
            "Follow-up"
        ])
        
        aria_e = st.selectbox("ARIA-E Status", ["None", "Mild", "Moderate", "Severe"])
        aria_h = st.selectbox("ARIA-H Status", ["None", "Mild", "Moderate", "Severe"])
        notes = st.text_area("Radiologist Notes")
        
        if st.form_submit_button("Save MRI Record"):
            mri_data = {
                'date': date.strftime('%Y-%m-%d'),
                'type': mri_type,
                'aria_e': aria_e,
                'aria_h': aria_h,
                'notes': notes
            }
            save_mri(mri_data)
            st.success("MRI record saved!")

    if st.session_state.mri_records:
        st.subheader("MRI History")
        df = pd.DataFrame(st.session_state.mri_records)
        st.dataframe(df)

# ARIA Monitoring Tab
with tabs[3]:
    st.subheader("ARIA Assessment")
    with st.form("aria_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("ARIA-E Assessment")
            aria_e_status = st.selectbox(
                "FLAIR Hyperintensity Severity",
                ["None", "Mild", "Moderate", "Severe"]
            )
        
        with col2:
            st.write("ARIA-H Assessment")
            microhemorrhages = st.selectbox(
                "Microhemorrhages",
                ["None", "Mild (≤4)", "Moderate (5-9)", "Severe (≥10)"]
            )
            siderosis = st.selectbox(
                "Superficial Siderosis",
                ["None", "Mild (1 area)", "Moderate (2 areas)", "Severe (>2 areas)"]
            )
        
        st.write("Symptoms")
        col3, col4 = st.columns(2)
        with col3:
            headache = st.checkbox("Headache")
            confusion = st.checkbox("Confusion")
            dizziness = st.checkbox("Dizziness")
        with col4:
            visual_changes = st.checkbox("Visual Changes")
            nausea = st.checkbox("Nausea")
            weakness = st.checkbox("Weakness")
        
        clinical_severity = st.selectbox(
            "Overall Clinical Severity",
            ["Asymptomatic", "Mild", "Moderate", "Severe"]
        )
        
        if st.form_submit_button("Save Assessment"):
            symptoms = []
            if headache: symptoms.append("Headache")
            if confusion: symptoms.append("Confusion")
            if dizziness: symptoms.append("Dizziness")
            if visual_changes: symptoms.append("Visual Changes")
            if nausea: symptoms.append("Nausea")
            if weakness: symptoms.append("Weakness")
            
            aria_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'aria_e_status': aria_e_status,
                'microhemorrhages': microhemorrhages,
                'siderosis': siderosis,
                'symptoms': symptoms,
                'clinical_severity': clinical_severity
            }
            save_aria(aria_data)
            st.success("ARIA assessment saved!")

    if st.session_state.aria_assessments:
        st.subheader("ARIA Assessment History")
        df = pd.DataFrame(st.session_state.aria_assessments)
        st.dataframe(df)

# Data Export
st.sidebar.title("Data Management")
if st.sidebar.button("Export Data"):
    data = {
        'infusions': st.session_state.infusions,
        'mri_records': st.session_state.mri_records,
        'aria_assessments': st.session_state.aria_assessments
    }
    st.sidebar.download_button(
        "Download JSON",
        data=json.dumps(data, indent=2),
        file_name="leqembi_data.json",
        mime="application/json"
    )
