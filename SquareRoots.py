# Square Roots
# Global Game Jam 2023
# Oslo
# Jordi Santonja
import pgzrun

from pygame import image, Color, Surface
from random import randint
from math import sqrt

gridWidth, gridHeight = 5, 7
grid = [[0 for x in range(gridWidth)] for y in range(gridHeight)]
tileSize = 70
gridStart = (400 - (gridWidth - 1) * tileSize / 2, tileSize)
connDecSize = 15

horiConnections = [[False for x in range(gridWidth - 1)] for y in range(gridHeight)]
vertConnections = [[False for x in range(gridWidth)] for y in range(gridHeight - 1)]

possibleNumbers = [1,2,3,5,6,7,10,11,13,15,17,19,23,27,31]
possibleSelection = 3
#max possibleSelection = len(possibleNumbers)

fallingNumber = possibleNumbers[randint(1, possibleSelection) - 1]
fallingPos = (gridWidth // 2, 0)

nextNumber = possibleNumbers[randint(1, possibleSelection) - 1]
nextNumberPos = (tileSize * 1.25, tileSize)

globalTime = 0
timeSleep = 0.7
timeClearing = 0
timeToClear = 1.0
timeToStart = 3.0

mouseOnNumber = (-1, -1)
mouseOnVertConnection = (-1, -1)
mouseOnHoriConnection = (-1, -1)

START = 0
PLAYING = 1
CLEARING = 2
GAME_OVER = 3
status = START

testedValues = [[0 for x in range(gridWidth)] for y in range(gridHeight)]
sumValues = []

score = 0
level = 1
totalBalls = 0

def draw():
    screen.fill((0, 0, 0))
    for y in range(gridHeight):
        for x in range(gridWidth - 1):
            color = (128,128,128)
            if (x,y) == mouseOnHoriConnection:
                color = (64,64,64)
            if horiConnections[y][x] or (x,y) == mouseOnHoriConnection:
                screen.draw.filled_rect(Rect(gridStart[0] + x * tileSize + connDecSize, gridStart[1] + (y - 0.5) * tileSize + connDecSize,
                                             tileSize - connDecSize*2, tileSize - connDecSize*2), color)
    for y in range(gridHeight - 1):
        for x in range(gridWidth):
            color = (128,128,128)
            if (x,y) == mouseOnVertConnection:
                color = (64,64,64)
            if vertConnections[y][x] or (x,y) == mouseOnVertConnection:
                screen.draw.filled_rect(Rect(gridStart[0] + (x - 0.5) * tileSize + connDecSize, gridStart[1] + y * tileSize + connDecSize,
                                             tileSize - connDecSize*2, tileSize - connDecSize*2), color)
    for y in range(gridHeight):
        for x in range(gridWidth):
            if grid[y][x] != 0:
                color = (128,128,128)
                if (x,y) == mouseOnNumber:
                    color = (192,192,192)
                ballCenter = (gridStart[0] + x * tileSize, gridStart[1] + y * tileSize)
                screen.draw.filled_circle(ballCenter, (tileSize - 10)//2, color)
                screen.draw.text(str(grid[y][x]), center=ballCenter, fontsize=45, color=0)
                
    screen.draw.line((gridStart[0] - tileSize/2, gridStart[1] - tileSize / 2),
                     (gridStart[0] - tileSize/2, gridStart[1] + tileSize * (gridHeight - 0.5)), (255,0,0))
    screen.draw.line((gridStart[0] - tileSize/2, gridStart[1] + tileSize * (gridHeight - 0.5)),
                     (gridStart[0] + tileSize * (gridWidth - 0.5), gridStart[1] + tileSize * (gridHeight - 0.5)), (255,0,0))
    screen.draw.line((gridStart[0] + tileSize * (gridWidth - 0.5), gridStart[1] - tileSize / 2),
                     (gridStart[0] + tileSize * (gridWidth - 0.5), gridStart[1] + tileSize * (gridHeight - 0.5)), (255,0,0))
    
    screen.draw.filled_circle(nextNumberPos, (tileSize - 10)//2, (128,128,128))
    screen.draw.text(str(nextNumber), center=nextNumberPos, fontsize=45, color=0)
    screen.draw.text("Next", center=(nextNumberPos[0],nextNumberPos[1] + tileSize/2 + 10), fontsize=35, color=(205,205,205))

    fallingBallCenter = (gridStart[0] + fallingPos[0] * tileSize, gridStart[1] + fallingPos[1] * tileSize)
    screen.draw.filled_circle(fallingBallCenter, (tileSize - 10)//2, (128,128,128))
    screen.draw.text(str(fallingNumber), center=fallingBallCenter, fontsize=45, color=0)
    
    for val in sumValues:
        barycenter = (gridStart[0] + val[1] * tileSize, gridStart[1] + gridHeight * tileSize)
        ballColor = (128,64,64)
        ballSize = (tileSize)//4
        if IsPerfectSquare(val[0]):
            ballColor = (255,32,32)
            ballSize = (tileSize)//3
        for center in val[2]:
            screen.draw.line(barycenter, (gridStart[0] + tileSize * center[0], gridStart[1] + tileSize * center[1]), ballColor)
        screen.draw.filled_circle(barycenter, ballSize, ballColor)
    for val in sumValues:
        barycenter = (gridStart[0] + val[1] * tileSize, gridStart[1] + gridHeight * tileSize)
        screen.draw.text(str(val[0]), center=barycenter, fontsize=35, color=0)
    if status == START:
        screen.draw.text("Obtain perfect square roots\nto clear the numbers.\n\nASD or cursor keys to move\nthe falling number\n\nClick on a number to invert it.\n\nClick between two numbers to connect them.",
                         center=(400,300), fontsize=35, color=(205,205,205))
    if status == GAME_OVER:
        screen.draw.text("GAME OVER", center=(400,300), fontsize=85, color=(255,0,0))
    if status == START or (status == GAME_OVER and globalTime > timeToStart):
        screen.draw.text("Click mouse to start", center=(400,500), fontsize=65, color=(205,205,205))
    
    screen.draw.text("Score:\n"+str(score)+"\n\nLevel:\n"+str(level), center=(700,100), fontsize=35, color=(255,255,255))
    screen.draw.text("  _\n\\/4 = 2\n  _\n\\/9 = 3\n  __\n\\/16 = 4\n  __\n\\/25 = 5"+
                     "\n  __\n\\/36 = 6\n  __\n\\/49 = 7\n  __\n\\/64 = 8\n  __\n\\/81 = 9\n  ___\n\\/100 = 10\n ...",
                     midleft =(680,400), fontsize=24, color=(128,128,128))
    
    

def update(dt):
    global globalTime, fallingPos, fallingNumber, nextNumber, status, timeClearing, score, level, totalBalls, possibleSelection
    if status == PLAYING or status == GAME_OVER:
        globalTime += dt
    if status == PLAYING:
        if globalTime >= timeSleep or keyboard.down or keyboard.S:
            globalTime = 0
            if fallingPos[1] < gridHeight - 1 and grid[fallingPos[1] + 1][fallingPos[0]] == 0:
                fallingPos = (fallingPos[0],fallingPos[1] + 1)
            elif fallingPos == (gridWidth // 2, 0):
                status = GAME_OVER
                globalTime = 0
            else:
                grid[fallingPos[1]][fallingPos[0]] = fallingNumber
                fallingNumber = nextNumber
                nextNumber = possibleNumbers[randint(1, possibleSelection) - 1]
                totalBalls += 1
                if totalBalls % 10 == 0:
                    level += 1
                    if possibleSelection < len(possibleNumbers):
                        possibleSelection += 1
                fallingPos = (gridWidth // 2, 0)
        for val in sumValues:
            if IsPerfectSquare(val[0]):
                score += val[0] * val[0]
                timeClearing = timeToClear
                status = CLEARING
    elif status == CLEARING:
        timeClearing -= dt
        if timeClearing <= 0:
            ClearPerfectSquares()
            timeClearing = 0
            status = PLAYING

def IsPerfectSquare(val):
    if val > 1:
        sqrtValue = sqrt(val)
        if int(sqrtValue) * int(sqrtValue) == val:
            return True
    return False

def on_key_down(key):
    global fallingPos
    if status == PLAYING:
        if key == keys.LEFT or key == keys.A:
            if fallingPos[0] > 0 and grid[fallingPos[1]][fallingPos[0] - 1] == 0:
                fallingPos = (fallingPos[0] - 1,fallingPos[1])
        elif key == keys.RIGHT or key == keys.D:
            if fallingPos[0] < gridWidth - 1 and grid[fallingPos[1]][fallingPos[0] + 1] == 0:
                fallingPos = (fallingPos[0] + 1,fallingPos[1])

def on_mouse_down(pos):
    global status, score, grid, horiConnections, vertConnections, testedValues, sumValues, level, totalBalls, possibleSelection
    if status == START or (status == GAME_OVER and globalTime > timeToStart):
        grid = [[0 for x in range(gridWidth)] for y in range(gridHeight)]
        horiConnections = [[False for x in range(gridWidth - 1)] for y in range(gridHeight)]
        vertConnections = [[False for x in range(gridWidth)] for y in range(gridHeight - 1)]
        testedValues = [[0 for x in range(gridWidth)] for y in range(gridHeight)]
        sumValues.clear()
        score = 0
        level = 1
        totalBalls = 0
        possibleSelection = 3
        status = PLAYING
    elif status == PLAYING:
        if mouseOnNumber != (-1, -1):
            grid[mouseOnNumber[1]][mouseOnNumber[0]] = -grid[mouseOnNumber[1]][mouseOnNumber[0]]
        elif mouseOnVertConnection != (-1, -1):
            vertConnections[mouseOnVertConnection[1]][mouseOnVertConnection[0]] = not vertConnections[mouseOnVertConnection[1]][mouseOnVertConnection[0]]
        elif mouseOnHoriConnection != (-1, -1):
            horiConnections[mouseOnHoriConnection[1]][mouseOnHoriConnection[0]] = not horiConnections[mouseOnHoriConnection[1]][mouseOnHoriConnection[0]]
        if mouseOnNumber != (-1, -1) or mouseOnVertConnection != (-1, -1) or mouseOnHoriConnection != (-1, -1):
            ComputeNumbers()
    
def on_mouse_move(pos):
    global mouseOnNumber, mouseOnVertConnection, mouseOnHoriConnection
    mouseOnNumber = (-1, -1)
    mouseOnVertConnection = (-1, -1)
    mouseOnHoriConnection = (-1, -1)
    if status == PLAYING:
        if pos[0] > gridStart[0] - tileSize / 4 and pos[1] > gridStart[1] - tileSize / 4:
            if pos[0] < gridStart[0] + tileSize * (gridWidth - 0.75) and pos[1] < gridStart[1] + tileSize * (gridHeight - 0.75):
                gridPos = (int((pos[0] - gridStart[0] + tileSize / 4) / (tileSize / 2)),
                           int((pos[1] - gridStart[1] + tileSize / 4) / (tileSize / 2)))
                if gridPos[0] % 2 == 0 and gridPos[1] % 2 == 0:
                    if grid[gridPos[1] // 2][gridPos[0] // 2] != 0:
                        mouseOnNumber = (gridPos[0] // 2, gridPos[1] // 2)
                elif gridPos[0] % 2 == 0:
                    if grid[gridPos[1] // 2][gridPos[0] // 2] != 0 and grid[gridPos[1] // 2 + 1][gridPos[0] // 2]:
                        mouseOnVertConnection = (gridPos[0] // 2, gridPos[1] // 2)
                elif gridPos[1] % 2 == 0:
                    if grid[gridPos[1] // 2][gridPos[0] // 2] != 0 and grid[gridPos[1] // 2][gridPos[0] // 2 + 1]:
                        mouseOnHoriConnection = (gridPos[0] // 2, gridPos[1] // 2)

def ComputeNumbers():
    global testedValues, sumValues
    sumValues.clear()
    testedValues = [[0 for x in range(gridWidth)] for y in range(gridHeight)]
    found = True
    currentIndex = 1
    while found:
        found = False
        for y in range(gridHeight):
            for x in range(gridWidth):
                if grid[y][x] != 0 and testedValues[y][x] == 0:
                    if x > 0 and grid[y][x - 1] != 0 and testedValues[y][x - 1] == 0 and horiConnections[y][x - 1]:
                        testedValues[y][x] = currentIndex
                        found = True
                        break
                    if y > 0 and grid[y - 1][x] != 0 and testedValues[y - 1][x] == 0 and vertConnections[y - 1][x]:
                        testedValues[y][x] = currentIndex
                        found = True
                        break
            if found:
                break
        foundNeighbor = True
        while foundNeighbor:
            foundNeighbor = False
            for y in range(gridHeight):
                for x in range(gridWidth):
                    if grid[y][x] != 0 and testedValues[y][x] == currentIndex:
                        if x > 0 and grid[y][x - 1] != 0 and testedValues[y][x - 1] == 0 and horiConnections[y][x - 1]:
                            testedValues[y][x - 1] = currentIndex
                            foundNeighbor = True
                        if x < gridWidth - 1 and grid[y][x + 1] != 0 and testedValues[y][x + 1] == 0 and horiConnections[y][x + 0]:
                            testedValues[y][x + 1] = currentIndex
                            foundNeighbor = True
                        if y > 0 and grid[y - 1][x] != 0 and testedValues[y - 1][x] == 0 and vertConnections[y - 1][x]:
                            testedValues[y - 1][x] = currentIndex
                            foundNeighbor = True
                        if y < gridHeight - 1 and grid[y + 1][x] != 0 and testedValues[y + 1][x] == 0 and vertConnections[y + 0][x]:
                            testedValues[y + 1][x] = currentIndex
                            foundNeighbor = True
        currentIndex += 1
    for i in range(1, currentIndex - 1):
        barycenterX = 0.0
        allCenters = []
        numValues = 0
        sumValue = 0
        for y in range(gridHeight):
            for x in range(gridWidth):
                if testedValues[y][x] == i:
                    sumValue += grid[y][x]
                    barycenterX += x
                    allCenters.append([x, y])
                    numValues += 1
        if numValues > 0:
            sumValues.append([sumValue, barycenterX / numValues, allCenters])        

def ClearPerfectSquares():
    global horiConnections, vertConnections, testedValues, sumValues
    for val in sumValues:
        if IsPerfectSquare(val[0]):
            for center in val[2]:
                grid[center[1]][center[0]] = 0
                if center[0] > 0:
                    horiConnections[center[1]][center[0] - 1] = False
                if center[1] > 0:
                    vertConnections[center[1] - 1][center[0]] = False
                if center[0] < gridWidth - 1:
                    horiConnections[center[1]][center[0]] = False
                if center[1] < gridHeight - 1:
                    vertConnections[center[1]][center[0]] = False
    sumValues.clear()
    #horiConnections = [[False for x in range(gridWidth - 1)] for y in range(gridHeight)]
    #vertConnections = [[False for x in range(gridWidth)] for y in range(gridHeight - 1)]
    fallingBalls = True
    while fallingBalls:
        fallingBalls = False
        for x in range(gridWidth):
            for y in reversed(range(gridHeight - 1)):
                if grid[y + 1][x] == 0 and grid[y][x] != 0:
                    grid[y + 1][x] = grid[y][x]
                    grid[y][x] = 0
                    fallingBalls = True
                    vertConnections[y][x] = False
                    if x > 0:
                        if horiConnections[y][x - 1]:
                            horiConnections[y][x - 1] = False
                    if x < gridWidth - 1:
                        if horiConnections[y][x]:
                            horiConnections[y][x] = False
    ComputeNumbers()
    
pgzrun.go()
