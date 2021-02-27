#!/usr/bin/env python3

import json
from difflib import get_close_matches
import numpy as np
import matplotlib.pyplot as plt
import random

numCats = 10
categories = ['types of furniture', 'vegetables', 'chain restaurants', 'breakfast foods', 'sports', 'clothing items', 'zoo animals', 'jobs', 'holidays', 'kitchen appliances']

with open('/Users/traceymills/Documents/generation_data.csv.json') as f:
  gen_data = json.load(f)
with open('/Users/traceymills/Documents/response_data.csv.json') as f:
    res_data = json.load(f)

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
            if len(get_close_matches(gen, ["n/a", "na", "dont know", "none"], 1, 0.85)) > 0:
                continue
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
        if len(get_close_matches(res, ["n/a", "na", "dont know", "none"], 1, 0.85)) > 0:
            continue
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
            if len(get_close_matches(con, ["n/a", "na", "dont know", "none"], 1, 0.85)) > 0:
                continue
            matches = get_close_matches(con, resCounts[cat][q]['considerations'], 1, 0.85)
            if len(matches) > 0:
                con = matches[0]
            resCounts[cat][q]['considerations'][con] = resCounts[cat][q]['considerations'].get(con, 0) + 1
            resList[cat][q][len(resList[cat][q])-1].append(con)
        resList[cat][q][len(resList[cat][q])-1] = list(set(resList[cat][q][len(resList[cat][q])-1]))
        i = i+1
    return resCounts, resList


#measures average number of common responses between 2 subjects - need to divide by num things
def aveCommon(list1, list2):
    total, totalRatio, div = 0, 0, 0
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
                ratioCommon = numCommon/len(l1+l2)
                #print(str(numCommon) + ": " + str(common))
                total = total + numCommon
                totalRatio = totalRatio + ratioCommon
                div = div + 1
    else:
        for l1 in list1:
            for l2 in list2:
                common = list(set(l1).intersection(set(l2)))
                for res in common:
                    commonCounts[res] = commonCounts.get(res, 0) + 1
                numCommon = len(common)
                ratioCommon = numCommon/len(l1+l2)
                #print(str(numCommon) + ": " + str(common))
                total = total + numCommon
                totalRatio = totalRatio + ratioCommon
                div = div + 1
    return total/div, totalRatio/div, sorted(commonCounts.items(), key=lambda x: x[1], reverse=True)

#print average number of responses in common between generation and response subject for each category/question
def printCommon(p):
    averageInCommon = {}
    for cat, qLists in resList.items():
        averageInCommon[cat] = {}
        total, totalRatio, div = 0, 0, 0
        if p:
            print(cat + ":")
        for q, qList in qLists.items():
            if p:
                print(q)
            av, avRatio, commonCounts = aveCommon(qList, genList[cat])
            averageInCommon[cat][q] = avRatio
            total = total + av
            totalRatio = totalRatio + avRatio
            div = div + 1
            if p:
                print("average: " + str(round(av, 3)) + " / " + str(round(avRatio, 3)))
                print(str(commonCounts))
                print(" ")
        averageInCommon[cat]["average"] = totalRatio/div
        if p:
            print(cat + " average: " + str(round(total/div, 3)) + " / " + str(round(totalRatio/div, 3)))
            print(" ")
    return averageInCommon

#by category: responses + number of times given, list of responses by subject
genCounts, genList = generations(gen_data)
#print(genCounts['zoo animals'])
#by category by question: responses + number of times given, list of responses by subject
resCounts, resList = considerations(res_data)
print(resCounts["zoo animals"])
#print(genList['zoo animals'])
def genProbs(genCounts):
    genProbs = {}
    for cat, gens in genCounts.items():
        genProbs[cat] = {}
        tot = sum(list(gens.values()))
        for g, n in gens.items():
            genProbs[cat][g] = n/tot
    return genProbs

#generations + probability of being generated for that category
genProbs = genProbs(genCounts)

def pareProbs(genProbs, prob):
    newProbs = {}
    for cat, gens in genProbs.items():
        newProbs[cat] = {}
        for g, p in gens.items():
            if p > prob:
                newProbs[cat][g] = p
    return newProbs

#genProbs = pareProbs(genProbs, 0.)





def overlapPerCategory(resCounts, genCounts):
    for cat in genCounts.keys():
        gens = list(genCounts[cat].keys())
        res = []
        tot = 0
        for q in resCounts[cat].keys():
            res = list(set(res + list(resCounts[cat][q]['considerations'].keys())))
            tot = tot + len(set(gens).intersection(set(resCounts[cat][q]['considerations'].keys())))/len(list(resCounts[cat][q]['considerations'].keys()))
            print(q + " " + str(len(list(resCounts[cat][q]['considerations'].keys()))) + " res, " + str(len(gens)) + " gen, " + str(len(set(gens).intersection(set(resCounts[cat][q]['considerations'].keys())))))
        gens = set(gens)
        res = set(res)
        print(tot/6)
        print(cat + ": " + str(len(res)) + " res, " + str(len(gens)) + " gen, " + str(len(gens.intersection(res))))
#get ratios of responses in common between generation and consideration - can compare to see which questions overlap most with generations
overlapPerCategory(resCounts, genCounts)
#common = printCommon(False)

#also want to find overlap between dif questions?
#what percentage of time are people picking options that are common generations?
def responseInGen(resCounts, genProbs):
    print("RESPONSES:")
    calc, calcc = 0, 0
    for cat, gens in genProbs.items(): #only gens over certain prob 
        catTotal, catInTotal, catTotalc, catInTotalc = 0, 0, 0, 0
        for q in resCounts[cat]:
            total, inTotal, totalc, inTotalc = 0,0,0,0
            res = resCounts[cat][q]['responses']
            cons = resCounts[cat][q]['considerations']
            for r, n in res.items():
                total = total + n
                if r in list(gens.keys()):
                    inTotal = inTotal + n
            for c, n in cons.items():
                totalc = totalc + n
                if c in list(gens.keys()):
                    inTotalc = inTotalc + n
            print("res " + q + " " + str(inTotal) + ", " + str(total) + " - " + str(inTotal/total))
            print("con " + q + " " + str(inTotalc) + ", " + str(totalc) + " - " + str(inTotalc/totalc))
            catTotal = catTotal + total
            catInTotal = catInTotal + inTotal
            catTotalc = catTotalc + totalc
            catInTotalc = catInTotalc + inTotalc
        print("res " + cat + " : " + str(catInTotal) + ", " + str(catTotal) + " - " + str(catInTotal/catTotal))
        calc = calc + catInTotal/catTotal
        print("con " + cat + " : " + str(catInTotalc) + ", " + str(catTotalc) + " - " + str(catInTotalc/catTotalc))
        calcc = calcc + catInTotalc/catTotalc
    print(str(calc/10))
    print(str(calcc/10))




#what percentage of considerations given are generations?
def considInGen(resCounts, genCounts):
    print("CONSIDERSTIONS:")
    for cat, gens in genCounts.items():
        catTotal, catInTotal = 0, 0
        for q in resCounts[cat]:
            total, inTotal = 0,0
            res = resCounts[cat][q]['considerations']
            for r, c in res.items():
                total = total + c
                if r in list(gens.keys()):
                    inTotal = inTotal + c
            print(q + " " + str(inTotal) + ", " + str(total) + " - " + str(inTotal/total))
            catTotal = catTotal + total
            catInTotal = catInTotal + inTotal
        print(cat + " : " + str(catInTotal) + ", " + str(catTotal) + " - " + str(catInTotal/catTotal))

#responseInGen(resCounts, genProbs)
#considInGen(resCounts, genCounts)






#more in common means that people's considerations for the question were more similar to random generations for that category
#this could indicate that they are relying on context free value (CFV) to generate considerations
    #could measure CFV by asking people to rank "goodness" of responses

#Theory: People rely more on CFV when the category is bigger
    #test: guage subjective size of category using distribution of generations for that category
        #record number of times each response is given, take av?
        #lower av means larger category, should have more in common for questions of that category
        #check for correlation between size(cat) and common[cat][all qs][avRatio] - average for qs of each category
def categorySize(genCounts):
    catSize = {}
    for cat, gens in genCounts.items():
        catSize[cat] = len(gens.keys())
        print(cat + ": " + str(catSize[cat]))
    return catSize
#catSize = categorySize(genCounts)

def CFVtoSize(catSize, common):
    x, y = [], []
    for cat in categories:
        x.append(catSize[cat]) #size of category
        y.append(sum(common[cat].values())/len(common[cat])) #average common ratio for questions in that category
    return np.corrcoef(x, y)[0][1]
#print("category size/overlap correlation: " + str(CFVtoSize(catSize, common)))




#Theory: People rely more on CFV when the question is harder
    #test: estimate (or ask ppl) about hardness of question, rank out of 5?
        #more hard should mean rely more on CFV, more in common for that question esp. compared to others in that category
        #check for correlation between hardness(q), common[cat][q][avRatio]
def qDifficulty():
    #check for correlation within category
    return {'breakfast foods': {'What breakfast food is eaten the most in October?': 5, 'What breakfast food is worst to eat before working out?': 2, 'What breakfast food is the most expensive?': 4, 'What breakfast food is the most colorful?': 1, 'What breakfast food takes the longest to eat?': 3},
        'jobs': {'What job has been around the longest?': 3, 'What job do people stay in for the longest amount of time?': 4, 'What job requires the most talking?':1, 'What job is the most common one to have?': 5, 'What job requires the best eyesight?': 2},
        'chain restaurants': {'What chain restaurant tends to be the dirtiest?': 3, 'What chain restaurant has the most items on their menu?': 5, 'What chain restaurant has the worst desserts?': 4, 'What chain restaurant has the most colorful logo?': 1, 'What chain restaurant is the most expensive?': 2},
        'clothing items': {'What clothing item is most often purchased online?': 4, 'What clothing item is borrowed most frequently?': 3, 'What clothing item is the most expensive for its weight?': 5, 'What clothing item do people keep the longest?': 2, 'What clothing item comes in the fewest colors?': 1,},
        'zoo animals': {'What zoo animal eats the most for its body weight?': 3, 'What zoo animal has the shortest lifespan?': 2, 'What zoo animal has the biggest feet relative to its body size?': 4, 'What zoo animal spends the most time awake?': 5, 'What zoo animal would you least want to have in your car?': 1},
        'vegetables': {'What vegetable is heaviest for its size?': 5, 'What vegetable comes in the most colors?': 1, 'What vegetable has the most sugar?': 4, 'What vegetable do people eat most often with breakfast?': 2, 'What vegetable is eaten the least in spring?': 3},
        'sports': {'What sport requires the most teamwork?': 1, 'What sport requires the most agility?': 2, 'What sport is easiest to learn?': 2, 'What sport requires the most gear?': 1, 'What sport has been around the longest?': 2},
        'types of furniture': {'What piece of furniture would make the best weapon?': 2, 'What piece of furniture is the most flammable?': 2, 'What piece of furniture do people donate the most often?': 2, 'What piece of furniture can support the least amount of weight?': 2, 'What piece of furniture would you be most surprised to see in a kitchen?': 3},
        'holidays': {'What holiday is the most forgettable?': 3, 'What holiday involves the most drinking?': 1, 'What holiday is the least religious?': 2, 'What holiday has the worst food associated with it?': 2, 'What holiday has the most different names?': 3},
        'kitchen appliances': {'What kitchen appliance requires the least energy?': 3, 'What kitchen appliance is used most in the winter?': 1, 'What kitchen appliance breaks the most?': 2, 'What kitchen appliance is used the least?': 2, 'What kitchen appliance is the noisiest?': 1}}  
    x= {'breakfast foods': {'What breakfast food is eaten the most in October?': 3, 'What breakfast food is worst to eat before working out?': 2, 'What breakfast food is the most expensive?': 2, 'What breakfast food is the most colorful?': 1, 'What breakfast food takes the longest to eat?': 3},
        'jobs': {'What job has been around the longest?': 2, 'What job do people stay in for the longest amount of time?': 2, 'What job requires the most talking?': 1, 'What job is the most common one to have?': 3, 'What job requires the best eyesight?': 2},
        'chain restaurants': {'What chain restaurant tends to be the dirtiest?': 2, 'What chain restaurant has the most items on their menu?': 3, 'What chain restaurant has the worst desserts?': 3, 'What chain restaurant has the most colorful logo?': 2, 'What chain restaurant is the most expensive?': 2},
        'clothing items': {'What clothing item is most often purchased online?': 2, 'What clothing item is borrowed most frequently?': 1, 'What clothing item is the most expensive for its weight?': 3, 'What clothing item do people keep the longest?': 2, 'What clothing item comes in the fewest colors?': 3,},
        'zoo animals': {'What zoo animal eats the most for its body weight?': 2, 'What zoo animal has the shortest lifespan?': 2, 'What zoo animal has the biggest feet relative to its body size?': 2, 'What zoo animal spends the most time awake?': 2, 'What zoo animal would you least want to have in your car?': 1},
        'vegetables': {'What vegetable is heaviest for its size?': 3, 'What vegetable comes in the most colors?': 1, 'What vegetable has the most sugar?': 2, 'What vegetable do people eat most often with breakfast?': 1, 'What vegetable is eaten the least in spring?': 2},
        'sports': {'What sport requires the most teamwork?': 1, 'What sport requires the most agility?': 2, 'What sport is easiest to learn?': 2, 'What sport requires the most gear?': 1, 'What sport has been around the longest?': 2},
        'types of furniture': {'What piece of furniture would make the best weapon?': 2, 'What piece of furniture is the most flammable?': 2, 'What piece of furniture do people donate the most often?': 2, 'What piece of furniture can support the least amount of weight?': 2, 'What piece of furniture would you be most surprised to see in a kitchen?': 3},
        'holidays': {'What holiday is the most forgettable?': 3, 'What holiday involves the most drinking?': 1, 'What holiday is the least religious?': 2, 'What holiday has the worst food associated with it?': 2, 'What holiday has the most different names?': 3},
        'kitchen appliances': {'What kitchen appliance requires the least energy?': 3, 'What kitchen appliance is used most in the winter?': 1, 'What kitchen appliance breaks the most?': 2, 'What kitchen appliance is used the least?': 2, 'What kitchen appliance is the noisiest?': 1}}
#def CFVtoDifficulty(qDifficulty, common):
#    x, y = [], []
#    for cat in categories:
#        for q, score in qDifficulty[cat].items():
#            x.append(score) #difficulty of question
#            y.append(common[cat][q])
#    return np.corrcoef(x, y)[0][1]
def CFVtoDifficulty(qDifficulty, common):
    for cat in categories:
        x, y = [], []
        for q, score in qDifficulty[cat].items():
            x.append(score) #difficulty of question
            y.append(common[cat][q])
        print(cat + ": " +str(np.corrcoef(x, y)[0][1]))

#print("question difficulty/overlap correlation: " + str(CFVtoDifficulty(qDifficulty(), common)))

#################################################
#need more data? (~10 per question)
#can go thru manually and clean?

#for cat in resCounts:
#    for q in resCounts[cat]:
#        print(q + " " + str(sum(resCounts[cat][q]['responses'].values())))

