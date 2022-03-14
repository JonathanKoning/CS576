import time
from numpy import random
from multiprocessing import Process, Value, Manager
import matplotlib.pyplot as plt
import os
from math import sqrt
class server:
	def __init__(self, ping, threshold):
		self.ping = ping 	#number of packets to process per second
		self.rate = 1/ping
		self.threshold = threshold
		# self.maxlength = maxlength.value
	
	def listen(self, throttle1, clientqueue, serverqueue):
		#Continue listening while the client is still transmitting or the server is still processesing
		random.seed(os.getpid())
		while (clientqueue.empty() == False or serverqueue.empty() == False):
			#While server is still processing
			while (serverqueue.empty() == False):
				#If the queue size is over the threshold, send the ECN
				if(serverqueue.qsize() >= self.threshold.value):
					throttle1.value = 1
				else:
					throttle1.value = 0
				#Get packet from the server queue
				packet = serverqueue.get_nowait()
				# print("Processed Packet: ", packet)
				# print("\n")
				time.sleep(random.poisson(lam=self.rate))
				# time.sleep(self.rate)
		print("Server is done processing")
			

class client:
	def __init__(self, ping, throttle, name, numPackets):
		self.ping = ping 	#number of packets to send per second
		self.rate = 1/ping	#Sleep time between each packet	
		self.throttle = throttle
		self.name = name
		self.numPackets = numPackets
		self.packets_dropped = 0

	def transmit(self, maxlength, clientqueue, serverqueue, dropped1):
		print("Transmission started")
		pps = self.ping # Packets Per Second
		#Continue transmitting until all packets have been sent
		random.seed(os.getpid())
		while clientqueue.empty() != True:
			#If the server is at maximum capacity, do not send packet and count as dropped packet
			if(serverqueue.qsize() >= maxlength.value):
					self.packets_dropped += 1
			else:
				#get packet from client queue
				packet = clientqueue.get_nowait()
				#place packet into the server queue
				serverqueue.put(packet)

			#If the throttle value is set to 0, continue with slow start algorithm
			if(self.throttle.value == 0):	
				#Sleep before sending next packet
				time.sleep(random.poisson(lam=self.rate))
				pps = min(pps*2, self.ping)
				self.rate = 1/pps

			#If throttle value is set to 1, send at half the rate
			else:
				pps = max(pps/2, 0.0005)
				self.rate = 1/pps
				time.sleep(random.poisson(lam=self.rate))

		print("PPS: ", pps)
		dropped1.value = self.packets_dropped
	
def Sn(x, Xbar, n):
	if(n == 1):
		return 0
	s = 0
	for i in range(n):
		s += (x[i]-Xbar) * (x[i]-Xbar)
	s = (1/(n-1)) * s
	s = sqrt(s)
	return s

def Traffic(numPackets):
	manager = Manager()
	#Set up client specific values
	throttle1 = manager.Value('i', 0) 	#Shared throttle value
	dropped1 = manager.Value('i', 0)	#Shared number of dropped packets
	clientqueue = manager.Queue()
	for i in range(numPackets):
		clientqueue.put(i)
	
	#create client
	c1 = client(20, throttle1, "C1", numPackets)


	#Set up server specific values
	serverqueue = manager.Queue()
	threshold = manager.Value('i', 14)
	maxlength = manager.Value('i', 30)

	#create server
	s1 = server(16, threshold)

	server1 = Process(target=s1.listen, args=(throttle1, clientqueue, serverqueue))
	server1.start()
	startTime = time.time()
	client1 = Process(target=c1.transmit, args=(maxlength, clientqueue, serverqueue, dropped1))
	client1.start()
	client1.join()
	server1.join()

	# while True:
	# 	if(serverqueue.empty() and clientqueue.empty()):
	# 		break
	endTime = time.time()
	throughput = numPackets/(endTime-startTime)
	print("Total packets dropped: ", dropped1.value)
	print("Time elapsed: ", endTime-startTime)
	print("Throughput: ", numPackets/(endTime-startTime), "Per second")
	print("")

	return dropped1.value, numPackets/(endTime-startTime)

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

	print("Simulating ", numTrials, " runs")
	for i in range(numTrials):
		print("Run ", i)
		drpPkt, throughput = Traffic(numPackets)

		#Packet loss info
		packetDroparr.append(drpPkt)		
		pktDropbar = sum(packetDroparr)/(i+1)
		pktDrop.append(pktDropbar)
		avgPktDrop = sum(pktDrop)/(i+1)
		ecnError.append(1.64 * Sn(pktDrop, avgPktDrop, i+1)/sqrt(i+1))

		#Percent Package loss info
		pktDrpPerarr.append((drpPkt/numPackets)*100)
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