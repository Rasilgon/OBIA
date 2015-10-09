# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 09:27:11 2015

@author: trashtos
"""
import rsgislib
from rsgislib import imageutils
from rsgislib import rastergis
from rsgislib import segmentation
from rsgislib.segmentation import segutils
import os
import subprocess

def assingGKprojection (inImage):
    wktString = '''PROJCS["DHDN / Gauss-Kruger zone 4",
    GEOGCS["DHDN",
        DATUM["Deutsches_Hauptdreiecksnetz",
            SPHEROID["Bessel 1841",6377397.155,299.1528128,
                AUTHORITY["EPSG","7004"]],
            AUTHORITY["EPSG","6314"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4314"]],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    PROJECTION["Transverse_Mercator"],
    PARAMETER["latitude_of_origin",0],
    PARAMETER["central_meridian",12],
    PARAMETER["scale_factor",1],
    PARAMETER["false_easting",4500000],
    PARAMETER["false_northing",0],
    AUTHORITY["EPSG","31468"],
    AXIS["Y",EAST],
    AXIS["X",NORTH]]'''
    imageutils.assignProj(inImage, wktString)
    
    
def selectImageBands(inImage, outImage, bandList):
    gdalFormat = 'KEA'
    dataType = rsgislib.TYPE_32FLOAT
    
    imageutils.selectImageBands(inImage, outImage, gdalFormat, dataType, bandList)
    
    
def ShepherdSeg(inImage, numClusters, minPxls,tmpath):    
    outputClumps = os.path.splitext(inImage)[0] + "_clumps_elim_final.kea"
    outputMeanImg = os.path.splitext(inImage)[0] +  "_clumps_elim_final_mean.kea"
    segutils.runShepherdSegmentation(inImage, outputClumps, outputMeanImg, 
                                     numClusters=numClusters, minPxls=minPxls,
                                     distThres=100, tmpath= tmpath)
                                     
def ShepherdSegTest(inImage, numClusters, minPxls,tmpath, band = [1]):    
    outputClumps = os.path.splitext(inImage)[0] + "_" + str(numClusters) + "_" + str(minPxls) + "_"+ ''.join([str(i) for i in band]) +  "_clumps.kea"
    outputMeanImg = os.path.splitext(inImage)[0] + "_" +  str(numClusters) + "_" + str(minPxls) + "_"+ ''.join([str(i) for i in band]) + "_clumps_mean.kea"
    
    segutils.runShepherdSegmentation(inImage, outputClumps, outputMeanImg, 
                                     numClusters=numClusters, minPxls=minPxls,
                                     distThres=100,  bands= band, tmpath= tmpath)   
    # export columns
    gdalFormat = 'KEA'
    dataType = rsgislib.TYPE_32INT
    field = 'Histogram'
    outImage=os.path.splitext(outputClumps)[0] + "export.kea"
    rastergis.exportCol2GDALImage(outputClumps, outImage, gdalFormat, dataType, field)
    # polygonize
    cmd = "gdal_polygonize.py " + outImage + """ -f "ESRI Shapefile" """ + os.path.splitext(outImage)[0] + ".shp"
    subprocess.call(cmd, shell = True)
                                         
def creating_stacks(layersList, bandNamesList, outName):
    #set format of data: assuming kea
    gdalformat = 'KEA'
    dataType = rsgislib.TYPE_32FLOAT
    imageutils.stackImageBands(layersList, None, outName, None, 0, gdalformat, dataType)                                         
    return(outName)