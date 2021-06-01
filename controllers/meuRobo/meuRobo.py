# Ratinho 
# Felipe Pires
# Gabriel Arruda
# Nícolas Oliveira
import sys
import _thread
import struct
import socket
import random
import os

from controller import Robot, GPS
from io import BytesIO
from PIL import Image,ImageDraw,ImageFont,ImageOps

timestep = 64
velocidade = 3



print("Iniciando")

def get_path(msg):
    vector_msg = msg.split("/")[1]
    vector_msg = vector_msg.split(" ")[0]
    return vector_msg

def get_port():
    return random.randint(1000, 9999)
    # return 8080

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255',1))    
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    return IP    

class MeuRobot:
    def __init__(self, robot):
        
        self.robot = robot
        self.nome  = robot.getName()
        print("Nome do robo : ", self.nome)
        
        # pegando motores
        self.motor_esq_back = self.robot.getDevice("roda_esq_back")
        self.motor_esq_front = self.robot.getDevice("roda_esq_front")
        self.motor_dir_back = self.robot.getDevice("roda_dir_back")
        self.motor_dir_front = self.robot.getDevice("roda_dir_front")

        self.motor_esq_back.setPosition(float('+inf'))
        self.motor_esq_front.setPosition(float('+inf'))
        self.motor_dir_back.setPosition(float('+inf'))
        self.motor_dir_front.setPosition(float('+inf'))

        # pegando sensores
        self.ir0 = self.robot.getDevice("ir0")
        self.ir0.enable(timestep)

        self.ir1 = self.robot.getDevice("ir1")
        self.ir1.enable(timestep)
        
        self.ir2 = self.robot.getDevice("ir2")
        self.ir2.enable(timestep)
        
        self.ir3 = self.robot.getDevice("ir3")
        self.ir3.enable(timestep)
        
        self.sensor_linha_dir = self.robot.getDevice("sensor_linha_dir")
        self.sensor_linha_dir.enable(timestep)
        
        self.sensor_linha_esq = self.robot.getDevice("sensor_linha_esq")
        self.sensor_linha_esq.enable(timestep)
        
        # Camera
        self.cv = self.robot.getDevice("camera")
        self.cv.enable(timestep)
        
        self.motor_esq_back.setVelocity(velocidade)
        self.motor_esq_front.setVelocity(velocidade)
        self.motor_dir_back.setVelocity(velocidade)
        self.motor_dir_front.setVelocity(velocidade)    

class TI502(MeuRobot):
    def move_forward(self):
        self.motor_esq_back.setVelocity(velocidade)
        self.motor_esq_front.setVelocity(velocidade)
        self.motor_dir_back.setVelocity(velocidade)
        self.motor_dir_front.setVelocity(velocidade)
        
    def move_backward(self):
        self.motor_esq_back.setVelocity(-velocidade)
        self.motor_esq_front.setVelocity(-velocidade)
        self.motor_dir_back.setVelocity(-velocidade)
        self.motor_dir_front.setVelocity(-velocidade) 
        
    def run(self):

        while self.robot.step(timestep) != -1:
            linha_dir = self.sensor_linha_dir.getValue()
            linha_esq = self.sensor_linha_esq.getValue()
            # print(linha_dir, linha_esq)
            # se sair da linha esquerda,
            # viramos a direita
            if(linha_esq != 1000 and linha_dir == 1000):
                self.motor_dir_back.setVelocity(10)
                self.motor_dir_front.setVelocity(10)
                self.motor_esq_back.setVelocity(0)
                self.motor_esq_front.setVelocity(0) 
            # se sair da linha direita,
            # viramos a esquerda
            elif(linha_dir != 1000 and linha_esq == 1000):
                self.motor_esq_back.setVelocity(10)
                self.motor_esq_front.setVelocity(10)
                self.motor_dir_back.setVelocity(0)
                self.motor_dir_front.setVelocity(0)
                
            else:
                self.move_forward()

    def take_a_picture(self):
        img = self.cv.getImage()
        im = Image.frombytes('RGBA',(self.cv.getWidth(), self.cv.getHeight()), img) 
        imagem = Image.open('foto.jpg')
        imagem.paste(im)
        imagem.save('foto.jpg')

robot = Robot()

robot_controler = TI502(robot)

def servidor(https, hport):
    print(f"Server em {https}:{hport}")
    sockHttp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sockHttp.bind((https, hport))
    except:
        sockHttp.bind(('', hport))
        
    sockHttp.listen(1)
    
    while True:
        client, addr = sockHttp.accept()
        msg = client.recv(2048).decode("utf-8") 
        rote = get_path(msg)
        if(rote == "foto"):
            robot_controler.take_a_picture()
            
            file = open('foto.jpg','rb') # open file , r => read , b => byte format
            response = file.read()
            file.close()

            header = 'HTTP/1.1 200 OK\n'
            header += 'Content-Type: image/jpg\n\n'

            final_response = header.encode('utf-8')
            final_response += response
            client.sendall(final_response)
            client.close()
        else:
            # client.send(foto().encode())
            client.close()   

_thread.start_new_thread(servidor, (get_ip(),get_port()))

robot_controler.run()   

             



