import numpy as np
import cv2 as cv
import paramiko

def off(coord, vec):
    out = [0, 0, 0]
    for i in range(0, 3):
        out[i] = coord[i] + vec[i]
    return out

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

        centerStamp_l = [-47, self.pageSizeMm[1]/2 + 5, 78]
        leftStamp_l = [-47, self.pageSizeMm[1]/2 + 41, 78]
        rightStamp_l = [-47, self.pageSizeMm[1]/2  - 32, 78]

        side_wiggle_amp = 15;
        self.centerTake_seq = self.make_take(centerStamp_l, side_wiggle_amp)
        self.centerDrop_seq = self.make_drop(centerStamp_l)

        self.leftTake_seq = self.make_take(leftStamp_l, side_wiggle_amp)
        self.leftDrop_seq = self.make_drop(leftStamp_l)

        self.rightTake_seq = self.make_take(rightStamp_l, side_wiggle_amp)
        self.rightDrop_seq = self.make_drop(rightStamp_l)

        print(self.centerTake_seq)
        self.inkPoolPosition = [30,45,40] #Arbitrary position (needs to be tested)
        self.refillValue = 25
        self.host = "poulpus.local"
        self.username = "poulpus"
        self.password = "davinkus"

        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.openSSH()

    def __del__(self):
        print("Fermeture du tunel ssh!")
        self.closeSSH()
        

    def make_take(self, init, side_wiggle):
        return self.rotate_seq([off(init, [77, 0, 7]), init, off(init, [0, side_wiggle, 8]), off(init, [0, -side_wiggle, 8]), off(init, [0, 0, 8]), off(init, [77, 0, 7])])
    def make_drop(self, init):
        return  self.rotate_seq([off(init, [77, 0, 7]), init, off(init, [0, 0, 40])])
    
    def openSSH(self):
        try:

            self.client.connect(self.host,22, username=self.username, password=self.password)
        except Exception as e:
            print("Incapable d'etablir la connection ssh")
            pass

    def closeSSH(self):
        self.client.close()

    
    def pixel_to_mm(self,positionPixel, refPixels, refMm):



        PositionMeters = (positionPixel/refPixels) * refMm
        return PositionMeters
    
    def rotate_matrix(self,x,y,z):
        x = -(x - (self.pageSizeMm[0])/2)
        y = self.pageSizeMm[1] - y - (self.pageSizeMm[1])/2
        angle = -np.pi/6
        X = np.cos(angle)*x - np.sin(angle)*y 
        Y = np.sin(angle)*x + np.cos(angle)*y 

        return [X,Y,z]
    
    def rotate_seq(self, seq):
        out = []
        for elem in seq:
            out.append(self.rotate_matrix(elem[0], elem[1], elem[2]))
        return out

    def position_to_gcode(self, X, Y, Z):  #Positions en pixels sauf Z, le changement d'unites ce fera ici

        self.gcode.append(f"G1 X{X:.2f} Y{Y:.2f} Z{Z:.2f} F{self.flowRate}\n")

    def go_home(self):

        self.gcode.append(f"G28\n")
    
    def stamp_path(self, x, y):

        self.position_to_gcode(x, y, self.pageHeight + self.hop)
        self.position_to_gcode(x, y, self.pageHeight)
        self.position_to_gcode(x, y, self.pageHeight + self.hop)
    
    
    def change_stamp(self, color, shape):
        

        # self.position_to_gcode(self.homeNotHome[0],self.homeNotHome[1],self.homeNotHome[2])

        #Sequences needs to be tested to find out the correct offsets and the correct Stamp positions
        #Put the stamp in the rack
        if self.currentShape == "Cercle":
            self.send_seq(self.leftDrop_seq)
            
        if self.currentShape == "Carré":
            self.send_seq(self.centerDrop_seq)

        if self.currentShape == "Triangle":
            self.send_seq(self.rightDrop_seq)
 
        #Take the next stamp
        if shape == "Cercle":
            self.send_seq(self.leftTake_seq)

        if shape == "Carré":
            self.send_seq(self.centerTake_seq)

        if shape == "Triangle":
            self.send_seq(self.rightTake_seq)

        self.currentColor = color
        self.currentShape = shape
        return
    def send_seq(self, seq):
        for elem in seq:
            self.position_to_gcode(elem[0], elem[1], elem[2])

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

        



