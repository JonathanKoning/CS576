import time
from numpy import random
from multiprocessing import Process, Value, Manager
import matplotlib.pyplot as plt
import os
from math import sqrt
import sys

class server:
	def __init__(self, ping, threshold):
		self.ping = ping 	#number of packets to process per second
		self.rate = 1/ping
		self.threshold = threshold
		# self.maxlength = maxlength.value
	
	def listen(self, throttle, clientqueuearr, serverqueuearr, numClients):
		print("server is listening")
		#Continue listening while the client is still transmitting or the server is still processesing
		random.seed(os.getpid())
		while (all(clientqueue.empty() for clientqueue in clientqueuearr) != True or all(serverqueue.empty() for serverqueue in serverqueuearr) != True):
			# print("Client or server queues not empty")
			#While server is still processing
			while (all(serverqueue.empty() for serverqueue in serverqueuearr) != True):
				# print("Server queues not empty")
				for i in range(numClients):
					if(serverqueuearr[i].empty() != True):
						#If the queue size is over the threshold, send the ECN
						if(serverqueuearr[i].qsize() >= self.threshold.value):
							throttle[i].value = 1
						else:
							throttle[i].value = 0
						#Get packet from the server queue
						packet = serverqueuearr[i].get_nowait()
						# print("Processed Packet: ", packet)
						# print("\n")
						time.sleep(random.poisson(lam=self.rate))
						# time.sleep(self.rate)
		print("Server is done processing")
			


class client:
	def __init__(self, ping, throttle, numPackets):
		self.ping = ping 	#number of packets to send per second
		self.rate = 1/ping	#Sleep time between each packet	
		self.throttle = throttle
		# self.name = name
		self.numPackets = numPackets
		self.packets_dropped = 0

	def transmit(self, maxlength, clientqueue, serverqueue, dropped):
		print("Transmission started")
		pps = self.ping # Packets Per Second
		#Continue transmitting until all packets have been sent
		pid = os.getpid()
		random.seed(pid)
		while clientqueue.empty() != True:
			#If the server is at maximum capacity, do not send packet and count as dropped packet
			if(serverqueue.qsize() >= maxlength.value):
					self.packets_dropped += 1
			else:
				#get packet from client queue
				packet = clientqueue.get_nowait()
				#place packet into the server queue
				# print(packet)
				serverqueue.put(packet)

			#If the throttle value is set to 0, continue with slow start algorithm
			if(self.throttle.value == 0):	
				#Sleep before sending next packet
				# print("PPS: ", pps)
				time.sleep(random.poisson(lam=self.rate))
				pps = min(pps*2, self.ping)
				self.rate = 1/pps

			#If throttle value is set to 1, send at half the rate
			else:
				# print("PID: ", pid, " PPS: ", pps)
				pps = max(pps/2, 0.0005)
				self.rate = 1/pps
				time.sleep(random.poisson(lam=self.rate))

		# print("PID: ", pid, " Final PPS: ", pps)
		dropped.value = self.packets_dropped



def Sn(x, Xbar, n):
	if(n == 1):
		return 0
	s = 0
	for i in range(n):
		s += (x[i]-Xbar) * (x[i]-Xbar)
	s = (1/(n-1)) * s
	s = sqrt(s)
	return s



def Traffic(numPackets, numClients):
	manager = Manager()
	#Set up client specific values
	clientqueuearr = []
	throttlearr = []
	droppedarr = []
	clientarr = []
	serverqueuearr = []
	for i in range(numClients):
		clientqueuearr.append(manager.Queue())
		for j in range(numPackets):
			clientqueuearr[i].put(j)
		
		throttlearr.append(manager.Value('i', 0))
		droppedarr.append(manager.Value('i', 0))
		clientarr.append(client(20, throttlearr[i], numPackets))
		serverqueuearr.append(manager.Queue())

	# throttle1 = manager.Value('i', 0) 	#Shared throttle value
	# throttle2 = manager.Value('i', 0)
	# dropped1 = manager.Value('i', 0)	#Shared number of dropped packets
	# clientqueue1 = manager.Queue()
	# clientqueue2 = manager.Queue()
	
	# clientqueuearr = [clientqueue1, clientqueue2]
	# throttlearr = [throttle1, throttle2]


	# for i in range(numPackets):
	# 	clientqueue1.put(i)
	# 	clientqueue2.put(i)
	
	

	


	#Set up server specific values
	# serverqueue1 = manager.Queue()
	# serverqueue2 = manager.Queue()

	# serverqueuearr = []
	# serverqueuearr.append(serverqueue1)
	# serverqueuearr.append(serverqueue2)
	
	
	threshold = manager.Value('i', 14)
	maxlength = manager.Value('i', 30)

	#create server
	s1 = server(32, threshold)

	#Create processes
	server1 = Process(target=s1.listen, args=(throttlearr, clientqueuearr, serverqueuearr, numClients))
	cProcessArr = []
	for i in range(numClients):
		cProcessArr.append(Process(target=clientarr[i].transmit, args=(maxlength, clientqueuearr[i], serverqueuearr[i], droppedarr[i])))
	server1.start()
	startTime = time.time()
	for i in range(numClients):
		cProcessArr[i].start()
	for i in range(numClients):
		cProcessArr[i].join()
	
	server1.join()

	endTime = time.time()

	totalPcktsDropped = 0
	for i in range(numClients):
		totalPcktsDropped += droppedarr[i].value

	throughput = (numPackets*numClients)/(endTime-startTime)
	print("Total packets dropped: ", totalPcktsDropped)
	print("Time elapsed: ", endTime-startTime)
	print("Throughput: ", throughput, "Per second")
	print("")

	return totalPcktsDropped, throughput

if __name__ == "__main__":
	print("Network Traffic simulator\n")
	numTrials = 10
	packetDroparr = []
	pktDrop = []
	ecnError = []
	pktDrpPerarr = []
	pktDrpPer = []
	pktPerErr = []
	simulation = []
	throughputarr = []
	thruput = []
	thruputError = []
	# manager = Manager()
	numPackets = 200
	numClients = 0
	if(len(sys.argv) == 1):
		numClients = input("Enter number of clients: ")

		while numClients.isdigit() == False:
			print("Number of clients must be a positive integer")
			print("You entered type: ", type(numClients))
			numClients = input("Enter number of clients: ")
	else:
		numClients = sys.argv[1]
		while numClients.isdigit() == False:
			print("Number of clients must be a positive integer")
			print("You entered type: ", type(numClients))
			numClients = input("Enter number of clients: ")

	numClients = int(numClients)

	print("Simulating ", numTrials, " runs")
	for i in range(numTrials):
		print("Run ", i)
		drpPkt, throughput = Traffic(numPackets, numClients)

		#Packet loss info
		packetDroparr.append(drpPkt)		
		pktDropbar = sum(packetDroparr)/(i+1)
		pktDrop.append(pktDropbar)
		avgPktDrop = sum(pktDrop)/(i+1)
		ecnError.append(1.64 * Sn(pktDrop, avgPktDrop, i+1)/sqrt(i+1))

		#Percent Package loss info
		pktDrpPerarr.append((drpPkt/(numPackets*numClients))*100)
		pktDrpPerbar = sum(pktDrpPerarr)/(i+1)
		pktDrpPer.append(pktDrpPerbar)
		avgPktDropPer = sum(pktDrpPer)/(i+1)
		pktPerErr.append(1.64 * Sn(pktDrpPer, avgPktDropPer, i+1)/sqrt(i+1))

		#Througput info
		throughputarr.append(throughput)		
		throughputbar = sum(throughputarr)/(i+1)
		thruput.append(throughputbar)
		avgthruput = sum(thruput)/(i+1)
		thruputError.append(1.64 * Sn(thruput, avgthruput, i+1)/sqrt(i+1))

		simulation.append(i)

	print(packetDroparr)
	print(pktDrpPerarr)
	
	#Make Graphs
	start = 0
	end = numPackets
	plt.title("90% Confidence")
	plt.xlabel("n")
	plt.ylabel("Dropped Packets")
	plt.errorbar(simulation[start:end], pktDrop[start:end], yerr = ecnError[start:end], color='b', label="Packet loss", capsize=10)
	plt.legend()

	plt.title("90% Confidence")
	plt.xlabel("n")
	plt.ylabel("Dropped Packets")
	plt.errorbar(simulation[start:end], pktDrpPer[start:end], yerr = pktPerErr[start:end], color='r', label="Percent Packet loss", capsize=10)
	plt.legend()

	plt.title("90% Confidence")
	plt.xlabel("n")
	plt.ylabel("Dropped Packets")
	plt.errorbar(simulation[start:end], thruput[start:end], yerr = thruputError[start:end], color='g', label="Throughput (pkts/sec)", capsize=10)
	plt.legend()
	
	plt.show()