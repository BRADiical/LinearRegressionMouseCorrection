import pygame
import MouseToolBelt
import math
import pickle

class button:
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.width = width
        self.height = height
        self.xPos = x
        self.yPos = y
        self.text = text

    def draw(self, win, outline=None):
        # Call this method to draw the button on screen
        if outline:
            pygame.draw.rect(win, outline, (self.xPos - 2, self.yPos - 2, self.width + 4, self.height + 4), 0)
        pygame.draw.rect(win, self.color, (self.xPos, self.yPos, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont('comicsans', 50)
            text = font.render(self.text, 1, (255, 255, 255))
            text_w = text.get_width()
            text_h = text.get_height()
            win.blit(text, (self.xPos + (self.width / 2 - text_w / 2), self.yPos + (self.height / 2 - text_h / 2)))

    def isOver(self, mousePos):

        print("XPos = ", self.xPos)
        print("YPos = ", self.yPos)
        print("XPos + width = ", self.xPos + self.width)
        print("YPos + height = ", self.yPos + self.height)
        print("Actual Mouse Coordinates = (", mousePos[0], " ", mousePos[1], ")")
        print(mousePos[0])
        print(mousePos[1])
        return MouseToolBelt.mouseOver(mousePos[0], mousePos[1], self.xPos, self.yPos, self.xPos + self.width,
                                       self.yPos + self.height)


class openingScreenManager:
    # -- Constructor --
    def __init__(self, screen, infoObj):

        # new attributes
        self.screen = screen  # screen object
        self.infoObj = infoObj  # display info object

        # setup functions
        self.openingMessage_Setup()  # Run Setup Function
        self.openingInput_Setup()  # Run Setup Function

    # -- Setup Functions --

    # title text
    def openingMessage_Setup(self):
        # Local Variables
        screen_size = self.screen.get_size()
        font = pygame.font.Font('Raleway-Regular.ttf', 32)

        # Generate New Attributes
        # First Level Rect
        self.titleTextRect0 = pygame.Rect(400, 100, 450, 150)  # rendered title text object     # rendered font setup
        self.titleText0 = font.render("Welcome To MouseBrace", True, (180, 205, 255))  # ALWAYS USE THIS screen_size
        self.titleTextRect0.topleft = (50, screen_size[1] * 0.15)

        # Second level rect
        self.titleTextRect1 = pygame.Rect(400, 100, 450,
                                          150)  # rendered title text object                              # rendered font setup
        self.titleText1 = font.render("Please Enter Your Name as follows: FirstName_LastName", True, (255, 255, 255))  # ALWAYS USE THIS screen_size
        self.titleTextRect1.topleft = (50, screen_size[1] * 0.30)  # This Is How You Use it

        # Third Level Rect
        self.titleTextRect2 = pygame.Rect(400, 100, 450, 150)
        self.titleText2 = font.render("Your report will be stored under this name", True, (255, 255, 255))
        self.titleTextRect2.topleft = (50, screen_size[1] * 0.4)  # This Is How You Use it

        return

    # input box
    def openingInput_Setup(self):

        # Generate New Attributes
        self.inputRect = pygame.Rect(150, 300, 400, 50)  # My Input Rect
        self.inputText = ''  # current text from user
        self.font = pygame.font.Font('Raleway-Regular.ttf', 26)  # rendered text object setup
        self.inputActive = False  # Is the input box active

        screen_size = self.screen.get_size()  # ALWAYS USE THIS screen_size
        self.inputRect.topleft = (50, screen_size[1] // 2)  # This Is How You Use it
        # Switch for the input bo
        return

    # -- Show Objects on screen --

    # title text box
    def openingMessage_Show(self):
        # blit the title text on the screen
        self.screen.blit(self.titleText0, self.titleTextRect0)
        self.screen.blit(self.titleText1, self.titleTextRect1)
        self.screen.blit(self.titleText2, self.titleTextRect2)
        return

    # input text box
    def openingInput_Show(self):
        if self.inputActive == False:
            pygame.draw.rect(self.screen, (255, 255, 255), self.inputRect, 2)  # draw a rectangle
        else:
            pygame.draw.rect(self.screen, (150, 255, 255), self.inputRect, 3)
        self.inputTextSurface = self.font.render(self.inputText, True, (255, 255, 255))  # rendered text object
        self.screen.blit(self.inputTextSurface, (self.inputRect.x + 5, self.inputRect.y + 5))  # blit the input
        self.inputRect.w = max(200, self.inputTextSurface.get_width() + 10)

    # Process input box behavior

    def openingInput_Process(self, event, mouseObj):
        screenState = 0
        if (self.inputActive):
            if event.key == pygame.K_RETURN:
                mouseObj.openLog(self.inputText)
                self.inputText = ''
                screenState = 1
            elif event.key == pygame.K_BACKSPACE:
                self.inputText = self.inputText[:-1]
            else:
                self.inputText += event.unicode

        return screenState

    # Turn input box off or on
    def openingInput_Activate(self, event):
        if self.inputRect.collidepoint(event.pos):
            self.inputActive = True
        else:
            self.inputActive = False


class secondScreen:
    def __init__(self, screen, infoObj):
        self.inTraining = False

        # new attributes
        self.screen = screen  # screen object
        self.infoObj = infoObj  # display info object

        # setup functions
        self.preTraining_setup()

    def preTraining_setup(self):
        # local variables
        screen_size = self.screen.get_size()
        font = pygame.font.Font('Raleway-Regular.ttf', 32)

        # TEXT
        #  first text
        self.preTextRect0 = pygame.Rect(400, 100, 800, 150)  # rendered pre text object
        self.preText0 = font.render("Welcome to the training phase where MouseBrace learns from your movements.", True,
                                    (0, 0, 0))  # ALWAYS USE THIS screen_size
        self.preTextRect0.topleft = (50, screen_size[1] * 0.15)

        # second text
        self.preTextRect1 = pygame.Rect(400, 100, 800, 150)  # rendered pre text object
        self.preText1 = font.render("Simply take your time clicking the dots as they appear by moving your "
                                    "mouse along the line presesnted", True, (0, 0, 0))  # ALWAYS USE THIS screen_size
        self.preTextRect1.topleft = (50, screen_size[1] * 0.3)

        # third text
        self.preTextRect2 = pygame.Rect(400, 100, 800, 150)  # rendered pre text object
        self.preText2 = font.render("Remember that the goal is to learn from your natural movements so "
                                    "this is not a race, move as you would clicking links on a webpage", True,
                                    (0, 0, 0))  # ALWAYS USE THIS screen_size
        self.preTextRect2.topleft = (50, screen_size[1] * 0.45)

        # START BUTTON
        self.startButton = button((70, 100, 140), 50, self.infoObj.current_h * 0.75, 300, 100, 'Start Training')

    def preTraining_Show(self):
        # blit the title text on the screen
        self.screen.blit(self.preText0, self.preTextRect0)
        self.screen.blit(self.preText1, self.preTextRect1)
        self.screen.blit(self.preText2, self.preTextRect2)
        self.startButton.draw(self.screen, (0, 0, 0))

    def preTraining_Process(self, pos):
        screenState = 1
        start_time = None
        if (self.startButton.isOver(pos)):
            print("Start Button Clicked")
            start_time = pygame.time.get_ticks()
            screenState = 2
        return screenState,start_time


class thirdScreen:
    def __init__(self, screen, infoObj, mouseTool):
        self.currentLine = 0
        self.screen = screen
        self.infoObj = infoObj
        self.mouseTool = mouseTool
        self.trainingLines = [((50, 800), (900, 20)),
                              ((2000, 900), (180, 100)),
                              ((180, 100), (1900, 1000)),
                              ((1900, 1000), (280, 100)),
                              ((280, 100), (1800, 1100)),
                              ((1800, 1100), (400, 100)),
                              ((900, 20), (900, 500)),
                              ((900, 500), (20, 500)),
                              ((20, 500), (20, 800)),
                              ((20, 800), (900, 800)),
                              ((900, 800), (30, 30)),
                              ((30, 30), (1800, 30)),
                              ((1800, 30), (2275, 1400)),
                              ((2275, 1400), (1100, 15)),
                              ((1100, 15), (1100, 1400)),
                              ((1100, 1400), (1200, 20)),
                              ((1200, 20), (1000, 1350)),
                              ((1000, 1350), (1300, 30)),
                              ((1300, 30), (900, 1300)),
                              ((900, 1300), (1400, 40)),
                              ((1400, 40), (800, 1250)),
                              ((800, 1250), (1500, 50)),
                              ((1500, 50), (700, 1240)),
                              ((700, 1240), (1600, 60)),
                              ((1600, 60), (600, 1230)),
                              ((600, 1230), (1700, 100)),
                              ((1700, 100), (500, 1200)),
                              ((500, 1200), (1800, 110)),
                              ((1800, 110), (400, 1180)),
                              ((400, 1180), (1900, 130)),
                              ((1900, 130), (300, 900)),
                              ((300, 900), (2000, 300)),
                              ((2000, 300), (200, 700)),
                              ((200, 700), (2100, 400)),
                              ((2100, 400), (100, 600)),
                              ((100, 600), (2200, 500)),
                              ((2200, 500), (100, 500)),
                              ((100, 500), (2200, 500)),
                              ((2200, 500), (100, 600)),
                              ((100, 600), (120, 400)),
                              ((120, 400), (2100, 700)),
                              ((2100, 700), (130, 300)),
                              ((130, 300), (2050, 800)),
                              ((2050, 800), (150, 200)),
                              ((150, 200), (2000, 900)),

                              ]

    def showTrainingLine(self):
        pygame.draw.line(self.screen, (0, 255, 100),
                         self.trainingLines[self.currentLine][0],
                         self.trainingLines[self.currentLine][1], 4)
        pygame.draw.circle(self.screen, (0, 100, 255), self.trainingLines[self.currentLine][1], 20)



    def nextTrainingLine(self, pos):
        if self.currentLine == self.trainingLines.__len__() - 1:
            self.mouseTool.writeTrainingDataToCSV()
            accuracy, errorCoef = self.mouseTool.generateDetailedCSV()
            self.mouseTool.alterMouse_Setup(accuracy, errorCoef)
            return 3
        circle_center = self.trainingLines[self.currentLine][1]
        x = pos[0]
        y = pos[1]

        sqx = (x - circle_center[0]) ** 2
        sqy = (y - circle_center[1]) ** 2

        # the radius of the circle is 20px
        if math.sqrt(sqx + sqy) < 20:
            self.currentLine += 1
        return 2
    def getCurrentTrainingLine(self):
        return self.trainingLines[self.currentLine]

class fourthScreen:
    def __init__(self, screen, infoObj):
        # new attributes
        self.screen = screen  # screen object
        self.infoObj = infoObj  # display info object

        # setup functions
        self.preTesting_setup()

    def preTesting_setup(self):
        # local variables
        screen_size = self.screen.get_size()
        font = pygame.font.Font('Raleway-Regular.ttf', 32)

        # TEXT
        #  first text
        self.preTextRect0 = pygame.Rect(400, 100, 800, 150)  # rendered pre text object
        self.preText0 = font.render("Welcome to the testing phase where MouseBrace uses "
                                    "what it learned to correct input errors.", True,
                                    (0, 0, 0))
        self.preTextRect0.topleft = (50, screen_size[1] * 0.15)

        # second text
        self.preTextRect1 = pygame.Rect(400, 100, 800, 150)  # rendered pre text object
        self.preText1 = font.render("Same as before, follow the lines to the dots and hopefully "
                                    "MouseBrace will make it easier this time", True, (0, 0, 0))
        self.preTextRect1.topleft = (50, screen_size[1] * 0.3)

        # START BUTTON
        self.startButton = button((70, 100, 140), 50, self.infoObj.current_h * 0.75, 300, 100, 'Start Testing')

    def preTesting_Show(self):
        # blit the title text on the screen
        self.screen.blit(self.preText0, self.preTextRect0)
        self.screen.blit(self.preText1, self.preTextRect1)
        self.startButton.draw(self.screen, (0, 0, 0))

    def preTesting_Process(self, pos, ):
        screenState = 3
        start_time = None
        if (self.startButton.isOver(pos)):
            print("Start Button Clicked")
            start_time = pygame.time.get_ticks()
            screenState = 4
        return screenState, start_time



    #def alterMousePosition(self):


class TestingScreen:
    def __init__(self, screen, infoObj, mouseTool):
        self.currentLine = 0
        self.screen = screen
        self.infoObj = infoObj

        self.mouseTool = mouseTool
        self.testingLines = [((50, 800), (900, 20)),
                             ((2000, 900), (180, 100)),
                             ((180, 100), (1900, 1000)),
                             ((1900, 1000), (280, 100)),
                             ((280, 100), (1800, 1100)),
                             ((1800, 1100), (400, 100)),
                             ((900, 20), (900, 500)),
                             ((900, 500), (20, 500)),
                             ((20, 500), (20, 800)),
                             ((20, 800), (900, 800)),
                             ((900, 800), (30, 30)),
                             ((30, 30), (1800, 30)),
                             ((1800, 30), (2275, 1400)),
                             ((2275, 1400), (1100, 15)),
                             ((1100, 15), (1100, 1400)),
                             ((1100, 1400), (1200, 20)),
                             ((1200, 20), (1000, 1350)),
                             ((1000, 1350), (1300, 30)),
                             ((1300, 30), (900, 1300)),
                             ((900, 1300), (1400, 40)),
                             ((1400, 40), (800, 1250)),
                             ((800, 1250), (1500, 50)),
                             ((1500, 50), (700, 1240)),
                             ((700, 1240), (1600, 60)),
                             ((1600, 60), (600, 1230)),
                             ((600, 1230), (1700, 100)),
                             ((1700, 100), (500, 1200)),
                             ((500, 1200), (1800, 110)),
                             ((1800, 110), (400, 1180)),
                             ((400, 1180), (1900, 130)),
                             ((1900, 130), (300, 900)),
                             ((300, 900), (2000, 300)),
                             ((2000, 300), (200, 700)),
                             ((200, 700), (2100, 400)),
                             ((2100, 400), (100, 600)),
                             ((100, 600), (2200, 500)),
                             ((2200, 500), (100, 500)),
                             ((100, 500), (2200, 500)),
                             ((2200, 500), (100, 600)),
                             ((100, 600), (120, 400)),
                             ((120, 400), (2100, 700)),
                             ((2100, 700), (130, 300)),
                             ((130, 300), (2050, 800)),
                             ((2050, 800), (150, 200)),
                             ((150, 200), (2000, 900)),
                             ]
    def showTestingLine(self):
        pygame.draw.line(self.screen, (0, 255, 100),
                         self.testingLines[self.currentLine][0],
                         self.testingLines[self.currentLine][1], 4)
        pygame.draw.circle(self.screen, (0, 100, 255), self.testingLines[self.currentLine][1], 20)

    def nextTestingLine(self, pos):
        if self.currentLine == self.testingLines.__len__() - 1:
            return 5, True
        circleWasClicked = False
        circle_center = self.testingLines[self.currentLine][1]
        x = pos[0]
        y = pos[1]

        sqx = (x - circle_center[0]) ** 2
        sqy = (y - circle_center[1]) ** 2

        # the radius of the circle is 20px
        if math.sqrt(sqx + sqy) < 20:
            circleWasClicked = True
            self.currentLine += 1

        return 4, circleWasClicked

    def getCurrentTestingLine(self):
        return self.testingLines[self.currentLine]


class finalScreen:
    def __init__(self, screen, infoObj):
        self.screen = screen
        self.infoObj = infoObj
        self.finalScreen_setup()

    def finalScreen_setup(self):
        screen_size = self.screen.get_size()
        font = pygame.font.Font('Raleway-Regular.ttf', 32)
        self.preTextRect0 = pygame.Rect(400, 100, 800, 150)  # rendered pre text object
        self.preText0 = font.render("Thank you for contributing to my research! Press esc to close.", True,
                                    (0, 0, 0))
        self.preTextRect0.topleft = (50, screen_size[1] * 0.15)

    def finalScreen_Show(self):
        # blit the title text on the screen
        self.screen.blit(self.preText0, self.preTextRect0)


def text_objects(font, text, color, text_center):
    rendered = font.render(text, True, color)
    return rendered, rendered.get_rect(center=text_center)

