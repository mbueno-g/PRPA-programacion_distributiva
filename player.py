from multiprocessing.connection import Client
import traceback
import pygame
import sys, os
import time


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
#Para cargar y reescalar las imágenes

def load_image(nombre,fit, alpha=False):
    try:
        image = pygame.image.load(dirImg + nombre)
        image = pygame.transform.scale(image, (fit, fit))
    except:
        print("Error, no se puede cargar la imagen: " + nombre)
        sys.exit(1)
    return image

#------------------------------------------------------------------------------
#Cargar el mapa y hacer la matriz del juego

def readFile(filename):
    matrix = []
    players = []
    nPinas = 0
    side = 0
    list_pinas = []
    f = open(dirMap + filename, "r")
    for y,line in enumerate(f):
        fila = []
        cells = line.strip("\n")
        for x,cell in enumerate(cells):
            if cell == "1":
                fila.append(Wall((x*K,y*K)))
            elif cell == "2":
                fila.append(cell)
                players.append(Player((x*K,y*K), side))
                side += 1
            elif cell == "3":
                fila.append(Object((x*K,y*K)))
                nPinas += 1
                list_pinas.append((x*K,y*K))
            else:
                fila.append(cell)
        matrix.append(fila)
    f.close()
    return matrix,players,nPinas,list_pinas

#------------------------------------------------------------------------------
# CLASES : Player, Wall, Object, Game, Display

class Player():
    def __init__(self, pos, side):
        self.side = side
        self.pos = pos
        self.dir = "C"
        self.img = {d:load_image("pacman{}.png".format(d),24,True) for d in ["N","S","E","O","C"]}
        self.img2 = {d:load_image("pacman2{}.png".format(d),24,True) for d in ["N","S","E","O","C"]}

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def set_pos(self, pos):
        self.pos = pos

    def set_dir(self, direccion):
        self.dir = direccion

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

    def paint(self,screen, pinas):
        if (self.side) == 0:
            screen.blit(self.img[self.dir], (self.pos[0]+3,self.pos[1]+3))
        else:
            screen.blit(self.img2[self.dir], (self.pos[0]+3,self.pos[1]+3))


class Wall():
    def __init__(self,pos):
        self.pos = pos
        self.img = load_image("wall.png",K)

    def paint(self,screen, pinas):
        screen.blit(self.img, (self.pos[0],self.pos[1]))


class Object():
    def __init__(self,pos):
        self.pos = pos
        self.taken = False
        self.img = load_image("pineapple.png",20,True)

    def paint(self,screen, pinas):
        ind = pinas.index(tuple(self.pos))
        if pinas[ind] != -1:
            screen.blit(self.img, (self.pos[0]+5,self.pos[1]+5))


class Game():
    def __init__(self):
        self.score = [0,0]
        self.running = True
        self.matrix, self.players, self.nPinas, self.list_pinas = readFile(filename)
        self.size = [K*len(self.matrix[0]), K*len(self.matrix)]

    def get_player(self, side):
        return self.players[side]

    def set_pos_player(self, side, pos):
        self.players[side].set_pos(pos)

    def set_dir_player(self, side, direccion):
        self.players[side].set_dir(direccion)

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score

    def set_matrix(self, matrix):
        self.matrix = matrix
    
    def set_list_pinas(self, list_pinas):
        self.list_pinas = list_pinas

    def update(self, gameinfo):
        self.set_pos_player(YELLOW, gameinfo['pos_left_player'])
        self.set_pos_player(BLUE, gameinfo['pos_right_player'])
        self.set_list_pinas(gameinfo['list_pinas'])
        self.set_dir_player(YELLOW, gameinfo['dir_yellow'])
        self.set_dir_player(BLUE, gameinfo['dir_blue'])
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
        self.screen.fill((75, 75, 75))
        for line in self.game.matrix:
            for cosa in line:
                try:
                    cosa.paint(self.screen, self.game.list_pinas)
                except:
                    pass
        for p in self.game.players:
            p.paint(self.screen, self.game.list_pinas)

        self.screen.blit(load_image("pineapple.png",20,True),(K//4,K//4))
        font = pygame.font.Font('freesansbold.ttf', 4*K//5)
        t = "x" + str(self.game.score[0])
        text = font.render(t, True, (255,255,150))
        textRect = text.get_rect()
        textRect.center = (font.size(t)[0]//2 + 25,font.size(t)[1]//2 + 5)
        self.screen.blit(text, textRect)
        self.screen.blit(load_image("pineapple.png",20,True),(self.game.size[0] - K,K//4))
        t1 = str(self.game.score[1]) + "x"
        text1 = font.render(t1, True, (255,255,150))
        textRect1 = text1.get_rect()
        textRect1.center = (self.game.size[0] - font.size(t1)[0]//2 - 25 ,font.size(t)[1]//2 + 5)
        self.screen.blit(text1, textRect1)
        pygame.display.flip()


    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()

#------------------------------------------------------------------------------
# Establecer ganador y pintar imagen del final

def won(ganador, display):
    display.screen.fill((75, 75, 75))
    font = pygame.font.Font('freesansbold.ttf', K)
    color = (255,255,150)
    t = "EL GANADOR ES YELLOW"
    if (ganador == "EMPATE"):
        t = "EMPATE!!"
        color = (190,229,176)
    elif (ganador == "BLUE"):
        color = (150,200,250)
        t = "EL GANADOR ES BLUE"
    text = font.render(t, True, color)
    textRect = text.get_rect()
    textRect.center = (display.game.size[0]//2, display.game.size[1]//2)
    display.screen.blit(text, textRect)
    pygame.display.flip()

#------------------------------------------------------------------------------

def main(ip_address,port):
    try:
        with Client((ip_address, port), authkey=b'secret password') as conn:
            game = Game()
            side,gameinfo = conn.recv()
            print(f"I am playing {SIDESSTR[side]}")
            game.update(gameinfo)
            display = Display(game)
            while game.is_running():
                events = display.analyze_events(side)
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()
                game.update(gameinfo)
                display.refresh()
                display.tick()
            ganador = "YELLOW"
            if (game.score[0] < game.score[1]):
                ganador = "BLUE"
                print("El ganador es " + ganador)
            elif (game.score[0] == game.score[1]):
                ganador = "EMPATE"
                print("EMPATE!")
            won(ganador, display)
            time.sleep(5)
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
