# GEOG41160– Assignment 2
## Spatial Autocorrelation and Hotspots
## Dublin Extensions Spatial Analysis

## Project Overview
This project creates a Python workflow to analyse where people in Dublin City extend their buildings, 
based on the density of planning applications for extensions by Electoral Division (ED) . 
It also examines global spatial autocorrelation and analyses local clusters and hotspots .
The project uses a shared Python codebase, with each person's contributions visible in the Git history.

## Repository Structure
-`data/` - Input datasets
-`scripts/` - Python scripts for Questions 1,2 and 3
-`outputs/`  - DuckDB working database, derived spatial datasets and maps
-`README.md/` - Project overview, data sources, CRS, workflow and sprint log
-`.gitignore/` - Files and folders Git should ignore 

## Coordinate Reference System (CRS)
The project will use Irish Transverse Mercator(ITM, EPSG:2157), the preferred CRS for spatial analysis in Ireland. 
Source datasets will be reprojected to EPSG:2157 where necessary to ensure consistency throught the project and 
accuracy of spatial analysis .

## Data Sources and Licences
-Planning applications: the Department of Housing, Local Government and Heritage’s Planning Application Points, 
the national database of planning applications from all 31 councils (data.gov.ie,CC BY 4.0), 
at https://data-housinggovie.opendata.arcgis.com/datasets/housinggovie::planning-application-points.
Download date:26 October 2026

-Electoral Divisions: Tailte Éireann’s CSO Electoral Divisions– National Statistical Boundaries
2022– Ungeneralised, all 3,420 EDs (data.gov.ie, CC BY 4.0), at 
https://data-osi.opendata.arcgis.com/datasets/osi::cso-electoral-divisions-national-statistical-boundaries-2022-ungeneralised.
Download date:26 October 2026

## Workflow
The workflow involves 
-collecting and preparing datasets, 
-performing spatial analysis using python scripts
-saving the results in `outputs/`.

Run the scripts in this order

Q1. Extension density
Run `scripts/Q1_ExtensionDensity.py` to map the extension density by Electoral Division. 

Q2. Global spatial autocorrelation
Run `scripts/Q2_GlobalMoran.py` to assess global spatial autocorrelation in extension density.

Q3. Local clusters and hotspots
Run `scripts/Q3_LISA_GiStar.py` to identify local clusters , hotspots and coldspots. 

## Sprint Log

## Sprint 0
**Date:** 25 October 2026

**Completed:** Initial repository setup, folder structure, `.gitignore`, and README.md.

## Sprint 1
**Date:** 26 October 2026 - 28 October 2026

**Completed:** 
Downloaded the source datasets and filtered the planning applications for Dublin City extensions received between 2019 and 2025.
Reprojected the application points layer to EPSG:2157 and performed spatial join with Electoral divisions layer. 
Calculated extension density by ED and saved the result as a GeoPackage. 
Visualized extension density By ED using a chropleth map.

**Next Steps:** Complete Q2.Global spatial autocorrelation in Sprint 2 and Q3.Local clusters and hotspots in Sprint 3.

## Sprint 2
**Date:** 29 - 30th October 2026

**Completed:**
Completed Question 2 (Global Spatial Autocorrelation) using Python. Examined the distribution of building extension density using a histogram and skewness calculations. Tested log and square-root transformations, with the square-root transformation reducing skewness from 1.391 to 0.354. Created Queen contiguity spatial weights for
the 162 Electoral Divisions and calculated Global Moran's I using 9,999 permutations and a fixed random seed of 42. Results showed statistically significant positive spatial autocorrelation, indicating clustering of similar extension-density values across Dublin City. Saved the Python script and histogram in the repository.

**Next Steps:** Complete Q3 (Local Clusters and Hotspots) in Sprint 3.
## Sprint 3
