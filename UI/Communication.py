import numpy as np
import cv2 as cv
import paramiko

class Communication:

    def __init__(self):
        self.hop = 30 #hop height constant in millimeter
        self.flowRate = 2000 
        self.pageSizeMm = [210, 297]
        self.pageSizePix = [400, 600] # NEEDS TO BE CHANGED
        self.pageHeight = 60  #height in the Z axis to stamp
        self.gcode = []
        self.currentColor = None
        self.currentShape = None
        self.homeNotHome = [0,0,120]
        self.centerStampOut  = self.rotate_matrix(30 , self.pageSizeMm[1]/2 + 5, 85) 
        self.centerStampIn = self.rotate_matrix(-47, self.pageSizeMm[1]/2 + 5, 78)
        self.centerStampOver = self.rotate_matrix(-47, self.pageSizeMm[1]/2 + 5, 100)
        self.leftStampOut = [80,-100,82] #Position of left stamp holder (left from front of holder pov)
        self.leftStampIn = [100,-110,82]
        self.leftStampOver = [100,-110,100]
        self.rightStampOut = [110,-20,82]
        self.rightStampIn = [145, -25, 82]
        self.rightStampOver = [145, -25, 100]
        self.inkPoolPosition = [30,45,40] #Arbitrary position (needs to be tested)
        self.refillValue = 25
        self.host = "poulpus.local"
        self.username = "poulpus"
        self.password = "davinkus"

        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.openSSH()

    def __del__(self):
        print("Closing ssh!")
        self.closeSSH()
        

    def openSSH(self):
        try:

            self.client.connect(self.host,22, username=self.username, password=self.password)
        except Exception as e:
            print("Pas branché")
            pass

    def closeSSH(self):
        
        self.client.close()

    
    def pixel_to_mm(self,positionPixel, refPixels, refMm):



        PositionMeters = (positionPixel/refPixels) * refMm
        return PositionMeters
    
    def rotate_matrix(self,x,y,z):
        x = -(x - (self.pageSizeMm[0])/2)
        y = self.pageSizeMm[1] - y - (self.pageSizeMm[1])/2
        print("recentered X={}, Y={}".format(x, y))
        angle = -np.pi/6
        X = np.cos(angle)*x - np.sin(angle)*y 
        Y = np.sin(angle)*x + np.cos(angle)*y 
        print("rotated X={}, Y={}".format(X, Y))

        return [X,Y,z]
        

    def position_to_gcode(self, X, Y, Z):  #Positions en pixels sauf Z, le changement d'unites ce fera ici

        self.gcode.append(f"G1 X{X:.2f} Y{Y:.2f} Z{Z:.2f} F{self.flowRate}\n")

    def go_home(self):

        self.gcode.append(f"G28\n")
    
    def stamp_path(self, x, y):

        self.position_to_gcode(x, y, self.pageHeight + self.hop)
        self.position_to_gcode(x, y, self.pageHeight)
        self.position_to_gcode(x, y, self.pageHeight + self.hop)
    
    
    def change_stamp(self, color, shape):
        

        self.position_to_gcode(self.homeNotHome[0],self.homeNotHome[1],self.homeNotHome[2])

        #Sequences needs to be tested to find out the correct offsets and the correct Stamp positions
        #Put the stamp in the rack
        if self.currentShape == "Cercle":
            self.position_to_gcode(self.leftStampOut[0], self.leftStampOut[1], self.leftStampOut[2] )
            self.position_to_gcode(self.leftStampIn[0], self.leftStampIn[1], self.leftStampIn[2] )
            self.position_to_gcode(self.leftStampOver[0], self.leftStampOver[1], self.leftStampOver[2])

        if self.currentShape == "Carré":
            self.position_to_gcode(self.centerStampOut[0], self.centerStampOut[1], self.centerStampOut[2])
            self.position_to_gcode(self.centerStampIn[0], self.centerStampIn[1], self.centerStampIn[2])
            self.position_to_gcode(self.centerStampOver[0],self.centerStampOver[1], self.centerStampOver[2])

        if self.currentShape == "Triangle":
            self.position_to_gcode(self.rightStampOut[0], self.rightStampOut[1], self.rightStampOut[2])
            self.position_to_gcode(self.rightStampIn[0], self.rightStampIn[1], self.rightStampIn[2])
            self.position_to_gcode(self.rightStampOver[0], self.rightStampOver[1], self.rightStampOver[2])

        #Take the next stamp
        if shape == "Cercle":
            self.position_to_gcode(self.leftStampOver[0], self.leftStampOver[1], self.leftStampOver[2])
            self.position_to_gcode(self.leftStampIn[0], self.leftStampIn[1], self.leftStampIn[2] )
            self.position_to_gcode(self.leftStampOut[0], self.leftStampOut[1], self.leftStampOut[2] )

        if shape == "Carré":
            self.position_to_gcode(self.centerStampOver[0], self.centerStampOver[1], self.centerStampOver[2])
            self.position_to_gcode(self.centerStampIn[0], self.centerStampIn[1], self.centerStampIn[2])
            self.position_to_gcode(self.centerStampOut[0], self.centerStampOut[1], self.centerStampOut[2])

        if shape == "Triangle":
            self.position_to_gcode(self.rightStampOver[0], self.rightStampOver[1], self.rightStampOver[2])
            self.position_to_gcode(self.rightStampIn[0], self.rightStampIn[1], self.rightStampIn[2])
            self.position_to_gcode(self.rightStampOver[0], self.rightStampOver[1], self.rightStampOver[2])

        self.currentColor = color
        self.currentShape = shape
        return
    def ink_stamp(self,color):
        #Set slower flow rate to avoid big Splash
        normalFr = self.flowRate
        self.flowRate = normalFr/2

        self.position_to_gcode(self.inkPoolPosition[0],self.inkPoolPosition[1],self.inkPoolPosition[2] + 50)
        self.position_to_gcode(self.inkPoolPosition[0],self.inkPoolPosition[1],self.inkPoolPosition[2])
        self.position_to_gcode(self.inkPoolPosition[0],self.inkPoolPosition[1],self.inkPoolPosition[2] + 50)

        #Set normal flow rate back
        self.flowRate = normalFr
        return 
    
    def send_Gcode(self):
        msg = ""
        k = 0
        for i in self.gcode:
            msg = msg + self.gcode[k]
            k+=1
        
        self.gcode = [] 
        print("Sending: '{}'".format(msg))
        stdin, stdout, stderr = self.client.exec_command("echo '{}' >> /tmp/printer".format(msg))
        


    # this function generate the total path, including hops and change of color/shape of stamps
    def gcode_logic(self, positions): #positions is one or n positions
        
        self.go_home()
        self.position_to_gcode(self.homeNotHome[0], self.homeNotHome[1], self.homeNotHome[2])
        stamp_counter = 0

        for x,y,shape,color  in positions:
            
            X = self.pixel_to_mm(x, self.pageSizePix[0], self.pageSizeMm[0])
            Y = self.pixel_to_mm(y, self.pageSizePix[1], self.pageSizeMm[1])
            print("to mm X={}, Y={}".format(X, Y))
            [X,Y,Z] = self.rotate_matrix(X,Y,self.pageHeight)

            #Checks if Stamp needs to be changed
            if shape != self.currentShape or color != self.currentColor:
                self.change_stamp(color, shape)
                #self.ink_stamp(shape)
                stamp_counter = 0
                
            #Checks if ink needs to be applied on the stamp
            if stamp_counter >= self.refillValue:
                self.ink_stamp(color)
                stamp_counter = 0
                
            self.stamp_path(X, Y)
            stamp_counter += 1

        self.send_Gcode()

        



