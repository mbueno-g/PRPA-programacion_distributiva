# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 16:32:23 2022

@author: Marcos
"""
import random
from PIL import Image,ImageDraw

dims = (21,15)

#------------------------------------------------------------------------------
#BÁSICOS

def createBlank(dims):
    return [[1 for i in range(dims[0])] for j in range(dims[1])]

def drawHorizontal(pos,length,mapa):
    for i in range(pos[0],pos[0]+length):
        mapa[pos[1]][i] = 0
        
def drawVertical(pos,length,mapa):
    for j in range(pos[1],pos[1]+length):
        mapa[j][pos[0]] = 0
        
#------------------------------------------------------------------------------
#CREAR PASILLOS

def createVerticals(mapa):
    for line in range(1,len(mapa[0]),2):
        counter = 1
        while counter < len(mapa)-1:
            paso = 1
            if random.randint(0,1):
                paso = random.randint(1,len(mapa)-counter-1)
                drawVertical([line,counter],paso,mapa)
            counter += paso
            
def createHorizontals(mapa):
    for line in range(1,len(mapa),2):
        counter = 1
        while counter < len(mapa[0])-1:
            paso = 1
            if random.randint(0,1):
                paso = random.randint(1,len(mapa[0])-counter-1)
                drawHorizontal([counter,line],paso,mapa)
            counter += paso
            
#------------------------------------------------------------------------------
#COLOCAR

def ponerPiñas(mapa,piñas):
    while piñas > 0:
        pos = [random.randint(1,len(mapa[0])-1),random.randint(1,len(mapa)-1)]
        if not(mapa[pos[1]][pos[0]]):
            mapa[pos[1]][pos[0]] = 3
            piñas -= 1

def ponerJugadores(mapa):
    counter = 0
    while counter < 2:
        pos = [random.randint(1,len(mapa[0])-1),random.randint(1,len(mapa)-1)]
        if not(mapa[pos[1]][pos[0]]):
            mapa[pos[1]][pos[0]] = 2
            counter += 1
            
#------------------------------------------------------------------------------

def main(dims,nPiñas):
    m = createBlank(dims)
    createVerticals(m)
    createHorizontals(m)
    ponerPiñas(m,nPiñas)
    ponerJugadores(m)
    return m

def visualizer(mapa):
    img = Image.new("RGB",(10*len(mapa[0]),10*len(mapa)),(0,0,0))
    lienzo = ImageDraw.Draw(img)
    for j,line in enumerate(mapa):
        for i,cell in enumerate(line):
            color = (0,0,0)
            if cell == 1:
                color = (200,200,200)
            if cell == 2:
                color = (255,0,0)
            if cell == 3:
                color = (255,255,0)
            lienzo.rectangle([i*10,j*10,(i+1)*10,(j+1)*10],color)
    return img

"""         
if __name__ == "__main__":
    m = main((29,15),16)
    for line in m:
        for cell in line:
            print(cell,end="")
        print()
    img = visualizer(m)
    img.show()
"""