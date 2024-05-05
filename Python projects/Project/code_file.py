import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn as skl
import sklearn.linear_model as skl_lm
from scipy import stats
from functools import wraps
from time import perf_counter


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

def readFile():
    return pd.read_csv("/Users/leevimalin/Library/Mobile Documents/com~apple~CloudDocs/Opinnot/Matikka/Tilastot ja ohjelmistot/Python/Project/harjoitustyodata.csv")

def part1(df):
    # 
    list_of_df = []
    list_of_plot = []
    partdf, partplt = calculatePart1(df,"freedom",[12,17,18,19])
    list_of_df.append(partdf)
    list_of_plot.append(partplt)
    partdf, partplt = calculatePart1(df,"nation",[17,18,19])
    list_of_df.append(partdf)
    list_of_plot.append(partplt)
    partdf, partplt = calculatePart1(df,"logic",[1,13,19,20])
    list_of_df.append(partdf)
    list_of_plot.append(partplt)
    partdf, partplt = calculatePart1(df,"normal",[2,6,13,14])
    list_of_df.append(partdf)
    list_of_plot.append(partplt)
    partdf, partplt = calculatePart1(df,"program",[2,6,5,19])
    list_of_df.append(partdf)
    list_of_plot.append(partplt)

    return list_of_df, list_of_plot

def part2(df, group1: int, group2: int):
    '''Calculates part 2 things for two(2) given groups''' 
    # Get message rows for groups
    gr1rows = getGroupRows(df,group1)
    gr2rows = getGroupRows(df,group2)
    
    # get total word count of each message
    wordCount1 = getAllWordCount(df,gr1rows)
    wordCount2 = getAllWordCount(df,gr2rows)

    lgwordCount1 = convertToLog(wordCount1)
    lgwordCount2 = convertToLog(wordCount2)

    plt.figure(1)
    lghistgr1 = plt.hist(lgwordCount1,80)
    plt.figure(2)
    lghistgr2 = plt.hist(lgwordCount2,80)

    tTesti = stats.ttest_ind(wordCount1,wordCount2)
    return lghistgr1, lghistgr2, tTesti

def part3(df):
    '''Calculate part 3 things'''
    group1 = 2
    group2 = 16

    allSecFromNight = np.array(df['secsfrommidnight'])
    plt.figure(1)
    plt.hist(allSecFromNight,200)
    

    allSecFrom8am = np.array(df['secsfrom8am'])
    mean, median, deviation = calculatePart3(allSecFrom8am)
    plt.figure(2)
    plt.hist(allSecFrom8am,200)
    
    gr1rows = getGroupRows(df,group1)
    gr2rows = getGroupRows(df,group2)
    
    meangr1 = np.mean(getRangeFromColumn(df,gr1rows,"secsfrom8am"))
    meangr2 = np.mean(getRangeFromColumn(df,gr1rows,"secsfrom8am"))

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
    histList = []
    figurenum = 1
    for sent in sentList:
        histList.append(plt.hist(sent,15))
        figurenum += 1
    
    # Calculate differences
    diff1 = stats.ttest_ind(sentList[3],sentList[4])
    diff2 = stats.ttest_ind(sentList[9],sentList[10])
    diff3 = stats.ttest_ind(sentList[7],sentList[8])

    part5results = {
        "correlation of sentiment" : corValues,
        "Sentimenttien jakauma" : statList,
        "Kolme suurinta" : three_highest,
        "Kolme pienintä" : three_lowest,
        "Histogrammit" : histList,
        "pc ja mac ero" : diff1,
        "baseball ja hockey ero" : diff2,
        "autos ja motorccyles ero" : diff3
    }
    return part5results

def part6(df):

    rows1 = np.array(getGroupRows(df,2))
    rows2 = np.array(getGroupRows(df,15))
    # tää on hiton tyhmä tapa tehä tätä mut fuck numpy ja sen tietorakenteet
    words = pd.DataFrame()
    words["X"] = df.loc[(df["groupID"] == 2) | (df["groupID"] == 15),"jpeg"]
    #words2 = df.loc[df["groupID"] == 15,["jpeg","freedom"]]

    print(words["X"])
    
    target = []
    #training = []
    for num in rows1:
        #training.append(df.at[num,"jpeg"])
        target.append(1)
    for num in rows2:
        #training.append(df.at[num,"jpeg"])
        target.append(-1)

    
    tulos = skl_lm.LinearRegression().fit(np.array(words["X"]),target)

    ypred = tulos.predict()

def calculatePart1(df,word: str,groups: list) -> list:
    '''
    Makes nececcary calculations for Part 1.
    return: list of statistic data frames and histogram plot
    '''
    totalWordCounts = {}
    statlist = {}
    for num in groups:
        # find list of rows for certain group
        rowlist = getGroupRows(df,num)
        # find word counts for messages in group 
        countList = getIndWordCount(df,rowlist,word)
        # add wor count sums to list for later use
        totalWordCounts[NEWSGROUPTRANSFORMER[num]] = np.sum(countList)
        # save stats for word counts
        statlist[NEWSGROUPTRANSFORMER[num]] = getStats(countList,0.001,0.999)

    statdf = pd.DataFrame(statlist)
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
    firstList = []
    for member in dictList:
        firstList.append(member["median"])
    return firstList
    

def getRangeFromColumn(df, rowlist, column: str) -> np.array:
    '''
    Params:
        rowlist: list of rows from function getGroupRows()
        column: Name of column where values are searched
    '''
    return np.array(df.loc[rowlist[0]:rowlist[-1], column])


def getRowWordCount(df,row):
    # Counts all words in single row
    wordcount = df.iloc[row, 5:963].sum()
    return wordcount

def getAllWordCount(df,groups: list) -> list:
    # iterates over list of rows and calculates
    # all words in their messages
    wordlist = []
    for row in groups:
        wordlist.append(getRowWordCount(df,row))
    return wordlist

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
    # finds row indexes for given group
    # returns list of row indexes
    index = 0
    rowList = []
    for ID in df["groupID"]:
        if ID == group:
            rowList.append(index)
        index += 1
    return rowList

def getIndWordCount(df,rowlist: list[int],word: str) -> list:
    
    # Finds all word counts for a newsGroup,word pair
    # Returns vector with indivitual message wordcounts
    wordCounts = []
    for num in rowlist:
        wordCounts.append(df.at[num,word])
    
    return wordCounts


def main():
    T1 = perf_counter()

    data = readFile()
    #part1Df ,part1Plt = part1(data)
    #lghist11, lghist12, tTesti1 = part2(data,10,11)
    #lghist21, lghist22, tTesti2 = part2(data,8,9)
    #part3(data)
    #corr1 = part4(data, "jpeg", "gif")
    #corr2 = part4(data, "write", "sale")
    #corr3 = part4(data, "jpeg", "gif", 2)    
    #part5(data)
    part6(data)

    testteii = np.array(data.loc[data["groupID"]==12,"jpeg"])

    T2 = perf_counter()
    print()
    print(f'Elapsed Time: f{T2-T1}')
    print()
    
if __name__ == "__main__":
    main()