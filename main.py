# python 2.7
from __future__ import print_function
import os
import sys
import time
import random
from copy import deepcopy, copy
from time import sleep

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from socket import *

_PORT = 13000
_BUFFER = 1024

pyqt_app = ""

class cell(object):
	def __init__(self):
		self.value = 0
		self.render_coordinate = [None,None]
	def state(self):
		return self.value
	def set_occupied(self):
		self.value = 1
	def set_free(self):
		self.value = 0

class grid_worker(QThread):

	update_grid = pyqtSignal()

	def __init__(self,parent=None):
		QThread.__init__(self,parent)
		self.connect(self,SIGNAL("update_grid()"),parent.repaint)
		self.exiting = False 
		self.job = None 

	def run(self):
		time_per_cell = 0.1
		if self.job=="bullet":
			cur_x,cur_y = self.bullet_start
			increments_per_cell = 8
			time_per_increment = float(float(time_per_cell)/float(increments_per_cell))

			if self.bullet_direction=="left":
				for i in range(0,cur_x):
					x_spot = cur_x-i
					y_spot = cur_y
					for i in range(increments_per_cell):
						self.bullet_loc = [x_spot,y_spot,i]
						sleep(time_per_increment)

			if self.bullet_direction=="right":
				for i in range(cur_x,self.num_cols):
					x_spot = i
					y_spot = cur_y
					self.bullet_loc = [x_spot,y_spot]
					for i in range(increments_per_cell):
						self.bullet_loc = [x_spot,y_spot,i]
						sleep(time_per_increment)
					
			if self.bullet_direction=="up":
				for i in range(0,cur_y):
					x_spot = cur_x 
					y_spot = cur_y-i
					self.bullet_loc = [x_spot,y_spot]
					for i in range(increments_per_cell):
						self.bullet_loc = [x_spot,y_spot,i]
						sleep(time_per_increment)

			if self.bullet_direction=="down":
				for i in range(cur_y,self.num_rows):
					x_spot = cur_x 
					y_spot = i
					for i in range(increments_per_cell):
						self.bullet_loc = [x_spot,y_spot,i]
						sleep(time_per_increment)

			self.bullet_direction = None 
			self.job = None 
			self.update_grid.emit()

class frame_manager(QThread):
	update_grid = pyqtSignal()

	def __init__(self,parent=None):
		QThread.__init__(self,parent)
		self.connect(self,SIGNAL("update_grid()"),parent.repaint)

	def run(self):
		refresh_period = 0.025
		while True:
			self.update_grid.emit()
			sleep(refresh_period)

# UI element (widget) that represents the interface with the grid
class eight_neighbor_grid(QWidget):

	def __init__(self,num_cols=35,num_rows=25,pyqt_app=None,parent=None):
		# constructor, pass the number of cols and rows
		super(eight_neighbor_grid,self).__init__()
		self.parent	  = parent
		self.num_cols = num_cols # width of the board
		self.num_rows = num_rows # height of the board
		self.pyqt_app = pyqt_app # allows this class to call parent functions
		self.init_ui() # initialize a bunch of class instance variables

	def init_cells(self):
		self.cells = []
		for _ in range(self.num_rows):
			row = []
			for _ in range(self.num_cols):
				cur_cell = cell()
				row.append(cur_cell)
			self.cells.append(row)

	def init_ui(self):
		# initialize ui elements
		self.worker_threads = []
		#self.connect(self,SIGNAL("call_worker()"),self.worker_thread.run)
		self.grid_line_color = [0,0,0]
		self.free_color = [255,255,255]
		self.occupied_color = [0,128,255]
		self.bullet_color = [255,0,0]
		self.last_direction = "right"
		self.bullet_direction = None
		self.current_location = None
		self.opponent_location = None
		self.opponent_color = [128,255,0]
		self.game_over = False
		self.init_cells()

		self.frame_updater = frame_manager(self)
		self.frame_updater.start()

	def paintEvent(self,e):
		qp = QPainter()
		qp.begin(self)
		self.drawWidget(qp)
		qp.end()

		if self.game_over:

			for y in range(self.num_rows):
				for x in range(self.num_cols):
					if self.cells[y][x].state()==1:
						self.cells[y][x].set_free()
			self.cells[0][0].set_occupied()
			self.current_location = [0,0]
			self.parent.game_over()
			self.game_over = False

	def drawWidget(self,qp):
		size = self.size()
		height = size.height()
		width = size.width()

		self.horizontal_step = int(round(width/self.num_cols))
		self.vertical_step = int(round(height/self.num_rows))

		grid_height = self.vertical_step*self.num_rows
		grid_width = self.horizontal_step*self.num_cols

		qp.setBrush(QColor(self.free_color[0],self.free_color[1],self.free_color[2]))
		qp.setPen(QPen(QColor(self.grid_line_color[0],self.grid_line_color[1],self.grid_line_color[2]),1,Qt.SolidLine))

		for y in range(self.num_rows):
			for x in range(self.num_cols):
				cell_state = self.get_cell_state(x,y)

				if cell_state==1:
					qp.setBrush(QColor(self.occupied_color[0],self.occupied_color[1],self.occupied_color[2]))
					self.current_location = [x,y]

				x_start = x*self.horizontal_step
				y_start = y*self.vertical_step
				qp.drawRect(x_start,y_start,self.horizontal_step,self.vertical_step)

				self.cells[y][x].render_coordinate = [x_start,y_start]

				if cell_state==1:
					qp.setBrush(QColor(self.free_color[0],self.free_color[1],self.free_color[2]))

		for t in self.worker_threads:
			if t.job=="bullet":
				try:
					render_loc = self.cells[t.bullet_loc[1]][t.bullet_loc[0]].render_coordinate
				except:
					print("Bullet left arena")
					continue

				qp.setBrush(QColor(self.bullet_color[0],self.bullet_color[1],self.bullet_color[2]))

				move_m = 2

				if t.bullet_direction in ["left","right"]:
					qp.drawEllipse(render_loc[0]+(t.bullet_loc[2]*move_m),render_loc[1]+6,4,4)
				else:
					qp.drawEllipse(render_loc[0]+6,render_loc[1]+(t.bullet_loc[2]*move_m),4,4)

				if self.current_location!=None and self.opponent_location!=None:
					if t.bullet_loc[0] in [self.current_location[0],self.opponent_location[0]]:
						if t.bullet_loc[1] in [self.current_location[1],self.opponent_location[1]]:
							self.game_over = True

		if self.opponent_location!=None:
			x = self.opponent_location[0]
			y = self.opponent_location[1]
			x_start = x*self.horizontal_step
			y_start = y*self.horizontal_step
			qp.setBrush(QColor(self.opponent_color[0],self.opponent_color[1],self.opponent_color[2]))
			qp.drawRect(x_start,y_start,self.horizontal_step,self.vertical_step)

	def get_cell_state(self,x,y):
		return self.cells[y][x].state()

	def get_open_cell(self):
		for y in range(self.num_rows):
			for x in range(self.num_cols):
				if self.cells[y][x].state()==0:
					return [x,y]
		return [-1,-1]

	def get_start_cell(self):
		x,y = self.get_open_cell()
		if x==-1 and y==-1:
			print("ERROR: get_start_cell() could not find open cell")
			return
		self.cells[y][x].set_occupied()
		self.repaint()

	def get_cell_attrib(self,attrib=1):
		for y in range(self.num_rows):
			for x in range(self.num_cols):
				if self.cells[y][x].state()==attrib:
					return [x,y]
		return [-1,-1]

	def move(self,action="none"):
		self.last_direction = action

		cur_x,cur_y = self.get_cell_attrib(attrib=1)
		if cur_x==-1 and cur_y==-1:
			print("ERROR: move() could not find current cell!")
			return [-1,-1]

		x,y = cur_x,cur_y

		if action=="left": x+=-1
		if action=="right": x+=1
		if action=="up": y+=-1
		if action=="down": y+=1

		if x==-1 or x==self.num_cols: 
			return [cur_x,cur_y]
		if y==-1 or y==self.num_rows: 
			return [cur_x,cur_y]

		self.cells[cur_y][cur_x].set_free()
		self.cells[y][x].set_occupied()
		self.current_location = [x,y]
		self.repaint()
		return [x,y]

	def clean_worker_threads(self):
		for t in self.worker_threads:
			if t.job==None: del self.worker_threads[self.worker_threads.index(t)]

	def action(self,what="shoot"):
		if what=="shoot":
			t = grid_worker(self)
			t.job = "bullet"
			t.bullet_direction = self.last_direction
			t.bullet_start = self.get_cell_attrib(1) if self.current_location==None else self.current_location
			t.num_cols = self.num_cols
			t.num_rows = self.num_rows
			self.worker_threads.append(t)
			t.start()
			self.clean_worker_threads()
			return [t.bullet_direction,t.bullet_start]

	def opponent_shoot(self,bullet_direction,start_x,start_y):
		t = grid_worker(self)
		t.job = "bullet"
		t.bullet_direction = bullet_direction
		t.bullet_start = [int(start_x),int(start_y)]
		t.num_cols = self.num_cols
		t.num_rows = self.num_rows
		self.worker_threads.append(t)
		t.start()

	def opponent_move(self,x,y):
		self.opponent_location = [int(x),int(y)]
		self.repaint()

	def set_current_location(self,location_descriptor):
		if location_descriptor=="opposite":
			for y in range(self.num_rows):
				for x in range(self.num_cols):
					if self.cells[y][x].state()==1:
						self.cells[y][x].set_free()
		self.current_location = [self.num_cols-1,self.num_rows-1]
		self.cells[self.num_rows-1][self.num_cols-1].set_occupied()
		self.repaint()
		return [self.num_cols-1,self.num_rows-1]

class sender_thread(QThread):
	def __init__(self):
		QThread.__init__(self)

	def run(self):
		# Called when the thread is started
		self.port = _PORT
		self.connect() 
		self.send()

	def connect(self):
		self.addr = (self.host, self.port)
		self.UDPSock = socket(AF_INET, SOCK_DGRAM)
		return True

	def send(self):
		self.UDPSock.sendto(str(self.message), self.addr)
		self.UDPSock.close()
		self.is_done = True

class receive_thread(QThread):

	def __init__(self):
		QThread.__init__(self)

	def run(self):
		# Called when the thread is started
		print ("Receiver thread online.")
		host 	= ""
		port 	= _PORT
		buf 	= _BUFFER
		
		addr 	= (host, port)
		UDPSock = socket(AF_INET, SOCK_DGRAM)
		UDPSock.bind(addr)

		while True:
			
			(data, addr) = UDPSock.recvfrom(buf)
			self.emit(SIGNAL("got_message(QString)"), data)

		UDPSock.close()

class main_window(QWidget):

	def __init__(self,parent=None):
		super(main_window,self).__init__()
		self.opponent_ip = None
		self.set_connected(False)
		self.init_ui()
		self.start_character()

	def set_connected(self,connected):
		cur_ip = str(gethostbyname(gethostname()))
		if connected:
			self.setWindowTitle("Me: ("+cur_ip+") - Opponent: ("+self.opponent_ip+")")
		else:
			self.setWindowTitle("Me: ("+cur_ip+") - Not Connected")

	def init_ui(self):

		self.receiver = receive_thread()
		self.receiver.start()

		self.sender_threads = []

		QObject.connect(self.receiver,SIGNAL("got_message(QString)"),self.receive_update)

		self.min_width = 625
		self.min_height = 425

		self.layout = QVBoxLayout(self)
		self.grid = eight_neighbor_grid(parent=self)

		if sys.platform in ["apple","Apple","darwin","Darwin"]:
			self.min_height = 470
			self.min_width = 675

		if sys.platform in ["linux","linux32","win32"]: 
			self.layout.addSpacing(25)
			self.min_height+=25

		self.layout.addWidget(self.grid)

		self.toolbar = QMenuBar(self)
		self.toolbar.setFixedWidth(self.min_width)

		file_menu = self.toolbar.addMenu("File")
		file_menu.addAction("Quit",self.quit,QKeySequence("Ctrl+Q"))

		connection_menu = self.toolbar.addMenu("Connection")
		connection_menu.addAction("Connect",self.connect)
		connection_menu.addAction("Disconnect",self.disconnect)

		self.setFixedWidth(self.min_width)
		self.setFixedHeight(self.min_height)
		self.show()

	def receive_update(self,update):
		if len(update)==0: return 

		items = update.split("|")

		if items[0]=="restart":
			self.grid.set_current_location("opposite")
			return

		if items[0]=="new":
			self.connect(opp_ip=items[1])
			x,y = self.grid.set_current_location("opposite")
			sender = sender_thread()
			sender.host = self.opponent_ip
			sender.message = "move|x:"+str(x)+"|y:"+str(y)
			sender.start()
			sender.is_done=False
			self.sender_threads.append(sender)
			return

		if items[0]=="shoot":
			bullet_direction = items[1]
			x = items[2].split(":")[1]
			y = items[3].split(":")[1]
			self.grid.opponent_shoot(bullet_direction=bullet_direction,start_x=x,start_y=y)
			return

		if items[0]=="move":
			x = items[1].split(":")[1]
			y = items[2].split(":")[1]
			self.grid.opponent_move(x,y)
			return

	def connect(self,opp_ip=None):
		if opp_ip==None:
			while True:
				resp,ok = QInputDialog.getText(self,"Connection","Enter IP (192.168.1.x): ")
				if not ok: return 

				broken = resp.split(".")
				if len(broken)==4:
					for b in broken:
						try:
							int(b)
						except:
							continue 
					break
		else:
			resp = opp_ip

		self.opponent_ip = resp
		self.set_connected(True)

		if opp_ip==None:
			sender = sender_thread()
			sender.host = self.opponent_ip
			sender.message = "new|"+str(gethostbyname(gethostname()))
			sender.start()
			sender.is_done = False 
			self.sender_threads.append(sender)

	def disconnect(self):
		self.opponent_ip = None

	def quit(self):
		sys.exit(1)

	def start_character(self):
		self.grid.get_start_cell()

	def keyPressEvent(self,e):
		action = None
		if e.key() == Qt.Key_Left: action="left"
		if e.key() == Qt.Key_Right: action="right"
		if e.key() == Qt.Key_Up: action="up"
		if e.key() == Qt.Key_Down: action="down"
		if e.key() == Qt.Key_Space: action="shoot"

		if action!=None:
			if action=="shoot": 
				bullet_direction, bullet_start = self.grid.action(action)
				message = "shoot|"+bullet_direction+"|"+"x:"+str(bullet_start[0])+"|y:"+str(bullet_start[1])
			else: 
				new_location = self.grid.move(action)
				message = "move|"+"x:"+str(new_location[0])+"|y:"+str(new_location[1])

			if self.opponent_ip!=None:
				sender = sender_thread()
				sender.host = self.opponent_ip
				sender.message = message
				sender.start()
				sender.is_done=False
				self.sender_threads.append(sender)
				self.clean_sender_threads()

	def clean_sender_threads(self):
		for s in self.sender_threads:
			if s.is_done:
				del self.sender_threads[self.sender_threads.index(s)]

	def game_over(self):
		sender = sender_thread()
		sender.host = self.opponent_ip
		sender.message = "restart|"
		sender.start()
		sender.is_done = False 
		self.sender_threads.append(sender)

def main():
	global pyqt_app
	pyqt_app = QApplication(sys.argv)
	_ = main_window()
	sys.exit(pyqt_app.exec_())

if __name__ == '__main__':
	main()