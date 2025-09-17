"""Mining-specific tools for the geodata chatbot agent."""

import random

from langchain_core.tools import tool


@tool
def analyze_ore_composition() -> str:
    """Analyze the mineral composition at a specific location in the mine."""
    ore_types = ["Iron Ore", "Copper", "Gold", "Silver", "Coal", "Limestone"]
    purity = random.uniform(45.0, 95.0)
    ore_type = random.choice(ore_types)
    return (f"{ore_type} detected with "
            f"{purity:.1f}% purity")


@tool
def measure_tunnel_stability() -> str:
    """Measure structural stability of mine tunnels."""
    stability_score = random.uniform(65.0, 98.0)
    risk_level = "LOW" if stability_score > 85 else "MEDIUM" if (
            stability_score > 70) else "HIGH"
    return (f"Stability score {stability_score:.1f}% "
            f"- Risk level: {risk_level}")


@tool
def detect_gas_levels() -> str:
    """Monitor dangerous gas concentrations in mining areas."""
    gases = {
        "Methane": random.uniform(0.1, 2.5),
        "Carbon Monoxide": random.uniform(0.05, 1.2),
        "Hydrogen Sulfide": random.uniform(0.01, 0.8)
    }
    status = "SAFE" if all(
        level < 1.0 for level in gases.values()) else "CAUTION"
    gas_readings = ", ".join(
        [f"{gas}: {level:.2f}ppm" for gas, level in gases.items()])
    return f"Gas levels: {gas_readings} - Status: {status}"


@tool
def calculate_ore_reserves() -> str:
    """Estimate remaining ore reserves in different mine sections."""
    sections = ["North Wing", "South Wing", "Deep Shaft", "Main Vein"]
    reserves = {}
    total_reserves = 0

    for section in sections:
        reserve_amount = random.uniform(1500, 8500)  # tons
        reserves[section] = reserve_amount
        total_reserves += reserve_amount

    section_details = ", ".join([f"{section}: {amount:.0f} tons"
                                for section, amount in reserves.items()])
    return (f"Estimated ore reserves - {section_details}. "
            f"Total: {total_reserves:.0f} tons")


@tool
def monitor_equipment_status() -> str:
    """Check operational status of mining equipment."""
    equipment = {
        "Excavator-A": random.choice(["OPERATIONAL", "MAINTENANCE", "OFFLINE"]),
        "Conveyor-1": random.choice(["OPERATIONAL", "SLOW", "STOPPED"]),
        "Drill-B": random.choice(["OPERATIONAL", "MAINTENANCE", "OPERATIONAL"]),
        "Ventilation": random.choice(["OPERATIONAL", "REDUCED", "OPERATIONAL"]),
        "Water Pump": random.choice(["OPERATIONAL", "MAINTENANCE", "OPERATIONAL"])
    }

    operational_count = sum(1 for status in equipment.values() if status == "OPERATIONAL")
    total_count = len(equipment)

    equipment_details = ", ".join([f"{name}: {status}"
                                  for name, status in equipment.items()])
    return (f"Equipment status - {equipment_details}. "
            f"Operational: {operational_count}/{total_count}")


# List of all mining tools for easy import
MINING_TOOLS = [
    analyze_ore_composition,
    measure_tunnel_stability,
    detect_gas_levels,
    calculate_ore_reserves,
    monitor_equipment_status
]