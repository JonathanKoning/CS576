from numpy import random
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from math import sqrt

######################### Part A Start ##########################
def Wi(AT, DT):
	T = [0]*10
	Q = 0
	W = 0
	n = 10
	Wbar = 0
	for i in range(10):
		if i == 0:
			T[0] = DT[0]
		else:
			if(AT[i] < (AT[i-1] + T[i-1])):
				Q = (AT[i-1] + T[i-1]) - AT[i]
			else:
				Q = 0
			#print(Q)
			T[i] = Q + DT[i]
			W += T[i]

	# print(W)
	return T

def avgW(AT, DT):
	n = 2000
	w = 0
	for i in range(n):
		w += Wi(AT, DT)
	return (w/n)


######################### Part A end ############################

######################### Part B Start ##########################

def COV(X,Y, n):
	cov = 0
	Xbar = sum(X)/(n)
	Ybar = sum(Y)/(n)
	for i in range(n):
		cov += (X[i] - Xbar) * (Y[i] - Ybar)
	cov = (1/(n-1)) * cov
	
	return cov
	

def VAR(Y, n):
	variance = 0
	Ybarn = (1/n) * sum(Y)
	for i in range(n):
		variance += (Y[i] - Ybarn)*(Y[i] - Ybarn)
	
	variance = (1/(n-1)) * variance

	return variance


def cstar(X,Y,n):
	if(n == 1):
		return 0
	cov = COV(X,Y,n)
	variance = VAR(Y,n)
	c = (-1) * cov / variance
	return c

def S(DT):
	# print("Ybar")
	Y = 0
	for i in range(10):
		Y += DT[i]

	return Y


######################### Part B end ############################

######################### Part C Start ##########################
def Ik(AT):
	x = 0
	for i in range(0,9):
		x += (AT[i+1] - AT[i])
	
	return x

######################### Part C end ############################

######################### Part D Start ##########################
def N(AT, DT, T):
	Ni = [0]*10
	for i in range(1, 10):
		j = i
		count = 0
		while (AT[i] < (AT[j-1] + T[j-1])) and j > 0:
			j -= 1
			count +=1
		Ni[i] = count
	# print("Ni: ", Ni)
	return Ni

def EofTgivenN(Ni, mu):
	x = 0
	for k in range(10):
		x += (Ni[k]+1)* (1/mu)
	return x


def Norm(arr):
	n = []
	mi = np.min(arr)
	ma = np.max(arr) 
	nArr = np.array([((x - mi)/(ma - mi)) for x in arr])

	return nArr	
	
def Sn(x, Xbar, n):
	if(n == 1):
		return 0
	s = 0
	for i in range(n):
		s += (x[i]-Xbar) * (x[i]-Xbar)
	s = (1/(n-1)) * s
	s = sqrt(s)
	return s


if __name__ == "__main__":
	
	n=200
	p=10
	mu=1
	lam = 2
	L = 0
	Wn = []
	Y = []
	Q = []
	onea = []
	oneb = []
	onec = []
	oned = []
	simulation = []
	Werror = []
	Zerror = []
	Herror = []
	Lerror = []
	Wfound = False
	Zfound = False
	Hfound = False
	Lfound = False
	for i in range(n):
		#Arrival Time
		AT = random.exponential(scale=2, size=10)
		AT.sort()
		AT -= AT[0]
	
		#Departure rate
		DT = random.exponential(scale=1, size=10)

		#Part A
		X = Wi(AT, DT)
		
		Wn.append(sum(X))
		Wbar = sum(Wn)/(i+1)
		onea.append(Wbar)
		avgWbar = sum(onea)/(i+1)
		
		Werror.append(1.64 * Sn(onea, avgWbar, i+1)/sqrt(i+1))
		if i>0 and Wbar+Werror[i] < (Wbar*1.1) and Wbar-Werror[i] > (Wbar*0.9) and Wfound==False:
			print("1a min: ", i)
			Wfound=True

		#Part B
		Y.append(sum(DT))
		Ybar = sum(Y)/(i+1)
		EofY = p/mu
		Zbar = Wbar + cstar(Wn,Y, i+1) * (Ybar - EofY)
		oneb.append(Zbar)
		avgZbar = sum(oneb)/(i+1)
		Zerror.append(1.64 * Sn(oneb, avgZbar, i+1)/sqrt(i+1))
		if i > 0 and Zbar+Zerror[i] < (Zbar*1.1) and Zbar-Zerror[i] > (Zbar*0.9) and Zfound==False:
			print("1b min: ", i)
			Zfound=True


		#Part C
		Q.append(sum(DT) - Ik(AT))
		Qbar = sum(Q)/(i+1)
		EofQ = p/mu - (p-1)/lam
		Hbar = Wbar + cstar(Wn,Q, i+1) * (Qbar - EofQ)
		onec.append(Hbar)
		avgHbar = sum(onec)/(i+1) 
		Herror.append(1.64 * Sn(onec, avgHbar, i+1)/sqrt(i+1))
		if i > 0 and Hbar+Herror[i] < (Hbar*1.1) and Hbar-Herror[i] > (Hbar*0.9) and Hfound==False:
			print("1c min: ", i)
			Hfound=True


		#Part D
		Ni = N(AT, DT, X)
		Li = EofTgivenN(Ni, mu)
		L += Li
		Lbar = L/(i+1)
		oned.append(Lbar)
		avgLbar = sum(oned)/(i+1)
		
		Lerror.append(1.64 * Sn(oned, avgLbar, i+1)/sqrt(i+1))
		if i > 0 and Lbar+Lerror[i] < (Lbar*1.1) and Lbar-Lerror[i] > (Lbar*0.9) and Lfound==False:
			print("1d min: ", i)
			Lfound=True

		simulation.append(i)

	print(Zerror[5], Zerror[n-1])

	#Make Graphs
	start = 0
	end = n
	plt.title("90% Confidence")
	plt.xlabel("n")
	plt.ylabel("Target")
	plt.errorbar(simulation[start:end], onea[start:end], yerr = Werror[start:end], color='b', label="Wbar")
	plt.errorbar(simulation[start:end], oneb[start:end], yerr = Zerror[start:end], color='orange', label="Zbar")
	plt.errorbar(simulation[start:end], onec[start:end], yerr = Herror[start:end], color='g', label="Hbar")
	plt.errorbar(simulation[start:end], oned[start:end], yerr = Lerror[start:end], color='r', label="Lbar")
	plt.legend()
		
	plt.show()
	plt.title("Estimations")
	plt.xlabel("n")
	plt.ylabel("Target")
	plt.plot(simulation[start:end], onea[start:end], color='b', label="Wbar")
	plt.plot(simulation[start:end], oneb[start:end], 'orange', label="Zbar")
	plt.plot(simulation[start:end], onec[start:end], 'g', label="Hbar")
	plt.plot(simulation[start:end], oned[start:end], 'r', label='Lbar')
	plt.legend()
		
	plt.show()