# -*- coding: utf-8 -*-

##### Import modules #######
import re
from itertools import chain, combinations


#### Functions #############


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


def grep(pattern, stringList, mask=True):
    expr = re.compile(pattern)
    if mask==True:
        return ([elem for elem in stringList if expr.match(elem)])
    if mask==False:
        return ([elem for elem in stringList if not expr.match(elem)])
    

def all_subsets(ss, length):
  return chain(*map(lambda x: combinations(ss, x), range(0, length)))

