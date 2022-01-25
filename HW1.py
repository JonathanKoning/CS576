from numpy import random
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from math import sqrt
# from math import sqr
# Part MF A
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

def COV(X,Y, Xbar):
	# print("COV")
	cov = 0
	for i in range(10):
		cov += (X[i] - Xbar) * (Y[i] - 10)
	# print("cov: ", cov)
	return cov
	#E[(X - E[X])(Y - E[Y])] = E[XY] - E[X]E[Y]
	#E[Y] = p/mu = 10
	#E[X] = theta
	#

def VAR(X, EX):
	# print("VAR")
	variance = 0
	for i in range(10):
		variance += (X[i] - EX)*(X[i] - EX)
	
	return variance


def cstar(X,Y, Xbar):
	# print("c*")
	
	c = COV(X,Y, Xbar)/VAR(Y, 10)
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
	s = 0
	for i in range(n):
		s += (x[i]-Xbar) * (x[i]-Xbar)
	s = (1/(n-1)) * s
	s = sqrt(s)
	return s


if __name__ == "__main__":
	
	n=200
	Wn = 0
	p=10
	mu=1
	Y = 0
	lam = 2
	Q = 0
	L = 0
	onea = []
	oneb = []
	onec = []
	oned = []
	simulation = []
	Ws = []
	Ys = []
	Zs = []
	Ls = []
	Hci = []
	Lci = []
	Wnorm = []
	Werror = []
	Zerror = []
	Herror = []
	Lerror = []
	Wfound = False
	Zfound = False
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
		
		Wn += sum(X)
		Ws.append(sum(X))
		Wbar = Wn/(i+1)
		onea.append(Wbar)
		if(i == 0):
			Werror.append(0)
		else:
			Werror.append(1.64 * Sn(Ws, Wbar, i+1)/sqrt(i+1))
			if Wbar+Werror[i] < (Wbar*1.1) and Wfound==False:
				print("1a min: ", i)
				Wfound=True

		#Part B
		Y += S(DT)
		Ys.append(sum(DT))
		Ybar = Y/(i+1)
		EofY = p/mu
		Zbar = Wbar + cstar(X,DT, Wbar) * (Ybar - EofY)
		oneb.append(Zbar)
		if(i == 0):
			Zerror.append(0)
		else:
			Zerror.append(1.64 * Sn(Ys, Ybar, i+1)/sqrt(i+1))
			if Zbar+Zerror[i] < (Zbar*1.1) and Zfound==False:
				print("1b min: ", i)
				Zfound=True


		#Part C
		Q += sum(DT) - Ik(AT)
		Qbar = Q/(i+1)
		EofQ = p/mu - (p-1)/lam
		Hbar = Wbar + cstar(X,DT, Wbar) * (Qbar - EofQ)
		onec.append(Hbar)
		Hci.append(1.64 * np.std(onec)/sqrt(i+1))


		#Part D
		Ni = N(AT, DT, X)
		Li = EofTgivenN(Ni, mu)
		L += Li
		Ls.append(Li)
		Lbar = L/(i+1)
		oned.append(Lbar)
		Lci.append(1.64 * np.std(oned)/sqrt(i+1))
		if(i == 0):
			Lerror.append(0)
		else:
			Lerror.append(1.64 * Sn(Ls, Lbar, i+1)/sqrt(i+1))
			if Lbar+Lerror[i] < (Lbar*1.1) and Lfound==False:
				print("1d min: ", i)
				Lfound=True

		simulation.append(i)

	# print(Werror[5], Werror[1999])
	start = 0
	end = 2000
	# figure, axis = plt.subplots(2, 1)
	plt.title("90% Confidence")
	plt.xlabel("n")
	plt.ylabel("Target")
	# underline = np.subtract(np.array(onea),np.array(Wci))
	# overline = (onea + Wci)
	plt.errorbar(simulation[start:end], onea[start:end], yerr = Werror[start:end], color='b', label="Wbar")
	# plt.errorbar(simulation[start:end], oneb[start:end], yerr = Zerror[start:end], color='orange', label="Zbar")
	plt.plot(simulation[start:end], oneb[start:end], 'orange', label="Zbar")
	plt.plot(simulation[start:end], onec[start:end], 'g', label="Hbar")
	plt.errorbar(simulation[start:end], oned[start:end], yerr = Lerror[start:end], color='r', label="Lbar")
	plt.legend()
		
	plt.show()
	# plt.plot(simulation[start:end], onea[start:end], 'b', label="Wbar")
	# axis[0].fill_between(underline[start:end], overline[start:end],'b')
	plt.title("Estimations")
	plt.xlabel("n")
	plt.ylabel("Target")
	plt.plot(simulation[start:end], onea[start:end], color='b', label="Wbar")
	plt.plot(simulation[start:end], oneb[start:end], 'orange', label="Zbar")
	plt.plot(simulation[start:end], onec[start:end], 'g', label="Hbar")
	plt.plot(simulation[start:end], oned[start:end], 'r', label='Lbar')
	plt.legend()
		
	plt.show()

	# print("Wbar: ", Wbar)
	# print("Zbar: ", Zbar)
	# print("Hbar: ", Hbar)
	# print("Lbar: ", Lbar)