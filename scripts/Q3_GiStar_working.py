
"""
GEOG41160 Assignment 2
Question 3 - Getis-Ord Gi* Hotspot Analysis
Team: 4
"""

# Libraries
from pathlib import Path
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
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
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

eds = gpd.read_file(INPUT_FILE)

print("Number of EDs:", len(eds))
print("CRS:", eds.crs)


# Square-root transformation 
eds["sqrt_extension_density"] = np.sqrt(
    eds["extension_density"]
)


# Queen contiguity spatial weights
weights = Queen.from_dataframe(
    eds,
    use_index=False
)

print("\nSpatial weights:")
print("Number of EDs:", weights.n)
print("Number of islands:", len(weights.islands))


# Q3.4 - Getis-Ord Gi* analysis
gi_star = G_Local(
    eds["sqrt_extension_density"].to_numpy(),
    weights,
    transform="B",
    star=True,
    permutations=PERMUTATIONS,
    seed=SEED,
    n_jobs=1
)

# Store Z-scores and calculate two-sided analytical p-values
eds["Gi_Z"] = gi_star.Zs
eds["Gi_p"] = np.minimum(gi_star.p_norm * 2, 1.0)

print("\nGetis-Ord Gi* results:")
print(eds[["Gi_Z", "Gi_p"]].describe())


# FDR correction (alpha = 0.05)
fdr_threshold = fdr(
    eds["Gi_p"].to_numpy(),
    alpha=0.05
)

print("\nFDR threshold:", fdr_threshold)

eds["Gi_significant"] = eds["Gi_p"] <= fdr_threshold


# Classify hotspots and coldspots
eds["Gi_class"] = "Not Significant"

eds.loc[
    (eds["Gi_Z"] > 1.96) & (eds["Gi_significant"]),
    "Gi_class"
] = "Hotspot"

eds.loc[
    (eds["Gi_Z"] < -1.96) & (eds["Gi_significant"]),
    "Gi_class"
] = "Coldspot"

print("\nGi* hotspot classification:")
print(eds["Gi_class"].value_counts())
print("Total classified EDs:", len(eds))


# Q3.5 - Create Gi* hotspot map
colors = {
    "Hotspot": "#d73027",
    "Coldspot": "#4575b4",
    "Not Significant": "#d9d9d9"
}

fig, ax = plt.subplots(figsize=(10, 10))

for category, color in colors.items():
    eds[eds["Gi_class"] == category].plot(
        ax=ax,
        color=color,
        edgecolor="white",
        linewidth=0.3
    )

ax.set_title(
    "Getis-Ord Gi* Hotspots of Extension Density\n"
    "Dublin Electoral Divisions (FDR corrected)",
    fontsize=13,
    pad=20
)

legend_elements = [
    Patch(facecolor=color, label=category)
    for category, color in colors.items()
]

ax.legend(handles=legend_elements, loc="lower left")
ax.set_axis_off()

plt.tight_layout()


# Save map
map_file = OUTPUTS / "GiStar_ExtensionDensity_DublinED.png"

plt.savefig(
    map_file,
    dpi=300,
    bbox_inches="tight"
)

print("\nMap saved:", map_file)


# Export Gi* results to GeoPackage
output_file = OUTPUTS / "DublinED_GiStar_Results.gpkg"

eds.to_file(
    output_file,
    layer="GiStar_Results",
    driver="GPKG"
)

print("Gi* results saved:", output_file)


# Display map
plt.show()
