# === RDTClient.py =============================
# UML: EECE 4830-5830
# Project Phase4, RDT 3.0
# Team: FastRedCar
# Chris Mills, Macaulay Rocha, Krishna_Kanagarayer, Edmundo Peralta.
# UDP Socket client (sender)
# References: 
# Computer Networking, Kurose-Ross

# === DESCRIPTION ==============================
# RDTClient instantiates the RDT3.0 UDP client function protocol from PP4.py
# to connect and transfer a file to a server over UTP.

# === RDTclient PROTOCOL =======================
# 1) Picks the file to be tranferred 
# 2) Connects to server [localhost] over UDP sockets
# 3) Brake up file into packets using the "make_packets(file_name, buffer_size)" function
# 4) Notify to the server (receiver) the Name of file and # of packets expected to receive.
# 5) Send packets to server one packet at a time over UDP.
# 6) Wait to receive message from the server

# === ERROR_OPTIONS ================================
# 1 : No loss/bit-errors.
# 2 : ACK packet bit-error
# 3 : Data packet bit-error
# 4 : ACK packet loss
# 5 : Data packet loss

# === EXECUTION ================================

# python RDTClient.py [file_name] [Error_option] [%Error]
# ---------------------------------------------

import PP4		# contains the main functions for RDT 3.0: Client and Server
PP4.RDTclient()	# import and execute RDTClient function for RDT3.0 UDP transfer
