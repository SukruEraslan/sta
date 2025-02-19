import string

#Parameters - 0 means all
goal = 0
achievement = 0
focus  = 0
communication = 0
confidence = 0
selfRegulation = 0
performance = 0

#STA Parameters
globalToleranceLevel = 0.75
dataFile = "data.txt"

#Program Global Variables
AoINames = []

#This function is an app-specific function
def getAOIMeaning(key):
    AOI_Meanings = {}
    AOI_Meanings["A"] = "gaze bubble"
    AOI_Meanings["B"] = "clipboard"
    AOI_Meanings["C"] = "nursing instructor"
    AOI_Meanings["D"] = "patient"
    AOI_Meanings["E"] = "vitals monitor"
    AOI_Meanings["F"] = "patient history screen"
    AOI_Meanings["G"] = "calculator"
    AOI_Meanings["H"] = "thermometer"
    AOI_Meanings["I"] = "syringe"
    AOI_Meanings["J"] = "med bottle"
    AOI_Meanings["K"] = "IV pump"
    AOI_Meanings["L"] = "oxygen bottle"

    return AOI_Meanings[key]

#This function is used to read the data file to generate paths, i.e., sequences
def getPaths(filename):
    file = open(filename, "r")
    next(file)
    records = file.read().split("\n")
    sequences = {}
    for record in records:
        fields = record.split("\t")
        participant, duration, object  = fields[0], fields[5], fields[6]

        f_goal = int(fields[14])
        f_achievement = int(fields[15])
        f_focus = int(fields[16])
        f_communication = int(fields[17])
        f_confidence = int(fields[18])
        f_selfRegulation = int(fields[19])
        f_performance = fields[21]

        if (int(object) < 0):
            continue
        else:
            object = string.ascii_uppercase[int(object)]
            if object not in AoINames:
                AoINames.append(object)

        if participant not in sequences:
            sequences[participant] = [[object, duration]]
        else:
            sequences[participant].append([object, duration])

        toRemove = False

        if goal != 0 and goal != f_goal:
            toRemove = True
        if achievement != 0 and achievement != f_achievement:
            toRemove = True
        if focus != 0 and focus != f_focus:
            toRemove = True
        if communication != 0 and communication != f_communication:
            toRemove = True
        if confidence != 0 and confidence != f_confidence:
            toRemove = True
        if selfRegulation != 0 and selfRegulation != f_selfRegulation:
            toRemove = True
        if performance != 0 and performance != f_performance:
            toRemove = True

        if toRemove == True:
            sequences[participant].pop()

    return sequences

#STA helper function
def getNumberedSequence(Sequence):
    numberedSequence = []
    numberedSequence.append([Sequence[0][0], 1, Sequence[0][1]])

    for y in range(1, len(Sequence)):
        if Sequence[y][0] == Sequence[y - 1][0]:
            numberedSequence.append([Sequence[y][0], numberedSequence[len(numberedSequence) - 1][1], Sequence[y][1]])
        else:
            numberedSequence.append([Sequence[y][0], getSequenceNumber(Sequence[0:y], Sequence[y][0]), Sequence[y][1]])

    AoIList = getExistingAoIListForSequence(numberedSequence)
    newSequence = []

    myList = []
    myDictionary = {}
    replacementList = []

    for x in range(0, len(AoIList)):
        totalDuration = 0
        for y in range(0, len(numberedSequence)):
            if numberedSequence[y][0:2] == AoIList[x]:
                totalDuration = totalDuration + int(numberedSequence[y][2])
        myList.append([AoIList[x], totalDuration])

    for x in range(0, len(AoINames)):
        myAoIList = [w for w in myList if w[0][0] == AoINames[x]]
        myAoIList.sort(key=lambda x: x[1])
        myAoIList.reverse()
        if len(myAoIList) > 0:
            myDictionary[AoINames[x]] = myAoIList

    for AoI in AoIList:
        index = [w[0] for w in myDictionary[AoI[0]]].index(AoI)
        replacementList.append([AoI, [AoI[0], (index + 1)]])

    for x in range(0, len(numberedSequence)):
        myReplacementList = [w[0] for w in replacementList]
        index = myReplacementList.index(numberedSequence[x][0:2])
        newSequence.append([replacementList[index][1][0]] + [replacementList[index][1][1]] + [numberedSequence[x][2]])

    return newSequence

#STA helper function
def getSequenceNumber(Sequence, Item):
    abstractedSequence = getAbstractedSequence(Sequence)
    return abstractedSequence.count(Item) + 1

#STA helper function
def getAbstractedSequence(Sequence):
    if len(Sequence) == 0:
        myAbstractedSequence = []
    else:
        myAbstractedSequence = [Sequence[0][0]]
        for y in range(1, len(Sequence)):
            if myAbstractedSequence[len(myAbstractedSequence) - 1] != Sequence[y][0]:
                myAbstractedSequence.append(Sequence[y][0])
    return myAbstractedSequence

#STA helper function
def getExistingAoIListForSequence(Sequence):
    AoIlist = []
    for x in range(0, len(Sequence)):
        try:
            AoIlist.index(Sequence[x][0:2])
        except:
            AoIlist.append(Sequence[x][0:2])
    return AoIlist

#STA helper function
def calculateImportanceThreshold(mySequences, Threshold):
    myAoICounter = getNumberDurationOfAoIs(mySequences)
    commonAoIs = []
    for myAoIdetail in myAoICounter:
        if myAoIdetail[3] >= Threshold:
            commonAoIs.append(myAoIdetail)

    if len(commonAoIs) == 0:
        return -1

    minValueCounter = commonAoIs[0][1]
    for AoIdetails in commonAoIs:
        if minValueCounter > AoIdetails[1]:
            minValueCounter = AoIdetails[1]

    minValueDuration = commonAoIs[0][2]
    for AoIdetails in commonAoIs:
        if minValueDuration > AoIdetails[2]:
            minValueDuration = AoIdetails[2]

    return [minValueCounter, minValueDuration]

#STA helper function
def getNumberDurationOfAoIs(Sequences):
    AoIs = getExistingAoIList(Sequences)
    AoIcount = []
    for x in range(0, len(AoIs)):
        counter = 0
        duration = 0
        flagCounter = 0
        keys = list(Sequences.keys())
        for y in range(0, len(keys)):
            if [s[0:2] for s in Sequences[keys[y]]].count(AoIs[x]) > 0:
                counter = counter + [s[0:2] for s in Sequences[keys[y]]].count(AoIs[x])
                duration = duration + sum([int(w[2]) for w in Sequences[keys[y]] if w[0:2] == AoIs[x]])
                flagCounter = flagCounter + 1

        AoIcount.append([AoIs[x], counter, duration, flagCounter])

    return AoIcount

#STA helper function
def updateAoIsFlag(AoIs, threshold):
    for AoI in AoIs:
        if AoI[1] >= threshold[0] and AoI[2] >= threshold[1]:
            AoI[3] = True
    return AoIs

#STA helper function
def removeInsignificantAoIs(Sequences, AoIList):
    significantAoIs = []
    for AoI in AoIList:
        if AoI[3] == True:
            significantAoIs.append(AoI[0])

    keys = list(Sequences.keys())
    for y in range(0, len(keys)):
        temp = []
        for k in range(0, len(Sequences[keys[y]])):
            try:
                significantAoIs.index(Sequences[keys[y]][k][0:2])
                temp.append(Sequences[keys[y]][k])
            except:
                continue
        Sequences[keys[y]] = temp
    return Sequences

#STA helper function
def getExistingAoIList(Sequences):
    AoIlist = []
    keys = list(Sequences.keys())
    for y in range(0, len(keys)):
        for x in range(0, len(Sequences[keys[y]])):
            try:
                AoIlist.index(Sequences[keys[y]][x][0:2])
            except:
                AoIlist.append(Sequences[keys[y]][x][0:2])
    return AoIlist

#STA helper function
def calculateNumberDurationOfFixationsAndNSV(Sequences):
    keys = list(Sequences.keys())
    for x in range(0, len(keys)):
        myAbstractedSequence = []
        if len(Sequences[keys[x]]) != 0:
            myAbstractedSequence = [Sequences[keys[x]][0][0:2] + [1] + [int(Sequences[keys[x]][0][2])]]
            for y in range(1, len(Sequences[keys[x]])):
                if myAbstractedSequence[len(myAbstractedSequence) - 1][0:2] != Sequences[keys[x]][y][0:2]:
                    myAbstractedSequence.append(Sequences[keys[x]][y][0:2] + [1] + [int(Sequences[keys[x]][y][2])])
                else:
                    myAbstractedSequence[len(myAbstractedSequence) - 1][2] = \
                    myAbstractedSequence[len(myAbstractedSequence) - 1][2] + 1
                    myAbstractedSequence[len(myAbstractedSequence) - 1][3] = \
                    myAbstractedSequence[len(myAbstractedSequence) - 1][3] + int(Sequences[keys[x]][y][2])

        Sequences[keys[x]] = myAbstractedSequence

    keys = list(Sequences.keys())
    for x in range(0, len(keys)):
        for y in range(0, len(Sequences[keys[x]])):
            if len(Sequences[keys[x]]) < 2:
                value = 0
            else:
                value = 0.9 / (len(Sequences[keys[x]]) - 1)
            NSV = 1 - round(y, 2) * value
            Sequences[keys[x]][y] = Sequences[keys[x]][y] + [NSV]
    return Sequences

#STA helper function
def calculateTotalNumberDurationofFixationsandNSV(AoIList, Sequences):
    for x in range(0, len(AoIList)):
        duration = 0
        counter = 0
        totalNSV = 0

        flag = 0
        keys = list(Sequences.keys())
        for y in range(0, len(keys)):
            for k in range(0, len(Sequences[keys[y]])):
                if Sequences[keys[y]][k][0:2] == AoIList[x]:
                    counter = counter + Sequences[keys[y]][k][2]
                    duration = duration + Sequences[keys[y]][k][3]
                    totalNSV = totalNSV + Sequences[keys[y]][k][4]
                    flag = flag + 1

        AoIList[x] = AoIList[x] + [counter] + [duration] + [totalNSV] + [flag]

    return AoIList

#STA helper function
def getValueableAoIs(AoIList, Threshold):
    commonAoIs = []
    valuableAoIs = []
    for myAoIdetail in AoIList:
        if myAoIdetail[5] >= Threshold:
            commonAoIs.append(myAoIdetail)

    minValue = commonAoIs[0][4]
    for AoIdetails in commonAoIs:
        if minValue > AoIdetails[4]:
            minValue = AoIdetails[4]

    for myAoIdetail in AoIList:
        if myAoIdetail[4] >= minValue:
            valuableAoIs.append(myAoIdetail)

    return valuableAoIs

#STA function
def STA(mySequences, toleranceLevel):
    # STA Algorithm
    # First-Pass
    mySequences_num = {}
    keys = list(mySequences.keys())
    for y in range(0, len(keys)):
        # print keys[y], mySequences[keys[y]]
        if (len(mySequences[keys[y]]) != 0):
            mySequences_num[keys[y]] = getNumberedSequence(mySequences[keys[y]])
        else:
            mySequences_num[keys[y]] = []

    ToleranceThreshold = toleranceLevel * len(keys)
    myImportanceThreshold = calculateImportanceThreshold(mySequences_num, ToleranceThreshold)
    if myImportanceThreshold != -1:
        myImportantAoIs = updateAoIsFlag(getNumberDurationOfAoIs(mySequences_num), myImportanceThreshold)
        myNewSequences = removeInsignificantAoIs(mySequences_num, myImportantAoIs)

        # Second-Pass
        myNewAoIList = getExistingAoIList(myNewSequences)
        myNewAoIList = calculateTotalNumberDurationofFixationsandNSV(myNewAoIList,
                                                                     calculateNumberDurationOfFixationsAndNSV(
                                                                         myNewSequences))
        myFinalList = getValueableAoIs(myNewAoIList, ToleranceThreshold)
        myFinalList.sort(key=lambda x: (x[4], x[3], x[2]))
        myFinalList.reverse()

        commonSequence = []
        for y in range(0, len(myFinalList)):
            commonSequence.append(myFinalList[y][0])
        return getAbstractedSequence(commonSequence)
    else:
        return []

#Main function to use STA
if __name__ == "__main__":
    sequences = getPaths(dataFile)
    STA_output = STA(sequences, globalToleranceLevel)
    trendingpath = []
    for item in STA_output:
        trendingpath.append(getAOIMeaning(item))
    print(trendingpath)



