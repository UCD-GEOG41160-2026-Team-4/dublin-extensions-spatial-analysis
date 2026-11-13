
"""
GEOG41160 Assignment 2 Team 4
Question 2: Global Spatial Autocorrelation

1. Distribution:
   A histogram was used to examine the distribution of extension
   density. The distribution was positively skewed (skewness = 1.391).
   A square-root transformation reduced skewness to 0.354, making
   the distribution more symmetrical. A log transformation increased
   the absolute skewness to 1.530, so the square-root transformation
   was preferred.

2. Spatial weights:
   Queen contiguity weights were used because Electoral Divisions
   sharing an edge or corner were treated as neighbours. This provides
   a geographic definition of neighbouring EDs. The weights were
   row-standardised so each ED's neighbour weights sum to one.
   All 162 EDs had at least one neighbour.

3. Global Moran's I:
   Original density: I = 0.3319, permutation p = 0.0001.
   Square-root-transformed density: I = 0.3751,
   permutation p = 0.0001.
   The log-transformed result was also calculated for comparison:
   I = 0.3516, permutation p = 0.0001.
   Each result used 9,999 permutations and a fixed random seed of 42.

4. Interpretation:
   All three Moran's I values were positive and statistically
   significant, indicating clustering of similar extension-density
   values across Dublin Electoral Divisions. The conclusion did not
   change after transformation. The square-root transformation
   reduced skewness most effectively, although Moran's I increased
   slightly after transformation.

"""
# Import tools for working with file paths
from pathlib import Path

# Find the main project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Define the location of the Question 1 output
DENSITY_FILE = PROJECT_DIR / "outputs" / "DublinED_ExtensionDensity.gpkg"

# Display the paths
print("Project folder:", PROJECT_DIR)
print("Density file:", DENSITY_FILE)
print("Does the density file exist?", DENSITY_FILE.exists())

# Check the packages are installed
import importlib.util

packages = [
    "geopandas",
    "pandas",
    "matplotlib",
    "libpysal",
    "esda",
    "pyogrio"
]

for package in packages:
    if importlib.util.find_spec(package):
        print(package, "- installed")
    else:
        print(package, "- NOT installed")
        
# Import GeoPandas to read the geographic data
import geopandas as gpd

# Load the Task 1 output
density_data = gpd.read_file(DENSITY_FILE)

# Import tools for spatial autocorrelation
import numpy as np
from libpysal.weights import Queen
from esda.moran import Moran

# Set the random seed for reproducible results
SEED = 42
np.random.seed(SEED)

# Number of random permutations for Moran's I
PERMUTATIONS = 9999

# Display the first five rows
print("\nFirst five rows of the density data:")
print(density_data.head())

# Display the column names
print("\nColumn names:")
print(density_data.columns.tolist())

# Display the number of Electoral Divisions
print("\nNumber of Electoral Divisions:", len(density_data))

# Check the distribution of extension density
import matplotlib.pyplot as plt

# Remove any missing density values
density_values = density_data["extension_density"].dropna()

# Print summary statistics
print("\nExtension density summary:")
print(density_values.describe())

# Calculate skewness
print("\nSkewness:", density_values.skew())

# Create a histogram
plt.figure(figsize=(8, 5))
plt.hist(density_values, bins=20, edgecolor="black")
plt.xlabel("Extension density")
plt.ylabel("Number of Electoral Divisions")
plt.title("Distribution of Extension Density across Dublin EDs")
plt.tight_layout()
plt.savefig(
    PROJECT_DIR / "outputs" / "Q2_ExtensionDensity_Histogram.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

# Create a natural log-transformed density variable
import numpy as np

density_data["log_extension_density"] = np.log(
    density_data["extension_density"]
)

# Check the transformed distribution
print("\nLog-transformed density summary:")
print(density_data["log_extension_density"].describe())

print(
    "\nLog-transformed skewness:",
    density_data["log_extension_density"].skew()
)

# Plot the transformed distribution
plt.figure(figsize=(8, 5))
plt.hist(
    density_data["log_extension_density"].dropna(),
    bins=20,
    edgecolor="black"
)
plt.xlabel("Log-transformed extension density")
plt.ylabel("Number of Electoral Divisions")
plt.title("Distribution of Log-Transformed Extension Density")
plt.tight_layout()
plt.show()

# Prepare spatial weights for Global Moran's I
from libpysal.weights import Queen

# Give each Electoral Division an ID
density_data = density_data.reset_index(drop=True)

# Create Queen contiguity spatial weights
weights = Queen.from_dataframe(density_data, use_index=False)

# Row-standardise the weights
weights.transform = "R"

# Print information about the spatial weights
print("\nSpatial weights information:")
print("Number of EDs:", len(density_data))
print("Number of EDs in weights:", weights.n)
print(
    "Number of neighbour pairs:",
    sum(len(n) for n in weights.neighbors.values()) // 2
)
print("Number of EDs with no neighbours:", len(weights.islands))
print("EDs with no neighbours:", weights.islands)

# Calculate Global Moran's I
from esda.moran import Moran

# Set a fixed random seed for reproducible results
SEED = 42
np.random.seed(SEED)
PERMUTATIONS = 9999

# Get the original and log-transformed values
raw_values = density_data["extension_density"].to_numpy()
log_values = density_data["log_extension_density"].to_numpy()

# Calculate Moran's I for original density
moran_log = Moran(
    log_values,
    weights,
    transformation="R",
    permutations=PERMUTATIONS,
)

# Calculate Moran's I for log-transformed density
moran_raw = Moran(
    raw_values,
    weights,
    transformation="R",
    permutations=PERMUTATIONS,
)

# Print the results
print("\nGLOBAL MORAN'S I RESULTS")

print("\nOriginal extension density:")
print("Moran's I:", moran_raw.I)
print("Permutation p-value:", moran_raw.p_sim)

print("\nLog-transformed extension density:")
print("Moran's I:", moran_log.I)
print("Permutation p-value:", moran_log.p_sim)

# Test a square-root transformation
density_data["sqrt_extension_density"] = np.sqrt(
    density_data["extension_density"]
)

print(
    "\nSquare-root transformed skewness:",
    density_data["sqrt_extension_density"].skew()
)

# Calculate Global Moran's I for square-root-transformed density
sqrt_values = density_data["sqrt_extension_density"].to_numpy()

moran_sqrt = Moran(
    sqrt_values,
    weights,
    transformation="R",
    permutations=PERMUTATIONS,
)

print("\nSquare-root-transformed extension density:")
print("Moran's I:", moran_sqrt.I)
print("Permutation p-value:", moran_sqrt.p_sim)
