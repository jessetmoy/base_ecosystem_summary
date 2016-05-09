import arcpy
import arcpy.sa
import time
import os



time_stamp = time.strftime("%Y%m%d_%H%M")
script = 'eco_area_v2'

if arcpy.CheckExtension ('Spatial') == "Available":
    arcpy.CheckOutExtension('Spatial')
else:
    print 'spatial analyst extension unavailable'

# Set workspace
ROOT_DIR = os.path.join('D:\\', '_data', 'Visonmaker', 'Visionmaker_validation', 'base_ecosystem_summary')
arcpy.env.workspace = ROOT_DIR
arcpy.env.overwriteOutput = True

INPUT_DIR = os.path.join(ROOT_DIR, 'inputs')
BASE_ECOSYSTEMS = os.path.join(INPUT_DIR, '20151108_1m_base_ecosystems.tif')
FAR = os.path.join(INPUT_DIR, '20150820_1m baseecosystems_FAR.tif')
REGION_GROUP = os.path.join(INPUT_DIR, '20151108_1m_base_ecosystem_region_group.tif')

borough_boundaries = os.path.join(INPUT_DIR, 'nybbwi.shp')

cursor = arcpy.SearchCursor(borough_boundaries)

for feature in cursor:
    print feature.BoroName

    base_ecosystems = os.path.join(INPUT_DIR, feature.BoroName, '%s_base_ecosystem_1m.tif' % feature.BoroCode)
    arcpy.Clip_management(in_raster=BASE_ECOSYSTEMS,
                          out_raster=base_ecosystems,
                          in_template_dataset=feature.Shape,
                          clipping_geometry='ClippingGeometry')

    far = os.path.join(INPUT_DIR, feature.BoroName, '%s_far_1m.tif' % feature.BoroCode)
    arcpy.Clip_management(in_raster=FAR,
                          out_raster=far,
                          in_template_dataset=feature.Shape,
                          clipping_geometry='ClippingGeometry')

    region_group = os.path.join(INPUT_DIR, feature.BoroName, '%s_region_group_1m.tif' % feature.BoroCode)
    arcpy.Clip_management(in_raster=REGION_GROUP,
                          out_raster=region_group,
                          in_template_dataset=feature.Shape,
                          clipping_geometry='ClippingGeometry')