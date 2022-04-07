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
    pass

class Wall():
    def __init__(self,pos):
        self.pos = pos
        self.img = load_image("wall.png",K)
    
    def paint(self,screen):
        screen.blit(self.img, (self.pos[0],self.pos[1]))

class Object():
    pass

#------------------------------------------------------------------------------
#Cargar el mapa y hacer la matriz del juego

def readFile(filename):
    matrix = []
    f = open(dirMap + filename, "r")
    for y,line in enumerate(f):
        fila = []
        cells = line.strip("\n")
        for x,cell in enumerate(cells):
            if cell == "1":
                fila.append(Wall((x*K,y*K)))
            else:
                fila.append(cell)
        matrix.append(fila)
    f.close()
    return matrix

#------------------------------------------------------------------------------
#Update screen

def paintAll(screen,mapa):
    for line in mapa:
        for cosa in line:
            try:
                cosa.paint(screen)
            except:
                pass
        
#------------------------------------------------------------------------------
#Main

def main():
    pygame.init()
    mapa = readFile(filename)
    SCREEN_WIDTH = K*len(mapa[0])
    SCREEN_HEIGHT = K*len(mapa)
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ComePiñas")
    
    
    
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(True)

    while True:
        clock.tick(25)
        #pos_mouse = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            #if event.type == pygame.KEYDOWN:
                #if event.key == K_SPACE:
        
        pygame.display.flip()
        screen.fill((75, 75, 75))
        paintAll(screen,mapa)
        #accesories(screen,M,time)

#------------------------------------------------------------------------------
        
if __name__ == "__main__":
    main()
    """
    pygame.init()
    mapa = readFile(filename)
    print(mapa)
    """