import numpy as np
import cv2 as cv
import paramiko

def off(coord, vec):
    out = [0, 0, 0]
    for i in range(0, 3):
        out[i] = coord[i] + vec[i]
    return out

class Communication:

    def __init__(self, window = None):

        self.window = window
        self.hop = 40 #hop height constant in millimeter
        self.flowRate = 2500 
        self.pageSizeMm = [175, 195]
        self.pageSizePix = [400, 445] # NEEDS TO BE CHANGED
        self.pageHeight = 72  #height in the Z axis to stamp
        self.gcode = []
        self.currentColor = None
        self.currentShape = None
        self.homeNotHome = [0,0,120]

        stamp1_l = [-35, self.pageSizeMm[1]/2 + 65, 112]
        stamp2_l = [-35, self.pageSizeMm[1]/2 + 4, 113]
        stamp3_l = [-35, self.pageSizeMm[1]/2  - 50, 112]
        stamp4_l = [-35, self.pageSizeMm[1]/2 - 127, 112]

        side_wiggle_amp = 10
        self.stampsTake_seqs = [self.make_take(stamp1_l, side_wiggle_amp), self.make_take(stamp2_l, side_wiggle_amp), self.make_take(stamp3_l, side_wiggle_amp), self.make_take(stamp4_l, side_wiggle_amp)]
        self.stampsDrop_seqs = [self.make_drop(stamp1_l), self.make_drop(stamp2_l), self.make_drop(stamp3_l), self.make_drop(stamp4_l)]
        
        self.inkPoolPosition = self.rotate_matrix(self.pageSizeMm[0]/2 - 20, -30, 103)

        self.refillValue = 3
        self.host = "poulpus.local"
        self.username = "poulpus"
        self.password = "davinkus"
        
        self.openSSH()

    def __del__(self):
        print("Fermeture du tunel ssh!")
        self.closeSSH()
        

    def make_take(self, init, side_wiggle):
        return self.rotate_seq([off(init, [80, 0, 7]), init, off(init, [0, side_wiggle, 8]), off(init, [0, -side_wiggle, 8]), off(init, [0, 0, 8]), off(init, [80, 0, 7])])
    def make_drop(self, init):
        return  self.rotate_seq([off(init, [80, 0, 7]), init, off(init, [0, 0, 20]), off(init, [80, 0, 20])])
    
    def openSSH(self):
        try:
            self.client = paramiko.client.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.host,22, username=self.username, password=self.password, timeout=30, allow_agent=False)
            if self.window:
                self.window.update_connection_status(True)
            
            self.client.get_transport().set_keepalive(5)


        except Exception as e:
            print("Incapable d'etablir la connection ssh")
            if self.window:
                self.window.update_connection_status(False)
            pass

    def closeSSH(self):
        self.client.close()

    
    def pixel_to_mm(self,positionPixel, refPixels, refMm):



        PositionMeters = (positionPixel/refPixels) * refMm
        return PositionMeters
    
    def rotate_matrix(self,x,y,z):
        x = -(x+20 - (self.pageSizeMm[0])/2)
        y = self.pageSizeMm[1] - (y+40) - (self.pageSizeMm[1])/2
        angle = -np.pi/6
        X = np.cos(angle)*x - np.sin(angle)*y 
        Y = np.sin(angle)*x + np.cos(angle)*y 

        return [X,Y,z]
    def rotate_matrix(self, listthing):
        return self.rotate_matrix(listthing[0], listthing[1], listthing[2])

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
            self.send_seq(self.stampsDrop_seqs[0])
            
        if self.currentShape == "Carré":
            self.send_seq(self.stampsDrop_seqs[1])

        if self.currentShape == "Triangle":
            self.send_seq(self.stampsDrop_seqs[2])
 
        #Take the next stamp
        if shape == "Cercle":
            self.send_seq(self.stampsTake_seqs[0])

        if shape == "Carré":
            self.send_seq(self.stampsTake_seqs[1])

        if shape == "Triangle":
            self.send_seq(self.stampsTake_seqs[2])

        self.currentColor = color
        self.currentShape = shape
        return
    def send_seq(self, seq):
        for elem in seq:
            self.position_to_gcode(elem[0], elem[1], elem[2])

    def ink_stamp(self,color):
        #Set slower flow rate to avoid big Splash
        normalFr = self.flowRate
        
        pool_index = 0
        if color == "#ff0000": # Red
            pool_index = 0
        elif color == "#ffff00": # Blue
            pool_index = 1
        elif color == "#00ffff": # Yellow
            pool_index = 2
        else: # Black
            pool_index = 3

        self.position_to_gcode(self.inkPoolPosition[pool_index][0], self.inkPoolPosition[pool_index][1], self.inkPoolPosition[pool_index][2] + 60)
        self.flowRate = normalFr/2
        self.position_to_gcode(self.inkPoolPosition[pool_index][0], self.inkPoolPosition[pool_index][1], self.inkPoolPosition[pool_index][2])
        self.position_to_gcode(self.inkPoolPosition[pool_index][0], self.inkPoolPosition[pool_index][1], self.inkPoolPosition[pool_index][2] + 60)

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
        stamp_counter = 0

        for x,y,shape,color  in positions:
            
            X = self.pixel_to_mm(x, self.pageSizePix[0], self.pageSizeMm[0])
            Y = self.pixel_to_mm(y, self.pageSizePix[1], self.pageSizeMm[1])
            print("to mm X={}, Y={}".format(X, Y))
            [X,Y,Z] = self.rotate_matrix(X,Y,self.pageHeight)

            #Checks if Stamp needs to be changed
            if shape != self.currentShape or color != self.currentColor:
                self.change_stamp(color, shape)
                self.ink_stamp(shape)
                stamp_counter = 0
                
            #Checks if ink needs to be applied on the stamp
            if stamp_counter >= self.refillValue:
                self.ink_stamp(color)
                stamp_counter = 0
                
            self.stamp_path(X, Y)
            stamp_counter += 1

        self.send_Gcode()

        



