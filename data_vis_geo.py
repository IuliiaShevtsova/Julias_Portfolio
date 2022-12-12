
#########################
#DATA VISUALISATION
########################
"""
1. Rasterio
2. Fiona
3.GDAL

"""

#-----------------------------------
# Raster data analysis with RasterIO
#-----------------------------------
import rasterio

#check versiion
rasterio.__version__
#path and name of the file
path_raster = r'/Users/iuliiashevtsova/Documents/Python_stuff/srtm_germany_dtm.tif'
#open raster
raster = rasterio.open(path_raster)
#convert to an array
data_rs = raster.read()
data_rs

raster.meta
"""What you see:
{'driver': 'GTiff',
 'dtype': 'int16',
 'nodata': None,
 'width': 13201,
 'height': 10801,
 'count': 1,---------------------one band
 'crs': CRS.from_epsg(4326),-----coordinate system
 'transform': Affine(0.0008333333333333301, 0.0, 4.999583333333334,
        0.0, -0.0008333333333333301, 56.000416666666666)}
"""
raster.name#path to file
raster.count#band number
raster.shape#(rows, columns)
raster.driver
raster.crs#coordinated system
raster.transform
raster.descriptions

data_rs.size#byte size
data_rs.dtype#data type
data_rs.min()#min value
data_rs.max()#max value
#combine in a function to see all meta data for a file

"""
print('--Quick statistics--')
print('min value:',data_rs.min())
print('max value:',data_rs.max())
print('mean value:', data_rs.mean())
print('standard deviation:', data_rs.std())
"""

#FUNCTION TO RETRIEVE ALL VALUABLE META DATA
def meta_full(r):
    #path and name of the file
    pr = r
    #open raster
    raster = rasterio.open(pr)
    #convert to an array
    data_rs = raster.read()
    
    print('driver:', raster.driver)
    print('CRS:', raster.crs)
    print('image resolution:', raster.height, "x", raster.width)
    print('transformation:', raster.transform)
    print('number of bands:', raster.count)
    print('number of rows:',raster.shape[0],' and columns:', raster.shape[1])
    print('size in bytes:',data_rs.size)
    print('data type:',data_rs.dtype)
    if raster.nodatavals==(None,):
        print('nodata values: None')
    else:
        print('nodata values under:', raster.nodata)
        print('--Quick statistics--')
        print('Unavailable due to presence of NA values')
        
a = r'/Users/iuliiashevtsova/Documents/Python_stuff/srtm_germany_dtm.tif'    
b = r'/Users/iuliiashevtsova/Documents/Python_stuff/DEM_crropped.tiff'

meta_full(a)#example with no NAs
meta_full(b)#example with NAs

#Visualising data
from rasterio.plot import show#, show_hist

def visual_data(r):
    #path and name of the file
    pr = r
    #open raster
    raster = rasterio.open(pr)
    
    #show the image of raster
    if raster.nodatavals==(None,):
        show(raster, cmap="turbo", title="DEM")
    else:
        show(raster, cmap="gist_earth", title="DEM")
    #show_hist(raster, bins=50, title="DEM")


visual_data(b)

#Statistics
raster = rasterio.open(b)
raster.tags(1)#band number
raster.tags(2)
raster.tags(3)
raster.tags(4)

#-----------------------------------
# Shapefiles with Fiona
#-----------------------------------
import fiona
from shapely.geometry import Polygon,mapping
import matplotlib.pyplot as plt
from descartes import PolygonPatch

#open clip layer
aoi = fiona.open('/Users/iuliiashevtsova/Documents/Python_stuff/AOI.shp')
aoiGeom = Polygon(aoi[0]['geometry']['coordinates'][0])

#open polygon and create list of Polygons
polyShp = fiona.open('/Users/iuliiashevtsova/Documents/Python_stuff/hills.shp')
polyList = []
polyProperties = []
for poly in polyShp:
    polyGeom = Polygon(poly['geometry']['coordinates'][0])
    polyList.append(polyGeom)
    polyProperties.append(poly['properties'])
print(polyList[0])
print(polyProperties[0])

#plot sample of polygon and clip layer
fig, ax = plt.subplots(figsize=(12,8))

for poly in polyList:
    polyPatch = PolygonPatch(poly,alpha=0.5,color='orangered')
    ax.add_patch(polyPatch)
clipPatch = PolygonPatch(aoiGeom,alpha=0.8,color='royalblue')
ax.add_patch(clipPatch)
outline = 2000
ax.set_xlim(aoiGeom.bounds[0]-outline,aoiGeom.bounds[2]+outline)
ax.set_ylim(aoiGeom.bounds[1]-outline,aoiGeom.bounds[3]+outline)
plt.show()

#clip polygons to clip layer
clipPolyList = []
clipPolyProperties = []
for index, poly in enumerate(polyList):
    result = aoiGeom.intersection(poly)
    if result.area:
        clipPolyList.append(result)
        clipPolyProperties.append(polyProperties[index])
print(clipPolyList[0])
print(clipPolyProperties[0])


#plot clipped polygon and clip layer
fig, ax = plt.subplots(figsize=(12,8))

for poly in clipPolyList:
    polyPatch = PolygonPatch(poly,alpha=0.5,color='orangered')
    ax.add_patch(polyPatch)
clipPatch = PolygonPatch(aoiGeom,alpha=0.5,color='royalblue')
ax.add_patch(clipPatch)
outline = 2000
ax.set_xlim(aoiGeom.bounds[0]-outline,aoiGeom.bounds[2]+outline)
ax.set_ylim(aoiGeom.bounds[1]-outline,aoiGeom.bounds[3]+outline)
plt.show()


#export clipped polygons as shapefile
schema = polyShp.schema

outFile = fiona.open('/Users/iuliiashevtsova/Documents/Python_stuff/hills_clipped.shp',mode = 'w',driver = 'ESRI Shapefile', schema=schema)
for index, poly in enumerate(clipPolyList):
    outFile.write({
        'geometry':mapping(poly),
        'properties':clipPolyProperties[index]
    })
outFile.close()

#-----------------------------------
# Create masks with GDAL
#-----------------------------------

import os
from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt

os.chdir('/Users/iuliiashevtsova/Documents/Python_stuff')

ds = gdal.Open("srtm_germany_dtm.tif")
#here is example of data with no missing values
dt = ds.GetGeoTransform()
proj = ds.GetProjection()

band = ds.GetRasterBand(1)

array_dem = band.ReadAsArray()

plt.figure()
plt.imshow(array_dem)

binmask = np.where(array_dem >= np.mean(array_dem), 1,0)
plt.figure()
plt.imshow(binmask)

driver = gdal.GetDriverByName("GTiff")
driver.Register()
outds = driver.Create("binmask.tif", xsize=binmask.shape[1], ysize=binmask.shape[0], bands=1, eType=gdal.GDT_Int16)

outds.SetGeoTransform(dt)
outds.SetProjection(proj)
outband = outds.GetRasterBand(1)
outband.WriteArray(binmask)
outband.SetNoDataValue(np.nan)
outband.FlushCache()

outband = None
outds = None

#-----------------------------------
# NDVI calculating using Sentinel data
#-----------------------------------
import os
import numpy as np

os.chdir("/Users/iuliiashevtsova/Documents/Python_stuff/Sentinel2")
print(os.listdir(os.getcwd()))

NIR = rasterio.open(r'clip_RT_S2A_OPER_MSI_L1C_TL_MTI__20160506T214824_A004555_T18LTM_B08.tif')
RED = rasterio.open(r'clip_RT_S2A_OPER_MSI_L1C_TL_MTI__20160506T214824_A004555_T18LTM_B04.tif')

red = RED.read(1).astype('float64')
nir = NIR.read(1).astype('float64')

# ndvi calculation, empty cells or nodata cells are reported as 0
ndvi=np.where( (nir==0.) | (red ==0.), -255 , np.where((nir+red)==0., 0, (nir-red)/(nir+red)))

plt.figure(facecolor="ghostwhite")
c = plt.imshow(ndvi, cmap="YlGn")
plt.colorbar(c)
plt.title('NDVI', fontweight ="bold")
plt.show()

#----------------------------------
# Basic shapes visualisation
#----------------------------------

#Points

from shapely.geometry import Point

point = Point(0.0,0.0)

print("Area", point.area)
print("Length", point.length)
print("Bounds", point.bounds)
print("Longitude", point.x)
print("Latitude", point.y)

import matplotlib.pyplot as plt

points = [Point(-4,0.),
          Point(-5,12.),
          Point(-6,3.),
          Point(-1,6.)]

xs = [point.x for point in points]
ys = [point.y for point in points]
plt.scatter(xs,ys)
plt.show()

#Lines

from shapely.geometry import LineString

line = LineString([(0,0),(1,1)])

print("Area", line.area)
print("Length", line.length)
print("Bounds", line.bounds)
print("Longitude, Latitude", line.xy)

Lines =[LineString([Point(-4,0.),Point(-5,12.), Point(-6.,3.)]),
        LineString([Point(-8.,7.), Point(-4.,8.), Point(-3,2.)])]

plt.plot(Lines[0].xy[0], Lines[0].xy[1])
plt.plot(Lines[1].xy[0], Lines[1].xy[1])
plt.show()

#Polygons

from shapely.geometry import Polygon

polygon = Polygon([(0,0),(1,1),(1,0)])

print("Area", polygon.area)
print("Length", polygon.length)
print("Bounds", polygon.bounds)
print("Boundary", polygon.boundary)
print("Center", polygon.centroid)

Polygons = Polygon([(-4,0.),(-5,0.),(-6,3.)])

plt.figure(figsize=(10,5))
plt.fill(*Polygons.exterior.xy)
plt.show()

#Multipolygons

import shapely.ops as so
import matplotlib.pyplot as plt

r1 =Polygon([(0,0),(0,1),(1,1),(1,0),(0,0)])
r2 =Polygon([(1,1),(1,2),(2,2),(2,1),(1,1)])
r3 =Polygon([(1,3),(3,2),(2,5),(5,1),(1,3)])

polygons = [r1,r2,r3]
new_shape = so.unary_union([r1,r2])
multipolygon=so.unary_union([r1,r2,r3])

####### Geopandas 
import geopandas as gpd
import pandas as pd

points = [Point(-4,0.), Point(-5,12.), Point(-6.,3.),
          Point(-3,1.), Point(-6,10.), Point(-8.,4.)]

Lines = [LineString([Point(-4,0), Point(-5,12.), Point(-6.,3.)]),
         LineString([Point(-3,1.), Point(-6,10.), Point(-8.,4.)])]

geoms = Polygon([(0,0.),(0,5.),(5,7.),(7.,0)])

points_gdf = gpd.GeoDataFrame(pd.DataFrame({'Name':["P1","P2","P3","P4","P5","P6"]}),
             crs="EPSG:4326",
             geometry=points)

lines_gdf = gpd.GeoDataFrame(pd.DataFrame({'Name':["Line1","Line2"]}),
             crs="EPSG:4326",
             geometry=Lines)

polygon_gdf = gpd.GeoDataFrame(pd.DataFrame({'Name':["Polygon1"]}),
             crs="EPSG:4326",
             geometry=[geoms])

gdf = pd.concat([points_gdf, lines_gdf, polygon_gdf]).reset_index(drop=True)
gdf["area"]=gdf.area
gdf["boundary"]=gdf.boundary
gdf["centroid"]=gdf.centroid

gdf.plot()
plt.show()

#Fusing polygons

geoms = [Polygon([(0,0),(0,5.),(5,7.),(7.,0),(0,0)]),
         Polygon([(2.,5),(5.,8),(8.,3),(3.,2),(2.,5)])]

polygon1_gdf = gpd.GeoDataFrame(pd.DataFrame({'Name':["Polygon1"]}),
                                crs="EPSG:4326",
                                geometry=[geoms[0]])

polygon2_gdf = gpd.GeoDataFrame(pd.DataFrame({'Name':["Polygon2"]}),
                                crs="EPSG:4326",
                                geometry=[geoms[1]])


intersection = polygon2_gdf.overlay(polygon1_gdf, how='intersection')
union = polygon2_gdf.overlay(polygon1_gdf, how='union')
sym_diff = polygon2_gdf.overlay(polygon1_gdf, how='symmetric_difference')
diff = polygon2_gdf.overlay(polygon1_gdf, how='difference')

intersection.plot()
plt.show()

union.plot()
plt.show()

sym_diff.plot()
plt.show()

diff.plot()
plt.show()

#----------------------------------
# Projections with Cartopy
#----------------------------------

#Read World Map from available datasets

gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

gdf.plot()
plt.show()

## Projections 
import cartopy.crs as ccrs

plt.figure(figsize=(10,5))
ax=plt.axes(projection=ccrs.Mercator())
gdf.plot(ax=ax,transform=ccrs.PlateCarree())
gl=ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                linewidth=2, color='black', alpha=0.5,linestyle='--')
plt.show()


#----------------------------------
# Advanced visualisation
#----------------------------------

import pandas as pd

sites = pd.read_csv("/Users/iuliiashevtsova/Documents/Python_stuff/test_points.csv")
sites.rename(columns = {'rand_point_id':'point_no'}, inplace = True)
sites.rename(columns = {'NAME_1':'land'}, inplace = True)

from shapely.geometry import Point
import geopandas as gpd

sites_geometry = [Point(xy) for xy in zip(sites['X'], sites['Y'])]
sites_geodata = gpd.GeoDataFrame(sites,
                                 crs="EPSG:4326",
                                 geometry=sites_geometry)

import matplotlib.pyplot as plt

ax = plt.scatter(sites_geodata['X'].values, sites_geodata['Y'].values, color='green', s=0.5, label='land', alpha=0.8)
ax.axes.set_title('Test sites')
ax.figure.set_size_inches(6,5)
plt.show()


from matplotlib.collections import PathCollection
from matplotlib.legend_handler import HandlerPathCollection, HandlerLine2D
groups = sites_geodata.groupby('land')


fig, ax = plt.subplots(figsize=(20, 12))
for name, group in groups:
    ax.plot(group.X, group.Y, marker='o', linestyle='', ms=12, label=name, alpha=0.1)
ax.legend()
ax.axes.set_title('Test sites')

def update(handle, orig):
    handle.update_from(orig)
    handle.set_alpha(1)

plt.legend(handler_map={PathCollection : HandlerPathCollection(update_func= update), plt.Line2D : HandlerLine2D(update_func = update)})
    
plt.show()













