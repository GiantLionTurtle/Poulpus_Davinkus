import numpy as np
import cv2 as cv
from PIL import Image, ImageDraw
from manip_image_simple import ManipImage
from dataclasses import dataclass

class Communication:
    hop = 0.03 #hop height constant in meter
    pageHeight = 0#height in the Z axis to stamp
    def __init__(self):
        return

    def pixel_to_meters(positionPixel, refPixels, refMeters):

        PositionMeters = (positionPixel/refPixels) * refMeters
        return PositionMeters

    def offset_to_gcode(self, X, Y, Z, color, shape):   #X,Y,Z en metres, color et shape sont des int

        gcode = f"G00 X{X:.2f} Y{Y:.2f} Z{Z:.2f} C{color} S{shape}"

        return gcode

    def position_to_gcode(self, X, Y, Z, color, shape):  #X,Y,Z en metres, color et shape sont des int

        gcode = f"G01 X{X:.2f} Y{Y:.2f} Z{Z:.2f} C{color} S{shape}"

        return gcode

    def path_to_gcode(self, path, color, shape): #path is the set of stamp positions given by the function analyse()

        gcode = []
      
        for i  in path[i]:
            gcode.append(self.position_to_gcode(path.x, path.y, self.pageHeight, color, shape))

        return gcode

    def write_gcode(self, gcode, txt_file, output_path):

            with open(output_path, "w") as txt_file:
                for line in gcode:
                    txt_file.write("".join(line) + "\n")
