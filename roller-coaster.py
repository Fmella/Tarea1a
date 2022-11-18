import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import sys

import transformations as tr
import easy_shaders as es
import scene_graph as sg
import numpy as np

import funciones as rc

# A class to store the application control
class Controller:
    def __init__(self):
        self.jump = False
        self.falling = False
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

# Global controller as communication with the callback function
controller = Controller()

def on_key(window, key, scancode, action, mods):
    if action != glfw.PRESS:
        return

    global controller

    if key == glfw.KEY_SPACE:
        if controller.jump==False:
            controller.jump = True

    elif key == glfw.KEY_ESCAPE:
        sys.exit()

    else:
        print('Unknown key')

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Roller Coaster", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program (pipeline) with both shaders
    pipeline = es.SimpleTextureTransformShaderProgram()

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    N = 40

    # Read the vertices info from the csv file
    base_vertices = rc.readCsv(str(sys.argv[1]))
    curve_vertices = rc.createRailVertices(base_vertices, N)

    # Creating shapes on GPU memory
    elements = rc.createElements(curve_vertices)

    # velocidad del vagon
    vel = 0.7
    # Limites del movimiento
    T = len(curve_vertices)
    t = 0
    # Variable para el salto
    salto = np.pi
    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        if t<T-2:
            t = int(np.floor(glfw.get_time()*N*vel))

        # Etapa de control del programa
        # vertices divididos por 4 por escalado como en createRailTexture()
        controller.x = curve_vertices[t, 1]/4

        # Si el vagon encuentra un hueco y no ha saltado se activa la caida
        if curve_vertices[t, 0]==0 and controller.jump==False:
            controller.falling = True

        # Si el vagon salta sin estar cayendo
        elif controller.jump==True and controller.falling==False:
            if salto > 0:
                controller.y = curve_vertices[t, 2]/4 + np.sin(salto)/8
                salto -= 0.12
            else:
                controller.jump=False
                salto = np.pi

        # Si pasa normalmente sin caer el vagon se mueve a lo largo del riel
        elif curve_vertices[t, 0]==1 and controller.falling==False:
            controller.y = curve_vertices[t, 2]/4

        # Si el vagon cae solo puede seguir cayendo
        if controller.falling == True:
            controller.y -= 0.02

        # Modificando el nodo scenery en el scene graph
        # Representa el movimiento del vagon por la pista
        sceneryTranslateNode = sg.findNode(elements, "scenery")
        sceneryTranslateNode.transform = tr.matmul([tr.translate(-controller.x, -controller.y, 0)])

        # Modificando el nodo wagon en el scene graph
        # x_1 e y_1 son el vertice siguiente a la posicion del vagon
        # theta es el angulo de inclinacion del vagon
        x_1 = curve_vertices[t + 1, 1] / 4
        y_1 = curve_vertices[t + 1, 2] / 4
        if controller.jump != True:
            controller.theta = np.arctan((y_1 - controller.y) / (x_1 - controller.x))
        wagonRotationNode = sg.findNode(elements, "wagon")
        wagonRotationNode.transform = tr.rotationZ(controller.theta)

        # Modificando el nodo wheelRotation en el scene graph
        wheelRotationNode = sg.findNode(elements, "wheelRotation")
        wheelRotationNode.transform = tr.rotationZ(t)

        # Modificando el nodo elements en el scene graph
        # Representa donde se fija la camara
        elements.transform = tr.matmul([tr.translate(1.4, 0.9, 0), tr.uniformScale(2)])

        sg.drawSceneGraphNode(elements, pipeline, "transform")

        # Si el vagon cae bajo esta posicion el juego termina y se cierra
        if controller.y<-0.5/4:
            sys.exit()

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    glfw.terminate()