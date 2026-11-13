
"""
GEOG41160 Assignment 2, Question 3-Local clusters and hotspots
Team:4

ANSWERS:

Question 1:
Calculate Local moran's I

ED Count: 162
Average Local moran's I:0.3728
Local moran's I Min:-1.1618
Local moran's I Max:3.7255
EDs with significant local autocorrelation(p≤0.05):54
EDs with insignificant local autocorrelation:108
Number of permutations:9,999
Seed value for the random number generator:42

Using the Local Moran’s I index to detect the existence of local clusters and spatial outliers for extension density values, it was possible to identify spatial autocorrelation, with a positive mean value (0.3728) showing a concentration of similar values of extension density for neighbouring EDs.

Question 2: 
FDR correction

FDR threshold:0.00679
Significant EDs before correction:54
Significant EDs after correction:22

Significant EDs were reduced from 54 to 22 by applying Benjamini-Hochberg. After this correction, false positives were more likely to be reduced. These 22 EDs were used to identify the statistically significant clusters in the LISA map.

Question 3:
LISA cluster map

High-High:10
Low-High:2
Low-Low:10
High-Low:0
Not significant:140
Total:162

There are 10 clusters of EDs with both high extension density and another 10 clusters with low extension density. Out of 162 EDs in Dublin City, 140 were found to not have a statistically significant spatial correlation. The remaining 22 EDs (around 14%) include 10 High-High clusters, 10 Low-Low clusters, 2 Low-High outliers, and no High-Low outliers.

Q4-Getis-Ord Gi*
Q5-FDR correction
Q6-Comparison of LISA and Gi*
"""

#libraries and path setup

from pathlib import Path
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from libpysal.weights import Queen
from esda.moran import Moran_Local
from esda import fdr

ROOT=Path(__file__).resolve().parents[1]
OUTPUTS=ROOT / "outputs"
OUTPUTS.mkdir(exist_ok=True)
SEED=42
PERMUTATIONS=9999
INPUT_FILE=OUTPUTS/"DublinED_ExtensionDensity.gpkg"

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")
eds=gpd.read_file(INPUT_FILE)
print("Number of EDs:",len(eds))
print("CRS:",eds.crs)

#Square root transformation from Q2
eds["sqrt_extension_density"]=np.sqrt(eds["extension_density"])

#Queen contiguity weights
w=Queen.from_dataframe(eds, use_index=False)
w.transform="R"
print("Number of spatial weights:",w.n)
print("Number of islands:",len(w.islands))
print("Weights transformation:",w.transform)


#1.Local moran's I

#calculation
lisa=Moran_Local(eds["sqrt_extension_density"],w,transformation="R",permutations=PERMUTATIONS,seed=SEED)
print("LISA quadrant values:", np.unique(lisa.q, return_counts=True))

#Storing local moran's I and P values
eds["local_moran_i"]=lisa.Is
eds["p_value"]=lisa.p_sim
print("\nQ3.1 - Local Moran's I")
print("Mean Local Moran's I:",lisa.Is.mean())
print("Minimum Local Moran's I:",lisa.Is.min())
print("Maximum Local Moran's I:",lisa.Is.max())

#Count significant EDs for p<=0.05
significant=eds["p_value"]<=0.05
print("Significant EDs (p <= 0.05):",significant.sum())
print("Non-significant EDs:",(~significant).sum())


#2.FDR correction

#Apply FDR correction
fdr_threshold = fdr(lisa.p_sim, alpha=0.05)

eds["fdr_significant"] = lisa.p_sim <= fdr_threshold
print("\nQ3.2 - FDR Correction")
print("FDR threshold:", fdr_threshold)
print("Significant EDs before FDR:", (lisa.p_sim <= 0.05).sum())
print("Significant EDs after FDR:", eds["fdr_significant"].sum())


#3.LISA cluster map

#cluster categories
cluster_labels = {1:"High-High",2:"Low-High",3:"Low-Low",4:"High-Low"}

#Assign cluster categories using FDR significance
eds["LISA_cluster"]=[cluster_labels[q] if sig else "Not Significant"for q,sig in zip(lisa.q, eds["fdr_significant"])]

#Print quadrant values 
print("Significant quadrant values:",np.unique(lisa.q[eds["fdr_significant"].to_numpy()],return_counts=True))

#Print cluster counts
print("\nQ3.3 - LISA Cluster Counts")
print(eds["LISA_cluster"].value_counts())

#Plot LISA cluster map
fig,ax=plt.subplots(1,1,figsize=(12,10))
eds.plot(column="LISA_cluster",categorical=True,legend=True,linewidth=0.2,edgecolor="black",ax=ax)
ax.set_title("LISA Cluster Map of Extension Density in Dublin City",fontsize=14)
ax.set_axis_off()
plt.tight_layout()

#Save map
map_file = OUTPUTS/"LISA_ExtensionDensity_DublinED.png"
plt.savefig(map_file, dpi=300, bbox_inches="tight")
plt.show()
print("LISA map saved to:", map_file)

# Export LISA results for Q3.6 comparison
output_file = OUTPUTS / "DublinED_LISA_Results.gpkg"
eds.to_file(output_file,driver="GPKG")
print("LISA results saved:",output_file)
