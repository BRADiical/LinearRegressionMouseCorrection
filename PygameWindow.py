import tensorflow
import keras
import numpy as np

import sklearn
from sklearn import linear_model
from sklearn.utils import shuffle
import matplotlib.pyplot as pyplot
import pickle
from matplotlib import style
import pyautogui

import math
import pygame, sys
from pygame.locals import *

# My Custom imports
import MouseToolBelt
import PygameTrainingKit
import LinearRegressionAlg


def main():
    # responsible for terminating the infinite while loop
    running = True

    # responsible for managing active screen
    atScreen = 0

    # lists dots on testing screen
    observedPositionDots = []
    correctiveDots = []

    # Handles Frame Rate
    clock = pygame.time.Clock()

    # Provides info about the display
    infoObject = pygame.display.Info()

    demo = pygame.display.set_mode((infoObject.current_w + 510, infoObject.current_h + 310), FULLSCREEN)

    # Set a caption
    pygame.display.set_caption("Parkinsons Alg")

    # object to log mouse data
    mouseObj = MouseToolBelt.mouseLogger()

    # object to manage the first screen you see
    opScreenObj = PygameTrainingKit.openingScreenManager(demo, infoObject)
    trainingScreenObj = PygameTrainingKit.secondScreen(demo, infoObject)
    thirdScreenObj = PygameTrainingKit.thirdScreen(demo, infoObject, mouseObj)
    fourthScreenObj = PygameTrainingKit.fourthScreen(demo, infoObject)
    testingScreenObj = PygameTrainingKit.TestingScreen(demo, infoObject, mouseObj)
    finalScreenObj = PygameTrainingKit.finalScreen(demo, infoObject)

    print(MouseToolBelt.convertVectorToUnitVector((5,5),(8,9), 5))

    while running:
        mouseX, mouseY = pyautogui.position()
        # FIRST SCREEN
        if (atScreen == 0):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    atScreen = opScreenObj.openingInput_Process(event, mouseObj)
                if event.type == MOUSEBUTTONDOWN:
                    opScreenObj.openingInput_Activate(event)
            # fill the screen with dark gray
            demo.fill((70, 70, 70))
            # Draw Boxes
            opScreenObj.openingMessage_Show()
            opScreenObj.openingInput_Show()
            # update the screen

        # PRE TRAINING SCREEN
        if (atScreen == 1):
            # fill the screen with near-white
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    atScreen, start_time = trainingScreenObj.preTraining_Process(pyautogui.position())

            demo.fill((220, 220, 220))
            trainingScreenObj.preTraining_Show()

        # TRAINING SCREEN
        if (atScreen == 2):
            # fill the screen with mid-gray
            current_time = pygame.time.get_ticks() - start_time
            demo.fill((100, 100, 100))
            for event in pygame.event.get():
                if event.type == pygame.MOUSEMOTION:
                    mouseObj.logMouse(mouseX, mouseY, current_time, thirdScreenObj.getCurrentTrainingLine())
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    atScreen = thirdScreenObj.nextTrainingLine((mouseX, mouseY))
            thirdScreenObj.showTrainingLine()

        # PRE TESTING SCREEN
        if (atScreen == 3):
            # fill the screen with white

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    atScreen, start_time = fourthScreenObj.preTesting_Process(pyautogui.position())
            demo.fill((250, 250, 250))
            fourthScreenObj.preTesting_Show()

        # TESTING SCREEN

        if (atScreen == 4):
            nextWasClicked = False
            current_time = pygame.time.get_ticks() - start_time
            demo.fill((250, 250, 250))
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                if event.type == MOUSEMOTION:
                    # log basic mouse data
                    mouseObj.logMouse(mouseX, mouseY, current_time, testingScreenObj.getCurrentTestingLine())
                    # improve mouse data to advanced data
                    # then alter mouse position
                    alteredPosition = mouseObj.alterMouse()
                    #alteredPosition = mouseObj.getNextAlteredPoint()
                    correctiveDots.append((int(alteredPosition[0]), int(alteredPosition[1])))
                    observedPositionDots.append((mouseX, mouseY))

                if event.type == pygame.MOUSEBUTTONDOWN:
                    atScreen, nextWasClicked = testingScreenObj.nextTestingLine((mouseX, mouseY))
                    if nextWasClicked:
                        observedPositionDots = []
                        correctiveDots = []
            for index in range(observedPositionDots.__len__()):
                if index > 1:
                    pygame.draw.line(demo, (255, 0, 0), observedPositionDots[index - 1], observedPositionDots[index], 3)
                    pygame.draw.circle(demo, (255, 0, 0), observedPositionDots[index], 6)
            for index in range(correctiveDots.__len__()):
                if index > 1:
                    pygame.draw.line(demo, (0, 0, 255), correctiveDots[index - 1], correctiveDots[index], 2)
                    pygame.draw.circle(demo, (255, 0, 0), correctiveDots[index], 5)
            testingScreenObj.showTestingLine()

        if (atScreen == 5):
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            demo.fill((250, 250, 250))
            finalScreenObj.finalScreen_Show()

        pygame.display.update()


        # set frame rate
        clock.tick(60)
    pygame.quit()



if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()