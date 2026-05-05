import streamlit as st
import pandas as pd
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Asbestos Estimator", layout="wide")
st.image("logo.png", width=200)

# ---------------- SESSION STATE INIT ----------------
if "line_items" not in st.session_state:
    st.session_state["line_items"] = []

# ---------------- DEFAULT COSTS ----------------
MATERIAL_COSTS = {
    "Floor Tile & Mastic": {"unit": "sq ft", "cost": 8.0},
    "Popcorn Ceiling": {"unit": "sq ft", "cost": 12.0},
    "Pipe Insulation": {"unit": "linear ft", "cost": 25.0},
    "Duct Wrap": {"unit": "sq ft", "cost": 15.0},
    "Spray Fireproofing": {"unit": "sq ft", "cost": 18.0},
    "Transite Panels": {"unit": "sq ft", "cost": 9.0},
    "Roofing": {"unit": "sq ft", "cost": 75.0},
    "Other Friable": {"unit": "sq ft", "cost": 20.0},
}

# ---------------- PDF FUNCTION ----------------
def generate_pdf(project_info, items, total):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.drawImage("logo.png", 1*inch, height - 1.7*inch, 
	width=2*inch, preserveAspectRatio=True)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, height - 1*inch, "ASBESTOS ESTIMATE")

    c.setFont("Helvetica", 11)
    y = height - 1.8*inch
    c.drawString(1*inch, y, f"Project: {project_info['name']}")
    y -= 0.25*inch
    c.drawString(1*inch, y, f"Customer: {project_info['customer']}")
    y -= 0.25*inch
    c.drawString(1*inch, y, f"Address: {project_info['address']}")
    y -= 0.25*inch
    c.drawString(1*inch, y, f"Date: {datetime.now().strftime('%B %d, %Y')}")

    y -= 0.5*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y, "Scope of Work:")
    y -= 0.3*inch

    c.setFont("Helvetica", 10)
    for item in items:
        line = f"- {item['material']}: {item['quantity']} {item['unit']} @ ${item['unit_cost']:.2f} = ${item['total']:.2f}"
        c.drawString(1*inch, y, line)
        y -= 0.2*inch

    y -= 0.4*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y, f"TOTAL: ${total:,.2f}")

    c.save()
    buffer.seek(0)
    return buffer

# ---------------- TITLE ----------------
st.title("🏗️ Asbestos Abatement Cost Estimator")
st.markdown("Professional tool for estimating asbestos removal costs.")

# ---------------- PROJECT INFO ----------------
with st.expander("Project Information", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        proj_name = st.text_input("Project Name / Job #")
        customer = st.text_input("Customer Name")
    with col2:
        address = st.text_input("Site Address")

# ---------------- ADD ITEMS ----------------
with st.expander("Add Removal Items", expanded=True):
    col1, col2, col3, col4 = st.columns([3,1,1,1])

    with col1:
        mat_type = st.selectbox("Material Type", list(MATERIAL_COSTS.keys()))
    with col2:
        qty = st.number_input("Quantity", min_value=0.0, step=1.0)
    with col3:
        u_cost = st.number_input("Unit Cost ($)", value=MATERIAL_COSTS[mat_type]["cost"])
    with col4:
        st.write("")
        if st.button("Add Item"):
            if qty > 0:
                st.session_state["line_items"].append({
                    "material": mat_type,
                    "quantity": qty,
                    "unit": MATERIAL_COSTS[mat_type]["unit"],
                    "unit_cost": u_cost,
                    "total": qty * u_cost
                })
            else:
                st.error("Quantity must be greater than 0")

# ---------------- DATAFRAME ----------------
df = pd.DataFrame(st.session_state["line_items"]) if st.session_state["line_items"] else pd.DataFrame(columns=["material","quantity","unit","unit_cost","total"])

st.subheader("Items")

header = st.columns([2,1,1,1,1,1])
header[0].markdown("**Material**")
header[1].markdown("**Qty**")
header[2].markdown("**Unit Cost ($)**")
header[3].markdown("**Unit**")
header[4].markdown("**Item Cost ($)**")  # 👈 NOVO
header[5].markdown("**Action**")
    
    with col1:
           st.write(f"**{item['material']}**")
    with col2:
           new_qty = st.number_input("Qty", value=item["quantity"], key=f"qty_{i}")
    with col3:
           st.write(item["unit"])
    with col4:
           new_cost = st.number_input("Unit $", value=item["unit_cost"], key=f"cost_{i}")
    with col5:
           st.write(f"${item['total']:.2f}")  # sada je jasno da je Item Cost
    with col6:
           if st.button("❌ Delete", key=f"del_{i}"):
               st.session_state["line_items"].pop(i)
               st.rerun()

       # Update logic
       st.session_state["line_items"][i]["quantity"] = new_qty
       st.session_state["line_items"][i]["unit_cost"] = new_cost
       st.session_state["line_items"][i]["total"] = new_qty * new_cost


if st.button("Clear All Items"):
    st.session_state["line_items"] = []
    st.rerun()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.sidebar.image("logo.png", width=150)
    st.header("Additional Costs")
    mob = st.number_input("Mobilization ($)", value=1500)
    disp = st.number_input("Waste Disposal ($)", value=0)
    air = st.number_input("Air Monitoring ($)", value=850)
    permits = st.number_input("Permits ($)", value=450)
    markup = st.slider("Profit Margin (%)", 0, 100, 35)

# ---------------- CALCULATION ----------------
if st.session_state["line_items"]:
    subtotal = sum(i["total"] for i in st.session_state["line_items"])
    direct = subtotal + mob + disp + air + permits
    markup_val = direct * (markup / 100)
    total = direct + markup_val

    st.subheader("Cost Summary")
    st.write(f"Labor & Material: **${subtotal:,.2f}**")
    st.write(f"Additional Costs: **${(mob+disp+air+permits):,.2f}**")
    st.write(f"Markup: **${markup_val:,.2f}**")

    st.metric("TOTAL ESTIMATE", f"${total:,.2f}")

    # PDF
    project_info = {"name": proj_name, "customer": customer, "address": address}
    pdf = generate_pdf(project_info, st.session_state["line_items"], total)

    st.download_button("Download PDF", pdf, file_name="estimate.pdf")

    # ---------------- SAVE PROJECT ----------------
    project_data = {
        "project": project_info,
        "items": st.session_state["line_items"],
        "costs": {
            "mob": mob,
            "disp": disp,
            "air": air,
            "permits": permits,
            "markup": markup
        }
    }

    st.download_button(
        "💾 Save Project",
        data=json.dumps(project_data, indent=2),
        file_name="project.json",
        mime="application/json"
    )

# ---------------- LOAD PROJECT ----------------
st.subheader("Load Existing Project")
uploaded_file = st.file_uploader("Upload Project JSON", type="json")

if uploaded_file:
    data = json.load(uploaded_file)
    st.session_state["line_items"] = data["items"]
    st.success("Project loaded successfully!")
    st.rerun()
	
