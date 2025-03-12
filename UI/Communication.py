import numpy as np
import cv2 as cv
from PIL import Image, ImageDraw
from manip_image_simple import ManipImage
from dataclasses import dataclass

class Communication:

    def __init__(self,output_path, text_file):
        self.hop = 0.03 #hop height constant in meter
        self.pageHeight = 0  #height in the Z axis to stamp
        self.gcode = []
        self.currentColor = None
        self.currentShape = None
        self.output_path = output_path
        self.text_file = text_file
        self.roundStampPosition  = [15,20,60]  #Arbitrary position (needs to be tested)
        self.squareStampPosition = [15,25,60]  #Arbitrary position (needs to be tested)
        self.inkPoolPosition = [30,45,10] #Arbitrary position (needs to be tested)
        self.refillValue = 50

        self.go_home()


        return

    def pixel_to_mm(positionPixel, refPixels, refMm):

        PositionMeters = (positionPixel/refPixels) * refMm
        return PositionMeters


    def position_to_gcode(self,X,Y, Z):  #Positions en millimetres, color et shape sont des int

        self.gcode.append(f"G1 X{X:.2f} Y{Y:.2f} Z{Z:.2f}")

    def go_home(self):

        self.gcode.append(f"G28")
    
    def stamp_path(self, x, y):

        self.position_to_gcode(x, y, self.pageHeight +50)
        self.position_to_gcode(x, y, self.pageHeight)
        self.position_to_gcode(x, y, self.pageHeight +50)
    
    
    def change_stamp(self, color, shape):
        

        self.go_home()

        #Sequences needs to be tested to find out the correct offsets and the correct Stamp positions
        #Put the stamp in the rack
        if self.currentShape == "round":
            self.position_to_gcode(self.roundStampPosition[1] -50, self.roundStampPosition[2], self.roundStampPosition[3] )
            self.position_to_gcode(self.roundStampPosition[1] ,self.roundStampPosition[2], self.roundStampPosition[3] )
            self.position_to_gcode(self.roundStampPosition[1],self.roundStampPosition[2], self.roundStampPosition[3] + 50)

        if self.currentShape == "square":
            self.position_to_gcode(self.squareStampPosition[1] -50 , self.squareStampPosition[2] , self.squareStampPosition[3])
            self.position_to_gcode(self.squareStampPosition[1] ,self.squareStampPosition[2], self.squareStampPosition[3])
            self.position_to_gcode(self.squareStampPosition[1] ,self.squareStampPosition[2],self.squareStampPosition[3]+ 50)

        #Take the next stamp
        if shape == "round":
            self.position_to_gcode(self.roundStampPosition[1] ,self.roundStampPosition[2], self.roundStampPosition[3] + 50)
            self.position_to_gcode(self.roundStampPosition[1] ,self.roundStampPosition[2], self.roundStampPosition[3] )
            self.position_to_gcode(self.roundStampPosition[1] -50, self.roundStampPosition[2], self.roundStampPosition[3] )

        if shape == "square":
            self.position_to_gcode(self.squareStampPosition[1] ,self.squareStampPosition[2],self.squareStampPosition[3]+ 50)
            self.position_to_gcode(self.squareStampPosition[1] ,self.squareStampPosition[2],self.squareStampPosition[3] )
            self.position_to_gcode(self.roundStampPosition[1] -50, self.roundStampPosition[2], self.roundStampPosition[3] )

        self.currentColor = color
        self.currentShape = shape
        return
    def ink_stamp(self,color):
        
        return
    def write_gcode(self, txt_file, output_path):

        with open(output_path, "w") as txt_file:
            for line in self.gcode:
                txt_file.write("".join(line) + "\n")

        return
        


    # this function generate the total path, including hops and change of color/shape of stamps
    def gcode_logic(self, positions): #positions is one or n positions
        
        self.go_home()
        stamp_counter = 0

        for x,y,shape,color  in positions:

            #Checks is Stamp needs to be changed
            if shape != self.currentShape or color != self.currentColor:
                self.change_stamp(color, shape)
                self.ink_stamp(color)
                stamp_counter = 0
                
            #Checks if ink needs to be applied on the stamp
            if stamp_counter >= self.refillValue:
                self.ink_stamp(color)
                stamp_counter = 0
                
            self.stamp_path(x, y)
            stamp_counter += 1

        self.go_home()

        self.write_gcode(self.text_file,self.output_path)

        self.gcode = []

        


