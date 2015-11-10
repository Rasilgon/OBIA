# -*- coding: utf-8 -*-

##### Import modules #######
import fiona
from shapely.geometry import shape
from rasterstats import zonal_stats
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix


#### Functions #############


def mymean(x):
    return (np.mean(x))

def varianza(x):
    return (np.var(x)) #numpy.nanvar(x
    
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
    

def enhancedConfusionMatrix(actuals, predictions):
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
    accuracy = (float(np.sum(truePositives)) /
                    (np.sum(truePositives)+ np.sum(falseNegatives)))*100
    precision  = (float(np.sum(truePositives)) /
                    (np.sum(truePositives)+ np.sum(falsePositives)))*100
    #####
    return (cm, accuracy,  precision,  classesPrecision, classesAccuracy)

#Accuracy (also known as producer's accuracy): 
#it is the fraction of correctly classified pixels with regard to all pixels of that ground truth class. 
#For each class of ground truth pixels (row), the number of correctly classified pixels 
#is divided by the total number of ground truth or test pixels of that class.

#Reliability (also known as user's accuracy): The figures in row Reliability (REL) present the reliability 
#of classes in the classified image: it is the fraction of correctly classified pixels with regard to all 
#pixels classified as this class in the classified image. For each class in the classified image (column),
# the number of correctly classified pixels is divided by the total number of pixels which were classified as this class.

def kappa(y_true, y_pred, weights=None, allow_off_by_one=False):
    "http://skll.readthedocs.org/en/latest/_modules/skll/metrics.html"
    """
    Calculates the kappa inter-rater agreement between two the gold standard
    and the predicted ratings. Potential values range from -1 (representing
    complete disagreement) to 1 (representing complete agreement).  A kappa
    value of 0 is expected if all agreement is due to chance.

    In the course of calculating kappa, all items in `y_true` and `y_pred` will
    first be converted to floats and then rounded to integers.

    It is assumed that y_true and y_pred contain the complete range of possible
    ratings.

    This function contains a combination of code from yorchopolis's kappa-stats
    and Ben Hamner's Metrics projects on Github.

    :param y_true: The true/actual/gold labels for the data.
    :type y_true: array-like of float
    :param y_pred: The predicted/observed labels for the data.
    :type y_pred: array-like of float
    :param weights: Specifies the weight matrix for the calculation.
                    Options are:

                        -  None = unweighted-kappa
                        -  'quadratic' = quadratic-weighted kappa
                        -  'linear' = linear-weighted kappa
                        -  two-dimensional numpy array = a custom matrix of
                           weights. Each weight corresponds to the
                           :math:`w_{ij}` values in the wikipedia description
                           of how to calculate weighted Cohen's kappa.

    :type weights: str or numpy array
    :param allow_off_by_one: If true, ratings that are off by one are counted as
                             equal, and all other differences are reduced by
                             one. For example, 1 and 2 will be considered to be
                             equal, whereas 1 and 3 will have a difference of 1
                             for when building the weights matrix.
    :type allow_off_by_one: bool
    """
    #logger = logging.getLogger(__name__)

    # Ensure that the lists are both the same length
    assert(len(y_true) == len(y_pred))

    # This rather crazy looking typecast is intended to work as follows:
    # If an input is an int, the operations will have no effect.
    # If it is a float, it will be rounded and then converted to an int
    # because the ml_metrics package requires ints.
    # If it is a str like "1", then it will be converted to a (rounded) int.
    # If it is a str that can't be typecast, then the user is
    # given a hopefully useful error message.
    # Note: numpy and python 3.3 use bankers' rounding.
    try:
        y_true = [int(np.round(float(y))) for y in y_true]
        y_pred = [int(np.round(float(y))) for y in y_pred]
    except ValueError as e:
        print("For kappa, the labels should be integers or strings "
                     "that can be converted to ints (E.g., '4.0' or '3').")
        raise e

    # Figure out normalized expected values
    min_rating = min(min(y_true), min(y_pred))
    max_rating = max(max(y_true), max(y_pred))

    # shift the values so that the lowest value is 0
    # (to support scales that include negative values)
    y_true = [y - min_rating for y in y_true]
    y_pred = [y - min_rating for y in y_pred]

    # Build the observed/confusion matrix
    num_ratings = max_rating - min_rating + 1
    observed = confusion_matrix(y_true, y_pred,
                                labels=list(range(num_ratings)))
    num_scored_items = float(len(y_true))

    # Build weight array if weren't passed one
    if isinstance(weights, string_types):
        wt_scheme = weights
        weights = None
    else:
        wt_scheme = ''
    if weights is None:
        weights = np.empty((num_ratings, num_ratings))
        for i in range(num_ratings):
            for j in range(num_ratings):
                diff = abs(i - j)
                if allow_off_by_one and diff:
                    diff -= 1
                if wt_scheme == 'linear':
                    weights[i, j] = diff
                elif wt_scheme == 'quadratic':
                    weights[i, j] = diff ** 2
                elif not wt_scheme:  # unweighted
                    weights[i, j] = bool(diff)
                else:
                    raise ValueError('Invalid weight scheme specified for '
                                     'kappa: {}'.format(wt_scheme))

    hist_true = np.bincount(y_true, minlength=num_ratings)
    hist_true = hist_true[: num_ratings] / num_scored_items
    hist_pred = np.bincount(y_pred, minlength=num_ratings)
    hist_pred = hist_pred[: num_ratings] / num_scored_items
    expected = np.outer(hist_true, hist_pred)

    # Normalize observed array
    observed = observed / num_scored_items

    # If all weights are zero, that means no disagreements matter.
    kappa = 1.0
    if np.count_nonzero(weights):
        kappa -= (sum(sum(weights * observed)) / sum(sum(weights * expected)))

    return (kappa)
    
    

#Kappa = (N * sum(diagonal) - ( rowi * columj) )/ (N**2 - (rowi * columj ))

#where r is the number of rows in the matrix, xii is the number of observations in row i and column i,
# x i+ and x +i are the marginal totals of row i and column i, respectively, and N is the total number
# of observations (Bishop et al., 1975)
