import subprocess
import threading
import os
import sys
from serial import Serial
import select
import argparse
import time
"""packages """
import numpy as np
import pybullet as pb
import pybullet_data
import pyqtgraph as pg
import PySide6.QtWidgets as widgets
from PySide6.QtCore import QTimer

DATA_LEVEL = int(os.environ.get("DATA", "1"))
# HAND_LEVEL = int(os.environ.get("HAND", "R"))
REAL_TIME = 0
UPDATE_RATE = int(os.environ.get("UPDATE_RATE", "0"))
FUGAZI_DATA = int(os.environ.get("FUGAZI_DATA", "0"))
USB_ENABLE = int(os.environ.get("USB_ENABLE", "0"))
MAX_PLOT_POINTS = int(os.environ.get("MAX_PLOT","500"))
SIMULATION_RATE =  int(os.environ.get("SIMULATION_RATE","100"))
SIMULATION_PLOT_RATE =  int(SIMULATION_RATE/int(os.environ.get("PLOT_UPDATE_RATE","5")))
 
parser = argparse.ArgumentParser()
parser.add_argument("--usb", nargs="?", const="/dev/ttyUSB0",
                    type=str, default="/dev/ttyUSB0")

usb_channel = parser.parse_args().usb
current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)
model_folder_name = "models"
models_path = os.path.join(current_dir_path, model_folder_name)
port = Serial(usb_channel) if USB_ENABLE else None
fingers = ["pinky", "ring", "middle", "index", "thumb"]
fingetr_joints = ["bulk", "yaw", "pitch", "knuckle", "tip"]
right_finger_joint_indices = {
    "pinky": [10, 11, 12, 13, 14],
    "thumb": [19, 20, 21, 22, 23],
    "middle": [4, 15, 16, 17, 18],
    "index": [-1, 25, 26, 27, 28],
    "ring": [5, 6, 7, 8, 9]}

encoder_positions = [[],[],[],[],[]]
simulated_forces = [[],[],[],[],[]]
estimated_forces = [[],[],[],[],[]]
finger_order = []
encoder_position_buffer = [[],[],[],[],[],[]]
current_hand_position = [0, 0, 0, 0, 0]
current_force_position = [0.0, 0.0, 0.0, 0.0,0.0]
pb.connect(pb.GUI)
pb.setAdditionalSearchPath(models_path)
counter = 0
plane_id = pb.loadURDF("plane/plane.urdf")
right_hand_id = pb.loadURDF("hand/dexhand-right.urdf")
pb.enableRealTimeSimulation(1) if REAL_TIME else pb.setTimeStep(1/100)

def fugazi_data_generation():
    random_generator = np.random.default_rng()
    return random_generator.integers(low=0, high=14, size=5), random_generator.random(size=5)*10, random_generator.random(size=5)*10

def send_data_to_subprocess(msg_number: int, simulation_force_data: list[float], real_force_data: list[float], encoder_position: list[float]):
    simulation_force_data = [str(x) for x in simulation_force_data]
    real_force_data = [str(x) for x in real_force_data]
    position_data = [str(x) for x in encoder_position]
    formatted_msg = f"msg:{msg_number} | {' '.join(position_data)} | {' '.join(simulation_force_data)} | {' '.join(real_force_data)} \n"
    sys.stdout.write(formatted_msg)

def encoder_to_curl(finger_name: str, robot_hand_id: int, joint_index: int, encoder_position: int) -> list[int]:
    match finger_name:
        case "pinky" | "ring" | "middle" | "index":
            finger_joint_position = [encoder_position,0, 0, encoder_position, encoder_position]
            for x in range(len(finger_joint_position)):
                pb.setJointMotorControl2(robot_hand_id, right_finger_joint_indices[finger_name][x], control_mode=pb.POSITION_CONTROL, targetPosition=finger_join_position[x])
        case "thumb":
            print("Not yet implemented")

def get_simulation_contact_forces(body_id):
    if FUGAZI_DATA == 1:
        return [1, 2, 3, 4, 5]
    else:
        normal_forces_list = []
        for x in right_finger_joint_indices.keys():
            contact_forces = pb.getContactPoints(bodyA=body_id,linkIndexA=right_finger_joint_indices[x][4])
            normal_forces_list.append(contact_forces[0][9] if len(contact_forces) > 0 else 0)
        return normal_forces_list

def get_hand_data(port: Serial):
    return [1, 2, 3, 4, 5], [2, 3, 4, 5, 6]

class MainWindow(widgets.QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.resize(900,900)
        self.view = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.view)
        self.w1 = self.view.addPlot()
        self.w2 = self.view.addPlot()
        self.view.nextRow()
        self.w3 = self.view.addPlot()
        self.label = self.view.addLabel(" plotting graph")
        self.w1.setTitle("Encoder output graph latest updates")
        self.w1.resize(400,400)
        self.w1.setLabels(**{"left":"raw linear encoder output","bottom":"updates"})
        self.legend_1 = self.w1.addLegend()
        self.w2.setTitle("raw hand force output graph latest updates")
        self.w2.resize(400,400)
        self.w2.setLabels(**{"left":"raw hand force output","bottom":"updates"})
        self.legend_2 = self.w2.addLegend()
        self.w3.setTitle("simulated force output graph latest updates")
        self.w3.resize(400,400)
        self.w3.setLabels(**{"left":"simulatedhand force output","bottom":"updates"}) 
        self.legend_3 = self.w3.addLegend()
        self.timer = QTimer(self)
        self.timer.setInterval(100/SIMULATION_RATE)
        self.timer.timeout.connect(self.update_plots)
        self.timer.start()
        self.pens = [pg.mkPen('aquamarine'),
                     pg.mkPen('indianred'),
                     pg.mkPen('mediumorchid'),
                     pg.mkPen('seagreen'),
                     pg.mkPen('burlywood')]
        for i in range(len(encoder_positions)):
            self.w1.plot(encoder_positions[i],pen=self.pens[i],name=fingers[i])
        for i in range(len(simulated_forces)):
            self.w2.plot(simulated_forces[i],pen=self.pens[i],name=fingers[i])
        for i in range(len(estimated_forces)):
            self.w3.plot(estimated_forces[i],pen=self.pens[i],name=fingers[i])

    def plot_values(self):
        for i in range(len(encoder_positions)):
            self.w1.plot(encoder_positions[i],pen=self.pens[i])
        for i in range(len(simulated_forces)):
            self.w2.plot(simulated_forces[i],pen=self.pens[i])
        for i in range(len(estimated_forces)):
            self.w3.plot(estimated_forces[i],pen=self.pens[i])


    def update_plots(self):
        global encoder_positions, simulated_forces, estimated_forces
        current_hand_position, current_forces_sensed, simulation_contact_forces = [0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]
        if FUGAZI_DATA == 0:
            current_hand_position, current_forces_sensed = get_hand_data(port)
            simulation_contact_forces = get_simulation_contact_forces(right_hand_id)
            # send_desired_forces(simulation_contact_forces)
        else:
            current_hand_position, current_forces_sensed, simulation_contact_forces = fugazi_data_generation()
        if DATA_LEVEL == 1:
            if counter % SIMULATION_PLOT_RATE == 0:
                for i in range(5):
                    encoder_positions[i].append(current_hand_position[i])
                    simulated_forces[i].append(current_forces_sensed[i])
                    estimated_forces[i].append(simulation_contact_forces[i])
                if len(encoder_positions) > MAX_PLOT_POINTS: encoder_positions.pop(0) 
                if len(simulated_forces) > MAX_PLOT_POINTS: simulated_forces.pop(0)
                if len(estimated_forces) > MAX_PLOT_POINTS: estimated_forces.pop(0)
                self.plot_values()
        if REAL_TIME == 0:
            pb.stepSimulation()

app = pg.mkQApp("hand data plotting interface")
main_window = MainWindow()
main_window.show()
app.exec()
