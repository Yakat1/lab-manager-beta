"""
Laboratory Assistant & Calculator
A Streamlit application for common lab calculations and protocol design.
"""

import streamlit as st
import json
from pathlib import Path
from calculations import (
    calculate_mass,
    calculate_molarity,
    calculate_stock_volume,
    calculate_serial_dilution,
    calculate_percent_solution,
    scale_recipe,
    MassUnit,
    VolumeUnit,
    ConcentrationUnit,
    format_mass,
    format_volume,
    format_concentration,
)
from pdf_generator import create_protocol_pdf

# --- Common Recipes Data ---
COMMON_RECIPES = {
    "PBS (Phosphate Buffered Saline) 10X": [
        {"reagent": "Sodium Chloride (NaCl)", "amount_per_L": 80.0, "unit": "g"},
        {"reagent": "Potassium Chloride (KCl)", "amount_per_L": 2.0, "unit": "g"},
        {"reagent": "Sodium Phosphate Dibasic", "amount_per_L": 14.4, "unit": "g"},
        {"reagent": "Potassium Phosphate Monobasic", "amount_per_L": 2.4, "unit": "g"}
    ],
    "TAE Buffer 50X": [
        {"reagent": "Tris Base", "amount_per_L": 242.0, "unit": "g"},
        {"reagent": "Acetic Acid (Glacial)", "amount_per_L": 57.1, "unit": "mL"},
        {"reagent": "EDTA (0.5M, pH 8.0)", "amount_per_L": 100.0, "unit": "mL"}
    ],
    "LB Broth (Luria-Bertani)": [
        {"reagent": "Tryptone", "amount_per_L": 10.0, "unit": "g"},
        {"reagent": "Yeast Extract", "amount_per_L": 5.0, "unit": "g"},
        {"reagent": "Sodium Chloride (NaCl)", "amount_per_L": 10.0, "unit": "g"}
    ],
    "TE Buffer 1X": [
        {"reagent": "Tris-HCl (1M, pH 8.0)", "amount_per_L": 10.0, "unit": "mL"},
        {"reagent": "EDTA (0.5M, pH 8.0)", "amount_per_L": 2.0, "unit": "mL"}
    ]
}

# --- Page Configuration ---
st.set_page_config(
    page_title="Lab Assistant",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Look ---
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --accent: #22d3ee;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --text: #f8fafc;
        --text-muted: #94a3b8;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    /* Sidebar Text Fix - Force light text */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
    [data-testid="stSidebar"] [data-testid="stRadio"] label,
    [data-testid="stSidebar"] .stRadio p {
        color: #f8fafc !important;
    }
    
    /* Fix radio button unselected option text color if needed */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {
        color: #f8fafc !important;
    }
    
    /* Result display cards */
    .result-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
    }
    
    .result-value {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6366f1, #22d3ee);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
    }
    
    .result-label {
        font-size: 1rem;
        color: #94a3b8;
        text-align: center;
        margin-top: 8px;
    }
    
    /* Protocol step cards */
    .step-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        border-left: 4px solid #6366f1;
    }
    
    /* Hazard badges */
    .hazard-none { background: #10b981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; }
    .hazard-irritant { background: #f59e0b; color: black; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; }
    .hazard-flammable { background: #ef4444; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; }
    
    /* Large metric display */
    .big-metric {
        font-size: 2.5rem;
        font-weight: 600;
        color: #22d3ee;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 12px 24px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1, #4f46e5);
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(34, 211, 238, 0.1);
        border: 1px solid rgba(34, 211, 238, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(90deg, #6366f1, #22d3ee);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
""", unsafe_allow_html=True)


# --- Load Reagents ---
@st.cache_data
def load_reagents():
    """Load reagents from JSON file."""
    reagents_path = Path(__file__).parent / "reagents.json"
    try:
        with open(reagents_path, "r") as f:
            data = json.load(f)
            return data.get("reagents", [])
    except FileNotFoundError:
        st.error("reagents.json not found!")
        return []
        
        
def save_reagent(new_reagent):
    """Save a new reagent to the JSON file."""
    reagents_path = Path(__file__).parent / "reagents.json"
    try:
        # Load existing
        with open(reagents_path, "r") as f:
            data = json.load(f)
        
        # Check for duplicates
        if any(r["name"].lower() == new_reagent["name"].lower() for r in data["reagents"]):
            return False, "Reagent with this name already exists!"
            
        # Append and save
        data["reagents"].append(new_reagent)
        with open(reagents_path, "w") as f:
            json.dump(data, f, indent=4)
        
        # Clear cache to force reload
        load_reagents.clear()
        return True, "Reagent added successfully!"
        
    except Exception as e:
        return False, f"Error saving reagent: {str(e)}"

# --- Load User Recipes ---
def load_user_recipes():
    """Load user recipes from JSON file."""
    recipes_path = Path(__file__).parent / "saved_recipes.json"
    try:
        with open(recipes_path, "r") as f:
            data = json.load(f)
            return data.get("recipes", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_user_recipe_to_file(name, steps, base_vol_L):
    """Save a user recipe to the JSON file."""
    recipes_path = Path(__file__).parent / "saved_recipes.json"
    
    # Calculate amounts per L for storage (normalization)
    normalized_steps = []
    for step in steps:
        new_step = step.copy()
        # Normalize amount to per Liter
        if base_vol_L > 0:
            new_step["amount_per_L"] = step["amount"] / base_vol_L
            new_step.pop("amount", None) # Remove absolute amount
        normalized_steps.append(new_step)

    new_recipe = {
        "name": name,
        "steps": normalized_steps
    }
    
    try:
        existing = load_user_recipes()
        # Remove overwrite if exists
        existing = [r for r in existing if r["name"] != name]
        existing.append(new_recipe)
        
        with open(recipes_path, "w") as f:
            json.dump({"recipes": existing}, f, indent=4)
        return True, "Recipe saved successfully!"
    except Exception as e:
        return False, f"Error saving recipe: {str(e)}"




# --- Initialize Session State ---
def init_session_state():
    """Initialize session state variables."""
    if "protocol_steps" not in st.session_state:
        st.session_state.protocol_steps = []
    if "protocol_total_volume" not in st.session_state:
        st.session_state.protocol_total_volume = 100.0
    if "protocol_volume_unit" not in st.session_state:
        st.session_state.protocol_volume_unit = "mL"


# --- Sidebar Navigation ---
def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        st.markdown("# 🧪 Lab Assistant")
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["🧮 Calculators", "📋 Protocol Designer", "📚 Reagent Database", "📊 Unit Converter"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### Quick Reference")
        st.markdown("""
        **Common Formulas:**
        - `Mass = M × V × MW`
        - `C₁V₁ = C₂V₂`
        - `% w/v = (g/mL) × 100`
        """)
        
        st.markdown("---")
        st.markdown(
            "<p style='color: #64748b; font-size: 0.8rem;'>Laboratory Assistant v1.0</p>",
            unsafe_allow_html=True
        )
        
        return page


# --- Calculator Pages ---
def render_calculators():
    """Render the calculators page."""
    st.markdown("# 🧮 Laboratory Calculators")
    
    tabs = st.tabs(["💊 Molarity Calculator", "🔬 Dilution Calculator", "📈 Serial Dilution", "📊 Percent Solution"])
    
    reagents = load_reagents()
    reagent_names = ["Custom"] + [r["name"] for r in reagents]
    
    # --- Molarity Calculator Tab ---
    with tabs[0]:
        st.markdown("### Molarity Calculator")
        st.markdown("Calculate mass needed or resulting molarity using: `Mass = Molarity × Volume × MW`")
        
        col1, col2 = st.columns(2)
        
        with col1:
            solve_for = st.radio("Solve for:", ["Mass (g)", "Molarity (M)"], horizontal=True)
            
            selected_reagent = st.selectbox("Select Reagent", reagent_names, key="mol_reagent")
            
            if selected_reagent == "Custom":
                mw = st.number_input("Molecular Weight (g/mol)", min_value=0.01, value=100.0, step=0.01)
                purity = st.number_input("Purity (%)", min_value=0.1, max_value=100.0, value=100.0, step=0.1)
            else:
                reagent = next((r for r in reagents if r["name"] == selected_reagent), None)
                mw = reagent["mw"] if reagent else 100.0
                purity = reagent["purity"] if reagent else 100.0
                st.info(f"**MW:** {mw} g/mol | **Purity:** {purity}%")
        
        with col2:
            if solve_for == "Mass (g)":
                conc_col, conc_unit_col = st.columns([3, 1])
                with conc_col:
                    molarity = st.number_input("Desired Concentration", min_value=0.0, value=1.0, step=0.1)
                with conc_unit_col:
                    conc_unit = st.selectbox("Unit", ["M", "mM", "µM", "nM"], key="mol_conc_unit")
                
                vol_col, vol_unit_col = st.columns([3, 1])
                with vol_col:
                    volume = st.number_input("Volume", min_value=0.0, value=1.0, step=0.1)
                with vol_unit_col:
                    vol_unit = st.selectbox("Unit", ["L", "mL", "µL"], key="mol_vol_unit")
                
                # Map units
                conc_map = {"M": ConcentrationUnit.MOLAR, "mM": ConcentrationUnit.MILLIMOLAR, 
                           "µM": ConcentrationUnit.MICROMOLAR, "nM": ConcentrationUnit.NANOMOLAR}
                vol_map = {"L": VolumeUnit.LITERS, "mL": VolumeUnit.MILLILITERS, "µL": VolumeUnit.MICROLITERS}
                
                if st.button("Calculate Mass", use_container_width=True, key="calc_mass_btn"):
                    mass_g, formatted = calculate_mass(
                        molarity, volume, mw, purity,
                        volume_unit=vol_map[vol_unit],
                        conc_unit=conc_map[conc_unit]
                    )
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-value">{formatted}</div>
                        <div class="result-label">Mass of {selected_reagent} needed</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            else:  # Solve for Molarity
                mass_col, mass_unit_col = st.columns([3, 1])
                with mass_col:
                    mass = st.number_input("Mass", min_value=0.0, value=1.0, step=0.1)
                with mass_unit_col:
                    mass_unit = st.selectbox("Unit", ["g", "mg", "µg"], key="mol_mass_unit")
                
                vol_col, vol_unit_col = st.columns([3, 1])
                with vol_col:
                    volume = st.number_input("Volume", min_value=0.0, value=1.0, step=0.1, key="mol_vol2")
                with vol_unit_col:
                    vol_unit = st.selectbox("Unit", ["L", "mL", "µL"], key="mol_vol_unit2")
                
                # Map units
                mass_map = {"g": MassUnit.GRAMS, "mg": MassUnit.MILLIGRAMS, "µg": MassUnit.MICROGRAMS}
                vol_map = {"L": VolumeUnit.LITERS, "mL": VolumeUnit.MILLILITERS, "µL": VolumeUnit.MICROLITERS}
                
                if st.button("Calculate Molarity", use_container_width=True, key="calc_mol_btn"):
                    mol_M, formatted = calculate_molarity(
                        mass, volume, mw, purity,
                        mass_unit=mass_map[mass_unit],
                        volume_unit=vol_map[vol_unit]
                    )
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-value">{formatted}</div>
                        <div class="result-label">Resulting concentration</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # --- Dilution Calculator Tab ---
    with tabs[1]:
        st.markdown("### Stock Solution / Dilution Calculator")
        st.markdown("Calculate using the formula: `C₁V₁ = C₂V₂`")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Stock Solution (C₁)**")
            c1_col, c1_unit_col = st.columns([2, 1])
            with c1_col:
                c1 = st.number_input("Concentration", min_value=0.0, value=10.0, step=0.1, key="dil_c1")
            with c1_unit_col:
                c1_unit = st.selectbox("Unit", ["M", "mM", "µM"], key="dil_c1_unit")
        
        with col2:
            st.markdown("**Final Solution (C₂)**")
            c2_col, c2_unit_col = st.columns([2, 1])
            with c2_col:
                c2 = st.number_input("Concentration", min_value=0.0, value=1.0, step=0.1, key="dil_c2")
            with c2_unit_col:
                c2_unit = st.selectbox("Unit", ["M", "mM", "µM"], key="dil_c2_unit")
        
        with col3:
            st.markdown("**Final Volume (V₂)**")
            v2_col, v2_unit_col = st.columns([2, 1])
            with v2_col:
                v2 = st.number_input("Volume", min_value=0.0, value=100.0, step=1.0, key="dil_v2")
            with v2_unit_col:
                v2_unit = st.selectbox("Unit", ["L", "mL", "µL"], key="dil_v2_unit")
        
        conc_map = {"M": ConcentrationUnit.MOLAR, "mM": ConcentrationUnit.MILLIMOLAR, "µM": ConcentrationUnit.MICROMOLAR}
        vol_map = {"L": VolumeUnit.LITERS, "mL": VolumeUnit.MILLILITERS, "µL": VolumeUnit.MICROLITERS}
        
        if st.button("Calculate Dilution", use_container_width=True, key="calc_dil_btn"):
            v1_L, v1_fmt, diluent_L, diluent_fmt = calculate_stock_volume(
                c1, c2, v2,
                c1_unit=conc_map[c1_unit],
                c2_unit=conc_map[c2_unit],
                v2_unit=vol_map[v2_unit]
            )
            
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.markdown(f"""
                <div class="result-card">
                    <div class="result-value">{v1_fmt}</div>
                    <div class="result-label">Stock Solution (V₁)</div>
                </div>
                """, unsafe_allow_html=True)
            with res_col2:
                st.markdown(f"""
                <div class="result-card">
                    <div class="result-value">{diluent_fmt}</div>
                    <div class="result-label">Diluent to Add</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Instructions
            st.markdown(f"""
            <div class="info-box">
                <strong>📋 Instructions:</strong><br>
                1. Measure <strong>{v1_fmt}</strong> of your {c1} {c1_unit} stock solution<br>
                2. Add <strong>{diluent_fmt}</strong> of diluent (water/buffer)<br>
                3. Mix thoroughly to obtain {v2} {v2_unit} of {c2} {c2_unit} solution
            </div>
            """, unsafe_allow_html=True)
    
    # --- Serial Dilution Tab ---
    with tabs[2]:
        st.markdown("### Serial Dilution Calculator")
        st.markdown("Generate a dilution series for standard curves or dose-response experiments.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            initial_conc = st.number_input("Initial Concentration", min_value=0.0, value=1000.0, step=10.0)
            initial_unit = st.selectbox("Unit", ["µM", "nM", "mM", "M"], key="serial_unit")
        
        with col2:
            dilution_factor = st.number_input("Dilution Factor", min_value=1.1, value=10.0, step=0.5)
        
        with col3:
            num_dilutions = st.number_input("Number of Dilutions", min_value=1, max_value=20, value=6, step=1)
        
        if st.button("Generate Series", use_container_width=True, key="calc_serial_btn"):
            unit_map = {"M": ConcentrationUnit.MOLAR, "mM": ConcentrationUnit.MILLIMOLAR, 
                       "µM": ConcentrationUnit.MICROMOLAR, "nM": ConcentrationUnit.NANOMOLAR}
            
            series = calculate_serial_dilution(initial_conc, dilution_factor, num_dilutions, unit_map[initial_unit])
            
            st.markdown("#### Dilution Series")
            
            # Display as a nice table
            table_data = []
            for step, conc, formatted in series:
                table_data.append({
                    "Step": step,
                    f"Concentration ({initial_unit})": f"{conc:.4g}",
                    "Formatted": formatted
                })
            
            st.dataframe(table_data, use_container_width=True, hide_index=True)
    
    # --- Percent Solution Tab ---
    with tabs[3]:
        st.markdown("### Percent Solution Calculator")
        st.markdown("Calculate % w/v (weight/volume) solutions.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            mass_col, mass_unit_col = st.columns([3, 1])
            with mass_col:
                pct_mass = st.number_input("Mass of Solute", min_value=0.0, value=10.0, step=0.1, key="pct_mass")
            with mass_unit_col:
                pct_mass_unit = st.selectbox("Unit", ["g", "mg"], key="pct_mass_unit")
        
        with col2:
            vol_col, vol_unit_col = st.columns([3, 1])
            with vol_col:
                pct_vol = st.number_input("Volume of Solution", min_value=0.0, value=100.0, step=1.0, key="pct_vol")
            with vol_unit_col:
                pct_vol_unit = st.selectbox("Unit", ["mL", "L"], key="pct_vol_unit")
        
        mass_map = {"g": MassUnit.GRAMS, "mg": MassUnit.MILLIGRAMS}
        vol_map = {"mL": VolumeUnit.MILLILITERS, "L": VolumeUnit.LITERS}
        
        if st.button("Calculate % w/v", use_container_width=True, key="calc_pct_btn"):
            percent = calculate_percent_solution(pct_mass, pct_vol, mass_map[pct_mass_unit], vol_map[pct_vol_unit])
            
            st.markdown(f"""
            <div class="result-card">
                <div class="result-value">{percent:.3f}% w/v</div>
                <div class="result-label">Percent Weight/Volume Solution</div>
            </div>
            """, unsafe_allow_html=True)


# --- Protocol Designer Page ---
def render_protocol_designer():
    """Render the protocol designer page."""
    st.markdown("# 📋 Protocol Designer")
    st.markdown("Build step-by-step recipes for your experiments with automatic scaling.")
    
    reagents = load_reagents()
    reagent_names = [r["name"] for r in reagents]
    
    # --- 1. Recipe Manager (Enhanced) ---
    with st.expander("📂 Recipe Manager (Common & Personal)"):
        rm_tabs = st.tabs(["🧙‍♂️ Common Recipes", "👤 My Recipes"])
        
        # Shared Logic for Load & Scale
        def load_and_scale_recipe(recipe_steps, recipe_name, target_vol, target_unit):
            # Convert target volume to Liters for scaling
            target_vol_L = target_vol
            if target_unit == "mL":
                target_vol_L /= 1000.0
            elif target_unit == "µL":
                target_vol_L /= 1e6
                
            new_steps = []
            for i, item in enumerate(recipe_steps):
                # Calculate absolute amount for target volume
                scaled_amount = item["amount_per_L"] * target_vol_L
                
                # Smart Unit Converter for Display
                display_unit = item["unit"]
                display_amount = scaled_amount
                
                # Simple logic to keep numbers readable
                # (You could expand this with a proper formatting function if desired)
                
                new_steps.append({
                    "step_number": i + 1,
                    "reagent": item["reagent"],
                    "amount": float(f"{display_amount:.4g}"),
                    "unit": display_unit,
                    "notes": f"Standard {recipe_name}"
                })
            
            st.session_state.protocol_steps = new_steps
            st.session_state.prot_name = f"{recipe_name} ({target_vol} {target_unit})"
            st.session_state.protocol_total_volume = target_vol
            st.session_state.protocol_volume_unit = target_unit
            st.success(f"Loaded {recipe_name} for {target_vol} {target_unit}!")
            st.rerun()

        # Tab 1: Common Recipes
        with rm_tabs[0]:
            st.info("Standard lab buffers.")
            c_recipe_name = st.selectbox("Choose Recipe", ["Select..."] + list(COMMON_RECIPES.keys()), key="c_recipe_sel")
            
            c_col1, c_col2 = st.columns(2)
            c_target_vol = c_col1.number_input("Target Volume", value=st.session_state.protocol_total_volume, key="c_vol")
            c_target_unit = c_col2.selectbox("Unit", ["mL", "L", "µL"], index=0, key="c_unit")
            
            if c_recipe_name != "Select..." and st.button("Load Common Recipe"):
                load_and_scale_recipe(COMMON_RECIPES[c_recipe_name], c_recipe_name, c_target_vol, c_target_unit)

        # Tab 2: My Recipes
        with rm_tabs[1]:
            user_recipes = load_user_recipes()
            if not user_recipes:
                st.warning("No saved recipes yet. Build a protocol and click 'Save to My Recipes' below!")
            else:
                u_recipe_names = [r["name"] for r in user_recipes]
                u_recipe_name = st.selectbox("Choose Your Recipe", ["Select..."] + u_recipe_names, key="u_recipe_sel")
                
                u_col1, u_col2 = st.columns(2)
                u_target_vol = u_col1.number_input("Target Volume", value=st.session_state.protocol_total_volume, key="u_vol")
                u_target_unit = u_col2.selectbox("Unit", ["mL", "L", "µL"], index=0, key="u_unit")
                
                if u_recipe_name != "Select..." and st.button("Load My Recipe"):
                    selected_r = next(r for r in user_recipes if r["name"] == u_recipe_name)
                    load_and_scale_recipe(selected_r["steps"], u_recipe_name, u_target_vol, u_target_unit)


    # --- 2. Safety Dashboard ---
    st.markdown("### 🛡️ Safety Dashboard")
    current_hazards = set()
    for step in st.session_state.protocol_steps:
        # Find reagent in DB
        r_data = next((r for r in reagents if r["name"] == step["reagent"]), None)
        if r_data:
            h = r_data.get("hazard", "None")
            if h != "None":
                current_hazards.add(h)
    
    if current_hazards:
        st.warning(f"⚠️ **Caution: This protocol involves: {', '.join(current_hazards)}**")
        st.info("Recommended PPE: 🧤 Gloves, 🥽 Safety Glasses, 🥼 Lab Coat")
    else:
        st.success("✅ No hazardous reagents detected in database.")
    
    # Protocol settings
    st.markdown("### Protocol Settings")
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        default_name = st.session_state.get("prot_name", "My Protocol")
        protocol_name = st.text_input("Protocol Name", value=default_name, key="prot_name_input")
    
    with col2:
        old_volume = st.session_state.protocol_total_volume
        new_volume = st.number_input(
            "Final Volume", 
            min_value=0.1, 
            value=st.session_state.protocol_total_volume, 
            step=10.0,
            key="prot_vol"
        )
    
    with col3:
        vol_units = ["mL", "L", "µL"]
        current_unit = st.session_state.get("protocol_volume_unit", "mL")
        unit_index = vol_units.index(current_unit) if current_unit in vol_units else 0
        vol_unit = st.selectbox("Volume Unit", vol_units, index=unit_index, key="prot_vol_unit")
        st.session_state.protocol_volume_unit = vol_unit
    
    # Auto-scale if volume changed
    if new_volume != old_volume and old_volume > 0:
        st.session_state.protocol_steps = scale_recipe(
            st.session_state.protocol_steps, 
            new_volume, 
            old_volume
        )
        st.session_state.protocol_total_volume = new_volume
        st.toast(f"🔄 Recipe scaled from {old_volume} to {new_volume} {vol_unit}!", icon="✅")
    
    st.markdown("---")
    
    # Toggle calculation mode
    use_stock_calc = st.checkbox("🧪 Calculate volume from Stock Solution")
    
    add_col1, add_col2, add_col3, add_col4 = st.columns([3, 2, 1, 2])
    
    with add_col1:
        new_reagent = st.selectbox("Reagent", ["Select..."] + reagent_names, key="new_step_reagent")
    
    # Initialize variables
    final_amount = 0.0
    final_unit = "mL"
    auto_notes = ""
    
    if use_stock_calc:
        # Stock Calculation Mode
        with add_col2:
            st.caption("Stock (C₁)")
            c1_col, c1_u_col = st.columns([2, 1])
            c1 = c1_col.number_input("Stock Conc", value=10.0, step=0.1, key="step_c1")
            c1_unit = c1_u_col.selectbox("Unit", ["M", "mM", "µM"], key="step_c1_unit")

        with add_col3:
            st.caption("Target (C₂)")
            c2_col, c2_u_col = st.columns([2, 1])
            c2 = c2_col.number_input("Target Conc", value=1.0, step=0.1, key="step_c2")
            c2_unit = c2_u_col.selectbox("Unit", ["mM", "µM", "nM", "M"], key="step_c2_unit")
        
        # Calculate Volume
        try:
            # Re-map units locally for safety
            c_map = {"M": ConcentrationUnit.MOLAR, "mM": ConcentrationUnit.MILLIMOLAR, 
                    "µM": ConcentrationUnit.MICROMOLAR, "nM": ConcentrationUnit.NANOMOLAR}
            v_map = {"L": VolumeUnit.LITERS, "mL": VolumeUnit.MILLILITERS, "µL": VolumeUnit.MICROLITERS}
            
            # Get Protocol Volume in Liters
            prot_vol = st.session_state.protocol_total_volume
            prot_unit = st.session_state.protocol_volume_unit
            
            # Use calculate_stock_volume to get V1 in Liters
            v1_L, _, _, _ = calculate_stock_volume(
                c1, c2, prot_vol,
                c1_unit=c_map[c1_unit],
                c2_unit=c_map[c2_unit],
                v2_unit=v_map[prot_unit]
            )
            
            # Determine best unit for display
            if v1_L < 1e-4: # < 0.1 mL -> use µL
                final_amount = v1_L * 1e6
                final_unit = "µL"
            elif v1_L < 1: # < 1 L -> use mL
                final_amount = v1_L * 1e3
                final_unit = "mL"
            else:
                final_amount = v1_L
                final_unit = "L"
            
            # Round for cleanliness
            final_amount = float(f"{final_amount:.4g}")
            
            st.caption(f"**Add:** {final_amount} {final_unit}")
            auto_notes = f" (From {c1} {c1_unit} stock → {c2} {c2_unit})"
            
        except Exception as e:
            st.error("Calc Error")
            
    else:
        # Manual Mode
        with add_col2:
            final_amount = st.number_input("Amount", min_value=0.0, value=10.0, step=0.1, key="new_step_amount")
        
        with add_col3:
            final_unit = st.selectbox("Unit", ["mL", "µL", "L", "g", "mg", "µg"], key="new_step_unit")

    with add_col4:
        user_notes = st.text_input("Notes (optional)", key="new_step_notes")
        final_notes = (user_notes + auto_notes).strip()
    
    if st.button("➕ Add Step", use_container_width=True, key="add_step_btn"):
        if new_reagent != "Select...":
            step = {
                "step_number": len(st.session_state.protocol_steps) + 1,
                "reagent": new_reagent,
                "amount": final_amount,
                "unit": final_unit,
                "notes": final_notes
            }
            st.session_state.protocol_steps.append(step)
            st.rerun()
        else:
            st.warning("Please select a reagent!")
    
    st.markdown("---")
    
    # Display current steps
    st.markdown("### Recipe Steps")
    
    if not st.session_state.protocol_steps:
        st.info("No steps added yet. Add your first step above!")
    else:
        for i, step in enumerate(st.session_state.protocol_steps):
            with st.container():
                col1, col2, col3, col4 = st.columns([0.5, 3, 2, 1])
                
                with col1:
                    st.markdown(f"**{i+1}.**")
                
                with col2:
                    st.markdown(f"**{step['reagent']}**")
                    if step.get('notes'):
                        st.caption(step['notes'])
                
                with col3:
                    st.markdown(f"<span class='big-metric'>{step['amount']:.2f} {step['unit']}</span>", 
                               unsafe_allow_html=True)
                
                with col4:
                    if st.button("🗑️", key=f"del_step_{i}"):
                        st.session_state.protocol_steps.pop(i)
                        # Renumber steps
                        for j, s in enumerate(st.session_state.protocol_steps):
                            s["step_number"] = j + 1
                        st.rerun()
            
            st.markdown("---")
    
    # Export options
    if st.session_state.protocol_steps:
        st.markdown("### Export Protocol")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Copy as Text", use_container_width=True):
                text = f"# {protocol_name}\n"
                text += f"Final Volume: {new_volume} {vol_unit}\n\n"
                for step in st.session_state.protocol_steps:
                    text += f"{step['step_number']}. {step['reagent']}: {step['amount']:.2f} {step['unit']}"
                    if step.get('notes'):
                        text += f" - {step['notes']}"
                    text += "\n"
                st.code(text)
        
        with col2:
            if st.button("💾 Export JSON", use_container_width=True):
                export_data = {
                    "protocol_name": protocol_name,
                    "final_volume": new_volume,
                    "volume_unit": vol_unit,
                    "steps": st.session_state.protocol_steps
                }
                st.json(export_data)

            if st.button("💾 Save to My Recipes", use_container_width=True):
                # Calculate base volume in Liters for normalization
                base_vol_L = new_volume
                if vol_unit == "mL": base_vol_L /= 1000.0
                elif vol_unit == "µL": base_vol_L /= 1e6
                
                success, msg = save_user_recipe_to_file(protocol_name, st.session_state.protocol_steps, base_vol_L)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
        
        # --- 3. PDF Export ---
        with col2:
            try:
                pdf_bytes = create_protocol_pdf(
                    protocol_name, 
                    new_volume, 
                    vol_unit, 
                    st.session_state.protocol_steps, 
                    list(current_hazards)
                )
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_bytes,
                    file_name=f"{protocol_name.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF Error: {str(e)}")


# --- Reagent Database Page ---
def render_reagent_database():
    """Render the reagent database page."""
    st.markdown("# 📚 Reagent Database")
    st.markdown("Browse and search the reagent database.")
    
    reagents = load_reagents()
    
    # --- Add New Reagent Section ---
    with st.expander("➕ Add New Reagent"):
        with st.form("add_reagent_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Reagent Name (Required)")
                new_formula = st.text_input("Formula")
                new_category = st.selectbox("Category", ["Salt", "Buffer", "Solvent", "Acid", "Base", "Chelator", "Detergent", "Other"])
                new_hazard = st.selectbox("Hazard Class", ["None", "Irritant", "Flammable", "Corrosive", "Toxic"])
            
            with col2:
                new_mw = st.number_input("Molecular Weight (g/mol) (Required)", min_value=0.01, step=0.01)
                new_purity = st.number_input("Purity (%)", min_value=0.1, max_value=100.0, value=99.0, step=0.1)
                new_storage = st.selectbox("Storage", ["Room Temperature", "4°C", "-20°C", "-80°C", "Flammables Cabinet", "Acids Cabinet"])
            
            submit = st.form_submit_button("Save Reagent")
            
            if submit:
                if new_name and new_mw > 0:
                    reagent_data = {
                        "name": new_name,
                        "formula": new_formula,
                        "mw": new_mw,
                        "purity": new_purity,
                        "category": new_category,
                        "hazard": new_hazard,
                        "storage": new_storage
                    }
                    success, msg = save_reagent(reagent_data)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Name and Molecular Weight are required!")
    
    st.markdown("---")
    
    # Search/filter
    search = st.text_input("🔍 Search reagents...", key="reagent_search")
    
    # Filter by category
    categories = list(set(r.get("category", "Other") for r in reagents))
    selected_category = st.multiselect("Filter by Category", categories, default=categories)
    
    # Filter reagents
    filtered = [r for r in reagents 
                if (search.lower() in r["name"].lower() or search.lower() in r.get("formula", "").lower())
                and (not selected_category or r.get("category", "Other") in selected_category)]
    
    # Display as cards
    if not filtered:
        st.info("No reagents found matching your criteria.")
    else:
        for reagent in filtered:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1.5])
                
                with col1:
                    st.markdown(f"**{reagent['name']}**")
                    st.caption(f"Formula: {reagent.get('formula', 'N/A')}")
                
                with col2:
                    st.metric("MW", f"{reagent['mw']} g/mol")
                
                with col3:
                    st.metric("Purity", f"{reagent['purity']}%")
                
                with col4:
                    hazard = reagent.get("hazard", "None")
                    hazard_class = f"hazard-{hazard.lower()}" if hazard in ["None", "Irritant", "Flammable"] else "hazard-none"
                    st.markdown(f"<span class='{hazard_class}'>{hazard}</span>", unsafe_allow_html=True)
                    st.caption(f"Store: {reagent.get('storage', 'N/A')}")
                
                st.markdown("---")


# --- Unit Converter Page ---
def render_unit_converter():
    """Render the unit converter page."""
    st.markdown("# 📊 Unit Converter")
    
    tabs = st.tabs(["Mass", "Volume", "Concentration"])
    
    with tabs[0]:
        st.markdown("### Mass Converter")
        input_mass = st.number_input("Enter Mass", min_value=0.0, value=1.0, step=0.1, key="conv_mass")
        input_unit = st.selectbox("From", ["g", "mg", "µg", "kg"], key="conv_mass_unit")
        
        # Convert to grams first
        mass_factors = {"kg": 1000, "g": 1, "mg": 0.001, "µg": 0.000001}
        mass_g = input_mass * mass_factors[input_unit]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("kg", f"{mass_g / 1000:.6g}")
        col2.metric("g", f"{mass_g:.6g}")
        col3.metric("mg", f"{mass_g * 1000:.6g}")
        col4.metric("µg", f"{mass_g * 1000000:.6g}")
    
    with tabs[1]:
        st.markdown("### Volume Converter")
        input_vol = st.number_input("Enter Volume", min_value=0.0, value=1.0, step=0.1, key="conv_vol")
        input_unit = st.selectbox("From", ["L", "mL", "µL"], key="conv_vol_unit")
        
        vol_factors = {"L": 1, "mL": 0.001, "µL": 0.000001}
        vol_L = input_vol * vol_factors[input_unit]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("L", f"{vol_L:.6g}")
        col2.metric("mL", f"{vol_L * 1000:.6g}")
        col3.metric("µL", f"{vol_L * 1000000:.6g}")
    
    with tabs[2]:
        st.markdown("### Concentration Converter")
        input_conc = st.number_input("Enter Concentration", min_value=0.0, value=1.0, step=0.1, key="conv_conc")
        input_unit = st.selectbox("From", ["M", "mM", "µM", "nM"], key="conv_conc_unit")
        
        conc_factors = {"M": 1, "mM": 0.001, "µM": 0.000001, "nM": 0.000000001}
        conc_M = input_conc * conc_factors[input_unit]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("M", f"{conc_M:.6g}")
        col2.metric("mM", f"{conc_M * 1000:.6g}")
        col3.metric("µM", f"{conc_M * 1000000:.6g}")
        col4.metric("nM", f"{conc_M * 1000000000:.6g}")


# --- Main App ---
def main():
    """Main application entry point."""
    init_session_state()
    page = render_sidebar()
    
    if page == "🧮 Calculators":
        render_calculators()
    elif page == "📋 Protocol Designer":
        render_protocol_designer()
    elif page == "📚 Reagent Database":
        render_reagent_database()
    elif page == "📊 Unit Converter":
        render_unit_converter()


if __name__ == "__main__":
    main()
