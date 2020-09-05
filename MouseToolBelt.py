# Import Libraries
import csv
import math
import pickle
import LinearRegressionAlg
import sklearn
from sklearn import linear_model
import numpy as np

# Checks to see if the mouse is over a given box
def mouseOver(mouseX, mouseY, boxLeft, boxTop, boxRight, boxBottom):
    retValue = False

    if boxLeft <= mouseX <= boxRight and boxTop <= mouseY <= boxBottom:
        retValue = True

    return retValue


def distanceBetweenPointAndLine(linePoint1, linePoint2, point):

    # slope = (y2-y1)/(x2-x1)
    if linePoint1[0] == linePoint2[0]:
        return abs(point[0] - linePoint1[0])

    if linePoint1[1] != linePoint2[1]:
        slope = (linePoint2[1] - linePoint1[1]) / (linePoint2[0] - linePoint1[0])
    else:
        return abs(point[1] - linePoint1[1])

    # y = mx + b
    # given by the point-slope formula:  y = (slope * x) - (slope * linePoint2[0]) + linePoint2[1]

    b = linePoint2[1] - slope * linePoint2[0]

    perpendicularSlope = -1 / slope
    perpendicular_b = point[1] - perpendicularSlope * point[0]

    intersectionPoint = [0, 0]
    intersectionPoint[0] = (perpendicular_b - b) / (slope - perpendicularSlope)
    intersectionPoint[1] = perpendicularSlope*intersectionPoint[0] + perpendicular_b

    distance = math.sqrt((intersectionPoint[0] - point[0]) ** 2 +
                         (intersectionPoint[1] - point[1]) ** 2)
    return distance


def convertVectorToUnitVector(vectorTail, vectorHead, distanceBetweenThem):
    baseVector = [vectorHead[0] - vectorTail[0], vectorHead[1] - vectorTail[1]]
    if distanceBetweenThem != 0:
        multiplier = 1/distanceBetweenThem
        unitVector = [baseVector[0] * multiplier, baseVector[1] * multiplier]
        return unitVector
    else:
        return [0, 0]


def getAverageAngle(rootNode, fullQueue):
    currentUnitVectorSum = [0, 0]
    currentNode = rootNode
    counter = 0
    for j in range(rootNode.maxSize):
        currentNodeAsUnitVector = convertVectorToUnitVector((currentNode.prevNode.dataVal.MouseX, currentNode.prevNode.dataVal.MouseY),
                                                            (currentNode.dataVal.MouseX, currentNode.dataVal.MouseY),
                                                             currentNode.dataVal.ObservedDistance)
        currentUnitVectorSum[0] += currentNodeAsUnitVector[0]
        currentUnitVectorSum[1] += currentNodeAsUnitVector[1]
        currentNode = currentNode.prevNode
        counter += 1
        if fullQueue.finalNode == currentNode:
            break

    return math.atan2(currentUnitVectorSum[1], currentUnitVectorSum[0])


def getAverageSpeed(rootNode, fullQueue):
    speedSum = 0
    currentNode = rootNode
    counter = 0
    for j in range(rootNode.maxSize):
        currentSpeed = currentNode.dataVal.ObservedSpeed
        speedSum += currentSpeed
        currentNode = currentNode.prevNode
        counter += 1
        if fullQueue.finalNode == currentNode:
            break
    return speedSum / counter


def getDifferenceBetweenTwoAngles(angle1, angle2):
    r = abs(angle1 - angle2)
    if r > math.pi:
        r = 2 * math.pi - r
    return r


class mouseLogger:

    def __init__(self):
        self.mouseHistory = []
        self.filename = ""
        self.fieldnames = ['TimeStamp', 'MouseX', 'MouseY', 'StartLocation', 'TargetLocation']
        self.advancedFieldnames = ['Time_Stamp', 'MouseX', 'MouseY', 'Target_LocationX', 'Target_LocationY',
                                   'Intended_Direction', 'Target_Distance', 'Observed_Distance',
                                   'Observed_Speed', 'Observed_Direction', 'Directional_Error',
                                   'Distance_Of_Error', 'Recent_Average_Direction', 'Recent_Average_Speed']
        self.advancedHistory = []
        self.alteredNodes = []
        self.linearmodel = None
        # linked list used to track frames in real time. It also helps generate recent averages
        self.recentMovementQ = recentMovementQueue()
        self.alteredMovementQ = recentMovementQueue()
        self.algorithmAccuracy = None
        self.errorCoef = None

    def logMouse(self, x, y, current_time, currentTrainingLine):
        self.mouseHistory.append([current_time, x, y, currentTrainingLine[0], currentTrainingLine[1]])

    def openLog(self, filename):
        self.filename = filename
        with open(self.filename+'_basic', 'w') as new_file:
            csv_writer = csv.DictWriter(new_file, fieldnames=self.fieldnames, delimiter=';')
            csv_writer.writeheader()

    def writeTrainingDataToCSV(self):
        with open(self.filename+'_basic', 'a', newline='') as current_file:
            csv_writer = csv.writer(current_file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for moment in self.mouseHistory:
                csv_writer.writerow(moment)

    def generateDetailedCSV(self):

        self.advancedHistory = []

        for current in range(self.mouseHistory.__len__() - 1):
            self.generateAdvancedEntry(current)

        # clear basic history
        self.mouseHistory = []

        with open(self.filename+'_advanced', 'w') as new_file:
            csv_writer = csv.DictWriter(new_file, fieldnames=self.advancedFieldnames, delimiter=';')
            csv_writer.writeheader()
        
        with open(self.filename+'_advanced', 'a', newline='') as current_file:
            csv_writer = csv.writer(current_file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for moment in self.advancedHistory:
                csv_writer.writerow(moment)

        accuracy, errorCoef = LinearRegressionAlg.trainLinearModel(self.filename+'_advanced')
        return accuracy, errorCoef

    def generateAlteredEntry(self, index, changeFromPrev):

        thisEntry = []
        # If this is the first entry into alteredNodes, just use the observed data to fill everything
        # in with the simplest form possible
        if self.alteredNodes.__len__() == 0:
            # TIME STAMP (direct copy)
            thisEntry.append(self.mouseHistory[index][0])
            # MOUSE X (direct copy)
            thisEntry.append(self.mouseHistory[index][1])
            # MOUSE Y (direct copy)
            thisEntry.append(self.mouseHistory[index][2])
            # TARGET LOCATION X (copy)
            thisEntry.append(self.mouseHistory[index][4][0])
            # TARGET LOCATION Y (copy)
            thisEntry.append(self.mouseHistory[index][4][1])
            # INTENDED DIRECTION (give intended direction on first frame)
            targetVector = (self.mouseHistory[index][4][0] - self.mouseHistory[index][1],
                            self.mouseHistory[index][4][1] - self.mouseHistory[index][2])
            IntendedDirection = math.atan2(targetVector[1], targetVector[0])
            thisEntry.append(IntendedDirection)
            # TARGET DISTANCE (give target distance on first frame)
            TargetDistance = math.sqrt((self.mouseHistory[index][4][0] - self.mouseHistory[index][1]) ** 2 +
                                       (self.mouseHistory[index][4][1] - self.mouseHistory[index][2]) ** 2)
            thisEntry.append(TargetDistance)
            # OBSERVED DISTANCE
            thisEntry.append(0)
            # OBSERVED SPEED
            thisEntry.append(0)
            # OBSERVED DIRECTION
            thisEntry.append(0.1)
            # DIRECTIONAL ERROR
            thisEntry.append(0)
            # DISTANCE OF ERROR
            thisEntry.append(0)

            # RECENT AVERAGE DIRECTION
            # RECENT AVERAGE SPEED
            thisEntry.append(0)
            thisEntry.append(0)

            currentNodeData = advancedMouseMoment(thisEntry)
            currentNode = recentMovementNode(currentNodeData)

            self.alteredMovementQ.rootNode = currentNode
            self.alteredMovementQ.finalNode = currentNode
            self.alteredNodes.append(thisEntry)
            return
        currentAlteredIndex = self.alteredNodes.__len__()
        # TIME STAMP (direct copy)
        thisEntry.append(self.mouseHistory[index][0])
        # MOUSE X (add difference to prev)
        thisEntry.append(self.alteredNodes[currentAlteredIndex-1][1] + changeFromPrev[0])
        # MOUSE Y (add difference to prev)
        thisEntry.append(self.alteredNodes[currentAlteredIndex-1][2] + changeFromPrev[1])
        # TARGET LOCATION X (copy)
        thisEntry.append(self.mouseHistory[index][4][0])
        # TARGET LOCATION Y (copy)
        thisEntry.append(self.mouseHistory[index][4][1])
        # INTENDED DIRECTION (will get overwritten by the ML algorithm anyway)
        IntendedDirection = 0.1
        thisEntry.append(IntendedDirection)
        # TARGET DISTANCE (will get overwritten by the ML algorithm anyway)
        TargetDistance = 0
        thisEntry.append(TargetDistance)
        # OBSERVED DISTANCE
        ObservedDistance = math.sqrt((changeFromPrev[0]) ** 2 +
                                     (changeFromPrev[1]) ** 2)
        thisEntry.append(ObservedDistance)
        # OBSERVED SPEED
        delta_time = self.mouseHistory[index][0] - self.mouseHistory[index - 1][0]
        if delta_time != 0:
            ObservedSpeed = ObservedDistance / delta_time
        else:
            ObservedSpeed = ObservedDistance / 20
        thisEntry.append(ObservedSpeed)
        # OBSERVED DIRECTION
        # angle = tan-1(y3/x3)
        if index != 0:
            ObservedDirection = math.atan2(changeFromPrev[1], changeFromPrev[0])
        else:
            ObservedDirection = 0
        thisEntry.append(ObservedDirection)
        # DIRECTIONAL ERROR (found by the caller function using the ML target line) aka don't need it here so use 0
        thisEntry.append(0)
        # DISTANCE OF ERROR (found by the caller function using the ML target line) aka don't need it here so use 0
        thisEntry.append(0)

        # RECENT AVERAGE DIRECTION (over the past maxSize frames)
        # RECENT AVERAGE SPEED (over the past maxSize frames)
        thisEntry.append(0)
        thisEntry.append(0)

        currentNodeData = advancedMouseMoment(thisEntry)

        currentNode = recentMovementNode(currentNodeData)

        # connect the new node to the root of the linked list
        currentNode.prevNode = self.alteredMovementQ.rootNode
        self.alteredMovementQ.rootNode.nextNode = currentNode

        # make the new node the root node of the list
        self.alteredMovementQ.rootNode = currentNode

        # move the final node once you have seen at lease n moments where n is the max size of the queue
        if currentAlteredIndex >= self.alteredMovementQ.rootNode.maxSize:
            self.alteredMovementQ.finalNode = self.alteredMovementQ.finalNode.nextNode

        # RECENT AVERAGE DIRECTION (over the past maxSize frames)
        RecentAverageDirection = getAverageAngle(self.alteredMovementQ.rootNode, self.alteredMovementQ)
        thisEntry[12] = RecentAverageDirection

        # RECENT AVERAGE SPEED (over the past maxSize frames)
        RecentAverageSpeed = getAverageSpeed(self.alteredMovementQ.rootNode, self.alteredMovementQ)
        thisEntry[13] = RecentAverageSpeed
        currentNodeData.__init__(thisEntry)

        currentNode.dataVal = currentNodeData
        self.alteredNodes.append(thisEntry)
        return

    # Creates an advanced entry given a basic entry
    def generateAdvancedEntry(self, index):
            thisEntry = []

            # TIME STAMP (direct copy)
            thisEntry.append(self.mouseHistory[index][0])

            # MOUSE X (direct copy)
            thisEntry.append(self.mouseHistory[index][1])

            # MOUSE Y (direct copy)
            thisEntry.append(self.mouseHistory[index][2])

            # TARGET LOCATION X (copy)
            thisEntry.append(self.mouseHistory[index][4][0])

            # TARGET LOCATION Y (copy)
            thisEntry.append(self.mouseHistory[index][4][1])

            # INTENDED DIRECTION
            # (x2 - x1 , y2 - y1) are the values of the new vector (x3,y3)
            #  y3/x3 = tan(angle)
            # angle = tan-1(y3/x3)
            targetVector = (self.mouseHistory[index][4][0] - self.mouseHistory[index][1],
                            self.mouseHistory[index][4][1] - self.mouseHistory[index][2])

            IntendedDirection = math.atan2(targetVector[1], targetVector[0])
            thisEntry.append(IntendedDirection)

            # TARGET DISTANCE
            # distance = root((x2-x1)**2 + (y2-y1)**2)
            TargetDistance = math.sqrt((self.mouseHistory[index][4][0] - self.mouseHistory[index][1]) ** 2 +
                                       (self.mouseHistory[index][4][1] - self.mouseHistory[index][2]) ** 2)

            thisEntry.append(TargetDistance)

            # OBSERVED DISTANCE
            if index != 0:
                ObservedDistance = math.sqrt((self.mouseHistory[index][1] - self.mouseHistory[index - 1][1]) ** 2 +
                                             (self.mouseHistory[index][2] - self.mouseHistory[index - 1][2]) ** 2)
            else:
                ObservedDistance = 0
            thisEntry.append(ObservedDistance)

            # OBSERVED SPEED
            # speed = distance/delta_time
            if index != 0:
                delta_time = self.mouseHistory[index][0] - self.mouseHistory[index - 1][0]
                if delta_time != 0:
                    ObservedSpeed = ObservedDistance / delta_time
                else:
                    ObservedSpeed = ObservedDistance / 20
            else:
                ObservedSpeed = 0
            thisEntry.append(ObservedSpeed)

            # OBSERVED DIRECTION
            # angle = tan-1(y3/x3)
            if index != 0:
                observedVector = (self.mouseHistory[index][1] - self.mouseHistory[index - 1][1],
                                  self.mouseHistory[index][2] - self.mouseHistory[index - 1][2])
                ObservedDirection = math.atan2(observedVector[1], observedVector[0])
            else:
                ObservedDirection = 0
            thisEntry.append(ObservedDirection)

            # DIRECTIONAL ERROR
            if index != 0:
                DirectionalError = getDifferenceBetweenTwoAngles(IntendedDirection, ObservedDirection)
            else:
                DirectionalError = 0
            thisEntry.append(DirectionalError)

            # DISTANCE OF ERROR
            # aka the length of the perpendicular line connecting our current location
            # to the line from our previous location to the target point.
            # The first two tuples are used to create the formula for the target line from the previous frame
            # The final tuple returns a point at our current mouse position so we can ss how far away the user
            # has wandered from the target line

            DistanceOfError = distanceBetweenPointAndLine(
                (self.mouseHistory[index - 1][1], self.mouseHistory[index - 1][2]),
                (self.mouseHistory[index - 1][4][0], self.mouseHistory[index - 1][4][1]),
                (self.mouseHistory[index][1], self.mouseHistory[index][2]))

            thisEntry.append(DistanceOfError)

            # Keeping a linked list of the previous maxSize elements in the list

            # within the (for current) loop
            # create a new node for current
            # These two appends prevent an error in the __init__ function within
            # the advancedMouseMoment class since the final two indecies
            thisEntry.append(0)
            thisEntry.append(0)
            currentNodeData = advancedMouseMoment(thisEntry)

            currentNode = recentMovementNode(currentNodeData)

            if self.recentMovementQ.rootNode is not None:
                # connect the new node to the root of the linked list
                currentNode.prevNode = self.recentMovementQ.rootNode
                self.recentMovementQ.rootNode.nextNode = currentNode

            # make the new node the root node of the list
            self.recentMovementQ.rootNode = currentNode

            # Make the first moment measured the final node in the queue
            if index == 0:
                self.recentMovementQ.finalNode = currentNode

            # move the final node once you have seen at lease n moments where n is the max size of the queue
            if index >= self.recentMovementQ.rootNode.maxSize:
                self.recentMovementQ.finalNode = self.recentMovementQ.finalNode.nextNode

            if index != 0:
                # RECENT AVERAGE DIRECTION (over the past maxSize frames)
                RecentAverageDirection = getAverageAngle(self.recentMovementQ.rootNode, self.recentMovementQ)
                thisEntry[12] = RecentAverageDirection

                # RECENT AVERAGE SPEED (over the past maxSize frames)
                RecentAverageSpeed = getAverageSpeed(self.recentMovementQ.rootNode, self.recentMovementQ)
                thisEntry[13] = RecentAverageSpeed
                currentNodeData.__init__(thisEntry)

            currentNode.dataVal = currentNodeData
            self.advancedHistory.append(thisEntry)

    def logTesting(self, x, y, current_time, currentTrainingLine):
        self.logMouse(self, x, y, current_time, currentTrainingLine)
        self.generateAdvancedEntry(self.mouseHistory)

    def alterMouse_Setup(self, accuracy, errorCoef):
        # linear model
        self.linearmodel = pickle.load(open(self.filename + "_advanced.pickle", "rb"))
        self.algorithmAccuracy = accuracy
        self.errorCoef = errorCoef

    def alterMouse(self):

        print("-----------------------------------------------------------")
        # improve data in previous frame to advanced data
        self.generateAdvancedEntry(len(self.mouseHistory) - 1)

        # Get the mouse position this frame and previous frame
        mostRecentHistoryEntry = self.advancedHistory[len(self.advancedHistory) - 1]
        print("Most Recent History Entry: ", mostRecentHistoryEntry)

        if len(self.advancedHistory) > 1:
            previousHistoryEntry = self.advancedHistory[len(self.advancedHistory) - 2]

        # insert all of the known variables into the ML model to predict target distance and direction at this frame
        knowns = [mostRecentHistoryEntry[0], mostRecentHistoryEntry[1], mostRecentHistoryEntry[2], mostRecentHistoryEntry[7],
                  mostRecentHistoryEntry[8], mostRecentHistoryEntry[9], mostRecentHistoryEntry[12], mostRecentHistoryEntry[13]]

        x = np.array(knowns)
        x = [x]

        y = self.linearmodel.predict(x)
        print("Target Distance and Intended Direction: ", y)

        # reset the intended direction and target distance this frame to be used next frame using ML values
        self.advancedHistory[len(self.advancedHistory) - 1][5] = y[0][1]
        self.advancedHistory[len(self.advancedHistory) - 1][6] = y[0][0]

        # In order to get the distance of error (aka how far our point is from the target line) we generate a second
        # point on the target line to put into our distanceBetweenPointAndLine() function in addition to the observed
        # x,y coordinates in the previous frame

        # get the intended direction from the previous frame
        prevIntendedDirection = self.advancedHistory[len(self.advancedHistory) - 2][5]
        print("Previous Intended Direction: ", prevIntendedDirection)

        # get the slope of the intended direction line
        yxRatio = math.tan(prevIntendedDirection)
        print("yxRatio of Previous Intended Direction: ", yxRatio)

        # get the final x and y coordinates of the mouse in the previous frame
        prevX = previousHistoryEntry[1]
        prevY = previousHistoryEntry[2]
        print("Previous Observed X and Y Positions", prevX, prevY)

        # The new point represents a random point on the newly generated target line created by our ML algorithm
        newPoint = (prevX + 1, prevY + yxRatio)
        print("Additional Point On Previous Target Line = ", newPoint)

        # as long as the line between this location and the previous location is not horizontal or vertical
        # calculate the slope of that line normally, if else insert 0 or a large number (infinity won't work)
        if prevX != newPoint[0]:
            if prevY != newPoint[1]:
                slopeOfTargetLine = (newPoint[1] - prevY) / (newPoint[0] - prevX)
            else:
                slopeOfTargetLine = 0
        else:
            slopeOfTargetLine = 9999

        print("Slope Of Previous Target Line = ", slopeOfTargetLine)

        # finish building the formula for the target line using observed prevX and prevY
        # and the slope we just acquired in the above block. (now we have y = mx + b for ml generated target line)

        targetLine_b = prevY - slopeOfTargetLine * prevX
        print("b Of Previous Target Line = ", targetLine_b)
        print("Previous Target Line Equation --->  y = ", slopeOfTargetLine, "x + ", targetLine_b)

        # now build the y = mx + b formula for a perpendicular line connecting our current observed point
        # and the target line from the previous frame
        perpendicularSlope = -1 / slopeOfTargetLine
        perpendicular_b = mostRecentHistoryEntry[2] - perpendicularSlope * mostRecentHistoryEntry[1]
        print("Equation Of Perpendicular Line From Previous Target Line --> y = ",perpendicularSlope, "x + ", perpendicular_b)

        # now get the intersection point between the the target line from the previous frame and the observed
        # location of this frame
        intersectionPoint = [0, 0]
        intersectionPoint[0] = (perpendicular_b - targetLine_b) / (slopeOfTargetLine - perpendicularSlope)
        intersectionPoint[1] = perpendicularSlope * intersectionPoint[0] + perpendicular_b
        print("Intersection Point Between the two lines = ", intersectionPoint[0], intersectionPoint[1])

        errorDomain = (mostRecentHistoryEntry[1], intersectionPoint[0])
        error = errorDomain[1] - errorDomain[0]
        print("Error Domain (of the x axis): ", errorDomain)
        print("Size of Error = ", error)

        alteredMousePos = [mostRecentHistoryEntry[1], mostRecentHistoryEntry[2]]
        if abs(error) > abs(self.errorCoef/2):
            print("Mouse Position Altered")
            alteredMousePos[0] = mostRecentHistoryEntry[1] + error
            alteredMousePos[1] = perpendicularSlope * alteredMousePos[0] + perpendicular_b
        else:
            print("Mouse Position Not Altered")

        self.advancedHistory[1] = alteredMousePos[0]
        self.advancedHistory[2] = alteredMousePos[1]
        print("Algorithm Accuracy: ", self.algorithmAccuracy)
        print("Observed Mouse Position = ", mostRecentHistoryEntry[1], mostRecentHistoryEntry[2])
        print("Altered Mouse Position = ", alteredMousePos[0], alteredMousePos[1])

        return alteredMousePos[0], alteredMousePos[1]


    def getNextAlteredPoint(self):
        print("---------------------------------------------------")
        index = len(self.mouseHistory) - 1
        changeFromPrevPoint = [self.mouseHistory[index][1] - self.mouseHistory[index-1][1],
                               self.mouseHistory[index][2] - self.mouseHistory[index-1][2]]
        self.generateAlteredEntry(index, changeFromPrevPoint)

        yetToBeAlteredEntry = self.alteredNodes[len(self.alteredNodes) - 1]

        if len(self.alteredNodes) > 1:
            previousAlteredEntry = self.alteredNodes[len(self.alteredNodes) - 2]

        # insert all of the known variables into the ML model to predict target distance and direction at this frame
        knowns = [yetToBeAlteredEntry[0], yetToBeAlteredEntry[1], yetToBeAlteredEntry[2],
                  yetToBeAlteredEntry[7], yetToBeAlteredEntry[8], yetToBeAlteredEntry[9],
                  yetToBeAlteredEntry[12], yetToBeAlteredEntry[13]]

        x = np.array(knowns)
        x = [x]
        y = self.linearmodel.predict(x)

        self.alteredNodes[len(self.alteredNodes) - 1][5] = y[0][1]
        self.alteredNodes[len(self.alteredNodes) - 1][6] = y[0][0]

        if len(self.alteredNodes) <= 1:
            return yetToBeAlteredEntry[1], yetToBeAlteredEntry[2]

        # get the intended direction from the previous frame
        prevIntendedDirection = self.alteredNodes[len(self.alteredNodes) - 2][5]

        # get the slope of the intended direction line of the previous frame
        yxRatio = math.tan(prevIntendedDirection)
        print("yxRatio of Previous Intended Direction: ", yxRatio)

        # get the final x and y coordinates of the altered line in the previous frame
        prevX = previousAlteredEntry[1]
        prevY = previousAlteredEntry[2]
        print("Previous Observed X and Y Positions", prevX, prevY)

        # The new point represents a random point on the target line created by our ML algorithm in the previous frame
        # This point will be used to build a y=mx+b formula for the target line in the previous frame
        newPoint = (prevX + 1, prevY + yxRatio)
        print("Additional Point On Previous Target Line = ", newPoint)

        # as long as the line between this location and the previous location is not horizontal or vertical
        # calculate the slope of that line normally, if else insert 0 or a large number (infinity won't work)
        if prevX != newPoint[0]:
            if prevY != newPoint[1]:
                slopeOfTargetLine = (newPoint[1] - prevY) / (newPoint[0] - prevX)
            else:
                slopeOfTargetLine = 0
        else:
            slopeOfTargetLine = 9999

        print("Slope Of Previous Target Line = ", slopeOfTargetLine)

        # finish building the formula for the target line using observed prevX and prevY
        # and the slope we just acquired in the above block. (now we have y = mx + b for ML generated target line)

        targetLine_b = prevY - slopeOfTargetLine * prevX

        # now build the y = mx + b formula for a perpendicular line connecting our current observed point
        # and the target line from the previous frame
        perpendicularSlope = -1 / slopeOfTargetLine
        perpendicular_b = yetToBeAlteredEntry[2] - perpendicularSlope * yetToBeAlteredEntry[1]

        # now get the intersection point between the the target line from the previous frame and the observed
        # location of this frame
        intersectionPoint = [0, 0]
        intersectionPoint[0] = (perpendicular_b - targetLine_b) / (slopeOfTargetLine - perpendicularSlope)
        intersectionPoint[1] = perpendicularSlope * intersectionPoint[0] + perpendicular_b

        errorDomain = (yetToBeAlteredEntry[1], intersectionPoint[0])
        error = errorDomain[1] - errorDomain[0]
        print("ERROR ================== :", error)
        alteredMousePos = [yetToBeAlteredEntry[1], yetToBeAlteredEntry[2]]
        if abs(error) > abs(self.errorCoef / 2):
            print("Mouse Position Altered")
            print("ERROR AFTER ABS ==========:", error)
            alteredMousePos[0] = yetToBeAlteredEntry[1] + error * self.algorithmAccuracy
            alteredMousePos[1] = perpendicularSlope * alteredMousePos[0] + perpendicular_b
        else:
            print("Mouse Position Not Altered")

        return alteredMousePos[0], alteredMousePos[1]

class recentMovementNode:
    def __init__(self, dataVal=None):
        self.dataVal = dataVal
        self.prevNode = None
        self.nextNode = None
        self.maxSize = 12

class recentMovementQueue:
    def __init__(self):
        self.rootNode = None
        self.finalVal = None

class advancedMouseMoment:
    def __init__(self, componentData):
        self.TimeStamp = componentData[0]
        self.MouseX = componentData[1]
        self.MouseY = componentData[2]
        self.TargetLocationX = componentData[3]
        self.TargetLocationY = componentData[4]
        self.IntendedDirection = componentData[5]
        self.TargetDistance = componentData[6]
        self.ObservedDistance = componentData[7]
        self.ObservedSpeed = componentData[8]
        self.ObservedDirection = componentData[9]
        self.DirectionalError = componentData[10]
        self.DistanceOfError = componentData[11]
        self.RecentAverageDirection = componentData[12]
        self.RecentAverageSpeed = componentData[13]