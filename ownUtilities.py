# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 14:48:34 2015

@author: trashtos
"""

# own functions

def cleanTiles():
    tiles = [(7,18), (7,19), (8,21),(8,29), (10,14), (10,20), (10,24),(11,19),
        (12,15), (12,22), (12,27),(12,28), (14,18),(15,15),(18,15), (21,13),
        (22,8), (23,11), (23,6),(24,9),(24,7), (27,9),(27,12), (29,8) ] 
    tilesBasename = ["/media/trashtos/Meerkat/cleanTiles/Rows" +str(tile[0])+ "/Cols" +str(tile[1])+"/tile_row" +
str(tile[0]) + "col" +str(tile[1]) for tile in tiles]
    return (tilesBasename)
    
def shpClips():
    tiles = [(7,18), (7,19), (8,21),(8,29), (10,14), (10,20), (10,24),(11,19),
        (12,15), (12,22), (12,27),(12,28), (14,18),(15,15),(18,15), (21,13),
        (22,8), (23,11), (23,6),(24,9),(24,7), (27,9),(27,12), (29,8) ]
    shpBasename = "/home/trashtos/CleaningTiles/TilesSHP/BWTilesPolys_TileID__" 
    clippingSHP = [ shpBasename +"Rows" +str(tile[0])+ "Cols"+str(tile[1]) + ".shp" for tile in tiles ]
    return(clippingSHP)
    
def oldTiles():
    tiles = [(7,18), (7,19), (8,21),(8,29), (10,14), (10,20), (10,24),(11,19),
        (12,15), (12,22), (12,27),(12,28), (14,18),(15,15),(18,15), (21,13),
        (22,8), (23,11), (23,6),(24,9),(24,7), (27,9),(27,12), (29,8) ] 
    tilesBasename = ["/media/trashtos/Meerkat/Ramiro_Masterarbeit/Tiles/Rows" +str(tile[0])+ "/Cols" +str(tile[1])+"/tile_row" +
str(tile[0]) + "col" +str(tile[1]) for tile in tiles]
    return (tilesBasename)


def lidarTiles():
    tiles = [(7,18), (7,19), (8,21),(8,29), (10,14), (10,20), (10,24),(11,19),
        (12,15), (12,22), (12,27),(12,28), (14,18),(15,15),(18,15), (21,13),
        (22,8), (23,11), (23,6),(24,9),(24,7), (27,9),(27,12), (29,8) ] 
    tilesBasename = ["/media/trashtos/Meerkat/Ramiro_Masterarbeit/Tiles/Rows" +str(tile[0])+ "/Cols" +str(tile[1])+"/tile_row" +
str(tile[0]) + "col" +str(tile[1]) + "_2014_DHDNGK4_rmn_pmfmccgrd_1m_" for tile in tiles]
    return (tilesBasename)


def mymean(x):
    return (np.mean(x))

def varianza(x):
    return (np.var(x)) #numpy.nanvar(x
    
#

def segQuality(inVector, inImage):
    # open the vector
    lyr = fiona.open(inVector)
    features = [x for x in lyr]
    values = np.zeros([len(features), 5], dtype=float)
    # loop over features
    for  i in range(len(features)):
        geometry1 = shape(features[i]['geometry'])
        
        restFeatures = features[:i] + features[(i+ 1):]
        
        value = zonal_stats(geometry1, inImage, stats=['count'], add_stats={'mymean':mymean, "myvarianza":varianza } )
            
        df =  pd.DataFrame.from_dict(value, orient='columns', dtype=None)
        
            
        for j in range(len(restFeatures)):        
            geometry2 = shape(features[j]['geometry'])   
            if geometry2.intersects(geometry1) == True:
                #print("They touch")
                value = zonal_stats(geometry2, inImage, stats=['count'], add_stats={'mymean':mymean, "myvarianza":varianza } )
                df = df.append(pd.DataFrame.from_dict(value, orient='columns', dtype=None))
            
        values[i,0] = df.iloc[0,0] # count
        values[i,1] = df.iloc[0,1] # mean
        values[i,2] = df.iloc[0,2] # myvarianza
        values[i,3] = np.var(df.iloc[:,1]) # varianza between
        values[i,4] = len(df.iloc[1:]) # neighbours
    # get overal values   
    intraVarWeighted = np.nansum( values[:,0]*values[:,2] ) / np.nansum(values[:,0])
    interVarWeighted = np.nansum( values[:,4]*values[:,3] ) / np.nansum(values[:,4])
    normVariance = (intraVarWeighted - interVarWeighted) / (intraVarWeighted + interVarWeighted)
    numberSegments =  len(values[:,4])
    
    return( intraVarWeighted, interVarWeighted, normVariance, numberSegments )
    

def get_enhanced_confusion_matrix(actuals, predictions):
    """"enhances confusion_matrix by adding sensivity and specificity metrcs"""
    cm = confusion_matrix(actuals, predictions)
    #get total values
    truePositives = cm.diagonal()
    falsePositives = np.tril(cm, 0)#a
    falseNegatives = np.triu(cm, 0) #below diagonal
    # create list to hold data
    classesPrecision = np.zeros(len(cm[0]), dtype=np.float)
    classesAccuracy = np.zeros(len(cm[0]), dtype=np.float)
    for i in range(len(cm[0])):
        mask1D= np.ones(cm[0].shape,dtype=bool)
        mask1D[i]= 0
        truePos = cm[i,i]
        falsePos =np.sum(cm[:,i][mask1D])#below i
        falseNeg =np.sum(cm[i,:][mask1D])#same row than i 
        if truePos ==0:
            classPrecision = 0
            classAccuracy = 0
       # elif falsePos== 0:
       #     classPrecision =  (float(truePos) / (truePos + falsePos))*100
        #    classAccuracy = (float(truePos) / (falseNeg + truePos))*100 #becuase is groudn truth
        else:
            classPrecision =  (float(truePos) / (truePos + falsePos))*100
            classAccuracy = (float(truePos) / (falseNeg + truePos))*100 #becuase is groudn truth
        #append values
        classesPrecision[i] = classPrecision
        classesAccuracy[i] =classAccuracy
    ####
    sensitivity = (float(np.sum(truePositives)) /
                    (np.sum(truePositives)+ np.sum(falseNegatives)))*100
    precision  = (float(np.sum(truePositives)) /
                    (np.sum(truePositives)+ np.sum(falsePositives)))*100
    PPV = (float(np.sum(truePositives)) / 
                    (np.sum(truePositives)+ np.sum(falsePositives)))*100
    #####
    return cm, sensitivity,  precision,  classesPrecision, classesAccuracy, PPV

#Accuracy (also known as producer's accuracy): 
#it is the fraction of correctly classified pixels with regard to all pixels of that ground truth class. 
#For each class of ground truth pixels (row), the number of correctly classified pixels 
#is divided by the total number of ground truth or test pixels of that class.

#Reliability (also known as user's accuracy): The figures in row Reliability (REL) present the reliability 
#of classes in the classified image: it is the fraction of correctly classified pixels with regard to all 
#pixels classified as this class in the classified image. For each class in the classified image (column),
# the number of correctly classified pixels is divided by the total number of pixels which were classified as this class.
seta = [(" ").join((map(str,cm[i]))) for i in range(len(cm[0]))] 
peta = ("; ").join([(" ").join((map(str,cm[i]))) for i in range(len(cm[0]))] )
# bring it back
np.array(np.mat(peta))
