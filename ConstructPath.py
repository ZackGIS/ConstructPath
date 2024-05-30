import arcpy
import csv


# Function to add polylines to the shapefile. The function defines a polyline object and uses the InsertCursor to
# add rows in the attribute table for polyline and the lap number. This can be expanded for lap times associated with
# each lap and other features as well.
def addPolyline(cursor, array, sr, lapNum, lapTime):
    polyline = arcpy.Polyline(array, sr, lapNum, lapTime)
    cursor.insertRow((polyline, lapNum, lapTime))
    array.removeAll()


# The input CSV file location
inCSV = "C:/PSUGIS/GEOG485/GEOG485Lesson4/WakefieldParkRaceway_20160421.csv"

# The workspace location.
arcpy.env.workspace = "C:/PSUGIS/GEOG485/GEOG485Lesson4"

# The name of the shapefile we will create.
polylineFC = "tracklines.shp"
# Check to see if a feature class by the same name already exists. If so delete it.
if arcpy.Exists(polylineFC):
    arcpy.Delete_management(polylineFC)
# Defining a spatial reference object called SR to be passed in when the shapefile is created.
SR = arcpy.SpatialReference("GCS_WGS_1984")
# Creating the shapefile.
arcpy.CreateFeatureclass_management(arcpy.env.workspace, polylineFC, "POLYLINE", spatial_reference=SR)
# Adding a SHORT field called LAPS into the shapefile to keep track of the lap number associated with each polyline.
arcpy.AddField_management(polylineFC, "LAPS", "SHORT")
# Adding a field to display the lap time for each polyline.
arcpy.AddField_management(polylineFC, "LapTime", "TEXT")
# The spatial reference data to be passed into the addPolyline function will be the same as the shapefile.
desc = arcpy.Describe(polylineFC)
spatialRef = desc.spatialReference

# Open the .csv file.
with open(inCSV, "r") as gpsTrack:
    # Declaring a DictReader object. We're interested in the Lap values (keys) and the lon/lat values (value pairs).
    csvReader = csv.DictReader(gpsTrack, delimiter=",")
    try:
        # Using the InsertCursor to insert data into three fields. One for the polyline, the lap number, and lap time.
        with arcpy.da.InsertCursor(polylineFC, ["SHAPE@", "LAPS", "LapTime"]) as polylineCursor:
            # Declare the vertexArray after beginning the InsertCursor.
            vertexArray = arcpy.Array([])

            for row in csvReader:
                # Check if lap contains the data
                if row['Lap'] is not None:
                    # lap will be the key in the dictionary
                    lap = row['Lap']
                    # coordlist will be the value
                    coordlist = [float(row['Latitude']), float(row['Longitude'])]
                    # declare the dictionary object
                    lapCoordDict = {lap: coordlist}
                    # latitude is the 0 index of the coordlist
                    lat = coordlist[0]
                    # longitude is the 1 index
                    lon = coordlist[1]
                    # Append the vertexArray with the point. It's written (lon, lat) because the csv reversed them.
                    vertexArray.append(arcpy.Point(lon, lat))
                # If the data we're seeking for lap is not found that means it's the end of the current lap.
                else:
                    # time is set to row 'Time' in the attribute table.
                    time = row['Time']
                    # Check to see if it is the first or final lap. We don't want those in the attribute table.
                    if lap != "0" and lap != "6":
                        # Check to see if the vertexArray already has a point. If it does, add the polyline and
                        # associated fields.
                        if vertexArray.count > 0:
                            addPolyline(polylineCursor, vertexArray, spatialRef, lap, time)

    except arcpy.ExecuteError:
        print(arcpy.GetMessages("Something went terribly wrong!"))
