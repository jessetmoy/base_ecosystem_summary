__author__ = 'Jesse Moy'

import arcpy
import arcpy.sa
import csv
import time
import datetime
from tabulate import tabulate

time_stamp = time.strftime("%Y%m%d_%H%M")
script = 'eco_area_v2'

if arcpy.CheckExtension ('Spatial') == "Available":
    arcpy.CheckOutExtension('Spatial')
else:
    print 'spatial analyst extension unavailable'

# Set workspace
dir = 'W:/Visionmaker_validation/base_eco_statistics'
arcpy.env.workspace = dir
arcpy.env.overwriteOutput = True

# INPUTS
base_ecosystems = 'W:/Visionmaker_validation/VM_base_ecosystems_1m_boroclp.tif'
FAR = 'W:/Visionmaker_validation/VM_FAR_1m_boroclp.tif'
#region_group = 'W:/Visionmaker_validation/base_eco_statistics/eco_count/10m_reggrp'
resolution = raw_input('Enter Grid Resolution : ')

# list of all visonmaker ecosystem ids
eco_ids = [1, 2, 3, 5, 6, 7, 8, 9, 10,
           11, 12, 13, 14, 15, 16, 17,
           18, 19, 20, 21, 22, 23, 24,
           25, 26, 27, 28, 29, 30, 32,
           33, 34, 35, 36, 37, 38, 39,
           40, 41, 43, 44, 45, 46, 47,
           48, 49, 50, 51, 52, 53, 54,
           55, 56, 57, 58, 59, 60, 61,
           62, 63, 64, 65, 66, 67, 68,
           69, 70, 71, 72, 73, 74, 75,
           76, 77, 78, 79, 80, 82, 85,
           86, 87, 88, 89, 90, 91, 92,
           93, 94, 95, 96, 97, 98]

# Set scalar
scalar = int(resolution) ** 2

# CREATE DICTIONARY
eco_summary = {}

for id in eco_ids:
    eco_summary[id] = {'area': 0,
                       'floor_area': 0,
                       'count': 0}

# CALCULATE FOOTPRINT AREA
# Set fields
eco_id = 'Value'
area = 'Count'


# Set search cursor for base_ecosystem raster
eco_cursor = arcpy.SearchCursor(base_ecosystems)

print 'Calculating footprint area for each ecosystem'

# Find ecosystem area and add to eco_summary
# Area is calculated (area = count * scaler)
for row in eco_cursor:
    if row.getValue(eco_id) in eco_summary:
        eco_summary[row.getValue(eco_id)]['area'] = int(row.getValue(area) * scalar)


# CALCULATE ECOSYSTEM COUNTS

# Set search cursor for region_group raster
# count_cursor = arcpy.SearchCursor(region_group)
#
# print 'Calculating counts for each ecosystem'

# Add counts to eco_summary
# for row in count_cursor:
#     if row.getValue('LINK') in eco_summary:
#         eco_summary[row.getValue('LINK')]['count'] += 1

# CALCULATE FLOOR AREA
print 'Calculating floor area for each ecosystem'

# Subset FAR raster by ecosystem type
for id in eco_summary:
    eco_subset_path = (dir + '//eco_far//eco_far_' + str(id))
    eco_subset = arcpy.sa.Con(arcpy.Raster(base_ecosystems) == id, arcpy.Raster(FAR), 0)
    eco_subset.save(eco_subset_path)

# Get FAR subset grids
arcpy.env.workspace = dir + '/eco_far'

subset_grids = arcpy.ListRasters(raster_type = "GRID")

# Iterate through subset grids and calculate floor area
for subset_grid in subset_grids:
    file_name = str(subset_grid)
    eco_id = int(file_name.replace('eco_far_', ''))

    # Set cursor for subset grid
    cursor = arcpy.SearchCursor(subset_grid)

    # calculate floor area per FAR/ecosystem type
    for row in cursor:
        if eco_id in eco_summary:
            bldg_area_per_far = row.getValue('Value') * row.getValue('Count')
            eco_summary[eco_id]['floor_area'] += (bldg_area_per_far * scalar)

arcpy.env.workspace = dir

# OUTPUTS

# Write to CSV
csv_name = dir + '/eco_summary/' + time_stamp + '_eco_summary.csv'
out_csv = open(csv_name, "wb")
writer = csv.DictWriter(out_csv, fieldnames=['id', 'count', 'area', 'floor_area'])

writer.writeheader()
for id in eco_summary:
    writer.writerow({'id': id,
                     'count': eco_summary[id]['count'],
                     'area': eco_summary[id]['area'],
                     'floor_area': eco_summary[id]['floor_area']
                    })

out_csv.close()

# Write to text
# the text file contains:
# 1) Script version
# 2) Date calculated
# 3) List of input grid paths
# 4) Ecosystem summary table (count, area, floor area)

txt_name = dir + '/eco_summary/' + time_stamp + '_eco_summary.txt'
out_text = open(txt_name, 'w')
out_text.write('Base Ecosystem Summary Details \n \n')
out_text.write('Script : %r \n' % script)
out_text.write(str(datetime.datetime.now()) + ('\n \n'))
out_text.write('INPUTS \n')
out_text.write('Base Ecosystem Raster : %r \n' % base_ecosystems)
out_text.write('FAR Raster : %r \n' % FAR)
# out_text.write('Region Group Raster : %r \n' % region_group)
out_text.write('Grid Resolution : %r m sq \n \n' % str(resolution))

rows = []
for i in eco_summary:
    rows.append([i, eco_summary[i]['count'],eco_summary[i]['area'], eco_summary[i]['floor_area']])

out_text.write(tabulate(rows, headers= ['ECO ID', 'COUNT', 'FOOTPRINT AREA', 'FLOOR AREA'], tablefmt='psql'))

out_text.close()

print 'Calculations complete'