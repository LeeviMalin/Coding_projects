import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn as skl
import sklearn.linear_model as skl_lm
import sklearn.metrics as skl_m
from scipy import stats
from time import perf_counter
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split


NEWSGROUPTRANSFORMER = {
    1 : "alt.atheism",
    2 : "comp.graphics",
    3 : "comp.os.ms-windows.misc",
    4 : "comp.sys.ibm.pc.hardware",
    5 : "comp.sys.mac.hardware",
    6 : "comp.windows.x",
    7 : "misc.forsale",
    8 : "rec.autos",
    9 : "rec.motorcycles",
    10 : "rec.sport.baseball",
    11 : "rec.sport.hockey",
    12 : "sci.crypt",
    13 : "sci.electronics",
    14 : "sci.med",
    15 : "sci.space",
    16 : "soc.religion.christian",
    17 : "talk.politics.guns",
    18 : "talk.politics.mideast",
    19 : "talk.politics.misc",
    20 : "talk.religion.misc"
    }

def makeSave(name: str):
    '''Saves current plot to given location'''
    plt.savefig("/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Ohjelmointi/Python projects/Project/plots/"+name+".pdf")

#**********
# Part 1
#**********
def part1(df):
    list_of_df = []
    partdf, partplt = calculatePart1(df,"freedom",[12,17,18,19])
    list_of_df.append(partdf)
    makeSave("part1hist1")
    partdf, partplt = calculatePart1(df,"nation",[17,18,19])
    list_of_df.append(partdf)
    makeSave("part1hist2")
    partdf, partplt = calculatePart1(df,"logic",[1,13,19,20])
    list_of_df.append(partdf)
    makeSave("part1hist3")
    partdf, partplt = calculatePart1(df,"normal",[2,6,13,14])
    list_of_df.append(partdf)
    makeSave("part1hist4")
    partdf, partplt = calculatePart1(df,"program",[2,6,5,19])
    list_of_df.append(partdf)
    makeSave("part1hist5")
    plt.close()

    return list_of_df

#**********
# Part 2
#**********
def part2(df, group1: int, group2: int):
    '''Calculates part 2 things for two(2) given groups''' 
    
    # get total word count of each message
    wordCount1 = np.array(getAllWordCount(df,group1))
    wordCount2 = np.array(getAllWordCount(df,group2))

    # Avoid -inf when trying to log 0
    lgwordCount1 = np.log10(wordCount1, out=np.zeros_like(wordCount1), where=(wordCount1!=0))
    lgwordCount2 = np.log10(wordCount2, out=np.zeros_like(wordCount2), where=(wordCount2!=0))

    plt.figure(figsize=(20,15))
    plt.hist(lgwordCount1,80)
    makeSave("part2hist1")
    plt.figure(figsize=(20,15))
    plt.hist(lgwordCount2,80)
    makeSave("part2hist2")
    plt.close()

    tTesti = stats.ttest_ind(wordCount1,wordCount2)
    return tTesti

#**********
# Part 3
#**********
def part3(df):
    '''Calculate part 3 things'''
    group1 = 2
    group2 = 16

    allSecFromNight = np.array(df['secsfrommidnight'])
    plt.figure(figsize=(20,15))
    plt.hist(allSecFromNight,200)
    makeSave("part3hist1")

    allSecFrom8am = np.array(df['secsfrom8am'])
    mean, median, deviation = calculatePart3(allSecFrom8am)
    
    plt.figure(figsize=(20,15))
    plt.hist(allSecFrom8am,200)
    makeSave("part3hist2")
    
    gr1rows = getGroupRows(df,group1)
    gr2rows = getGroupRows(df,group2)
    
    meangr1 = np.mean(getRangeFromColumn(df,gr1rows,"secsfrom8am"))
    meangr2 = np.mean(getRangeFromColumn(df,gr2rows,"secsfrom8am"))

    res_list = [mean, median, deviation, meangr1, meangr2]

    return res_list

#**********
# Part 4
#**********
def part4(df, word1:str , word2: str, group=None):
    
    if group == None:

        wordCount1 = np.array(df[word1])
        wordCount2 = np.array(df[word2])

        return np.corrcoef(wordCount1,wordCount2)

    else:
        rowlist = getGroupRows(df,group)
        range1 = getRangeFromColumn(df,rowlist,word1)
        range2 = getRangeFromColumn(df,rowlist,word2)

        return np.corrcoef(range1,range2)

#**********
# Part 5
#**********
def part5(df):

  # Check for normal distribution
    sentValues = np.array(df["meanvalences"])
    corValues = stats.normaltest(sentValues)

    sentList, statList = calculatePart5(df)
    meanList = takeFirstFromDict(statList)
    sortedList = sorted(meanList)
    three_lowest = sortedList[:3]
    three_highest = sortedList[-3:]

    #Draw histograms
    fignum = 1
    for sent in sentList:
        plt.figure()
        plt.hist(sent,15)
        makeSave("part5hist"+str(fignum))
        fignum += 1
        plt.close()
    
    # Calculate differences
    diff1 = stats.ttest_ind(sentList[3],sentList[4])
    diff2 = stats.ttest_ind(sentList[9],sentList[10])
    diff3 = stats.ttest_ind(sentList[7],sentList[8])

    part5results = {
        "correlation of sentiment" : corValues,
        "Sentimenttien jakauma" : statList,
        "Kolme suurinta" : three_highest,
        "Kolme pienintä" : three_lowest,
        "pc ja mac ero" : diff1,
        "baseball ja hockey ero" : diff2,
        "autos ja motorccyles ero" : diff3
    }
    return part5results

#**********
# Part 6
#**********
def part6(df):
    # select the data we need in this part
    partdata = df.loc[(df["groupID"] == 2) | (df["groupID"] == 15)]
    # Create new array: if comp.graphics then 1 else -1
    target = partdata['groupID'].apply(lambda x: 1 if x == 2 else -1)

    mse1 = makeNewPredict(partdata,["jpeg"],target)
    mse2 = makeNewPredict(partdata,["jpeg","earth"],target)
    
    grpred = {
    "msegr1" : makeNewPredict(partdata, ["group1"], target),
    "msegr2" : makeNewPredict(partdata, ["group2"], target),
    "msegr3" : makeNewPredict(partdata, ["group3"], target),
    "msegr4" : makeNewPredict(partdata, ["group4"], target),
    "msegr5" : makeNewPredict(partdata, ["group5"], target),
    "msegr6" : makeNewPredict(partdata, ["group6"], target),
    "msegr7" : makeNewPredict(partdata, ["group7"], target),
    "msegr8" : makeNewPredict(partdata, ["group8"], target)
    }

    answlist = [mse1, mse2, grpred]

    return answlist

def makeNewPredict(df, words: list[str], target):
    '''Creates model for predicting group from fordcounts using linear regression model
    
    params: 
        words: array of words for used in creating prediction model
        target: Target array of set values for differentiating data
    '''
    wordsdf = df[words]
    
    # Create new prediction model and train it with given data
    tulos = skl_lm.LinearRegression().fit(wordsdf,target)
    pred = tulos.predict(wordsdf)
    mse = skl_m.mean_squared_error(target,pred)

    return mse

def tensorThings(df):
    '''Calculates part 6 things with tensor flow'''
    # Select the data we need in this part
    partdata = df.loc[(df["groupID"] == 2) | (df["groupID"] == 15)]
    target = partdata['groupID'].apply(lambda x: 1 if x == 2 else 0)
    # Split data to train and test
    X_train, X_test, y_train, y_test = train_test_split(partdata[["jpeg","earth"]], target, test_size=0.2, random_state=42)

    # create model
    model = Sequential()
    # Add hidden layers to model
    model.add(Dense(units=32, activation='relu', input_dim=len(X_train.columns)))
    model.add(Dense(units=64, activation='relu'))
    model.add(Dense(units=1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='sgd', metrics='accuracy')
    model.fit(X_train, y_train, epochs=200, batch_size=32)

    y_hat = model.predict(X_test)
    mse = skl_m.mean_squared_error(y_test, y_hat)



    eval = model.evaluate(X_test, y_test, batch_size=32)

    return mse, eval

def calculatePart1(df,word: str,groups: list) -> list:
    '''
    Makes nececcary calculations for Part 1.
    return: list of statistic data frames and histogram plot
    '''
    totalWordCounts = {}
    statlist = {}
    for num in groups:
        # find word counts for messages in group 
        countList = getIndividualWordCount(df,num,word)
        # add word count sums to list
        totalWordCounts[NEWSGROUPTRANSFORMER[num]] = np.sum(countList)
        # save stats for word counts
        statlist[NEWSGROUPTRANSFORMER[num]] = getStats(countList,0.001,0.999)

    statdf = pd.DataFrame(statlist)

    cm=1/2.54
    plt.figure(figsize=(20*cm,15*cm))
    histplt = plt.bar(totalWordCounts.keys(),totalWordCounts.values())
 
    return statdf, histplt

def calculatePart3(data: list):
    mean = np.mean(data)
    median = np.median(data)
    deviation = np.std(data)

    return mean, median, deviation

def calculatePart5(df):
    sentList = []
    # This loop finds sentimental values separately for all message groups
    for grnum in range(1,20):
        sentList.append(getRangeFromColumn(df,getGroupRows(df,grnum),"meanvalences"))
    statList = []
    for sent in sentList:
        statList.append(getStats(sent,0.25,0.75))

    return sentList, statList


def takeFirstFromDict(dictList: list[dict]):
    '''Takes the first element of dict and returns it
    (there propably is better way for this but...)'''
    firstList = []
    for member in dictList:
        firstList.append(member["median"])
    return firstList
    

def getRangeFromColumn(df, rowlist, column: str) -> np.array:
    '''
    Returns values from given column for given row indexes
    Params:
        rowlist: list of rows from function getGroupRows()
        column: Name of column where values are searched
    '''
    return np.array(df.loc[rowlist[0]:rowlist[-1], column])


def getAllWordCount(df,group: int):
    '''Returns sum of all words for given group'''

    return df[df["groupID"] == group][5:965].sum()


def convertToLog(input: list):
        np.log10(input)
        return input

def getStats(list: list, lowquantile: float, highquantile: float) -> dict:

    stats = {
    "mean" : np.mean(list),
    "median" : np.median(list),
    "deviation" : np.std(list),
    "0.1quantile" : np.quantile(list,lowquantile),
    "99.9quantile" : np.quantile(list,highquantile)
    }
    return stats

def getGroupRows(df,group: int) -> list:
    '''
    finds row indexes for given group
    returns list of row indexes
    '''
    index = 0
    rowList = []
    for ID in df["groupID"]:
        if ID == group:
            rowList.append(index)
        index += 1
    return rowList

def getIndividualWordCount(df,group: int,word: str):
    '''Finds all groups messages word count for single word'''
    
    return df.loc[df["groupID"] == group, word]

def allPart4(data):
    '''Calculates all part 4 things and returns them as a list of correlation coefficients'''
    corrList = []

    corrList.append(part4(data, "jpeg", "gif"))
    corrList.append(part4(data, "write", "sale"))
    corrList.append(part4(data, "jpeg", "gif", 2))

    return corrList

def main():
    T1 = perf_counter()

    data = pd.read_csv("/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Ohjelmointi/Python projects/Project/harjoitustyodata.csv")

    '''
    results = {
        "Part1 results" : part1(data),
        "Part2 results1" : part2(data,10,11),
        "Part2 results2" : part2(data,8,9),
        "Part3 results" : part3(data),
        "Part4 results" : allPart4(data),
        "Part5 results" : part5(data),
        "Part6 results" : part6(data)
    }
    '''

    mse, eval = tensorThings(data)

    T2 = perf_counter()
    print()
    print(f'Elapsed Time: f{T2-T1}')
    print()
    
if __name__ == "__main__":
    main()

#end of code_file.py