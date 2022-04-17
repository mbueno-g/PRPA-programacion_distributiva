# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 11:01:17 2022

@author: Marcos
"""

import pygame
from pygame.locals import *
import os
import sys

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
    #if alpha is True:
        #image = image.convert_alpha()
    #else:
        #image = image.convert()
    return image

#------------------------------------------------------------------------------
#Clases de objetos del juego

class Player():
    def __init__(self,pos):
        self.pos = pos
        self.dir = "C"
        self.img = {d:load_image("pacman{}.png".format(d),24,True) for d in ["N","S","E","O","C"]}
        self.points = 0
        
    def paint(self,screen):
        screen.blit(self.img[self.dir], (self.pos[0]+3,self.pos[1]+3))
    
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
        #return not(type(matrix[p[1]//K-1][p[0]//K]) == type(Wall([0,0],200)))
    
    def move(self,matrix):
        if self.canMove(matrix):
            d = directions[self.dir]
            self.pos = [self.pos[0]+d[0],self.pos[1]+d[1]]

class Wall():
    def __init__(self,pos):
        self.pos = pos
        self.img = load_image("wall.png",K)
    
    def paint(self,screen):
        screen.blit(self.img, (self.pos[0],self.pos[1]))

class Object():
    def __init__(self,pos):
        self.pos = pos
        self.img = load_image("pineapple.png",10,True)
        self.taken = False
        
    def paint(self,screen):
        if not(self.taken):
            screen.blit(self.img, (self.pos[0]+10,self.pos[1]+10))

#------------------------------------------------------------------------------
#Cargar el mapa y hacer la matriz del juego

def readFile(filename):
    matrix = []
    players = []
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
            else:
                fila.append(cell)
        matrix.append(fila)
    f.close()
    return matrix,players

#------------------------------------------------------------------------------
#Update screen

def paintAll(screen,mapa,players):
    for line in mapa:
        for cosa in line:
            try:
                cosa.paint(screen)
            except:
                pass
    for p in players:
        p.paint(screen)
        
#------------------------------------------------------------------------------
#Main

def main():
    pygame.init()
    mapa,players = readFile(filename)
    SCREEN_WIDTH = K*len(mapa[0])
    SCREEN_HEIGHT = K*len(mapa)
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ComePiñas")
    
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(True)

    while True:
        clock.tick(50)
        #pos_mouse = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_DOWN:
                    players[0].dir = "S"
                elif event.key == K_UP:
                    players[0].dir = "N"
                elif event.key == K_RIGHT:
                    players[0].dir = "E"
                elif event.key == K_LEFT:
                    players[0].dir = "O"
        
        players[0].move(mapa)
        pygame.display.flip()
        screen.fill((75, 75, 75))
        paintAll(screen,mapa,players)
        #accesories(screen,M,time)

#------------------------------------------------------------------------------
        
if __name__ == "__main__":
    main()
    """
    pygame.init()
    mapa = readFile(filename)
    print(mapa)
    """