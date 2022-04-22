from multiprocessing.connection import Client
import traceback
import pygame
import sys, os


YELLOW = 0
BLUE = 1

FPS = 60

SIDES = ["yellow", "blue"]
SIDESSTR = ["yellow", "blue"]

K = 30

dirImg = "./sprites/"
dirMap = "./mapas/"
filename = "mapa1.txt"

directions = {"N":[0,-1],"S":[0,1],"E":[1,0],"O":[-1,0],"C":[0,0]}

#------------------------------------------------------------------------------
#Para cargar y reescalar las imÃ¡genes

def load_image(nombre,fit, alpha=False):
    try:
        image = pygame.image.load(dirImg + nombre)
        image = pygame.transform.scale(image, (fit, fit))
    except:
        print("Error, no se puede cargar la imagen: " + nombre)
        sys.exit(1)
    #if alpha is True:
        #image = image.convert_alpha()
    #else:
        #image = image.convert()
    return image

#------------------------------------------------------------------------------
#Cargar el mapa y hacer la matriz del juego

def readFile(filename):
    matrix = []
    players = []
    nPiñas = 0
    f = open(dirMap + filename, "r")
    for y,line in enumerate(f):
        fila = []
        cells = line.strip("\n")
        for x,cell in enumerate(cells):
            if cell == "1":
                fila.append(Wall((x*K,y*K)))
            elif cell == "2":
                fila.append(cell)
                players.append(Player((x*K,y*K)))
            elif cell == "3":
                fila.append(Object((x*K,y*K)))
                nPiñas += 1
            else:
                fila.append(cell)
        matrix.append(fila)
    f.close()
    return matrix,players,nPiñas

#------------------------------------------------------------------------------

class Player():
    def __init__(self, side):
        self.side = side
        self.pos = [70+30*side,70+30*side]
        self.dir = "C"
        self.img = {d:load_image("pacman{}.png".format(d),24,True) for d in ["N","S","E","O","C"]}

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

    def paint(self,screen):
        screen.blit(self.img[self.dir], (self.pos[0]+3,self.pos[1]+3))


class Wall():
    def __init__(self,pos):
        self.pos = pos
        self.img = load_image("wall.png",K)


    def paint(self,screen):
        screen.blit(self.img, (self.pos[0],self.pos[1]))


class Object():
    def __init__(self,pos):
        self.pos = pos
        self.taken = False
        self.img = load_image("pineapple.png",20,True)


    def paint(self,screen):
        if not(self.taken):
            screen.blit(self.img, (self.pos[0]+10,self.pos[1]+10))


class Game():
    def __init__(self):
        self.score = [0,0]
        self.running = True
        self.matrix, self.players, self.nPiñas = readFile(filename)
        self.size = [K*len(self.matrix[0]), K*len(self.matrix)]

    def get_player(self, side):
        return self.players[side]

    def set_pos_player(self, side, pos):
        self.players[side].set_pos(pos)

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score

    def update(self, gameinfo):
        self.set_pos_player(YELLOW, gameinfo['pos_left_player'])
        self.set_pos_player(BLUE, gameinfo['pos_right_player'])
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def __str__(self):
        return f"G<{self.players[YELLOW]}:{self.players[BLUE]}>"

class Display():
    def __init__(self, game):
        self.game = game
        self.screen = pygame.display.set_mode(self.game.size)
        self.clock =  pygame.time.Clock()  #FPS
        pygame.init()

    def analyze_events(self, side):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
                elif event.key == pygame.K_UP:
                    events.append("up")
                elif event.key == pygame.K_DOWN:
                    events.append("down")
                elif event.key == pygame.K_LEFT:
                    events.append("left")
                elif event.key == pygame.K_RIGHT:
                    events.append("right")
            elif event.type == pygame.QUIT:
                events.append("quit")
        return events


    def refresh(self):
        pygame.display.flip()
        self.screen.fill((75, 75, 75))
        for line in self.game.matrix:
            for cosa in line:
                try:
                    cosa.paint(self.screen)
                except:
                    pass
        for p in self.game.players:
            p.paint(self.screen)

        self.screen.blit(load_image("pineapple.png",20,True),(K//4,K//4))
        font = pygame.font.Font('freesansbold.ttf', 4*K//5)
        t = "x" + str(self.game.score[0])
        text = font.render(t, True, (255,255,150))
        textRect = text.get_rect()
        textRect.center = (font.size(t)[0]//2 + 25,font.size(t)[1]//2 + 5)
        self.screen.blit(text, textRect)
        self.screen.blit(load_image("pineapple.png",20,True),(self.game.size[0] - K//4,K//4))
        t1 = str(self.game.score[1]) + "x"
        text1 = font.render(t1, True, (255,255,150))
        textRect1 = text1.get_rect()
        textRect1.center = (self.game.size[0] - font.size(t1)[0]//2 - 25 ,font.size(t)[1]//2 + 5)
        self.screen.blit(text1, textRect1)


    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()


def main(ip_address,port):
    try:
        with Client((ip_address, port), authkey=b'secret password') as conn:
            game = Game()
            side,gameinfo = conn.recv()
            print(f"I am playing {SIDESSTR[side]}")
            #game.update(gameinfo)
            display = Display(game)
            while game.is_running():
                events = display.analyze_events(side)
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()
                #game.update(gameinfo)
                display.refresh()
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "10.8.29"
    port = 6373
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    if len(sys.argv)>2:
        port = int(sys.argv[2])
    main(ip_address,port)
