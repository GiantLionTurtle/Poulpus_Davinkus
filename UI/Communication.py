import numpy as np
import cv2 as cv
import paramiko
from threading import Thread, Event
import time


def off(coord, vec):
    out = [0, 0, 0]
    for i in range(0, 3):
        out[i] = coord[i] + vec[i]
    return out

def keep_sftp_alive(transport, stop_event, interval=60):
    # https://stackoverflow.com/questions/50009688/python-paramiko-ssh-session-not-active-after-being-idle-for-many-hours
    while not stop_event.is_set():
        time.sleep(interval)
        transport.send_ignore()

class Communication:

    def __init__(self, window = None):

        self.window = window
        self.hop = 40 #hop height constant in millimeter
        self.flowRate = 9000 
        self.pageSizeMm = [175, 195]
        self.pageSizePix = [400, 445] # NEEDS TO BE CHANGED
        self.pageHeight = 72  #height in the Z axis to stamp
        self.gcode = []
        self.currentColor = None
        self.currentShape = None
        self.homeNotHome = [0,0,120]

        stamp1_l = [-40, self.pageSizeMm[1]/2 + 65, 112]
        stamp2_l = [-40, self.pageSizeMm[1]/2 + 6, 113]
        stamp3_l = [-40, self.pageSizeMm[1]/2  - 50, 112]
        stamp4_l = [-35, self.pageSizeMm[1]/2 - 97, 112]

        side_wiggle_amp = 8
        self.stampsTake_seqs = [self.make_take(stamp1_l, side_wiggle_amp), self.make_take(stamp2_l, side_wiggle_amp), self.make_take(stamp3_l, side_wiggle_amp), self.make_take(stamp4_l, side_wiggle_amp)]
        self.stampsDrop_seqs = [self.make_drop(stamp1_l), self.make_drop(stamp2_l), self.make_drop(stamp3_l), self.make_drop(stamp4_l)]
        
        middleinkpoolpos = [self.pageSizeMm[0]/2 - 20, -25, 103]
        self.inkPoolPosition = self.rotate_seq([off(middleinkpoolpos, [-40, 0, 0]), middleinkpoolpos, off(middleinkpoolpos, [35, 0, 0])])

        self.refillValue = 3
        self.host = "poulpus.local"
        self.username = "poulpus"
        self.password = "davinkus"
        self.rpi_shell = None

        self.openSSH()

        # self.stop_event= Event()
        # keep_alive_thread = Thread(target=keep_sftp_alive, args=(self.client.get_transport(), self.stop_event, ))
        # keep_alive_thread.daemon = True
        # keep_alive_thread.start()

    def __del__(self):
        print("Fermeture du tunel ssh!")
        # self.stop_event.set()
        # time.sleep(1)
        # self.closeSSH()
        

    def make_take(self, init, side_wiggle):
        return self.rotate_seq([off(init, [70, 0, 10]), off(init, [0, 0, 20]), init, off(init, [0, side_wiggle, 0]), off(init, [0, -side_wiggle, 0]), off(init, [0, 0, 10]), off(init, [70, 0, 10])])
    def make_drop(self, init):
        return  self.rotate_seq([off(init, [70, 0, 10]), init, off(init, [0, 0, 25]), off(init, [70, 0, 20])])
    
    def openSSH(self):
        try:
            self.client = paramiko.client.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.host, 22, username=self.username, password=self.password, allow_agent=False)
            if self.window:
                self.window.update_connection_status(True)
            
            self.client.get_transport().set_keepalive(60)
            # self.rpi_shell = self.client.invoke_shell()

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
        y = self.pageSizeMm[1] - (y+50) - (self.pageSizeMm[1])/2
        angle = -np.pi/6
        X = np.cos(angle)*x - np.sin(angle)*y 
        Y = np.sin(angle)*x + np.cos(angle)*y 

        return [X,Y,z]
    def rotate_matrix_l(self, listthing):
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
            self.send_seq(self.stampsDrop_seqs[3])
            
        if self.currentShape == "Carre":
            self.send_seq(self.stampsDrop_seqs[1])

        if self.currentShape == "Etoile":
            self.send_seq(self.stampsDrop_seqs[2])
 
        #Take the next stamp
        if shape == "Cercle":
            self.send_seq(self.stampsTake_seqs[3])

        if shape == "Carre":
            self.send_seq(self.stampsTake_seqs[1])

        if shape == "Etoile":
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
        # if color == "#ff0000": # Red
        #     pool_index = 0
        if color == "#0000ff": # Blue
            pool_index = 0
        elif color == "#ffff00": # Yellow
            pool_index = 1
        else: # Black
            pool_index = 2

        print("COULEUR:{}".format(color))

        self.position_to_gcode(self.inkPoolPosition[pool_index][0], self.inkPoolPosition[pool_index][1], self.inkPoolPosition[pool_index][2] + 40)
        self.flowRate = normalFr/2
        self.position_to_gcode(self.inkPoolPosition[pool_index][0], self.inkPoolPosition[pool_index][1], self.inkPoolPosition[pool_index][2] + 5)
        self.position_to_gcode(self.inkPoolPosition[pool_index][0], self.inkPoolPosition[pool_index][1], self.inkPoolPosition[pool_index][2] + 40)

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
        
        # self.openSSH()
        self.client.exec_command("echo '{}' >> /tmp/printer\n".format(msg))
        # self.closeSSH()


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
                self.ink_stamp(color)
                stamp_counter = 0
                
            #Checks if ink needs to be applied on the stamp
            if stamp_counter >= self.refillValue:
                self.ink_stamp(color)
                stamp_counter = 0
                
            self.stamp_path(X, Y)
            stamp_counter += 1

        self.send_Gcode()

        



