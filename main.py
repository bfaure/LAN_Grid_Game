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
		time_per_cell = 0.05
		if self.job=="bullet":
			self.bullet_loc = None
			cur_x,cur_y = self.bullet_start
			increments_per_cell = 8
			time_per_increment = float(float(time_per_cell)/float(increments_per_cell))

			if self.bullet_direction=="left":
				for i in range(-1,cur_x):
					if self.exiting: break
					x_spot = cur_x-i
					y_spot = cur_y
					for j in range(increments_per_cell):
						self.bullet_loc = [x_spot,y_spot,j]
						sleep(time_per_increment)

			if self.bullet_direction=="right":
				for i in range(cur_x,self.num_cols+1):
					if self.exiting: break
					x_spot = i
					y_spot = cur_y
					for j in range(increments_per_cell):
						self.bullet_loc = [x_spot,y_spot,j]
						sleep(time_per_increment)
					
			if self.bullet_direction=="up":
				for i in range(-1,cur_y):
					if self.exiting: break
					x_spot = cur_x 
					y_spot = cur_y-i
					for j in range(increments_per_cell):
						self.bullet_loc = [x_spot,y_spot,j]
						sleep(time_per_increment)

			if self.bullet_direction=="down":
				for i in range(cur_y,self.num_rows+1):
					if self.exiting: break
					x_spot = cur_x 
					y_spot = i
					for j in range(increments_per_cell):
						self.bullet_loc = [x_spot,y_spot,j]
						sleep(time_per_increment)

			if self.bullet_direction=="up_left":
				y_span = cur_y 
				x_span = cur_x 
				if y_span>x_span:
					for i in range(-1,cur_y):
						y_spot = cur_y-i 
						x_spot = cur_x-i
						for j in range(increments_per_cell):
							self.bullet_loc = [x_spot,y_spot,j]
							sleep(time_per_increment)
				else:
					for i in range(-1,cur_x):
						y_spot = cur_y-i 
						x_spot = cur_x-i
						for j in range(increments_per_cell):
							self.bullet_loc = [x_spot,y_spot,j]
							sleep(time_per_increment)

			if self.bullet_direction=="up_right":
				y_span = cur_y 
				x_span = self.num_cols-cur_x
				if y_span>x_span:
					for i in range(-1,cur_y):
						y_spot = cur_y-i
						x_spot = cur_x+i
						for j in range(increments_per_cell):
							self.bullet_loc = [x_spot,y_spot,j]
							sleep(time_per_increment)
				else:
					for i in range(cur_x,self.num_cols+1):
						y_spot = cur_y-i+cur_x 
						x_spot = i 
						for j in range(increments_per_cell):
							self.bullet_loc = [x_spot,y_spot,j]
							sleep(time_per_increment)

			if self.bullet_direction=="down_left":
				y_span = self.num_rows-cur_y 
				x_span = cur_x 
				if y_span>x_span:
					for i in range(cur_y,self.num_rows+1):
						y_spot = i 
						x_spot = cur_x-i+cur_y 
						for j in range(increments_per_cell):
							self.bullet_loc = [x_spot,y_spot,j]
							sleep(time_per_increment)

				else:
					for i in range(-1,cur_x):
						y_spot = cur_y+i 
						x_spot = cur_x-i 
						for j in range(increments_per_cell):
							self.bullet_loc = [x_spot,y_spot,j]
							sleep(time_per_increment)

			if self.bullet_direction=="down_right":
				y_span = self.num_rows-cur_y 
				x_span = self.num_cols-cur_x 
				if y_span>x_span:
					for i in range(cur_y,self.num_rows+1):
						y_spot = i 
						x_spot = cur_x+i-cur_y 
						for j in range(increments_per_cell):
							self.bullet_loc = [x_spot,y_spot,j]
							sleep(time_per_increment)

				else:
					for i in range(cur_x,self.num_cols+1):
						y_spot = cur_y+i-cur_x 
						x_spot = i 
						for j in range(increments_per_cell):
							self.bullet_loc = [x_spot,y_spot,j]
							sleep(time_per_increment)

			self.bullet_direction = None 
			self.job = None 
			#self.update_grid.emit()

		bot_sleep_time = 0.5
		if self.job=="bot":
			self.bot_loc = self.bot_start
			directions = ["left","right","up","down"]
			while True:
				if self.exiting: break 
				self.bot_dir = random.choice(directions)
				for self.inc in range(10):
					sleep(float(bot_sleep_time)/10.00)
				if self.bot_dir=="left": self.bot_loc = [self.bot_loc[0]-1,self.bot_loc[1]]
				if self.bot_dir=="right": self.bot_loc = [self.bot_loc[0]+1,self.bot_loc[1]]
				if self.bot_dir=="up": self.bot_loc = [self.bot_loc[0],self.bot_loc[1]-1]
				if self.bot_dir=="down": self.bot_loc = [self.bot_loc[0],self.bot_loc[1]+1]

			self.job = None

class frame_manager(QThread):
	update_grid = pyqtSignal()

	def __init__(self,parent=None):
		QThread.__init__(self,parent)
		self.connect(self,SIGNAL("update_grid()"),parent.repaint)

	def run(self):
		refresh_period = 0.02
		while True:
			if self.stop: break
			self.update_grid.emit()
			sleep(refresh_period)

# UI element (widget) that represents the interface with the grid
class eight_neighbor_grid(QWidget):
	end_game = pyqtSignal()

	def __init__(self,num_cols=35,num_rows=25,pyqt_app=None,parent=None):
		# constructor, pass the number of cols and rows
		super(eight_neighbor_grid,self).__init__()
		self.parent	  = parent
		self.connect(self,SIGNAL("end_game()"),parent.game_over)
		self.num_cols = num_cols # width of the board
		self.num_rows = num_rows # height of the board
		self.pyqt_app = pyqt_app # allows this class to call parent functions
		self.init_ui() # initialize a bunch of class instance variables
		self.bots = []

	def init_cells(self):
		self.cells = []
		for _ in range(self.num_rows):
			row = []
			for _ in range(self.num_cols):
				cur_cell = cell()
				row.append(cur_cell)
			self.cells.append(row)

		self.init_blocked_cells()

	def init_blocked_cells(self):

		self.user_health = 10
		self.user_has_gem = 0
		self.blocked_cells = []
		self.blocked_cell_life = []
		generate = False
		if generate:
			num_blocked_cells = 150

			while len(self.blocked_cells)<num_blocked_cells:
				x_coord = random.randint(0,self.num_cols-1)
				y_coord = random.randint(0,self.num_rows-1)
				if x_coord==0 and y_coord==0:
					continue
				if x_coord==self.num_cols-1 and y_coord==self.num_rows-1:
					continue 
				self.blocked_cells.append([x_coord,y_coord])
				self.blocked_cell_life.append(10)

			# select 8 random regions:
			self.hard_to_traverse_regions = []
			num_regions = 4
			for _ in range(num_regions):
				random.seed()
				x_rand = random.randint(0,self.num_cols-1)
				y_rand = random.randint(0,self.num_rows-1)
				coord = (x_rand,y_rand)
				self.hard_to_traverse_regions.append(coord)

			region_radius = 5
			region_circum = region_radius*2

			for region_center in self.hard_to_traverse_regions:

				region_center_x = region_center[0]
				region_center_y = region_center[1]

				# top left corner coordinates...
				region_start_x = region_center_x - region_radius
				region_start_y = region_center_y - region_radius

				# iterate over every cell in range and select with 50%
				# probability to mark it as partially blocked
				for y in range(region_start_y,region_start_y+region_circum):
					# check that the y coord is in the grid range
					if y>=0 and y<self.num_rows:
						for x in range(region_start_x,region_start_x+region_circum):
							# check that the x coord is in the grid range
							if x>=0 and x<self.num_cols:
								if random.randint(0,1)==1:
									self.blocked_cells.append([x,y])
									self.blocked_cell_life.append(5)

			f = open("grid","w")
			for coord,health in zip(self.blocked_cells,self.blocked_cell_life):
				line = str(coord[0])+","+str(coord[1])+" "+str(health)+"\n"
				f.write(line)
			f.write("end")
			f.close()
		else:
			f = open("grid","r")
			lines = f.read().split("\n")
			for line in lines:
				if line.find("end")!=-1: break
				items = line.split(" ")
				x,y = items[0].split(",")
				x = int(x)
				y = int(y)
				health = int(items[1])
				self.blocked_cells.append([x,y])
				self.blocked_cell_life.append(health)

		self.gem_locations = []
		num_gems = 5
		while len(self.gem_locations)<num_gems:
			idx = random.randint(0,len(self.blocked_cells)-1)
			if self.blocked_cell_life[idx]==10:
				self.gem_locations.append(self.blocked_cells[idx])

		for w in self.worker_threads:
			if w.job=="bot":
				w.exiting=True
				del self.worker_threads[self.worker_threads.index(w)]

		num_bots = 7
		bots = 0

		while bots<num_bots:
			new_bot = grid_worker(self)
			new_bot.job = "bot"
			bots+=1
			while True:
				x_start = random.randint(0,self.num_cols-1)
				y_start = random.randint(0,self.num_rows-1)
				if (x_start==0 and y_start==0) or (x_start==self.num_cols-1 and y_start==self.num_rows-1):
					continue
				break 
			new_bot.bot_start = [x_start,y_start]
			new_bot.start()
			self.worker_threads.append(new_bot)

	def init_ui(self):
		# initialize ui elements
		self.worker_threads = []
		self.gem_locations = None
		self.grid_line_color = [0,0,0]
		self.free_color = [46,139,87]#,255,255]
		self.occupied_color = [0,128,255]
		self.blocked_cell_color = [0,0,0]
		self.gem_color = [102,51,153]
		self.bullet_color = [255,0,0]
		self.bot_color = [255,0,0]
		self.last_direction = "right"
		self.bullet_direction = None
		self.current_location = None
		self.opponent_location = None
		self.opponent_color = [128,255,0]
		self.game_over = False
		self.init_cells()

		self.frame_updater = frame_manager(self)
		self.frame_updater.stop=False
		self.frame_updater.start()

	def paintEvent(self,e):
		qp = QPainter()
		qp.begin(self)
		self.drawWidget(qp)
		qp.end()

		if self.game_over: 
			self.user_health+=-1
			self.game_over = False
			self.end_game.emit()

	def drawWidget(self,qp):
		size = self.size()
		height = size.height()
		width = size.width()

		self.horizontal_step = int(round(width/self.num_cols))
		self.vertical_step = int(round(height/self.num_rows))

		grid_height = self.vertical_step*self.num_rows
		grid_width = self.horizontal_step*self.num_cols

		qp.setBrush(QColor(self.free_color[0],self.free_color[1],self.free_color[2]))
		qp.setPen(Qt.NoPen)

		for y in range(self.num_rows):
			for x in range(self.num_cols):
				cell_state = self.get_cell_state(x,y)

				if [x,y] in self.gem_locations:
					qp.setBrush(QColor(self.gem_color[0],self.gem_color[1],self.gem_color[2]))

				if cell_state==1:
					qp.setBrush(QColor(self.occupied_color[0],self.occupied_color[1],self.occupied_color[2]))
					self.current_location = [x,y]

				if [x,y] in self.blocked_cells:
					cell_health = self.blocked_cell_life[self.blocked_cells.index([x,y])]

					if cell_health>9:
						qp.setBrush(QColor(self.blocked_cell_color[0],self.blocked_cell_color[1],self.blocked_cell_color[2]))
					elif cell_health>5:
						qp.setBrush(QColor(130,130,130))
					elif cell_health>2:
						qp.setBrush(QColor(200,200,200))
					else:
						qp.setBrush(QColor(255,255,255))

				x_start = x*self.horizontal_step
				y_start = y*self.vertical_step
				qp.drawRect(x_start,y_start,self.horizontal_step,self.vertical_step)

				self.cells[y][x].render_coordinate = [x_start,y_start]

				if cell_state==1 or [x,y] in self.blocked_cells or [x,y] in self.gem_locations:
					qp.setBrush(QColor(self.free_color[0],self.free_color[1],self.free_color[2]))

		if [self.current_location[0],self.current_location[1]] in self.gem_locations:
			idx = self.gem_locations.index([self.current_location[0],self.current_location[1]])
			del self.gem_locations[idx]
			self.user_has_gem += 1
			sound_file = "resources/126422__cabeeno-rossley__level-up.wav"
			QSound(sound_file).play()

		if self.opponent_location!=None:
			x = self.opponent_location[0]
			y = self.opponent_location[1]
			x_start = x*self.horizontal_step
			y_start = y*self.vertical_step
			qp.setBrush(QColor(self.opponent_color[0],self.opponent_color[1],self.opponent_color[2]))
			qp.drawRect(x_start,y_start,self.horizontal_step,self.vertical_step)

		for t in self.worker_threads:
			if t.job=="bullet":
				try:
					render_loc = self.cells[t.bullet_loc[1]][t.bullet_loc[0]].render_coordinate
				except:
					continue

				if t.bullet_loc==None: continue 

				qp.setBrush(QColor(self.bullet_color[0],self.bullet_color[1],self.bullet_color[2]))

				move_m = 2
				x_spot = render_loc[0]
				y_spot = render_loc[1]
				offset = t.bullet_loc[2]
				full_offset = move_m*offset

				if t.bullet_direction == "right": qp.drawEllipse(x_spot+full_offset,y_spot+6,4,4)
				if t.bullet_direction == "left": qp.drawEllipse(x_spot-full_offset,y_spot+6,4,4)
				if t.bullet_direction == "up": qp.drawEllipse(x_spot+6,y_spot-full_offset,4,4)
				if t.bullet_direction == "down": qp.drawEllipse(x_spot+6,y_spot+full_offset,4,4)

				if t.bullet_direction == "up_left": qp.drawEllipse(x_spot-(full_offset),y_spot-(full_offset),4,4)
				if t.bullet_direction == "up_right": qp.drawEllipse(x_spot+(full_offset),y_spot-(full_offset),4,4)
				if t.bullet_direction == "down_left": qp.drawEllipse(x_spot-(full_offset),y_spot+(full_offset),4,4)
				if t.bullet_direction == "down_right": qp.drawEllipse(x_spot+(full_offset),y_spot+(full_offset),4,4)

				if self.current_location!=None:
					if t.bullet_loc[0]==self.current_location[0] and t.bullet_loc[1]==self.current_location[1] and t.player=="opponent":
						self.game_over = True 

				if [t.bullet_loc[0],t.bullet_loc[1]] in self.blocked_cells:
					t.exiting = True
					idx = self.blocked_cells.index([t.bullet_loc[0],t.bullet_loc[1]])
					self.blocked_cell_life[idx]+=-1
					if self.blocked_cell_life[idx]<=0:
						del self.blocked_cells[idx]
						del self.blocked_cell_life[idx]

			if t.job=="bot":
				try:
					render_loc = self.cells[t.bot_loc[1]][t.bot_loc[0]].render_coordinate
				except:
					continue

				qp.setBrush(QColor(self.bot_color[0],self.bot_color[1],self.bot_color[2]))
				move_m = 2

				if t.bot_dir == "right": qp.drawEllipse(render_loc[0]+(t.inc*move_m),render_loc[1]+6,4,4)
				if t.bot_dir == "left": qp.drawEllipse(render_loc[0]-(t.inc*move_m),render_loc[1]+6,4,4)
				if t.bot_dir == "up": qp.drawEllipse(render_loc[0]+6,render_loc[1]-(t.inc*move_m),4,4)
				if t.bot_dir == "down": qp.drawEllipse(render_loc[0]+6,render_loc[1]+(t.inc*move_m),4,4)

				if self.current_location[0]==t.bot_loc[0] and self.current_location[1]==t.bot_loc[1]:
					self.game_over = True

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

		if [x,y] in self.blocked_cells:
			return [cur_x,cur_y]

		self.cells[cur_y][cur_x].set_free()
		self.cells[y][x].set_occupied()
		self.current_location = [x,y]
		self.repaint()
		return [x,y]

	def clean_worker_threads(self):
		for t in self.worker_threads:
			if t.job==None: del self.worker_threads[self.worker_threads.index(t)]

	def get_opposite_direction(self,direction):
		if direction=="left": return "right"
		if direction=="right": return "left"
		if direction=="up": return "down"
		if direction=="down": return "up"
		return "none"

	def action(self,what="shoot"):
		if what=="shoot":
			bullet_start = self.get_cell_attrib(1) if self.current_location==None else self.current_location
			bullet_direction = self.last_direction

			t = grid_worker(self)
			t.job = "bullet"
			t.player = "me"
			t.bullet_direction = bullet_direction
			t.bullet_start = bullet_start
			t.bullet_loc = None
			t.num_cols = self.num_cols
			t.num_rows = self.num_rows
			self.worker_threads.append(t)
			t.start()

			if self.user_has_gem>0:
				t2 = grid_worker(self)
				t2.bullet_loc = None 
				t2.job = "bullet"
				t2.player = "me"
				t2.bullet_direction = self.get_opposite_direction(bullet_direction)
				t2.bullet_start = bullet_start
				t2.num_cols = self.num_cols
				t2.num_rows = self.num_rows
				t2.start()
				self.worker_threads.append(t2)

			if self.user_has_gem>1:
				if bullet_direction in ["left","right"]: perp_bullet_direction = "up"
				else: perp_bullet_direction = "left"
				t3 = grid_worker(self)
				t3.job = "bullet"
				t3.bullet_loc = None
				t3.player = "me"
				t3.bullet_direction = perp_bullet_direction
				t3.bullet_start = bullet_start
				t3.num_cols = self.num_cols
				t3.num_rows = self.num_rows
				t3.start()
				self.worker_threads.append(t3)

				t4 = grid_worker(self)
				t4.job = "bullet"
				t4.player = "me"
				t4.bullet_loc = None
				t4.bullet_direction = self.get_opposite_direction(perp_bullet_direction)
				t4.bullet_start = bullet_start
				t4.num_cols = self.num_cols
				t4.num_rows = self.num_rows
				t4.start()
				self.worker_threads.append(t4)

			if self.user_has_gem>2:
				dirs = ["up_right","up_left","down_right","down_left"]
				for d in dirs:
					temp = grid_worker(self)
					temp.job = "bullet"
					temp.player = "me"
					temp.bullet_direction = d 
					temp.bullet_loc = None
					temp.bullet_start = bullet_start
					temp.num_rows = self.num_rows 
					temp.num_cols = self.num_cols 
					temp.start()
					self.worker_threads.append(temp)

			self.clean_worker_threads()			

			if self.user_has_gem>2:
				return [None,t.bullet_start,None,"ALL"]
			if self.user_has_gem==1:
				return [t.bullet_direction,t.bullet_start,t2.bullet_direction,None]
			elif self.user_has_gem>1:
				return [None,t.bullet_start,None,None]
			else:
				return [t.bullet_direction,t.bullet_start,None,None]

	def opponent_shoot(self,bullet_direction,start_x,start_y):
		t = grid_worker(self)
		t.job = "bullet"
		t.player = "opponent"
		t.bullet_loc = None 
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
		if location_descriptor=="standard":
			for y in range(self.num_rows):
				for x in range(self.num_cols):
					if self.cells[y][x].state()==1:
						self.cells[y][x].set_free()
			self.current_location = [0,0]
			self.cells[0][0].set_occupied()
			self.repaint()
			return [0,0]

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
		#print("Sending: ",self.message)
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
			#print("Received: ",data)
			self.emit(SIGNAL("got_message(QString)"), data)

		UDPSock.close()

class ip_window(QWidget):
	got_ip = pyqtSignal()

	def __init__(self,parent=None):
		super(ip_window,self).__init__()
		self.parent = parent
		self.connect(self,SIGNAL("got_ip()"),self.parent.got_ip)
		self.init_vars()
		self.init_ui()

	def init_vars(self):
		self.full_ip = None 
		self.ip1 = "192"
		self.ip2 = "168"
		self.ip3 = "1"
		self.ip4 = ""

	def init_ui(self):
		self.setWindowTitle("IP Address Input")
		self.layout = QVBoxLayout(self)
		self.top_label = QLabel("Enter IP Address of other user:")
		self.layout.addWidget(self.top_label)

		ip_row = QHBoxLayout()

		self.ip1_input = QLineEdit(self.ip1)
		self.ip2_input = QLineEdit(self.ip2)
		self.ip3_input = QLineEdit(self.ip3)
		self.ip4_input = QLineEdit(self.ip4)

		ip_row.addSpacing(15)
		ip_row.addWidget(self.ip1_input)
		ip_row.addWidget(QLabel("."))
		ip_row.addWidget(self.ip2_input)
		ip_row.addWidget(QLabel("."))
		ip_row.addWidget(self.ip3_input)
		ip_row.addWidget(QLabel("."))
		ip_row.addWidget(self.ip4_input)
		ip_row.addSpacing(15)

		ok_cancel_row = QHBoxLayout()
		ok_button = QPushButton("Ok")
		cancel_button = QPushButton("Cancel")

		ok_cancel_row.addStretch()
		ok_cancel_row.addWidget(cancel_button)
		ok_cancel_row.addWidget(ok_button)
		ok_cancel_row.addStretch()

		ok_button.clicked.connect(self.ok_selected)
		cancel_button.clicked.connect(self.cancel_selected)

		self.layout.addLayout(ip_row)
		self.layout.addLayout(ok_cancel_row)
		self.layout.addSpacing(20)

		self.setFixedWidth(350)
		self.setFixedHeight(150)

	def keyPressEvent(self,e):
		if e.key() in [Qt.Key_Return,Qt.Key_Enter]:
			self.ok_selected()

	def ok_selected(self):
		self.ip1 = str(self.ip1_input.text())
		self.ip2 = str(self.ip2_input.text())
		self.ip3 = str(self.ip3_input.text())
		self.ip4 = str(self.ip4_input.text())
		self.full_ip = self.ip1+"."+self.ip2+"."+self.ip3+"."+self.ip4
		self.got_ip.emit()

	def cancel_selected(self):
		self.full_ip = None
		self.got_ip.emit()

	def closeEvent(self,e):
		self.cancel_selected()

class main_window(QWidget):

	def __init__(self,parent=None):
		super(main_window,self).__init__()
		self.opponent_ip = None
		self.ip_dialog_window = ip_window(self)
		self.num_cols = 35
		self.num_rows = 25
		self.set_connected(False)
		self.init_ui()
		self.start_character()

	def set_health(self,health):
		cur_ip = str(gethostbyname(gethostname()))
		if self.connected:
			self.setWindowTitle("Me: ("+cur_ip+") - Opponent: ("+self.opponent_ip+") - Health: "+str(health)+"/10")
		else:
			self.setWindowTitle("Me: ("+cur_ip+") - Not Connected - Health: "+str(health)+"/10")

	def set_connected(self,connected):
		self.connected = connected
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
		self.grid = eight_neighbor_grid(num_cols=self.num_cols,num_rows=self.num_rows,parent=self)

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
		connection_menu.addAction("Connect",self.connect,QKeySequence("Ctrl+C"))
		connection_menu.addAction("Disconnect",self.disconnect)

		self.setFixedWidth(self.min_width)
		self.setFixedHeight(self.min_height)
		self.show()

	def receive_update(self,update):
		if len(update)==0: return 

		items = update.split("|")

		if items[0]=="ready":
			self.grid.setEnabled(True)
			self.grid.opponent_move(0,0)

		if items[0]=="restart":
			self.grid.setEnabled(False)
			x,y = self.grid.set_current_location("standard")
			
			sender = sender_thread()
			sender.host = self.opponent_ip
			sender.message = "move|x:"+str(x)+"|y:"+str(y)
			sender.is_done=False
			sender.start()
			self.sender_threads.append(sender)

			sender2 = sender_thread()
			sender2.host = self.opponent_ip
			sender2.message = "ready| "
			sender2.is_done = False
			sender2.start()
			self.sender_threads.append(sender2)
			self.grid.setEnabled(True)

			self.grid.init_blocked_cells()
			self.grid.opponent_move(self.num_cols-1,self.num_rows-1)
			return

		if items[0]=="new":
			self.connect(opp_ip=items[1])
			x,y = self.grid.set_current_location("opposite")
			self.grid.opponent_location = [0,0]
			sender = sender_thread()
			sender.host = self.opponent_ip
			sender.message = "move|x:"+str(x)+"|y:"+str(y)
			sender.is_done=False
			sender.start()
			self.sender_threads.append(sender)
			return

		if items[0]=="shoot":
			bullet_direction = items[1]
			x = items[2].split(":")[1]
			y = items[3].split(":")[1]
			self.grid.opponent_shoot(bullet_direction=bullet_direction,start_x=x,start_y=y)
			return

		if items[0]=="shoot2":
			bullet_direction = items[1]
			bullet_direction2 = items[-1]
			x = items[2].split(":")[1]
			y = items[3].split(":")[1]
			self.grid.opponent_shoot(bullet_direction=bullet_direction,start_x=x,start_y=y)
			self.grid.opponent_shoot(bullet_direction=bullet_direction2,start_x=x,start_y=y)
			return

		if items[0]=="shoot4":
			x = items[1].split(":")[1]
			y = items[2].split(":")[1]
			self.grid.opponent_shoot(bullet_direction="up",start_x=x,start_y=y)
			self.grid.opponent_shoot(bullet_direction="down",start_x=x,start_y=y)
			self.grid.opponent_shoot(bullet_direction="left",start_x=x,start_y=y)
			self.grid.opponent_shoot(bullet_direction="right",start_x=x,start_y=y)

		if items[0]=="shootall":
			x = items[1].split(":")[1]
			y = items[2].split(":")[1]
			dirs = ["up","down","left","right","up_right","down_right","up_left","down_left"]
			for d in dirs:
				self.grid.opponent_shoot(bullet_direction=d,start_x=x,start_y=y)

		if items[0]=="move":
			x = items[1].split(":")[1]
			y = items[2].split(":")[1]
			self.grid.opponent_move(x,y)
			return

	def got_ip(self):
		self.opponent_ip = self.ip_dialog_window.full_ip
		self.ip_dialog_window.hide()
		self.show()
		if self.opponent_ip!=None:
			self.grid.set_current_location("standard")
			sender = sender_thread()
			sender.host = self.opponent_ip
			sender.message = "new|"+str(gethostbyname(gethostname()))
			sender.is_done = False 
			sender.start()
			self.sender_threads.append(sender)
			self.set_connected(True)

	def connect(self,opp_ip=None):
		if opp_ip==None:
			'''
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
			'''
			self.hide()
			self.ip_dialog_window.show()
			return
		else:
			resp = opp_ip

		self.opponent_ip = resp
		self.set_connected(True)

		if opp_ip==None:
			self.grid.set_current_location("standard")
			sender = sender_thread()
			sender.host = self.opponent_ip
			sender.message = "new|"+str(gethostbyname(gethostname()))
			sender.is_done = False 
			sender.start()
			self.sender_threads.append(sender)

	def disconnect(self):
		self.opponent_ip = None

	def quit(self):
		self.grid.frame_updater.stop=True
		sys.exit(1)

	def closeEvent(self,e):
		self.quit()

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
				bullet_direction, bullet_start, o_bullet_direction, extra = self.grid.action(action)

				if extra!=None:
					if extra=="ALL":
						message = "shootall|x:"+str(bullet_start[0])+"|y:"+str(bullet_start[1])
				elif bullet_direction==None and o_bullet_direction==None:
					message = "shoot4|x:"+str(bullet_start[0])+"|y:"+str(bullet_start[1])
				elif o_bullet_direction==None:
					message = "shoot|"+bullet_direction+"|"+"x:"+str(bullet_start[0])+"|y:"+str(bullet_start[1])
				else:
					message = "shoot2|"+bullet_direction+"|"+"x:"+str(bullet_start[0])+"|y:"+str(bullet_start[1])+"|"+o_bullet_direction

				shoot_sound = "resources/126423__cabeeno-rossley__shoot-laser.wav"
				QSound.play(shoot_sound)

			else: 
				new_location = self.grid.move(action)
				message = "move|"+"x:"+str(new_location[0])+"|y:"+str(new_location[1])

			if self.opponent_ip!=None:
				sender = sender_thread()
				sender.host = self.opponent_ip
				sender.message = message
				sender.is_done=False
				sender.start()
				self.sender_threads.append(sender)
				self.clean_sender_threads()

	def clean_sender_threads(self):
		for s in self.sender_threads:
			if s.is_done:
				del self.sender_threads[self.sender_threads.index(s)]

	def game_over(self):
		user_health = self.grid.user_health
		if user_health<=0:
			self.grid.set_current_location("opposite")
			pyqt_app.processEvents()
			if self.opponent_ip!=None:
				self.grid.opponent_move(0,0)
				sender = sender_thread()
				sender.host = self.opponent_ip
				sender.message = "restart| "
				sender.is_done = False 
				sender.start()
				self.sender_threads.append(sender)
			self.grid.init_blocked_cells()
			self.grid.setEnabled(False)
			self.grid.repaint()
		else:
			self.set_health(user_health)

def main():
	global pyqt_app
	pyqt_app = QApplication(sys.argv)
	_ = main_window()
	sys.exit(pyqt_app.exec_())

if __name__ == '__main__':
	main()