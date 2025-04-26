# Summarize SOWS data in geographies of interest
# Gray McKenna 
# Prepared for Puget Sound Restoration Fund

# this script is set up to run in an ArcGIS Pro project folder
# where necessary data is stored in "SOWs.gdb"

# could add some data tidying steps to main function 

# set env -------------------------------------------------
import arcpy
from arcgis import GeoAccessor, GeoSeriesAccessor
import pandas as pd 
import os 

# set path to this project folder and the project gdb
arcpy.env.workspace = os.path.join(os.getcwd(), "SOWs.gdb")
arcpy.env.overwriteOutput = True

# define functions ----------------------------------------

def get_sows_stats(summary_polygons, sows_fc, shoreline_fc):
    """
    Calculate SOW counts, size, spacing, and density in polygons of interest
    Load data into a .gdb and set arcpy.env.workspace to that .gdb
    
    Args:
        summary_polygons: feature class of polygons to summarize sow stats within
        sows_fc: feature class (polygons) of Small Overwater Structures
        shoreline_fc: feature class (line) with single feature defining shoreline
    
    Returns:
        Feature class of polygons 'summary_polygons_sum3' with all stats calculated -- located in env .gdb
    """

    # grab name of input summary polygon fc
    in_polygons_desc = arcpy.Describe(summary_polygons)
    poly_name = in_polygons_desc.name
    in_sows_desc = arcpy.Describe(sows_fc)
    print(f"Calculating statistics for {in_sows_desc.name} within {poly_name}")
    try:
        # get counts and area stats in polygons
        print("Getting SOWS count and area stats within polygons...")
        out_fc_1 = f"{poly_name}_sum1"
        arcpy.analysis.SummarizeWithin(summary_polygons, sows_fc, out_fc_1,
                                        "KEEP_ALL", 
                                        [['Area_M', "Mean"],
                                        ['Area_M', "Sum"],
                                        ['Area_M', "Min"],
                                        ['Area_M', "Max"],
                                        ['Area_M', "Stddev"]])
        print(arcpy.GetMessages())

        # get density by summarizing total length of shoreline in each polygon 
        print("Calculating total shoreline in each polygon...")
        out_fc_2 = f"{poly_name}_sum2"
        arcpy.analysis.SummarizeWithin(out_fc_1, shoreline_fc, out_fc_2,"KEEP_ALL","", "ADD_SHAPE_SUM", "KILOMETERS")
        print(arcpy.GetMessages())
        arcpy.management.AddField(out_fc_2, "density_sows_km", "DOUBLE")

        # get spacing 
        print("Calculating distance between SOWS alongshore...")
        ## get SOWS centroids
        print("Getting SOWS centroids...")
        sows_cent = "sows_centroids"
        arcpy.management.FeatureToPoint(sows_fc, sows_cent, "CENTROID")
        print(arcpy.GetMessages())

        ## snap to nearest shoreline edge
        print("Snapping to nearest shoreline...")
        arcpy.edit.Snap(in_features=sows_cent,
        snap_environment="noaa_shoreline_diss EDGE '500 Unknown'")
        print(arcpy.GetMessages())

        ## split shoreline at points
        print("Splitting shoreline...")
        shore_spl = "shoreline_split"
        arcpy.management.SplitLineAtPoint(shoreline_fc, sows_cent, shore_spl, "1 Feet")
        print(arcpy.GetMessages())

        ## calculate shoreline length in M field
        print("Calculating segment length...")
        arcpy.management.AddField(shore_spl, "sows_dist_km", "DOUBLE")
        arcpy.management.CalculateGeometryAttributes(shore_spl, 
                                                    [["sows_dist_km", "LENGTH"]],
                                                    "KILOMETERS")
        print(arcpy.GetMessages())

        ## select shorelines that are completely within the input polygons
        print("Calculating statistics for distance between SOWS...")
        shore_spl_lyr = "shoreline_lyr"
        arcpy.management.MakeFeatureLayer(shore_spl, shore_spl_lyr)
        arcpy.management.SelectLayerByLocation(shore_spl_lyr, 
                                            "COMPLETELY_WITHIN", 
                                            summary_polygons, "",
                                            "NEW_SELECTION")


        ## copy selected features
        shore_spl_sel = "shorelines_split_select"
        arcpy.analysis.Select(shore_spl_lyr, shore_spl_sel)

        ## summarize Within using selected features
        out_fc_3 = f"{poly_name}_sum3"
        arcpy.analysis.SummarizeWithin(
            in_polygons=out_fc_2,
            in_sum_features=shore_spl_sel,
            out_feature_class=out_fc_3,
            keep_all_polygons="KEEP_ALL",
            sum_fields=[
                ['sows_dist_km', 'Mean'],
                ['sows_dist_km', 'Sum'],
                ['sows_dist_km', 'Min'],
                ['sows_dist_km', 'Max'],
                ['sows_dist_km', 'Stddev']
            ]
        )
        print(arcpy.GetMessages())

        print(f"Analysis for count, size, spacing, and density of SOWS within {poly_name} complete!")
    except Exception as e:
        print("Processing error: ")
        print(arcpy.GetMessages())
        print(e)


# apply functions to geometries of interest ----------------
if __name__ == "__main__":
    sows_fc = "NOAA_SOWS_filtered"
    shoreline_fc = "noaa_shoreline_diss"
    
    subbasins = "Subbasins"
    get_sows_stats(subbasins, sows_fc, shoreline_fc)

    counties = "Counties"
    get_sows_stats(counties, sows_fc, shoreline_fc)

    driftcells = "DriftCells"
    get_sows_stats(driftcells, sows_fc, shoreline_fc)

    shoretypes = "Shoretypes"
    get_sows_stats(shoretypes, sows_fc, shoreline_fc)

    get_sows_stats()





