from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys

YELLOW = 0
BLUE = 1
SIDESSTR = ["yellow", "blue"]

K = 30

dirImg = "./sprites/"
dirMap = "./mapas/"
filename = "mapa1.txt"

directions = {"N":[0,-1],"S":[0,1],"E":[1,0],"O":[-1,0],"C":[0,0]}

#------------------------------------------------------------------------------
#CLASES 

class Player():
    def __init__(self, side,p):
        self.side = side
        self.dir = "C"
        self.pos = p 

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def canMove(self,matrix):
        d = directions[self.dir]
        p = [self.pos[0]+d[0],self.pos[1]+d[1]]
        n = 3
        if self.dir in ["N","C"]:
            esquina1 = [p[0]+n,p[1]+n]
            esquina2 = [p[0]+30-n,p[1]+n]
        elif self.dir == "O":
            esquina1 = [p[0]+n,p[1]+n]
            esquina2 = [p[0]+n,p[1]+30-n]
        elif self.dir == "E":
            esquina1 = [p[0]+30-n,p[1]+n]
            esquina2 = [p[0]+30-n,p[1]+30-n]
        elif self.dir == "S":
            esquina1 = [p[0]+n,p[1]+30-n]
            esquina2 = [p[0]+30-n,p[1]+30-n]

        if not(type(matrix[esquina1[1]//K][esquina1[0]//K]) == type(Wall([0,0]))):
            if not(type(matrix[esquina2[1]//K][esquina2[0]//K]) == type(Wall([0,0]))):
                return True
        return False
    
    def move(self,matrix,points,lock):
        if self.canMove(matrix):
            d = directions[self.dir]
            self.pos = [self.pos[0]+d[0],self.pos[1]+d[1]]
            o = matrix[(self.pos[1] + K//2)//K][(self.pos[0] +K//2)//K]
            if (type(o) == type(Object([0,0])) and o.taken == False):
                lock.acquire()
                points[self.side] += 1
                lock.release()
                o.taken = True
    def __str__(self):
        return f"P<{SIDESSTR[self.side]}, {self.pos}>"


class Wall():
    def __init__(self,pos):
        self.pos = pos


class Object():
    def __init__(self,pos):
        self.pos = pos
        self.taken = False


class Game():
    def __init__(self, manager):
        self.score = manager.list([0,0])
        self.running = Value('i', 1) # 1 running
        self.lock = Lock()
        m, players, self.nPiñas = readFile()
        self.matrix = manager.lista([manager.list(lista) for lista in m])
        self.players = manager.list([Player(YELLOW,players[0]), Player(BLUE,players[1])])

    def get_player(self, side):
        return self.players[side]

    def get_score(self):
        return list(self.score)

    def is_running(self):
        return self.running.value == 1

    def isComplete(self):
        self.lock.acquire()
        boolean = self.score[0] + self.score[1] == self.nPiñas
        self.lock.release()
        return boolean     
            
    def stop(self):
        self.running.value = 0

    def changeDir(self, player, direction):
        self.lock.acquire()
        p = self.players[player]
        p.dir = direction
        self.players[player] = p
        self.lock.release()

    def get_info(self):
        info = {
            'pos_left_player': self.players[YELLOW].get_pos(),
            'pos_right_player': self.players[BLUE].get_pos(),
            'score': list(self.score),
            'is_running': self.running.value == 1
        }
        return info

    def __str__(self):
        return f"G<{self.players[YELLOW]}:{self.players[BLUE]}:{self.running.value}>"

#------------------------------------------------------------------------------
#Función de procesos

def player(side, conn, game):
    try:
        print(f"starting player {SIDESSTR[side]}:{game.get_info()}")
        conn.send( (side, game.get_info()) )
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "up":
                    game.changeDir(side,"N")
                elif command == "down":
                    game.changeDir(side,"S")
                elif command == "left":
                    game.changeDir(side,"O")
                elif command == "right":
                    game.changeDir(side,"E")
                elif command == "quit" or game.isComplete():
                    game.stop()
            conn.send(game.get_info())
            game.get_player(side).move(game.matrix,game.score,game.lock)
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")

#------------------------------------------------------------------------------

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
                players.append([x*K,y*K])
            elif cell == "3":
                fila.append(Object((x*K,y*K)))
                nPiñas += 1
            else:
                fila.append(cell)
        matrix.append(fila)
    f.close()
    return matrix,players,nPiñas

#------------------------------------------------------------------------------
#Main

def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address, 6020),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == 2:
                    players[0].start()
                    players[1].start()
                    n_player = 0
                    players = [None, None]
                    game = Game(manager)

    except Exception as e:
        traceback.print_exc()

#------------------------------------------------------------------------------

if __name__=='__main__':
    ip_address = "127.0.0.1"
    port = 37282
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    if len(sys.argv)>2:
        port = int(sys.argv[2])
    main(ip_address,port)
