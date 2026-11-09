
"""
GEOG41160 Assignment 2
Question 3 - Getis-Ord Gi* Hotspot Analysis
Team: 4
"""

# Libraries and path setup

from pathlib import Path
import numpy as np
import geopandas as gpd
from libpysal.weights import Queen
from esda.getisord import G_Local
from esda import fdr

# Setup

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"

SEED = 42
PERMUTATIONS = 9999

INPUT_FILE = OUTPUTS / "DublinED_ExtensionDensity.gpkg"

# Load Dublin Electoral Division data

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found: {INPUT_FILE}"
    )

eds = gpd.read_file(INPUT_FILE)

print("Number of EDs:", len(eds))
print("CRS:", eds.crs)

# Check extension density

print("\nExtension density summary:")
print(eds["extension_density"].describe())

# Square-root transformation from Q2

eds["sqrt_extension_density"] = np.sqrt(
    eds["extension_density"]
)

print("\nSquare-root transformed density:")
print(eds["sqrt_extension_density"].describe())

# Queen contiguity spatial weights

weights = Queen.from_dataframe(
    eds,
    use_index=False
)

print("\nSpatial weights:")
print("Number of EDs:", weights.n)
print("Number of islands:", len(weights.islands))


# Q3.4 - Getis-Ord Gi* analysis
# Calculate Getis-Ord Gi* using square-root transformed density

gi_star = G_Local(
    eds["sqrt_extension_density"].to_numpy(),
    weights,
    transform="B",
    star=True,
    permutations=PERMUTATIONS,
    seed=SEED,
    n_jobs=1
)

# Store Gi* Z-scores
eds["Gi_Z"] = gi_star.Zs

# Calculate two-sided analytical p-values
eds["Gi_p"] = np.minimum(gi_star.p_norm * 2, 1.0)

print("\nGetis-Ord Gi* results:")
print(eds[["Gi_Z", "Gi_p"]].describe())

# Q3.4 - FDR correction and hotspot classification

# Calculate FDR significance threshold at alpha = 0.05
fdr_threshold = fdr(eds["Gi_p"].to_numpy(), alpha=0.05)

print("\nFDR threshold:", fdr_threshold)

# Create Boolean column for FDR significance
eds["Gi_significant"] = eds["Gi_p"] <= fdr_threshold

# Classify hotspots and coldspots
eds["Gi_class"] = "Not Significant"

# Hotspots: positive Z-score and FDR significant
eds.loc[
    (eds["Gi_Z"] > 1.96) & (eds["Gi_significant"]),
    "Gi_class"
] = "Hotspot"

# Coldspots: negative Z-score and FDR significant
eds.loc[
    (eds["Gi_Z"] < -1.96) & (eds["Gi_significant"]),
    "Gi_class"
] = "Coldspot"

# Print classification results
print("\nGi* hotspot classification:")
print(eds["Gi_class"].value_counts())

# Check total number of EDs
print("\nTotal classified EDs:", len(eds))

# Q3.5 - Getis-Ord Gi* hotspot map

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Define colours for hotspot classification
colors = {
    "Hotspot": "#d73027",
    "Coldspot": "#4575b4",
    "Not Significant": "#d9d9d9"
}

# Create map
fig, ax = plt.subplots(figsize=(10, 10))

for category, color in colors.items():
    eds[eds["Gi_class"] == category].plot(
        ax=ax,
        color=color,
        edgecolor="white",
        linewidth=0.3
    )

# Add map title
ax.set_title(
    "Getis-Ord Gi* Hotspots of Extension Density\n"
    "Dublin Electoral Divisions (FDR corrected)",
    fontsize=13,
    pad=20
)

# Add legend
legend_elements = [
    Patch(facecolor=color, label=category)
    for category, color in colors.items()
]

ax.legend(handles=legend_elements, loc="lower left")
ax.set_axis_off()

plt.tight_layout()

# Save map
map_file = OUTPUTS / "Q3_GiStar_Hotspot_Map.png"
plt.savefig(map_file, dpi=300, bbox_inches="tight")

plt.show()

print("Map saved:", map_file)

# Q3.5 - Export Gi* results to GeoPackage

output_file = OUTPUTS / "DublinED_GiStar_Results.gpkg"

eds.to_file(
    output_file,
    layer="GiStar_Results",
    driver="GPKG"
)

print("\nGi* results saved:", output_file)