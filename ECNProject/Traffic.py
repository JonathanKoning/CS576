import time
from numpy import random
from multiprocessing import Process, Value, Manager
import matplotlib.pyplot as plt
import os
from math import sqrt
import sys

class ECNserver:
	def __init__(self, ping, threshold):
		self.ping = ping 	#number of packets to process per second
		self.rate = 1/ping
		self.threshold = threshold
	
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
		print("Server is done processing")
			


class ECNclient:
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







class QAECNserver:
	def __init__(self, ping):
		self.ping = ping 	#number of packets to process per second
		self.rate = 1/ping
		# self.threshold = threshold
	def listen(self, throttle, clientqueuearr, serverqueuearr, thresholdarr, maxlengtharr, numClients):
		print("server is listening")
		#Continue listening while the client is still transmitting or the server is still processesing
		random.seed(os.getpid())
		while (all(clientqueue.empty() for clientqueue in clientqueuearr) != True or all(serverqueue.empty() for serverqueue in serverqueuearr) != True):
			# print("Client or server queues not empty")
			#While server is still processing
			while (all(serverqueue.empty() for serverqueue in serverqueuearr) != True):
				
				# print("Server queues not empty")
				for i in range(numClients):
					# kj = (serverqueuearr[i].qsize()/qjsum) * kport
					# kj = thresholdarr[i].value
					if(serverqueuearr[i].empty() != True):
						kport = sum(threshold.value for threshold in thresholdarr)
						qjsum = sum(qj.qsize() for qj in serverqueuearr)
						qj = serverqueuearr[i].qsize()
						kj = thresholdarr[i].value

						if((qj > kj) and (qjsum > kport)):
							kj = 14
							thresholdarr[i].value = kj
						elif((qj < kj) and (qjsum < kport)):
							kj = 14
							thresholdarr[i].value = kj
						elif((qj >= kj) and (qjsum <= kport)):
							kj = (qj/qjsum) * kport
							thresholdarr[i].value = kj
						
						#If the queue size is over the threshold, send the ECN
						if(serverqueuearr[i].qsize() >= thresholdarr[i].value):
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
			


class QAECNclient:
	def __init__(self, ping, throttle, numPackets):
		self.ping = ping 	#number of packets to send per second
		self.rate = 1/ping	#Sleep time between each packet	
		self.throttle = throttle
		# self.name = name
		self.numPackets = numPackets
		self.packets_dropped = 0

	def transmit(self, ID, maxlengtharr, clientqueue, serverqueuearr, dropped):
		print("Transmission started")
		pps = self.ping # Packets Per Second
		#Continue transmitting until all packets have been sent
		pid = os.getpid()
		random.seed(pid)
		while clientqueue.empty() != True:
			#If the server is at maximum capacity, do not send packet and count as dropped packet
			if(serverqueuearr[ID].qsize() >= maxlengtharr[ID].value):
					self.packets_dropped += 1
			else:
				#get packet from client queue
				packet = clientqueue.get_nowait()
				#place packet into the server queue
				# print(packet)
				serverqueuearr[ID].put(packet)

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



def ECN(numPackets, numClients, clientspeed, serverspeed):
	print("ECN")
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
		clientarr.append(ECNclient(clientspeed, throttlearr[i], numPackets))
		serverqueuearr.append(manager.Queue())
	
	
	threshold = manager.Value('i', 14)
	maxlength = manager.Value('i', 30)

	
	#create server
	s1 = ECNserver(serverspeed, threshold)

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



def QAECN(numPackets, numClients, clientspeed, serverspeed):
	print("QAECN")
	manager = Manager()
	#Set up client specific values
	clientqueuearr = []
	throttlearr = []
	droppedarr = []
	clientarr = []
	serverqueuearr = []
	thresholdarr = []
	maxlengtharr = []
	for i in range(numClients):
		clientqueuearr.append(manager.Queue())
		for j in range(numPackets):
			clientqueuearr[i].put(j)
		
		throttlearr.append(manager.Value('i', 0))
		droppedarr.append(manager.Value('i', 0))
		clientarr.append(QAECNclient(clientspeed, throttlearr[i], numPackets))
		serverqueuearr.append(manager.Queue())
		thresholdarr.append(manager.Value('i', 14))
		maxlengtharr.append(manager.Value('i', 30))

	
	#create server
	s1 = QAECNserver(serverspeed)

	#Create processes
	server1 = Process(target=s1.listen, args=(throttlearr, clientqueuearr, serverqueuearr, thresholdarr, maxlengtharr, numClients))
	cProcessArr = []
	for i in range(numClients):
		cProcessArr.append(Process(target=clientarr[i].transmit, args=(i, maxlengtharr, clientqueuearr[i], serverqueuearr, droppedarr[i])))
	
	#Start Server and Clients
	server1.start()
	startTime = time.time()
	for i in range(numClients):
		cProcessArr[i].start()
	server1.join()
	for i in range(numClients):
		cProcessArr[i].join()
	
	endTime = time.time()

	#Count total number of dropped packets
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
	numTrials = 15
	ECNpacketDroparr = []
	ECNpktDrop = []
	ecnError = []
	ECNpktDrpPerarr = []
	ECNpktDrpPer = []
	ECNpktPerErr = []
	ECNthroughputarr = []
	ECNthruput = []
	ECNthruputError = []


	QAECNpacketDroparr = []
	QAECNpktDrop = []
	QAecnError = []
	QAECNpktDrpPerarr = []
	QAECNpktDrpPer = []
	QAECNpktPerErr = []
	QAECNthroughputarr = []
	QAECNthruput = []
	QAECNthruputError = []

	simulation = []

	clientspeed = 20
	numPackets = 200
	numClients = 0

	#Get number of clients from user input
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

	#Set server speed proportional to number of clients
	serverspeed = 0.8 *(numClients*numPackets)

	print("Simulating ", numTrials, " runs")
	for i in range(numTrials):
		print("Run ", i)
		#Run ECN
		drpPkt, throughput = ECN(numPackets, numClients, clientspeed, serverspeed)

		#Packet loss info
		ECNpacketDroparr.append(drpPkt)		
		ECNpktDropbar = sum(ECNpacketDroparr)/(i+1)
		ECNpktDrop.append(ECNpktDropbar)
		ECNavgPktDrop = sum(ECNpktDrop)/(i+1)
		ecnError.append(1.64 * Sn(ECNpktDrop, ECNavgPktDrop, i+1)/sqrt(i+1))

		#Percent Package loss info
		ECNpktDrpPerarr.append((drpPkt/(numPackets*numClients))*100)
		ECNpktDrpPerbar = sum(ECNpktDrpPerarr)/(i+1)
		ECNpktDrpPer.append(ECNpktDrpPerbar)
		ECNavgPktDropPer = sum(ECNpktDrpPer)/(i+1)
		ECNpktPerErr.append(1.64 * Sn(ECNpktDrpPer, ECNavgPktDropPer, i+1)/sqrt(i+1))

		#Througput info
		ECNthroughputarr.append(throughput)		
		ECNthroughputbar = sum(ECNthroughputarr)/(i+1)
		ECNthruput.append(ECNthroughputbar)
		ECNavgthruput = sum(ECNthruput)/(i+1)
		ECNthruputError.append(1.64 * Sn(ECNthruput, ECNavgthruput, i+1)/sqrt(i+1))



		#Run QAECN
		drpPkt, throughput = QAECN(numPackets, numClients, clientspeed, serverspeed)

		#Packet loss info
		QAECNpacketDroparr.append(drpPkt)		
		QAECNpktDropbar = sum(QAECNpacketDroparr)/(i+1)
		QAECNpktDrop.append(QAECNpktDropbar)
		QAECNavgPktDrop = sum(QAECNpktDrop)/(i+1)
		QAecnError.append(1.64 * Sn(QAECNpktDrop, QAECNavgPktDrop, i+1)/sqrt(i+1))

		#Percent Package loss info
		QAECNpktDrpPerarr.append((drpPkt/(numPackets*numClients))*100)
		QAECNpktDrpPerbar = sum(QAECNpktDrpPerarr)/(i+1)
		QAECNpktDrpPer.append(QAECNpktDrpPerbar)
		QAECNavgPktDropPer = sum(QAECNpktDrpPer)/(i+1)
		QAECNpktPerErr.append(1.64 * Sn(QAECNpktDrpPer, QAECNavgPktDropPer, i+1)/sqrt(i+1))

		#Througput info
		QAECNthroughputarr.append(throughput)		
		QAECNthroughputbar = sum(QAECNthroughputarr)/(i+1)
		QAECNthruput.append(QAECNthroughputbar)
		QAECNavgthruput = sum(QAECNthruput)/(i+1)
		QAECNthruputError.append(1.64 * Sn(QAECNthruput, QAECNavgthruput, i+1)/sqrt(i+1))

		simulation.append(i)

	# print(packetDroparr)
	# print(pktDrpPerarr)
	
	#Make Graphs
	start = 0
	end = numPackets
	plt.title("90% Confidence")
	plt.xlabel("Simulations")
	plt.ylabel("Dropped Packets")
	plt.errorbar(simulation[start:end], ECNpktDrop[start:end], yerr = ecnError[start:end], color='b', label="ECN", capsize=10)
	plt.legend()
	
	plt.title("90% Confidence")
	plt.xlabel("Simulations")
	plt.ylabel("Dropped Packets")
	plt.errorbar(simulation[start:end], QAECNpktDrop[start:end], yerr = QAecnError[start:end], color='g', label="QAECN", capsize=10)
	plt.legend()

	plt.show()



	plt.title("90% Confidence")
	plt.xlabel("n")
	plt.ylabel("Percent Packet Loss")
	plt.errorbar(simulation[start:end], ECNpktDrpPer[start:end], yerr = ECNpktPerErr[start:end], color='b', label="ECN", capsize=10)
	plt.legend()

	plt.title("90% Confidence")
	plt.xlabel("Simulations")
	plt.ylabel("Percent Packet Loss")
	plt.errorbar(simulation[start:end], QAECNpktDrpPer[start:end], yerr = QAECNpktPerErr[start:end], color='g', label="QAECN", capsize=10)
	plt.legend()

	plt.show()



	plt.title("90% Confidence")
	plt.xlabel("Simulations")
	plt.ylabel("Throughput (Packets/Second)")
	plt.errorbar(simulation[start:end], ECNthruput[start:end], yerr = ECNthruputError[start:end], color='b', label="ECN", capsize=10)
	plt.legend()

	plt.title("90% Confidence")
	plt.xlabel("Simulations")
	plt.ylabel("Throughput (Packets/Second)")
	plt.errorbar(simulation[start:end], QAECNthruput[start:end], yerr = QAECNthruputError[start:end], color='g', label="QAECN", capsize=10)
	plt.legend()
	
	plt.show()