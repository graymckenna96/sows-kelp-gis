# Batch export to csv

import arcpy
import os

try:
    gdb_path = os.path.join(os.getcwd(), "SOWS_deliverables.gdb")
    output_folder = os.path.join(os.getcwd(), "deliverables")  

    arcpy.env.workspace = gdb_path

    # List feature classes and tables
    feature_classes = arcpy.ListFeatureClasses()
    tables = arcpy.ListTables()

    if not feature_classes and not tables:
        print("No data found in geodatabase.")
    else:
        for item in feature_classes + tables:
            out_csv = os.path.join(output_folder, f"{item}.csv")
            print(f"Exporting {item} to {out_csv}")
            arcpy.conversion.TableToTable(item, output_folder, f"{item}.csv")
        print("Export completed.")

except Exception as e:
    print("Error occurred:", e)