#!/usr/bin/env python3

#for each category...
#make list of all responses
#try to combine duplicates/mispellings?
#for each participants list...
#for each place 1-10...
#note how many times each response occurs in each place
#10 lists of average appearances (times in that spot/all participants), one for each place holding averages for each response
#or list for each response with average appearance order

import json
from difflib import get_close_matches
import numpy as np
import matplotlib.pyplot as plt
import random

numCats = 10

with open('/Users/traceymills/Documents/generation_data.csv.json') as f:
  gen_data = json.load(f)
with open('/Users/traceymills/Documents/response_data.csv.json') as f:
    res_data = json.load(f)

#returns dict of all responses given by category, and
#returns dict where keys are categories, holding dict where keys are each response given for that category,
#which holds dict where keys are order # and values are probability of that response being given at that order #
def getProbs(data):
    trialsPerCat = len(data)/numCats
    resProbs = {}
    resCounts = {}
    for trial in data:
        cat = trial['category']
        resProbs[cat] = resProbs.get(cat, {})
        for i in range(1, 11):
            key = 'response' + str(i)
            res = trial[key].lower()
            resCounts[cat] = resCounts.get(cat, {})
            matches = get_close_matches(res, resCounts[cat], 1, 0.85)
            if len(matches) > 0:
                res = matches[0]
            resCounts[cat][res] = resCounts[cat].get(res, 0) + 1
            resProbs[cat][res] = resProbs[cat].get(res, {})
            resProbs[cat][res][i] = (resProbs[cat][res].get(i, 0)+1)/trialsPerCat #for probability rather than count
    #for response x, resProbs[category][x].get(i, 0) = probability of x being generated ith by any subject
    responses = {}
    for cat in resCounts.keys():
        responses[cat] = list(resCounts[cat].keys())
    return responses, resCounts, resProbs

def generations(data):
    trialsPerCat = len(data)/numCats
    genCounts = {}
    genList = {}
    for trial in data:
        cat = trial['category']
        genCounts[cat] = genCounts.get(cat, {})
        genList[cat] = genList.get(cat, [])
        genList[cat].append([])
        for i in range(1, 11):
            key = 'response' + str(i)
            gen = trial[key].lower()
            matches = get_close_matches(gen, genCounts[cat].keys(), 1, 0.85)
            if len(matches) > 0:
                gen = matches[0]
            genCounts[cat][gen] = genCounts[cat].get(gen, 0) + 1
            genList[cat][len(genList[cat])-1].append(gen)
    return genCounts, genList

#takes resProbs calculated above and returns, for each category,
#the weighted probability of each given response
#weighted probability calculated by summing prob of response at each order, multiplied by 1/order #, then dividing by sum of weights
def weightProbs(resProbs):
    probs = {}
    for cat, resDict in resProbs.items():
        for res, prob in resDict.items():
            total = 0
            div = 0
            for i in range(1, 11):
                total = total + (prob.get(i, 0))/(i)
                div = div + (1/(i))
            probs[cat] = prob.get(cat, {})
            probs[cat][res] = total/div
    return probs

#plots responses for each category
def plotData(responses):
    for cat in responses.keys():
        fig = plt.figure()
        ax = fig.add_axes([0,0,1,1])
        res = list(responses[cat].keys())
        res.sort(reverse=True, key=lambda k: responses[cat][k])
        counts = list(responses[cat].values())
        counts.sort(reverse=True)
        ax.bar(res, counts)
        plt.show()

#measures average number of common responses between 2 subjects
def ave_in_common(data, responses):
    vectors = getVecs(data, responses)
    aveCommon = {}
    for cat, vecs in vectors.items():
        #one hot encodings array
        total, div = 0, 0
        for i in range(len(vecs)):
            for j in range(i+1, len(vecs)):
                common = 0
                for k in range(len(vecs[0])):
                    if vecs[i][k] + vecs[j][k] == 2:
                        common = common + 1
                total = total + common
                div = div + 1
        aveCommon[cat] = total/div
    return aveCommon

#compare one hot encodings vs random one hot
def getSimilarity(data, responses):
    vectors = getVecs(data, responses)
    catSims = {}
    for cat, vecs in vectors.items():
        #one hot encodings array
        cm = np.corrcoef(*vecs)
        rand_vecs = []
        for i in range(len(vecs)):
            rand_vec = [0]*len(vecs[0])
            x = 0
            while x<10:
                i = random.randint(0, len(rand_vec)-1)
                if(rand_vec[i] == 0):
                    rand_vec[i] = 1
                    x = x+1
            rand_vecs.append(rand_vec)
        rand_cm = np.corrcoef(*rand_vecs)
        total, rand_total = 0, 0
        div = 0
        for r in range (len(cm)):
            for c in range(len(cm[0])):
                if(r != c):
                    total = total + cm[r][c]
                    rand_total = rand_total + rand_cm[r][c]
                    div = div + 1
        catSims[cat] = (total/div, rand_total/div)

    #sim = sum(list(catSims.values()))/numCats
    sim = 0
    return sim, catSims

#correlation coefficient for one-hot encodingd
#responses contains list of all responses for each category
#go thru each trial, for that trial's category, get right res list, make vector 1 or 0 for each response, add vector to vector list for that cat
#compare vecs within category, return these and average
def getSimilarity3(data, responses):
    vectors = getVecs(data, responses)
    catSims = {}
    for cat, vecs in vectors.items():
        print(vecs)
        cm = np.corrcoef(*vecs)
        total = 0
        div = 0
        for r in range (len(cm)):
            for c in range(len(cm[0])):
                if(r != c):
                    total = total + cm[r][c]
                    div = div + 1
        catSims[cat] = total/div
    sim = sum(list(catSims.values()))/numCats
    return sim, catSims

#returns one hot encodings for a list of trials
def getVecs(data, responses):
    vectors = {}
    for trial in data:
        cat = trial['category']
        vectors[cat] = vectors.get(cat, [])
        vec = [0] * len(responses[cat])
        for i in range(1,11):
            key = 'response' + str(i)
            res = trial[key].lower()
            matches = get_close_matches(res, responses[cat], 1, 0.85)
            if len(matches) > 0:
                res = matches[0]
            vec[responses[cat].index(res)] = 1
        vectors[cat].append(vec)
    return vectors


#calc similarity using intersection of weighted response sets / union of weighted response sets
def getSimilarity2(data):
    lists = {}
    for trial in data:
        cat = trial['category']
        lists[cat] = lists.get(cat, [])
        responses = []
        for i in range(1,11):
            key = 'response' + str(i)
            responses.append(trial[key].lower())
        lists[cat].append(responses)
    #now have list of lists of responses for each category
    allSim = {}
    for cat in lists.keys():
        catLists = lists[cat]
        catSim = 0
        div = 0
        for i in range(len(catLists)):
            #list1 = weightByRank(catLists[i])
            list1 = catLists[i]
            for j in range(i+1, len(catLists)):
                #list2 = weightByRank(catLists[j])
                list2 = catLists[j]
                #calc sim of list1 and list2
                sim = len(intersect(list1, list2))/len(list1 + list2)
                catSim = catSim + sim
                div = div + 1
        catSim = catSim/div        
        allSim[cat] = catSim
    return allSim, sum(allSim.values())/numCats

def weightByRank(oldList):
    newList = []
    for i in range(len(oldList)):
        for mult in range(len(oldList)-i, 1, -1):
            for j in range(mult):
                newList.append(oldList[i])
    return newList

def intersect(list1, list2):
    intersect = []
    for i in range(len(list1)):
        for j in range(len(list2)):
            if list1[i] == list2[j]:
                intersect.append(list1[i])
                list2[j] = ""
    return intersect

def generations(data):
    trialsPerCat = len(data)/numCats
    genCounts = {}
    genList = {}
    for trial in data:
        cat = trial['category']
        genCounts[cat] = genCounts.get(cat, {})
        genList[cat] = genList.get(cat, [])
        genList[cat].append([])
        for i in range(1, 11):
            key = 'response' + str(i)
            gen = trial[key].lower()
            matches = get_close_matches(gen, genCounts[cat].keys(), 1, 0.85)
            if len(matches) > 0:
                gen = matches[0]
            genCounts[cat][gen] = genCounts[cat].get(gen, 0) + 1
            genList[cat][len(genList[cat])-1].append(gen)
        genList[cat][len(genList[cat])-1] = list(set(genList[cat][len(genList[cat])-1]))
    return genCounts, genList

#for each category, for each question, record all responses/considerations and counts, and a list of each subjects responses
def considerations(data):
    resCounts = {}
    resList = {}
    i = 0
    for trial in data:
        cat = trial['category']
        resCounts[cat] = resCounts.get(cat, {})
        resList[cat] = resList.get(cat, {})
        q = trial['question'] 
        resCounts[cat][q] = resCounts[cat].get(q, {})
        resList[cat][q] = resList[cat].get(q, [])
        res = trial['response'].lower()
        matches = get_close_matches(res, resCounts[cat][q].get('considerations', []), 1, 0.85)
        if len(matches) > 0:
            res = matches[0]
        resCounts[cat][q]['responses'] = (resCounts[cat][q].get('responses', {}))
        resCounts[cat][q]['responses'][res] = resCounts[cat][q]['responses'].get(res, 0) + 1
        resCounts[cat][q]['considerations'] = resCounts[cat][q].get('considerations', {})
        resList[cat][q].append([res])
        for i in range(1, 8):
            key = 'consideration' + str(i)
            con = trial[key].lower()
            if len(get_close_matches(con, ["n/a", "na", "dont know"], 1, 0.85)) > 0:
                continue
            matches = get_close_matches(con, resCounts[cat][q]['considerations'], 1, 0.85)
            if len(matches) > 0:
                con = matches[0]
            resCounts[cat][q]['considerations'][con] = resCounts[cat][q]['considerations'].get(con, 0) + 1
            resList[cat][q][len(resList[cat][q])-1].append(con)
        resList[cat][q][len(resList[cat][q])-1] = list(set(resList[cat][q][len(resList[cat][q])-1]))
        i = i+1
    return resCounts, resList


categories = ['types of furniture', 'vegetables', 'chain restaurants', 'breakfast foods', 'sports', 'clothing items', 'zoo animals', 'jobs', 'holidays', 'kitchen appliances']

#measures average number of common responses between 2 subjects - need to divide by num things
def aveCommon(list1, list2):
    total = 0
    div = 0
    commonCounts = {}
    if list2 == {}: #only one set of lists
        for i in range(0, len(list1)):
            l1 = list1[i]
            for j in range(i+1, len(list1)):
                l2 = list1[j]
                common = list(set(l1).intersection(set(l2)))
                for res in common:
                    commonCounts[res] = commonCounts.get(res, 0) + 1
                numCommon = len(common)
                #print(str(numCommon) + ": " + str(common))
                total = total + numCommon
                div = div + 1
    else:
        for l1 in list1:
            for l2 in list2:
                common = list(set(l1).intersection(set(l2)))
                for res in common:
                    commonCounts[res] = commonCounts.get(res, 0) + 1
                numCommon = len(common)
                #print(str(numCommon) + ": " + str(common))
                total = total + numCommon
                div = div + 1
    return total/div, sorted(commonCounts.items(), key=lambda x: x[1], reverse=True)

genCounts, genList = generations(gen_data)
resCounts, resList = considerations(res_data)
averageInCommon = {}
for cat, qLists in resList.items():
    averageInCommon[cat] = {}
    total, div = 0, 0
    print(cat + ":")
    for q, qList in qLists.items():
        print(q)
        av, commonCounts = aveCommon(qList, genList[cat])
        averageInCommon[cat][q] = av
        total = total + av
        div = div + 1
        print("average: " + str(av))
        print(str(commonCounts))
        print(" ")
    averageInCommon[cat]["average"] = total/div
    print(cat + " average: " + str(total/div))
    print(" ")

newRes = {}
for d in resCounts['zoo animals'].values():
    for i in d['considerations'].items():
        animal = i[0]
        count = i[1]
        print(animal)
        print(count)
        newRes[animal] = newRes.get(animal, 0) + count
print(sorted(newRes.items(), key=lambda item: item[1]))

print(sorted(genCounts['zoo animals'].items(), key=lambda item: item[1]))
#print(str(averageInCommon))
#print(resCounts)
#print(resList)
#plotData(genCounts)
#aveCommon = getSimilarity4(data, generations)
#print(aveCommon) #average number of generation responses in common per category
#
#con = considerations()
#print(con['types of furniture'])
#print("\n")
#print(con['vegetables'])
#print("\n")
#print(con['chain restaurants'])
#print("\n")
#print(con['breakfast foods'])
#print("\n")
#print(con['sports'])
#print("\n")
#print(con['clothing items'])
#print("\n")
#print(con['zoo animals'])
#print("\n")
#print(con['jobs'])
#print("\n")
#print(con['holidays'])
#print("\n")
#print(con['kitchen appliances'])
#print("\n")
###


















#determines average similarity between response lists by comparing, within each category, each list to each other
#first weights lists by putting first response into list 10 times, second in 9 times, ... tenth in 1 time
#then compares lists by calculating (num elements in intersection)/(num elements in union)
#averages similarities by summing and then dividing by number of responses per category
#also returns total similarity, average of similarities for each category
