import numpy as np
import cv2 as cv
import paramiko

class Communication:

    def __init__(self):
        self.hop = 30
        self.flowRate = 5000 #hop height constant in meter
        self.pageSizeMm = [210, 297]
        self.pageSizePix = [2000, 3000] # NEEDS TO BE CHANGED
        self.pageHeight = 0  #height in the Z axis to stamp
        self.gcode = []
        self.currentColor = None
        self.currentShape = None
        self.roundStampPosition  = [15,20,60]  #Arbitrary position (needs to be tested)
        self.squareStampPosition = [15,25,60]  #Arbitrary position (needs to be tested)
        self.inkPoolPosition = [30,45,10] #Arbitrary position (needs to be tested)
        self.refillValue = 25
        self.host = "poulpus.local"
        self.username = "poulpus"
        self.password = "davinkus"

        #self.client = paramiko.client.SSHClient()
        #self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        #self.openSSH()

        self.go_home()


    
    #def __del__(self):
        #self.closeSSH()
        

    def openSSH(self):

        self.client.connect(self.host, username=self.username, password=self.password)

    def closeSSH(self):
        
        self.client.close()


    def pixel_to_mm(positionPixel, refPixels, refMm):

        PositionMeters = (positionPixel/refPixels) * refMm
        return PositionMeters
    
    def rotate_matrix(self,x,y):
        
        X = -np.cos(np.pi/3)*x + np.sin(np.pi/3)*x - (self.pageSizeMm[1])/2
        Y = np.sin(np.pi/3)*y + np.cos(np.pi/3)*y - (self.pageSizeMm[2])/2

        return [X,Y]
        

    def position_to_gcode(self,X,Y, Z):  #Positions en pixels sauf Z, le changement d'unites ce fera ici

        self.gcode.append(f"G1 X{X:.2f} Y{Y:.2f} Z{Z:.2f} F{self.flowRate}\n")

    def go_home(self):

        self.gcode.append(f"G28\n")
    
    def stamp_path(self, x, y):

        self.position_to_gcode(x, y, self.pageHeight +self.hop)
        self.position_to_gcode(x, y, self.pageHeight)
        self.position_to_gcode(x, y, self.pageHeight +self.hop)
    
    
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
    
    def send_Gcode(self):
        msg = ""
        for i in self.gcode:
            msg = msg + self.gcode[i]
        
        stdin, stdout, stderr = self.client.exec_command("echo '{}' >> /tmp/printer".format(msg))
        


    # this function generate the total path, including hops and change of color/shape of stamps
    def gcode_logic(self, positions): #positions is one or n positions
        
        self.go_home()
        stamp_counter = 0

        for x,y,shape,color  in positions:
            
            X = self.pixel_to_mm(x, self.pageSizePix[1],self.pageSizeMm[1])
            Y = self.pixel_to_mm(y, self.pageSizePix[1],self.pageSizeMm[2])

            [X,Y] = self.rotate_matrix(X,Y)
            #Checks is Stamp needs to be changed
            if shape != self.currentShape or color != self.currentColor:
                self.change_stamp(color, shape)
                self.ink_stamp(color)
                stamp_counter = 0
                
            #Checks if ink needs to be applied on the stamp
            if stamp_counter >= self.refillValue:
                self.ink_stamp(color)
                stamp_counter = 0
                
            self.stamp_path(X, Y)
            stamp_counter += 1

        self.go_home()

        self.send_Gcode()

        self.gcode = []

        



