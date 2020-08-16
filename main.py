import pygame
from queue import PriorityQueue

boardWidth = 800
totalRows = 50
width = boardWidth // totalRows
grid = [[] for i in range(totalRows)]

pygame.init()
win = pygame.display.set_mode((boardWidth, boardWidth + 75))
pygame.display.set_caption('Path Finder')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (225, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


class Button:
    def __init__(self, colour, x, y, width, height, size, text=''):
        self.colour = colour
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.text_size = size

    def draw(self, win, outline=None):
        if outline:
            pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(win, self.colour, (self.x, self.y, self.width, self.height), 0)

        font = pygame.font.SysFont('comics', self.text_size)
        text = font.render(self.text, 1, (0, 0, 0))
        win.blit(text, (
            self.x + (self.width // 2 - text.get_width() // 2),
            self.y + (self.height // 2 - text.get_height() // 2)))

    def isOver(self, pos):
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True


class Point:
    def __init__(self, row, col, width):
        self.x = row * width
        self.y = col * width
        self.width = width
        self.row = row
        self.col = col
        self.colour = WHITE
        self.neighbours = []

    def draw(self, win):
        pygame.draw.rect(win, self.colour, (self.x, self.y, self.width, self.width))

    def isOver(self, pos):
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.width:
                return True

    def makeBarrier(self):
        self.colour = BLACK

    def makeUnmark(self):
        self.colour = WHITE

    def makeStart(self):
        self.colour = ORANGE

    def makeEnd(self):
        self.colour = TURQUOISE

    def makePath(self):
        self.colour = PURPLE

    def isBarrier(self):
        return self.colour == BLACK

    def isUnmark(self):
        return self.colour == WHITE

    def isStart(self):
        return self.colour == ORANGE

    def isEnd(self):
        return self.colour == TURQUOISE

    def findNeighbours(self):
        self.neighbours = []
        if self.row < totalRows - 1 and not grid[self.row + 1][self.col].isBarrier():  # DOWN
            self.neighbours.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].isBarrier():  # UP
            self.neighbours.append(grid[self.row - 1][self.col])
        if self.col < totalRows - 1 and not grid[self.row][self.col + 1].isBarrier():  # RIGHT
            self.neighbours.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].isBarrier():  # LEFT
            self.neighbours.append(grid[self.row][self.col - 1])

    def seen(self):
        self.colour = RED

    def end(self):
        self.colour = GREEN


resetButton = Button(BLUE, boardWidth - 150, boardWidth + 12, 125, 50, 30, 'RESET')
eraseButton = Button(BLUE, 25, boardWidth + 12, 125, 50, 30, 'ERASE')
markButton = Button(BLUE, 25, boardWidth + 12, 125, 50, 30, 'MARK')
findPathButton = Button(BLUE, boardWidth // 2 - 175 // 2, boardWidth + 12, 175, 50, 30, 'FIND PATH')


def makeGrid():
    for i in range(totalRows):
        for j in range(totalRows):
            grid[i].append(Point(i, j, width))


def resetBoard():
    global erasing, start, end
    for row in grid:
        for point in row:
            point.makeUnmark()
    erasing = False
    start = end = None


def hScore(p1):
    x1, y1 = p1.x, p1.y
    x2, y2 = end.x, end.y

    return abs(x1 - y2) + abs(y1 - y2)


def findPath():
    count = 0
    queue = PriorityQueue()
    queue.put((0, count, start))
    cameFrom = {}

    gScore = {point: float('inf') for row in grid for point in row}
    gScore[start] = 0
    fScore = {point: float('inf') for row in grid for point in row}
    fScore[start] = hScore(start)

    tempQueue = {start}

    while not queue.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = queue.get()[2]
        tempQueue.remove(current)

        if current == end:
            currentPath = end
            while currentPath in cameFrom:
                currentPath = cameFrom[currentPath]
                currentPath.makePath()

            end.makeEnd()
            start.makeStart()

            return True

        for neighbour in current.neighbours:
            temp_gScore = gScore[current] + 1

            if temp_gScore < gScore[neighbour]:
                cameFrom[neighbour] = current
                gScore[neighbour] = temp_gScore
                fScore[neighbour] = temp_gScore + hScore(neighbour)

                if neighbour not in tempQueue:
                    count += 1
                    queue.put((fScore[neighbour], count, neighbour))
                    tempQueue.add(neighbour)
                    neighbour.seen()

        if current != start:
            current.end()

        reDrawWindow()

    return False


def reDrawWindow():
    win.fill((255, 255, 255))
    for row in grid:
        for point in row:
            point.draw(win)

    for i in range(totalRows + 1):
        pygame.draw.line(win, BLACK, (i * width, 0), (i * width, boardWidth), 1)
        pygame.draw.line(win, BLACK, (0, i * width), (boardWidth, i * width), 1)

    resetButton.draw(win, BLACK)

    if not done:
        findPathButton.draw(win, BLACK)

        if not erasing:
            eraseButton.draw(win, BLACK)
        else:
            markButton.draw(win, BLACK)

    pygame.display.update()


makeGrid()
start = end = None
erasing = starting = done = False
row = col = 0
run = True
while run:
    for event in pygame.event.get():
        pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        if event.type == pygame.QUIT:
            run = False

        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()

            for row in grid:
                for point in row:
                    if point.isOver(pos):
                        if not erasing:
                            if start is None:
                                point.makeStart()
                                start = point
                            elif end is None and start != point:
                                point.makeEnd()
                                end = point
                            elif point.isUnmark():
                                point.makeBarrier()
                        else:
                            if start == point:
                                start = None
                            elif end == point:
                                end = None
                            else:
                                point.makeUnmark()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not done:
                if eraseButton.isOver(pos) and not erasing:
                    erasing = True

                elif markButton.isOver(pos) and erasing:
                    erasing = False

                if findPathButton.isOver(pos) and start is not None and end is not None:
                    for row in grid:
                        for point in row:
                            point.findNeighbours()
                    starting = True
                    findPath()
                    done = True

            if resetButton.isOver(pos):
                resetBoard()
                done = False

        if event.type == pygame.MOUSEMOTION:
            if not done:
                if not erasing:
                    if eraseButton.isOver(pos):
                        eraseButton.colour = GREEN
                    else:
                        eraseButton.colour = BLUE
                else:
                    if markButton.isOver(pos):
                        markButton.colour = GREEN
                    else:
                        markButton.colour = BLUE

                if findPathButton.isOver(pos) and start is not None and end is not None:
                    findPathButton.colour = GREEN
                else:
                    findPathButton.colour = BLUE

            if resetButton.isOver(pos):
                resetButton.colour = GREEN
            else:
                resetButton.colour = BLUE

    reDrawWindow()

pygame.quit()
