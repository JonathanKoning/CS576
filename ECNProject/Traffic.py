import time
from numpy import random
from multiprocessing import Process, Value, Manager
import matplotlib.pyplot as plt

class server:
	def __init__(self, ping):
		self.ping = ping 	#number of packets to process per second
		self.rate = 1/ping
		self.threshold = threshold.value
		self.maxlength = maxlength.value
	
	def listen(self):
		#Continue listening while the client is still transmitting or the server is still processesing
		while (clientqueue.empty() == False or serverqueue.empty() == False):
			#While server is still processing
			while (serverqueue.empty() == False):
				#If the queue size is over the threshold, send the ECN
				if(serverqueue.qsize() >= self.threshold):
					throttle1.value = 1
				else:
					throttle1.value = 0
				#Get packet from the server queue
				packet = serverqueue.get_nowait()
				# print("Processed Packet: ", packet)
				# print("\n")
				time.sleep(random.poisson(lam=self.rate))
				# time.sleep(self.rate)
			

class client:
	def __init__(self, ping, throttle, name, numPackets):
		self.ping = ping 	#number of packets to send per second
		self.rate = 1/ping	#Sleep time between each packet	
		self.throttle = throttle
		self.name = name
		self.numPackets = numPackets
		self.packets_dropped = 0

	def transmit(self):
		print("Transmission started")

		#Continue transmitting until all packets have been sent
		while clientqueue.empty() != True:
			#If the throttle value is set to 0, send at full speed
			if(self.throttle.value == 0):
				#If the server is at maximum capacity, do not send packet and count as dropped packet
				if(serverqueue.qsize() >= maxlength.value):
					# print("Packet Dropped!")
					self.packets_dropped += 1
				else:
					#get packet from client queue
					packet = clientqueue.get_nowait()
					#place packet into the server queue
					serverqueue.put(packet)
					# print("Transmitting Packet: ", packet)
				# print("Throttle value: ", self.throttle.value)
				
				#Sleep before sending next packet
				time.sleep(random.poisson(lam=self.rate))
				# time.sleep(self.rate)

			#If throttle value is set to 1, send at half the rate
			else:
				if(serverqueue.qsize() >= maxlength.value):
					# print("Packet Dropped!")
					self.packets_dropped += 1
				else:
					packet = clientqueue.get_nowait()
					serverqueue.put(packet)
					# print("Transmitting Packet: ", packet)
				# print("Throttle value: ", self.throttle.value)
				time.sleep(random.poisson(lam=(self.rate*2)))
				# time.sleep(self.rate*2)
		
		dropped1.value = self.packets_dropped
		# print("Total packets dropped: ", self.packets_dropped)
	



if __name__ == "__main__":
	print("Network Traffic simulator\n")
	numTrials = 5
	packetDroparr = []
	manager = Manager()
	numPackets = 200

	#Set up client specific values
	throttle1 = manager.Value('i', 0) 	#Shared throttle value
	dropped1 = manager.Value('i', 0)	#Shared number of dropped packets
	clientqueue = manager.Queue()
	# for i in range(numPackets):
	# 	clientqueue.put(i)

	#create client
	# c1 = client(10, throttle1, "C1", numPackets)


	#Set up server specific values
	serverqueue = manager.Queue()
	threshold = manager.Value('i', 14)
	maxlength = manager.Value('i', 30)

	#create server
	# s1 = server(4)

	# server1 = Process(target=s1.listen)
	# client1 = Process(target=c1.transmit)

	for i in range(numTrials):
		dropped1 = manager.Value('i', 0)

		#create client
		c1 = client(20, throttle1, "C1", numPackets)

		#create server
		s1 = server(8)

		for j in range(numPackets):
			clientqueue.put(i)

		print("client queue size: ", clientqueue.qsize())
		
		#Start the clients and server	
		server1 = Process(target=s1.listen)
		server1.start()
		client1 = Process(target=c1.transmit)
		client1.start()
	
		while True:
			if(serverqueue.empty() and clientqueue.empty()):
				break
	
		#Join the threads back into a single process
		client1.join()
		server1.join()
		packetDroparr.append(dropped1.value)
		print("Total packets dropped: ", dropped1.value)
		print("")

	print(packetDroparr)
	
	