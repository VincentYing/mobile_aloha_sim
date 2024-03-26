#!/usr/bin/env python3 
#codeing =utf-8 

import math
import time
import mujoco_py
from mujoco_py import load_model_from_path, MjSim, MjViewer
import glfw  # 用于检查窗口关闭事件
import os
import rospy
import numpy as np
import cv2
from sensor_msgs.msg import JointState
import _thread
from threading import Thread

from mujoco_py import GlfwContext
GlfwContext(offscreen=True)

class Mujoco_Model():
    def __init__(self) -> None:
        # 寻找模型路径
        current_path = os.path.dirname(os.path.dirname(__file__))
        current_path = current_path + "/meshes_mujoco"
        model_path = current_path + "/aloha_v1.xml"
        print("The directory is ",model_path)
        # 加载仿真环境
        model = load_model_from_path(model_path)
        self.sim = MjSim(model)
        self.viewer = MjViewer(self.sim)
        self.offscreen_l = mujoco_py.MjRenderContextOffscreen(self.sim, 0, quiet = True)
        self.offscreen_r = mujoco_py.MjRenderContextOffscreen(self.sim, 0, quiet = True)

    def pos_ctrl(self, joint_name, target_angle):
        '''
        仿真环境中设定的position执行器控制
        '''
        joint_id = self.sim.model.get_joint_qpos_addr(joint_name)
        current_angle = self.sim.data.qpos[joint_id]
        # print(joint_name, ": ", current_angle)
        actuator_id = self.sim.model.actuator_name2id(joint_name)
        self.sim.data.ctrl[actuator_id] = target_angle

    def sim_stop(self):
        while not glfw.window_should_close(self.viewer.window):
            self.sim.step()
            self.viewer.render()
    
    def test1(self):
        import time
        count = 0
        while not glfw.window_should_close(self.viewer.window):
            if(count > 200 and count < 600):
                self.pos_ctrl("fl_joint1",3.14)
                self.pos_ctrl("fl_joint2",0.958)
                self.pos_ctrl("fl_joint3",0.99)

                self.pos_ctrl("fr_joint1",3.14)
                self.pos_ctrl("fr_joint2",0.958)
                self.pos_ctrl("fr_joint3",0.99)
            if(count > 600 and count < 1000):
                self.pos_ctrl("fl_joint1",1.67)
                self.pos_ctrl("fr_joint1",1.67)
            if(count > 600 and count < 1000):
                self.pos_ctrl("fl_joint1",0)
                self.pos_ctrl("fl_joint2",0)
                self.pos_ctrl("fl_joint3",0)

                self.pos_ctrl("fr_joint1",0)
                self.pos_ctrl("fr_joint2",0)
                self.pos_ctrl("fr_joint3",0)
            if(count > 1000 and count < 1400):
                self.pos_ctrl("fl_joint1",3.14)
                self.pos_ctrl("fl_joint2",0.958)
                self.pos_ctrl("fl_joint3",0.99)

                self.pos_ctrl("fr_joint1",3.14)
                self.pos_ctrl("fr_joint2",0.958)
                self.pos_ctrl("fr_joint3",0.99)
            if(count > 1400 and count < 1800):
                self.pos_ctrl("fl_joint1",-3.14)
                self.pos_ctrl("fl_joint2",0)
                self.pos_ctrl("fl_joint3",0)

                self.pos_ctrl("fr_joint1",-3.14)
                self.pos_ctrl("fr_joint2",0)
                self.pos_ctrl("fr_joint3",0)
                count = 0
            # 获取窗口屏幕图像
            self.offscreen_l.render(width=640, height=480, camera_id=0)
            data_l = self.offscreen_l.read_pixels(width=640, height=480, depth=False)
            self.offscreen_r.render(width=640, height=480, camera_id=1)
            data_r = self.offscreen_r.read_pixels(width=640, height=480, depth=False)

            # 从渲染结果中提取相机图像
            image_l = np.flipud(data_l)
            image_r = np.flipud(data_r)

            # 显示相机图像
            cv2.imshow("Camera Image_l", image_l)
            cv2.imshow("Camera Image_r", image_r)
            cv2.waitKey(1)
            self.sim.step()
            self.viewer.render()
            time.sleep(0.01)
            count = count + 1

class JointStatesSubscriber:
    def __init__(self):
        self.joint_positions_bl = {}
        self.joint_positions_br = {}
        # 初始化订阅者
        self.subscriber_bl = rospy.Subscriber("/master/joint_left", JointState, self.callback_bl)
        self.subscriber_br = rospy.Subscriber("/master/joint_reft", JointState, self.callback_br)
        # 初始化仿真环境
        self.mujocoCtrl = Mujoco_Model()
    
    def callback_bl(self, data):
        for i in range(len(data.name)):
            joint_name = data.name[i]
            if joint_name == "joint0" or joint_name == "joint1" or joint_name == "joint2" \
                    or joint_name == "joint3" or joint_name == "joint4" or joint_name == "joint5" \
                    or joint_name == "joint6" or joint_name == "joint7":
                self.joint_positions_bl[joint_name] = data.position[i]
    
    def callback_br(self, data):
        for i in range(len(data.name)):
            joint_name = data.name[i]
            if joint_name == "joint0" or joint_name == "joint1" or joint_name == "joint2" \
                    or joint_name == "joint3" or joint_name == "joint4" or joint_name == "joint5" \
                    or joint_name == "joint6" or joint_name == "joint7":
                self.joint_positions_br[joint_name] = data.position[i]

    def get_joint_position(self, arm_joint:dict, joint_name):
        if joint_name in self.arm_joint:
            return self.arm_joint[joint_name]
        else:
            rospy.logwarn("Joint position for {} not found!".format(joint_name))
            return None

    def MujocoCtrl(self):

        while not glfw.window_should_close(self.mujocoCtrl.viewer.window):
            if(self.joint_positions_bl != {}):
                # print(self.joint_positions_bl)
                self.mujocoCtrl.pos_ctrl("fl_joint1",self.get_joint_position(self.joint_positions_bl, "joint0"))
                self.mujocoCtrl.pos_ctrl("fl_joint2",self.get_joint_position(self.joint_positions_bl, "joint1"))
                self.mujocoCtrl.pos_ctrl("fl_joint3",self.get_joint_position(self.joint_positions_bl, "joint2"))
                self.mujocoCtrl.pos_ctrl("fl_joint4",self.get_joint_position(self.joint_positions_bl, "joint3"))
                self.mujocoCtrl.pos_ctrl("fl_joint5",self.get_joint_position(self.joint_positions_bl, "joint4"))
                self.mujocoCtrl.pos_ctrl("fl_joint6",self.get_joint_position(self.joint_positions_bl, "joint5"))
                self.mujocoCtrl.pos_ctrl("fl_joint7",self.get_joint_position(self.joint_positions_bl, "joint6")/90)
                self.mujocoCtrl.pos_ctrl("fl_joint8",self.get_joint_position(self.joint_positions_bl, "joint6")/90)
            if(self.joint_positions_br != {}):
                # print(self.joint_positions_bl)
                self.mujocoCtrl.pos_ctrl("fl_joint1",self.get_joint_position(self.joint_positions_br, "joint0"))
                self.mujocoCtrl.pos_ctrl("fl_joint2",self.get_joint_position(self.joint_positions_br, "joint1"))
                self.mujocoCtrl.pos_ctrl("fl_joint3",self.get_joint_position(self.joint_positions_br, "joint2"))
                self.mujocoCtrl.pos_ctrl("fl_joint4",self.get_joint_position(self.joint_positions_br, "joint3"))
                self.mujocoCtrl.pos_ctrl("fl_joint5",self.get_joint_position(self.joint_positions_br, "joint4"))
                self.mujocoCtrl.pos_ctrl("fl_joint6",self.get_joint_position(self.joint_positions_br, "joint5"))
                self.mujocoCtrl.pos_ctrl("fl_joint7",self.get_joint_position(self.joint_positions_br, "joint6")/90)
                self.mujocoCtrl.pos_ctrl("fl_joint8",self.get_joint_position(self.joint_positions_br, "joint6")/90)
            # 获取窗口屏幕图像
            self.mujocoCtrl.offscreen_l.render(width=640, height=480, camera_id=0)
            data_l = self.mujocoCtrl.offscreen_l.read_pixels(width=640, height=480, depth=False)
            self.mujocoCtrl.offscreen_r.render(width=640, height=480, camera_id=1)
            data_r = self.mujocoCtrl.offscreen_r.read_pixels(width=640, height=480, depth=False)

            # 从渲染结果中提取相机图像
            image_l = np.flipud(data_l)
            image_r = np.flipud(data_r)

            # 显示相机图像
            cv2.imshow("Camera Image_l", image_l)
            cv2.imshow("Camera Image_r", image_r)
            cv2.waitKey(1)
            self.mujocoCtrl.sim.step()
            self.mujocoCtrl.viewer.render()
    

def main():
    rospy.init_node('mujoco_joint_states_subscriber', anonymous=True)
    joint_states_subscriber = JointStatesSubscriber()
    joint_states_subscriber.MujocoCtrl()
    # joint_states_subscriber.mujocoCtrl.test1()
    
if __name__ == "__main__":  
    try:
        main()
    except rospy.ROSInterruptException:
        pass
