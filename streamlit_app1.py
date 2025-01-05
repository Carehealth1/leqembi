import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json

# Initialize session state variables if they don't exist
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'completed_steps' not in st.session_state:
    st.session_state.completed_steps = []
if 'completion_dates' not in st.session_state:
    st.session_state.completion_dates = {}

# Define workflow steps
WORKFLOW_STEPS = [
    {
        "title": "Initial Provider Requirements",
        "content": """
        1. Healthcare provider enrolls in REMS program
        2. Complete required training
        3. Obtain certification
        """
    },
    {
        "title": "Patient Screening & Education",
        "content": """
        1. Assess patient eligibility
        2. Provide REMS education materials
        3. Discuss meningococcal infection risks
        4. Issue Patient Safety Card
        """
    },
    {
        "title": "Vaccination Requirements",
        "content": """
        1. Verify meningococcal vaccination status
        2. Schedule/complete vaccinations (A, C, W, Y and B)
        3. If urgent treatment needed, initiate antibiotic prophylaxis
        """
    },
    {
        "title": "REMS Enrollment",
        "content": """
        1. Enroll patient in REMS program
        2. Complete enrollment forms
        3. Submit documentation to REMS administrator
        """
    },
    {
        "title": "Treatment Initiation",
        "content": """
        1. Verify all requirements met
        2. Prescribe Soliris
        3. Schedule first infusion
        """
    },
    {
        "title": "Ongoing Monitoring",
        "content": """
        1. Monitor for signs of infection
        2. Schedule follow-up visits
        3. Maintain vaccination status
        4. Update safety documentation
        """
    }
]

def display_workflow():
    st.subheader("Current Workflow Steps")
    
    for idx, step in enumerate(WORKFLOW_STEPS, 1):
        with st.expander(f"Step {idx}: {step['title']}", 
                        expanded=(idx == st.session_state.current_step)):
            st.write(step['content'])
            
            if idx == st.session_state.current_step and idx not in st.session_state.completed_steps:
                if st.button(f"Complete Step {idx}", key=f"complete_{idx}"):
                    st.session_state.completed_steps.append(idx)
                    st.session_state.completion_dates[idx] = datetime.now().strftime("%Y-%m-%d")
                    if idx < len(WORKFLOW_STEPS):
                        st.session_state.current_step += 1
                    st.rerun()  # Updated from experimental_rerun to rerun

def display_timeline():
    st.subheader("Completed Steps Timeline")
    
    if not st.session_state.completed_steps:
        st.info("No steps completed yet.")
        return
    
    for step in st.session_state.completed_steps:
        with st.expander(f"{WORKFLOW_STEPS[step-1]['title']} - Completed on {st.session_state.completion_dates[step]}", expanded=True):
            st.write(WORKFLOW_STEPS[step-1]['content'])

def display_monitoring():
    st.subheader("Ongoing Monitoring Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Next Scheduled Activities")
        activities_data = {
            "Activity": ["Meningococcal Vaccination Review", "REMS Re-certification", "Safety Assessment"],
            "Status": ["Due in 3 months", "Due in 6 months", "Up to date"]
        }
        st.table(pd.DataFrame(activities_data))

    with col2:
        st.markdown("### Monitoring Checklist")
        st.checkbox("Signs of meningococcal infection")
        st.checkbox("Patient carrying Safety Card")
        st.checkbox("Vaccination status current")
        st.checkbox("Recent adverse events")

    st.warning("**Active Monitoring Required:** Continue monitoring for signs of meningococcal infection. "
               "Ensure patient is aware of symptoms and emergency procedures.")

    st.markdown("### Documentation Requirements")
    
    st.markdown("#### Required Documentation")
    st.markdown("""
    - Updated vaccination records
    - Safety monitoring logs
    - Patient education confirmation
    - Adverse event reports (if any)
    """)

    st.markdown("#### Next Steps")
    st.markdown("""
    - Schedule follow-up assessment
    - Review vaccination timeline
    - Update REMS documentation
    """)

def main():
    st.set_page_config(page_title="Soliris® REMS Program", layout="wide")
    
    st.title("Soliris® REMS Program")
    
    # Tab selection
    tab_selected = st.radio(
        "Select View",
        ["Current Workflow", "Completed Steps", "Ongoing Monitoring"],
        horizontal=True
    )
    
    st.divider()
    
    # Display selected tab content
    if tab_selected == "Current Workflow":
        display_workflow()
    elif tab_selected == "Completed Steps":
        display_timeline()
    else:
        display_monitoring()

if __name__ == "__main__":
    main()