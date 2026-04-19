# === RDTServer.py =============================
# UML: EECE 4830-5830
# Project Phase4, RDT 3.0
# Team: FastRedCar
# Chris Mills, Macaulay Rocha, Krishna_Kanagarayer, Edmundo Peralta.
# UDP Socket server (receiver)
# References: 
# Computer Networking, Kurose-Ross

# === DESCRIPTION ==============================
# RDTServer instantiates the RDT3.0 UDP server function protocol from PP4.py
# to create a UDP connection and receive a file from a client (sender) over UTP.

# === RDTserver PROTOCOL =======================
# 1) Create UDP socket connection to allow client to connect.
# 2) Receive message from client (sender) with filename and # of Packets of the file is expected to receive.
# 3) Wait to receive each packet.
# 4) Collect each of the packets received, "extract" function.
# 5) Save the file received, "deliver_data" function.
# 6) Notify the client (sender) the File and # packets received.
# 7) Close connection

# === EXECUTION ================================
# python RDTServer.py
# ---------------------------------------------

import PP4		#contains the main functions for RDT 3.0: Client and Server
PP4.RDTserver()	#import and execute RDTserver function for RDT3.0 UDP receive
