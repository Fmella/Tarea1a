
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import csv
import math

import transformations as tr
import basic_shapes as bs
import scene_graph as sg
import easy_shaders as es
import ex_curves as ec


def readCsv(csvName):
    with open(csvName, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        # Se agrega un vertice inicial para hacer la pista
        vertices_info = [[1, 0, 0]]
        for row in csv_reader:
            # Se forma una lista de (n x 3) con la posicion de los vertices
            if row[0][0] is not "x":
                # El primer valor es 1 si no tiene "x" al inicio
                vertices_info.append([1, int(row[0]), int(row[1])])
            else:
                # El primer valor es 0 si tiene "x" al inicio
                vertices_info.append([0, int(row[0][1:]), int(row[1])])
        # Se agrega un vertice final para hacer la pista
        vertices_info.append([1, vertices_info[-1][1]+1, 5])
        return np.array(vertices_info)

def createRailVertices(base_vertices, N):
    # Se tiene la cantidad de vertices entregados
    largo = len(base_vertices)
    # Se almacenan los vertices que forman la curva
    curve_vertices = []

    # Vectores tangentes iguales para todos los vertices
    T1 = np.array([[1.7, 0, 0]]).T
    T2 = np.array([[1.7, 0, 0]]).T

    # Cada punto base forma una curva con el siguiente punto base
    for i in range(largo-1):
        P1 = np.array([[base_vertices[i,   1], base_vertices[i,   2], 0]]).T
        P2 = np.array([[base_vertices[i+1, 1], base_vertices[i+1, 2], 0]]).T

        Gmh = ec.hermiteMatrix(P1, P2, T1, T2)
        hermiteCurve = ec.evalCurve(Gmh, N)

        ancho = math.ceil(N/6)
        # Se agregan los vertices de la curva a una lista que contiene todos los puntos
        if base_vertices[i, 0]!=0:
            for j in range(N-1):
                curve_vertices += [[1, hermiteCurve[j, 0], hermiteCurve[j, 1]]]
        # Se forma un hueco con un ancho dependiendo si el vertice base contenia una "x"
        else:
            for k in range(ancho):
                curve_vertices += [[0, hermiteCurve[k, 0], hermiteCurve[k, 1]]]
            for l in range(ancho, N-1):
                curve_vertices += [[1, hermiteCurve[l, 0], hermiteCurve[l, 1]]]

    # Se incluye el ultimo vertice
    curve_vertices += [base_vertices[-1]]
    return np.array(curve_vertices)

def createLongTexture(image_filename, length):

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
    #   positions                 texture
        -2.0,          -1.0, 0.0,      0, 1,
        -2.0+3*length, -1.0, 0.0, length, 1,
        -2.0+3*length,  2.0, 0.0, length, 0,
        -2.0,           2.0, 0.0,      0, 0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         0, 1, 2,
         2, 3, 0]

    textureFileName = image_filename

    return bs.Shape(vertices, indices, textureFileName)

def createRailTexture(image_filename, curve_vertices):
    n = len(curve_vertices)

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = []
    indices = []
    j = 0
    ind = 0
    # Se toman los vertices de curva, agregando un vertice base que esta en la parte inferior
    # y un vertice superior que corresponde a la curva
    for i in curve_vertices:
        if i[0] == 1:
            # vertices de la curva divididos por 4 como escalado
            vertices += [ -1.0 + i[1]/4,          -1.0, 0.0, i[1], 1]
            vertices += [ -1.0 + i[1]/4, -0.8 + i[2]/4, 0.0, i[1], 0]
            # Se agregan los indices de vertices formando triangulos con los vertices delanteros
            # Si un vertice tiene 0 en su primero numero no se agrega, formando los huecos
            if j < n-1 and curve_vertices[j+1, 0] != 0:
                indices += [ind, ind+2, ind+3, ind, ind+3, ind+1]
            ind += 2
        j += 1
    textureFileName = image_filename
    return bs.Shape(vertices, indices, textureFileName)

def createWagon():

    gpuCar = es.toGPUShape(bs.createTextureQuad("carro.png"), GL_REPEAT, GL_NEAREST) # Agregar texturas wagon
    gpuWheel = es.toGPUShape(bs.createTextureQuad("rueda.png"), GL_REPEAT, GL_NEAREST) # Agregar texturas wheels

    # Creating a single wheel
    wheel = sg.SceneGraphNode("wheel")
    wheel.transform = tr.uniformScale(0.2)
    wheel.childs += [gpuWheel]

    wheelRotation = sg.SceneGraphNode("wheelRotation")
    wheelRotation.childs += [wheel]

    # Instantiating two wheels, for the front and back
    frontWheel = sg.SceneGraphNode("frontWheel")
    frontWheel.transform = tr.translate(0.2, 0.1, 0)
    frontWheel.childs += [wheelRotation]

    backWheel = sg.SceneGraphNode("backWheel")
    backWheel.transform = tr.translate(-0.3, 0.1, 0)
    backWheel.childs += [wheelRotation]

    # Creando la caja del vagon
    box = sg.SceneGraphNode("box")
    box.transform = tr.translate(0, 0.3, 0)
    box.childs += [gpuCar]

    # Agregando los objetos al nodo wagon
    wagon = sg.SceneGraphNode("wagon")
    wagon.childs += [box, frontWheel, backWheel]

    # Creamos un nodo que escale el vagon al un tamaño necesitado
    scaledWagon = sg.SceneGraphNode("scaledWagon")
    scaledWagon.transform = tr.uniformScale(0.1)
    scaledWagon.childs += [wagon]

    # Creamos un nodo de movimiento que se fija el vagon en un lugar de la pantalla
    traslatedWagon = sg.SceneGraphNode("traslatedWagon")
    traslatedWagon.transform = tr.translate(-1, -0.8, 0)
    traslatedWagon.childs += [scaledWagon]

    return traslatedWagon

def createBackground(length):

    gpuBackground = es.toGPUShape(createLongTexture("fondo.png", length), GL_REPEAT, GL_NEAREST) # Agregar texturas background

    # Creando background
    background = sg.SceneGraphNode("background")
    background.childs += [gpuBackground]

    return background

def createRails(curve_vertices):

    gpuRails = es.toGPUShape(createRailTexture("structure.png", curve_vertices), GL_REPEAT, GL_NEAREST)

    # Creando la estructura
    rails = sg.SceneGraphNode("rails")
    rails.childs += [gpuRails]

    return rails

def createScenery(curve_vertices):

    length = curve_vertices[-1, 1] - curve_vertices[0, 1]

    # Se crea el paisaje que se movera hacia atras, arriba y abajo, simulando el movimiento horizontal y vertical
    scenery = sg.SceneGraphNode("scenery")
    scenery.childs += [createBackground(length), createRails(curve_vertices)]

    return scenery

def createElements(curve_vertices):

    # Se crea un nodo que aloja todos los demas nodos, se usara para enfocar el vagon
    elements = sg.SceneGraphNode("elements")
    elements.childs += [createScenery(curve_vertices), createWagon()]

    return elements