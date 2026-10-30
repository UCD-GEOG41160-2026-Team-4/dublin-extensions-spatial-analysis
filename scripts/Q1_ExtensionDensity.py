"""
GEOG41160 Assignment 2, Question 1: Extension density by ED
Team: 4

ANSWERS
Question 1:

1. Filtering:
   Planning applications:
   ------------------------------------------------------------
   Filtering condition                         Records remaining
   ------------------------------------------------------------
   Original dataset                            510,390
   Dublin City Council                         24,879
   Received year 2019-2025                     23,176
   Description contains "extension"            9,914
   ------------------------------------------------------------

   Electoral Divisions (EDs):
   ------------------------------------------------------------
   Filtering condition                         Records remaining
   ------------------------------------------------------------
   Original dataset                            3,420
   Dublin City                                 162
   ------------------------------------------------------------

2. Feature count, CRS and geometry type:
                Dataset	                     | Feature count |	       CRS	          |  Geometry type
---------------------------------------------|---------------|------------------------|-----------------
Dublin City Electoral Divisions (eds_dublin) |	   162	     | EPSG:2157 (ITM)	      |  MULTIPOLYGON
Planning extensions (planning_extension)	 |    9,914	     |EPSG:3857 (Web Mercator)|  POINT

Irish Transverse Mercator (EPSG:2157) is a projected CRS designed for Ireland and is more suitable 
for accurate measurements than Web Mercator (EPSG:3857), which distorts distances and areas.
Reprojecting the planning extensions layer to EPSG:2157, ensures both layers 
use the same CRS for the spatial join and allows more accurate area-based density calculations. 

3. Spatial join and Extension counts by ED:
Result	                      | Count
-------------------------------------------
Total filtered extensions	  |  9,914
Electoral Divisions	          |  162

Extensions assigned to EDs	  |  9,900
Extensions outside every ED	  |  14

Of the 9,914 filtered planning extension applications, 9,900 were assigned to the 162 Electoral Divisions, 
while 14 fell outside every ED. The 14 unmatched points neither lay within nor intersected any ED polygon, 
based on the `ST_Within()` and `ST_Intersects()` checks. Therefore, those 14 points fall outside the spatial 
extent of the ED polygons and could not be assigned to an ED by the spatial join. 

4.Calculate extension density by Electoral Division
The extension application density was calculated by dividing the number of extension applications in each ED 
by its area in square kilometres.The results were saved as `DublinED_ExtensionDensity.gpkg`.

5. Map extension density
A map was created to visualise extension application density across Dublin City EDs for 2019-2025,
using five quantile classes and Blues color scheme. 
The  choropleth map was saved as `ExtensionDensity_DublinED.png`.
"""

#1.Filtering
#Setup the paths

from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]     
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(parents=True, exist_ok=True)

PLANNING= DATA/"planning"/"planning_applications_national.gpkg"
EDS=DATA/"boundaries"/"eds_national.gpkg"
DATABASE=OUTPUTS/"extensions.duckdb"

#Check the input paths 
print("Project root:",ROOT)
print("Planning file exists:",PLANNING.exists())
print("EDS file exists:",EDS.exists())

if not PLANNING.exists():
    raise FileNotFoundError(f"Planning file not found:{PLANNING}")
if not EDS.exists():
    raise FileNotFoundError(f"EDS file not found:{EDS}")

#Create the database and add the spatial functions
import duckdb

con=duckdb.connect(DATABASE)

con.install_extension("spatial")
con.load_extension("spatial")

print("DuckDB databse:",DATABASE)
print("Spatial extension loaded successfully")

# Load geopackages into DuckDB
con.sql(f"""CREATE OR REPLACE TABLE planning AS
            SELECT *FROM ST_Read('{PLANNING}')""")

con.sql(f"""CREATE OR REPLACE TABLE eds AS
            SELECT * FROM ST_Read('{EDS}')""")

print("Planning table created")
print(con.sql("SELECT COUNT(*) FROM planning"))

print("EDS table created")
print(con.sql("SELECT COUNT(*) FROM eds"))

#Filter ED to Dublin City 
con.sql("""CREATE OR REPLACE TABLE eds_dublin AS
           SELECT * FROM eds
           WHERE COUNTY_ENGLISH = 'DUBLIN CITY' """)

print("Dublin city ED count :",con.sql("SELECT COUNT(*) FROM eds_dublin"))

#Filter Planning applications by 
## Planning Authority
con.sql("""CREATE OR REPLACE TABLE planning_auth AS
           SELECT * FROM planning
           WHERE PlanningAuthority='Dublin City Council' """)

print("After Planning Authority filter:",con.sql("SELECT COUNT(*) FROM planning_auth"))

##Received year 2019-2025
con.sql("""CREATE OR REPLACE TABLE planning_auth_year AS
           SELECT * FROM planning_auth
           WHERE year(ReceivedDate) BETWEEN 2019 AND 2025""")

print("After year filter:",con.sql("SELECT COUNT(*) FROM planning_auth_year"))

##Development Description containing "extension"
con.sql("""CREATE OR REPLACE TABLE planning_extension AS
           SELECT * FROM planning_auth_year
           WHERE DevelopmentDescription ILIKE '%extension%' """)

print("After description extension filter:",con.sql("SELECT COUNT(*) FROM planning_extension"))

#2.Feature count,CRS,geometry and Reprojection
#Feature count
print ("Number of features of Dublin City ED:",con.sql("SELECT COUNT(*) FROM eds_dublin"))
print ("Number of features of Planning extension:",con.sql("SELECT COUNT(*) FROM planning_extension"))

# CRS 
print("Dublin City ED schema:",con.sql("DESCRIBE eds_dublin"))
print("CRS of Dublin City ED:EPSG:2157")
print("Planning extension schema:",con.sql("DESCRIBE planning_extension"))
print("CRS of Planning extension:EPSG:3857")

#Geometry 
print("Geometry type of Dublin City ED :")
print(con.sql("""SELECT DISTINCT ST_GeometryType(SHAPE)
                 FROM eds_dublin """))
print("Geometry type of Planning extension:")
print(con.sql("""SELECT DISTINCT ST_GeometryType(SHAPE)
                 FROM planning_extension """))

#Reproject Planning extensions to EPSG:2157
con.sql("""CREATE OR REPLACE TABLE planning_extension_itm AS
           SELECT * EXCLUDE(SHAPE),ST_Transform(SHAPE,'EPSG:3857','EPSG:2157',always_xy:=true) AS SHAPE
           FROM planning_extension """)
print ("Number of reprojected planning extensions:",con.sql("SELECT COUNT(*) FROM planning_extension_itm"))

#3.Spatial join 
# Inspect columns before the spatial join
print("Electoral Division columns:")
print(con.sql("DESCRIBE eds_dublin"))

print("Planning extension columns:")
print(con.sql("DESCRIBE planning_extension_itm"))

#Spatial join : count extensions in each ED 
con.sql("""CREATE OR REPLACE TABLE ed_extension_counts AS
           SELECT ed.ED_ENGLISH,ed.SHAPE,COUNT(p.ApplicationNumber) AS extension_count
           FROM eds_dublin AS ed
           LEFT JOIN planning_extension_itm AS p ON ST_Within(p.SHAPE,ed.SHAPE)
           GROUP BY ed.ED_ENGLISH,ed.SHAPE""")

# Display summary and extension counts for each ED
print("Number of EDs and total extensions:")
print(con.sql("""SELECT COUNT(*) AS number_of_EDs,
                   SUM(extension_count) AS total_extensions
                 FROM ed_extension_counts """))

print("Number of extensions per ED:")
print(con.sql("""SELECT ED_ENGLISH, extension_count
                 FROM ed_extension_counts
                 ORDER BY extension_count DESC"""))

#Count extensions outside all EDs
print("Extensions not within any ED:")
print(con.sql("""SELECT COUNT(*) AS unmatched_extensions
                 FROM planning_extension_itm AS p
                 WHERE NOT EXISTS(SELECT 1
                                  FROM eds_dublin AS ed
                                  WHERE ST_Within(p.SHAPE,ed.SHAPE)) """))

#Inspection of unmatched extensions 
print("Spatial checks of unmatched extensions:")

print(con.sql("""
    SELECT
        CASE
            WHEN EXISTS (SELECT 1
                         FROM eds_dublin AS ed
                         WHERE ST_Intersects(p.SHAPE, ed.SHAPE))
            THEN 'Intersects an ED boundary'
            ELSE 'Outside all EDs'
        END AS spatial_relationship,
        COUNT(*) AS number_of_extensions
    FROM planning_extension_itm AS p
    WHERE NOT EXISTS (SELECT 1
                      FROM eds_dublin AS ed
                      WHERE ST_Within(p.SHAPE, ed.SHAPE))
    GROUP BY spatial_relationship"""))

#4.Calculate Extension Density by Electoral Division
#Retrieve ED extension counts from the database
df=con.sql("""SELECT ED_ENGLISH, extension_count, ST_AsWKB(SHAPE) AS wkb
              FROM ed_extension_counts""").df()

print("ED extension counts retrieved from the databse:")
print(df.head())
print("Number of EDs:",len(df))

#Convert Dataframe to GeoDataFrame
eds_gdf=gpd.GeoDataFrame(df.drop(columns="wkb"),geometry=gpd.GeoSeries.from_wkb(df["wkb"].apply(bytes)),crs="EPSG:2157")

print("ED extension counts converted to a GeoDataFrame:")
print(eds_gdf.head())
print("CRS:",eds_gdf.crs)
print("Number of EDs:",len(eds_gdf))

#Calculate area and extension density
eds_gdf["area_km2"]=eds_gdf.geometry.area/1e6
eds_gdf["extension_density"]=(eds_gdf["extension_count"]/eds_gdf["area_km2"])

print("Extension density calculated for each ED:")
print(eds_gdf[["ED_ENGLISH","extension_count","area_km2","extension_density"]].head())

#Save extension density results as a Geopackage
density_output=OUTPUTS/"DublinED_ExtensionDensity.gpkg"
eds_gdf.to_file(density_output,driver="GPKG")
print("Extension density GeoPackage saved :",density_output)

#5.Map the Extension Density 
ax=eds_gdf.plot(column="extension_density",scheme="Quantiles",k=5,cmap="Blues",edgecolor="grey",
                linewidth=0.3,figsize=(7,6),legend=True,legend_kwds={"title":"Applications per km²","fmt":"{:.0f}","loc":"lower right"})
ax.set_title("Extension Application Density, Dublin City EDs, 2019-2025",fontsize=14,pad=15)
ax.set_axis_off()
plt.savefig(OUTPUTS/"ExtensionDensity_DublinED.png",dpi=180,bbox_inches="tight",facecolor="white")
plt.show()



















