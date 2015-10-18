# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 08:23:19 2015

@author: trashtos
"""
import subprocess
import os
import sys

from osgeo import ogr

def vectorClip(inVector, coverVector, outVector):
    try:
        cmd = "ogr2ogr -clipsrc " + coverVector + " " + outVector + " " + inVector
        subprocess.call(cmd, shell = True)
    except OSError as e:
        print >>sys.stderr, ("Execution failed:", e)
        sys.exit 
    
    
    

def gdal_warp(inImage, outResolution, method):
    
    ext = os.path.splitext(inImage)[1]    
    
    # near (default), bilinear, cubic, cubicspline, lanczos, average, mode.
    cmd = "gdalwarp -tr "+ str(outResolution) + " " + str(outResolution) + " -r " + method + " -of KEA " + inImage + " " + os.path.splitext(inImage)[0] + "_" + method + str(outResolution) + ext 

    subprocess.call(cmd, shell = True)
    
    return (os.path.splitext(inImage)[0] + method + str(outResolution) + ext)
    


def gdal_translate(inImage, outFormat):
    
    runFunction = True
    
    if outFormat == "GTiff":
        outImage = os.path.splitext(inImage)[0] + ".tif"
        outType = "Int32"
    elif outFormat == "KEA":
        outImage = os.path.splitext(inImage)[0] + ".kea"
        outType = "Float32"
    else:
        print ("You have not provided a valid format : GTiff, KEA")
        runFunction = False
    
    if runFunction == True:       
        cmd = "gdal_translate -ot "+ outType + " -of " + outFormat + " " + inImage + " "  + outImage
        subprocess.call(cmd, shell = True)
        
        return (outImage)



def countFeatshp(shpFile):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shpFile, 0) # 0 means read-only. 1 means writeable.
    # Check to see if shapefile is found.
    if dataSource is None:
        print ('Could not open %s' % (shpFile))
    else:
        print ('Opened %s' % (shpFile))
        layer = dataSource.GetLayer()
        featureCount = layer.GetFeatureCount()
        return (featureCount)
    
def createDataStack(inFiles, outResolution, outFile, outFormat):
    #format
    if outFormat == 'KEA':
        extension = '.kea'
    elif outFormat == 'GTiff':
        extension = '.tif'
    else:
        print ('Format not supported: only KEA or GTiff')
        sys.exit         

     # do image list
    listFiles = os.path.splitext(outFile)[0]  +'.txt'     
    with open(listFiles, 'w') as f:
        f.write('\n'.join(inFiles))
        
    print ('####################### Create shell script #######################')   
    shellScript = os.path.splitext(outFile)[0]  +'.sh'     
    with open(shellScript, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("############# export GDAL_DRIVER_KEA #############\n")
        #f.write("source activate rsgislibenv\n")
        f.write("export GDAL_DRIVER_PATH=~/anaconda3/lib/gdalplugins\n")
        f.write("export GDAL_DATA=~/anaconda3/share/gdal/\n")    
        f.write("############# process STACK #############\n")
        f.write('gdalbuildvrt -tr '+ str(outResolution)+ ' '+str(outResolution)+' -tap -separate -input_file_list '+  listFiles +' '+ os.path.splitext(outFile)[0]+'.vrt\n')
        f.write('gdal_translate -of KEA '+ os.path.splitext(outFile)[0]+'.vrt '+ outFile+'\n')
        f.write('gdalcalcstats ' + outFile+'\n')
    print ('##################### Sent Script to Terminal #####################')
    cmd = "bash " + shellScript
    print (cmd)
    try:
        subprocess.call(cmd, shell = True)        
    except OSError as e:
        print >>sys.stderr, ("Execution failed:", e)
        sys.exit 
        
    
