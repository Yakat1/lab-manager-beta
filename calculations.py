"""
Laboratory Calculations Module
Provides functions for common lab calculations: molarity, dilution, unit conversions, and recipe scaling.
"""

from typing import Tuple, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

# --- Unit Conversion Constants ---
class MassUnit(Enum):
    GRAMS = "g"
    MILLIGRAMS = "mg"
    MICROGRAMS = "µg"
    KILOGRAMS = "kg"

class VolumeUnit(Enum):
    LITERS = "L"
    MILLILITERS = "mL"
    MICROLITERS = "µL"

class ConcentrationUnit(Enum):
    MOLAR = "M"
    MILLIMOLAR = "mM"
    MICROMOLAR = "µM"
    NANOMOLAR = "nM"
    PERCENT_WV = "% w/v"
    PERCENT_VV = "% v/v"

# Conversion factors to base units (g, L, M)
MASS_TO_GRAMS = {
    MassUnit.KILOGRAMS: 1000,
    MassUnit.GRAMS: 1,
    MassUnit.MILLIGRAMS: 0.001,
    MassUnit.MICROGRAMS: 0.000001,
}

VOLUME_TO_LITERS = {
    VolumeUnit.LITERS: 1,
    VolumeUnit.MILLILITERS: 0.001,
    VolumeUnit.MICROLITERS: 0.000001,
}

CONC_TO_MOLAR = {
    ConcentrationUnit.MOLAR: 1,
    ConcentrationUnit.MILLIMOLAR: 0.001,
    ConcentrationUnit.MICROMOLAR: 0.000001,
    ConcentrationUnit.NANOMOLAR: 0.000000001,
}

# --- Core Calculation Functions ---

def calculate_mass(
    molarity: float,
    volume: float,
    mw: float,
    purity: float = 100.0,
    volume_unit: VolumeUnit = VolumeUnit.LITERS,
    conc_unit: ConcentrationUnit = ConcentrationUnit.MOLAR
) -> Tuple[float, str]:
    """
    Calculate mass of reagent needed.
    Formula: Mass (g) = Molarity (M) × Volume (L) × MW (g/mol) / (Purity/100)
    
    Returns: (mass_in_grams, formatted_string)
    """
    # Convert to base units
    molarity_M = molarity * CONC_TO_MOLAR.get(conc_unit, 1)
    volume_L = volume * VOLUME_TO_LITERS.get(volume_unit, 1)
    
    # Calculate mass, adjusting for purity
    purity_fraction = purity / 100.0
    mass_g = (molarity_M * volume_L * mw) / purity_fraction
    
    return mass_g, format_mass(mass_g)


def calculate_molarity(
    mass: float,
    volume: float,
    mw: float,
    purity: float = 100.0,
    mass_unit: MassUnit = MassUnit.GRAMS,
    volume_unit: VolumeUnit = VolumeUnit.LITERS
) -> Tuple[float, str]:
    """
    Calculate molarity from mass of reagent.
    Formula: Molarity (M) = Mass (g) / (Volume (L) × MW (g/mol)) × (Purity/100)
    
    Returns: (molarity_in_M, formatted_string)
    """
    # Convert to base units
    mass_g = mass * MASS_TO_GRAMS.get(mass_unit, 1)
    volume_L = volume * VOLUME_TO_LITERS.get(volume_unit, 1)
    
    if volume_L == 0 or mw == 0:
        return 0.0, "0 M"
    
    purity_fraction = purity / 100.0
    molarity_M = (mass_g / (volume_L * mw)) * purity_fraction
    
    return molarity_M, format_concentration(molarity_M)


def calculate_stock_volume(
    c1: float,
    c2: float,
    v2: float,
    c1_unit: ConcentrationUnit = ConcentrationUnit.MOLAR,
    c2_unit: ConcentrationUnit = ConcentrationUnit.MOLAR,
    v2_unit: VolumeUnit = VolumeUnit.LITERS
) -> Tuple[float, str, float, str]:
    """
    Calculate volume of stock solution needed for dilution.
    Formula: C1 × V1 = C2 × V2 → V1 = (C2 × V2) / C1
    
    Returns: (v1_in_liters, formatted_v1, diluent_volume, formatted_diluent)
    """
    # Convert to base units
    c1_M = c1 * CONC_TO_MOLAR.get(c1_unit, 1)
    c2_M = c2 * CONC_TO_MOLAR.get(c2_unit, 1)
    v2_L = v2 * VOLUME_TO_LITERS.get(v2_unit, 1)
    
    if c1_M == 0:
        return 0.0, "0 L", v2_L, format_volume(v2_L)
    
    v1_L = (c2_M * v2_L) / c1_M
    diluent_L = v2_L - v1_L
    
    return v1_L, format_volume(v1_L), diluent_L, format_volume(diluent_L)


def calculate_percent_solution(
    mass: float,
    volume: float,
    mass_unit: MassUnit = MassUnit.GRAMS,
    volume_unit: VolumeUnit = VolumeUnit.MILLILITERS
) -> float:
    """
    Calculate % w/v solution.
    Formula: % w/v = (mass in g / volume in mL) × 100
    """
    mass_g = mass * MASS_TO_GRAMS.get(mass_unit, 1)
    volume_mL = volume * VOLUME_TO_LITERS.get(volume_unit, 1) * 1000
    
    if volume_mL == 0:
        return 0.0
    
    return (mass_g / volume_mL) * 100


def calculate_serial_dilution(
    initial_conc: float,
    dilution_factor: float,
    num_dilutions: int,
    conc_unit: ConcentrationUnit = ConcentrationUnit.MOLAR
) -> List[Tuple[int, float, str]]:
    """
    Calculate concentrations for a serial dilution series.
    
    Returns: List of (step_number, concentration, formatted_string)
    """
    results = []
    current_conc = initial_conc
    
    for i in range(num_dilutions + 1):
        results.append((i, current_conc, format_concentration(current_conc * CONC_TO_MOLAR.get(conc_unit, 1))))
        current_conc /= dilution_factor
    
    return results


# --- Recipe/Protocol Scaling ---

@dataclass
class RecipeStep:
    """Represents a single step in a protocol recipe."""
    step_number: int
    reagent_name: str
    amount: float
    amount_unit: str
    notes: str = ""
    
def scale_recipe(
    steps: List[Dict[str, Any]],
    new_total_volume: float,
    old_total_volume: float
) -> List[Dict[str, Any]]:
    """
    Scale all recipe step amounts proportionally when total volume changes.
    
    Args:
        steps: List of recipe step dictionaries with 'amount' key
        new_total_volume: New desired total volume
        old_total_volume: Original total volume
    
    Returns: New list with scaled amounts
    """
    if old_total_volume == 0:
        return steps
    
    scale_factor = new_total_volume / old_total_volume
    scaled_steps = []
    
    for step in steps:
        new_step = step.copy()
        new_step['amount'] = round(step['amount'] * scale_factor, 4)
        scaled_steps.append(new_step)
    
    return scaled_steps


# --- Formatting Helpers ---

def format_mass(mass_g: float) -> str:
    """Format mass with appropriate unit based on magnitude."""
    if mass_g >= 1000:
        return f"{mass_g / 1000:.3f} kg"
    elif mass_g >= 1:
        return f"{mass_g:.3f} g"
    elif mass_g >= 0.001:
        return f"{mass_g * 1000:.3f} mg"
    else:
        return f"{mass_g * 1000000:.3f} µg"


def format_volume(volume_L: float) -> str:
    """Format volume with appropriate unit based on magnitude."""
    if volume_L >= 1:
        return f"{volume_L:.3f} L"
    elif volume_L >= 0.001:
        return f"{volume_L * 1000:.3f} mL"
    else:
        return f"{volume_L * 1000000:.3f} µL"


def format_concentration(conc_M: float) -> str:
    """Format concentration with appropriate unit based on magnitude."""
    if conc_M >= 1:
        return f"{conc_M:.3f} M"
    elif conc_M >= 0.001:
        return f"{conc_M * 1000:.3f} mM"
    elif conc_M >= 0.000001:
        return f"{conc_M * 1000000:.3f} µM"
    else:
        return f"{conc_M * 1000000000:.3f} nM"


# --- Validation Helpers ---

def validate_positive(value: float, name: str) -> None:
    """Raise ValueError if value is not positive."""
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero.")


def validate_purity(purity: float) -> None:
    """Raise ValueError if purity is not between 0 and 100."""
    if not (0 < purity <= 100):
        raise ValueError("Purity must be between 0 and 100%.")
