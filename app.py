import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image

st.set_page_config(page_title="Fastener Torque Calculator", page_icon="🔩", layout="centered")

st.title("🔩 Fastener Torque Calculator")

st.write("""
This tool helps you calculate the required tightening torque based on bolt parameters and conditions.
""")

st.subheader("Single Fastener Torque Calculation")

# 1. Input: Diameter
diameter = st.number_input("Enter Bolt Diameter (mm):", min_value=0.0, format="%.2f")

# 2. Input: Pitch
pitch = st.number_input("Enter Bolt Pitch (mm):", min_value=0.0, format="%.2f")

# 3. Bolt Condition Selection (k value visible)
st.subheader("Select Bolt Condition (k value will be shown)")

bolt_conditions = {
    "Cadmium Plated": 0.16,
    "Lubricated": 0.18,
    "Zinc Plated, Dry": 0.2,
    "Non-plated, Black Finish": 0.3,
    "Custom": None
}

selected_condition = st.selectbox("Bolt Condition:", list(bolt_conditions.keys()))

if selected_condition == "Custom":
    k_value = st.number_input("Enter Custom k Value:", min_value=0.01, format="%.3f")
else:
    k_value = bolt_conditions[selected_condition]
    st.write(f"Selected k Value: **{k_value}**")

# 4. Input: Yield Tensile Strength (YTS)
yts = st.number_input("Enter Bolt Yield Tensile Strength (N/mm²):", min_value=0)

# 5. Proof Strength Factor (0 - 100%)
proof_strength_factor = st.slider(
    "Select Proof Strength Factor (%): (Recommended: 85% - 95%)",
    min_value=0.0, max_value=1.0, value=0.85, step=0.01
)

# 6. Clamping Load Factor (0 - 100%)
clamping_load_factor = st.slider(
    "Select Clamping Load Factor (%): (Recommended: 75% - 90%)",
    min_value=0.0, max_value=1.0, value=0.75, step=0.01
)

# 7. Torque Unit Selection
torque_unit = st.selectbox("Select Torque Unit:", ["Nm", "lbf·ft", "lbf·in"])

# Calculation Button
if st.button("🔧 Calculate Torque"):
    if k_value is None:
        st.error("Please enter a valid k value.")
    elif diameter <= 0 or pitch <= 0 or yts <= 0:
        st.error("Please enter positive values for Diameter, Pitch, and YTS.")
    else:
        stress_area = 0.7854 * (diameter - 0.9382 * pitch) ** 2
        proof_load = proof_strength_factor * stress_area * yts
        target_clamping_load = clamping_load_factor * proof_load
        required_torque_Nm = (k_value * target_clamping_load * diameter) / 1000

        if torque_unit == "Nm":
            required_torque = required_torque_Nm
        elif torque_unit == "lbf·ft":
            required_torque = required_torque_Nm * 0.73756
        else:  # lbf·in
            required_torque = required_torque_Nm * 8.85075

        st.subheader("📊 Results")
        st.write(f"Stress Area: **{stress_area:.2f} mm²**")
        st.write(f"Proof Load: **{proof_load:.2f} N**")
        st.write(f"Target Clamping Load: **{target_clamping_load:.2f} N**")
        st.markdown(f"<h3 style='color: green;'>Required Tightening Torque: {required_torque:.2f} {torque_unit}</h3>", unsafe_allow_html=True)

        st.info("Torque calculation completed successfully. Tighten wisely!")

        # Prepare PDF Report
        pdf = FPDF()
        pdf.add_page()

        # Add Logo Top Right
        pdf.image("KBL_Logo.png", x=160, y=10, w=30)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 20, "Fastener Torque Report", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Diameter: {diameter} mm", ln=True)
        pdf.cell(0, 10, f"Pitch: {pitch} mm", ln=True)
        pdf.cell(0, 10, f"Bolt Condition: {selected_condition}", ln=True)
        pdf.cell(0, 10, f"k Value: {k_value}", ln=True)
        pdf.cell(0, 10, f"Yield Tensile Strength: {yts} N/mm²", ln=True)
        pdf.cell(0, 10, f"Proof Strength Factor: {proof_strength_factor}", ln=True)
        pdf.cell(0, 10, f"Clamping Load Factor: {clamping_load_factor}", ln=True)
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Calculated Torque: {required_torque:.2f} {torque_unit}", ln=True)

        pdf_output = f"Torque_Report_{diameter:.1f}mm_{pitch:.1f}mm_{selected_condition.replace(' ', '_')}.pdf"
        pdf.output(pdf_output)

        with open(pdf_output, "rb") as file:
            st.download_button(label="📥 Download Torque Report as PDF", data=file, file_name=pdf_output)

# Multi-Fastener Section
st.write("---")
st.subheader("Multi-Fastener Torque Calculation")

st.write("Enter data for multiple fasteners below:")

sample_data = {
    'Diameter (mm)': [16.0],
    'Pitch (mm)': [2.0],
    'k Value': [0.16],
    'YTS (N/mm²)': [800]
}

df = st.data_editor(pd.DataFrame(sample_data), num_rows="dynamic")

if st.button("🔩 Calculate Multi-Fastener Torque"):
    try:
        stress_areas = 0.7854 * (df['Diameter (mm)'] - 0.9382 * df['Pitch (mm)']) ** 2
        proof_loads = proof_strength_factor * stress_areas * df['YTS (N/mm²)']
        clamping_loads = clamping_load_factor * proof_loads
        torques_Nm = (df['k Value'] * clamping_loads * df['Diameter (mm)']) / 1000

        if torque_unit == "Nm":
            torques = torques_Nm
        elif torque_unit == "lbf·ft":
            torques = torques_Nm * 0.73756
        else:  # lbf·in
            torques = torques_Nm * 8.85075

        result_df = pd.DataFrame({
            'Diameter (mm)': df['Diameter (mm)'],
            'Pitch (mm)': df['Pitch (mm)'],
            'k Value': df['k Value'],
            'YTS (N/mm²)': df['YTS (N/mm²)'],
            'Stress Area (mm²)': stress_areas.round(2),
            'Proof Load (N)': proof_loads.round(2),
            'Clamping Load (N)': clamping_loads.round(2),
            f'Torque ({torque_unit})': torques.round(2)
        })

        st.subheader("🛠️ Multi-Fastener Results")
        st.dataframe(result_df)

    except Exception as e:
        st.error(f"Error in calculation: {e}")

# Footer
st.write("---")
st.write("Designed with care by Akshay Sawant. ⚙️ Tradition meets technology.")
st.write("For suggestions or improvements, reach out to Akshay Sawant. 🚀")

# Use command "python -m streamlit run fastener_torque_calculator.py" to run the calculator
