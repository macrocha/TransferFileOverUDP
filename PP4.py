# === PP4.py =============================
# UML: EECE 4830-5830
# Project Phase4
# Team: FastRedCar
# Chris Mills, Macaulay Rocha, Krishna_Kanagarayer, Edmundo Peralta.
# UDP Socket client/server
# References:
# [1] Computer Networking, Kurose-Ross
# [2] Socket Programming 101 - Python.pptx downloaded from Network design class.
# [3] https://stackoverflow.com/questions/42464514/how-to-convert-bitarray-to-an-integer-in-python
# [4] https://stackoverflow.com/questions/32675679/convert-binary-string-to-bytearray-in-python-3
# ==================================

from socket import *            # needed to create sockets
import bitarray as bit          # Array data structure
import os                       # Provides functionality to interact with the operating system
import sys                      # Module that provides us access to system-specific functions and variables
import numpy as np              # Numpy library contains multi-dimesional matrix data structures
import struct                   # Interprets bytes as packed binary data
import time                     # functions when working with time as a variable

# Defined classes for server and client to increase their functionality and improve code efficiency
# and flexbility, while maintaingin simplicity.


# Defined 'Server' class which includes variables, default states, and constants necessary for Phase 3
class server:
    #general
    serverName = 'localhost'        # Host defined as 'localhost' since file transfer will originate from host computer
    serverPort = 12000              # Server Port 12000 is selected to receive and send
    buffer_size = 1024              # Buffersize of 1024 is set
    terminate = 0                   # initalize terminate to 0
    #specific to project 3
    sequence0 = '10111101101111011011110110111101'  #Sequence 0 defined and initialized
    sequence1 = '11000011110000111100001111000011'  #Sequence 1 defined and initialized

# Defined 'Client' class which includes variables, default states, and constants necessary for Phase 3
class client:
    #general
    serverName = 'localhost'        # Host defined as 'localhost' since file transfer will originate from host computer
    serverPort = 12000              # Client Port 12000 is selected to receive and send
    buffer_size = 1024              # Buffersize of 1024 is set
    #specifc to project 3
    sequence0 = '10111101101111011011110110111101' #Sequence 0 defined and initialized
    sequence1 = '11000011110000111100001111000011' #Sequence 1 defined and initialized

# Defined 'Data Send' class which includes variables, default states, and constants necessary for Phase 3
class data_send:
    filename = ''                   # Empty 'filename' variable created
    error_state = int()  # 0 = no error, 1 = checksum error, 2 = message error
    error_rate = float()
    npackets = 0                    # Number of Packets set to 0
    send_data = list()              # Send_data function defined as list
    checksums = list()              # Checksums function defined as list
    size_checksum = 2               # set size of checksum to 2 bytes
    size_sequence = 4               # set size of sequence to 4 bytes
    size_sequence_chksum = 2        # set size of size_sequenece_chksum to 2 bytes

# Defined 'Data Receive' class which includes variables, default states, and constants necessary for Phase 3
class data_rcv:
    name = ''                       # Empty 'name' variable created
    npackets = 0                    # Number of Packets set to 0
    fullfile = []                   # FullFile variable intiliazed as empty data structure
    tempdata = ''                   # Empty 'tempdata' variable created
    checksum = str()                # Checksum for Receiver will be treated as string
    size_checksum = 2               # set size of checksum to 2 bytes
    size_sequence = 4               # set size of sequenece to 4 bytes
    size_sequence_chksum = 2        # set size of sequence_chksum to 2 bytes

# Defined 'Receiver Error' class which includes variables, default states, and constants necessary for Phase 3
class rcv_error:
    sequence = 0                    # initalize sequence to 0
    #variables for error counters
    data = 0                        # initalize data to 0
    duplicate = 0                   # initalize duplicate to 0
    ack_drop = 0                    # initalize ack_drop to 0
    data_drop = 0                   # initalize data_drop to 0
    #variables for packet error
    error_rate = 0                  # initalize error_rate to 0
    error_state = 0                 # initalize error_state to 0



########################################################################################################################

# RDTClient function that will connect to server and send file
def RDTclient():
    t0 = time.time()              # t0 set to current timeer
    c = client()                  # c defined as client() class
    data = data_send()            # data defined as data_send() class

    data.filename = sys.argv[1]  # use 1st argument to define file to send
    data.error_state = sys.argv[2]  # use 2nd argument to define error state
    data.error_rate = sys.argv[3]  # use 3rd argument to define error rate

    clientSocket = socket(AF_INET, SOCK_DGRAM)  # AF_INET = IPv4, SOCK_DGRAM = UDP
    data = readData(data, c.buffer_size)  # create a list: split the file into chunks of size: buffer_size
    sequence = 0                 # Sequence set to 0
    for i in range(data.npackets):  # loop through while i< than # in datapackets
        out = 0  #set to 0 each iteration
        while not out:
            out = sendDataClient(stateToSequence(sequence, c), clientSocket, c, data, data.send_data[i])
        sequence = not sequence  # invert sequence state
    t1 = time.time()             # record time to complete loop and store in t1
    total_time = t1 - t0         # Save completion time in total_time
    print('Time to run program with error rate', data.error_rate, 'was:', total_time) # Display message to user

# RDTServer function that will connect to client and receive file
def RDTserver():
    s = server()                 # s defined as server() class
    data = data_rcv()            # data defined as data_rcv() class
    err = rcv_error()            # err defined as rcv_error() class
    # setup socket as UDP
    serverSocket = socket(AF_INET, SOCK_DGRAM)  # AF_INET = IPv4, SOCK_DGRAM = UDP
    serverSocket.bind(('', s.serverPort))  # bind port number to the server's socket
    print('The Server is ready to receive')  # server is ready to receive

    # Control variables
    good_data = 0  # flag to tell if received data is good and should be saved.  0 is bad data, 1 is good data, 2 is last packet
    sequence = 0  # 0 or 1 depending on what was received from client, initialize to 0
    idx = 0  # Keeps count of the packets that were received

    while good_data != 2:  # While the last received packet was not the last packet
        correctly_received = 0  # reset to false each time
        previous_sequence = not sequence  # next sequence each iteration
        while not correctly_received:  # as long this packet is not received correctly
            if idx == 0:    
                temp, clientAddress = serverSocket.recvfrom((s.buffer_size))
            else:
                serverSocket.settimeout(0.02) #TODO modify time when working
                try:
                    temp, clientAddress = serverSocket.recvfrom(s.buffer_size)  # receive the message from the client
                except:
                    err.data_drop += 1  
                    temp = '00000000'.encode()
            received_sequence = readHeader(temp, data)  # make sure header is correct
            if err.error_state == 4:
                drop_this_packet = np.random.binomial(1, float(err.error_rate))  # binary variable telling us if we drop this packet or not
            else:
                drop_this_packet = 0
            if sequenceToState(received_sequence, s) == sequence:
                good_data, data, err = extract(data, temp, err, idx)  # extract data and make sure it matches checksum
                if good_data == 1:  # regular packet received correctly
                    correctly_received = not correctly_received  # we successfully received the data
                    if not drop_this_packet:
                        sendDataServer(stateToSequence(sequence, s), err, serverSocket, clientAddress)  # send sequence that we received
                    else:
                        err.ack_drop += 1
                        print('ACK loss in transmission to client')
                elif good_data == 2:  # terminate message received correctly
                    correctly_received = not correctly_received  # we successfully received the last packet message
                    err.error_state = 1
                    sendDataServer(stateToSequence(sequence, s), err, serverSocket, clientAddress )  # send sequence that we received
                    deliver_data(data.name, data.fullfile)
                else:  # something went wrong, let the client know
                    print('Packet', idx, 'error') 
                    if not drop_this_packet:
                        sendDataServer(stateToSequence(previous_sequence, s), err, serverSocket, clientAddress)  # send 'not sequence' that we received
                    else:
                        err.ack_drop += 1  # increase error counter and print ACK loss in transmission occured
                        print('ACK loss in transmission to client')
            else:  # received the same sequence twice in a row.  Ack the previous sequence and wait for next message
                if not drop_this_packet:
                    err.duplicate += 1  # duplicate packet, try to receive again
                    print('Packet', idx - 1, ' error')  # print out whic packet number has an error
                    sendDataServer(stateToSequence(previous_sequence, s), err, serverSocket, clientAddress)  # send sequence that we received
                else:
                    err.ack_drop += 1   #increase error counter for ACK drops and print following message
                    print('ACK loss in transmission to client')

        if idx == 0: # if idx count equals 0 print message that file was received
            print('Filename received')
        elif good_data == 2: #if last packet is received print following messages including variables
            print('Last packet received') #print if Last packet was received
            print('Error in data packet or checksum:', err.data) #print Error in checksum or datapacket
            print('Duplicate data or sequence error:', err.duplicate + err.sequence) #print duplicate or sequence error
            print('Lost ACK occurrences:', err.ack_drop)   # print ACK lost ocrrued
            print('Lost data occurrences:', err.data_drop) # print data lost occurred

            #print('Effective error rate', (err.data + 2*err.duplicate + err.sequence) / (idx + 2 + err.data + err.sequence + 2*err.duplicate))
        else:
            print('Packet', idx, 'received') # print message with idx count
        idx += 1                # increae idx count
        sequence = not sequence # invert sequence

########################################################################################################################

# [CLIENT]
# readData function to create chunks to send from a file
def readData(data, buffer_size):
    read_len = buffer_size - data.size_sequence_chksum - data.size_sequence - data.size_checksum
    file_name = data.filename
    f = open(file_name, "rb")  # open file
    file_size = os.path.getsize(file_name)  # get file size
    packets = list()  # create packet list, empty list
    temp = f.read(read_len)  # read first buffer
    num_packets = 0  # reset counter
    while temp:  # loop to transfer buffer
        packets.append(temp)  # add packet to the list
        temp = f.read(read_len)  # read next set of data, size=buffer_size
        num_packets += 1  # update number of packets (count up)
    f.close()  # close file

    file_name_bytes = data.filename.encode()
    error_info = str(data.error_state) + 'xxxx' + str(data.error_rate)
    error_info_bytes = error_info.encode()
    end_message = 'zzzzzzzzzz'
    end_message_bytes = end_message.encode()

    packets.insert(0, error_info_bytes) #add error information as second packet.
    packets.insert(0, file_name_bytes)  # add file name as first packet
    packets.append(end_message_bytes)   # add last message as last packet

    data.send_data = packets
    data.npackets = num_packets + 3  # one for filename, one for error data,  and one for last message
    return data  # return file divided into packets, in list

# [CLIENT]
# Sends data from the client to the server and waits for ACK.  Returns an integer 1 once the server correctly receives.
def sendDataClient(sequence, socket, cli_object, data ,chunk):  # chunk is data to send to server
    state_in = sequenceToState(sequence, cli_object)
    recv = not state_in
    while recv != state_in:
        packet = makePacket(sequence, data.error_rate, data.error_state, chunk)  # create full packet header and data
        if int(data.error_state) == 5:
             drop_this_packet = np.random.binomial(1, float(data.error_rate))  # binary variable telling us if we drop this packet or not
        else:
            drop_this_packet = 0
        if not drop_this_packet:
            socket.sendto(packet, (cli_object.serverName, cli_object.serverPort))
        else:
            print('Data packet lost in transmission to receiver')
        socket.settimeout(0.02) #TODO reduce timer value once good
        try:
            temp, address = socket.recvfrom(cli_object.buffer_size)  # want to receive back same as what is sent
        except:
            print('Client Timeout')
            temp = '000000000'.encode()
        temp2 = readHeader(temp, data)  # temp2 in this line is a sequence
        state_out = sequenceToState(temp2, cli_object)  # convert to state
        if state_out == state_in:  # compare what server received to what we send
            state_in = not state_in  # if the equal return a 1 to the above function
            return 1

########################################################################################################################

# [SERVER]
# sends packet to client with only seq_checksum and sequence in header.  rest of packet is empty
def sendDataServer(sequence, err, socket, address):

    packet = makePacket(sequence, err.error_rate, err.error_state)  # create header only packet
    #if we need error on server side. Add it here
    socket.sendto(packet, address)

# [SERVER]
# function that reads the header and returns sequence as long as seq_checksum = check_sum(sequence)
def readHeader(temp, data):  # reads only the sequence num checksum and sequence number from a packet.

    seq_sum_read = bytes_to_bitstring(temp[0:data.size_sequence_chksum]) # convert sequence read from header to bits
    seq_sum_calc, received_sequence = check_sum(temp[data.size_sequence_chksum:data.size_sequence_chksum + data.size_sequence], 1) # calculate sequence from header

    if seq_sum_read == seq_sum_calc: # if calculated and read sequence number equal, then return received sequence or else return '000111'
        out_sequence = received_sequence
    else:
        out_sequence = '000111'
    return out_sequence  # return the received sequence or failed value '0'

# [SERVER]
# function to split header into parts, check the checksum and collect received packets
def extract(data, temp, err, *args):
    idx = int(-1)  # here to handle first packet, filename
    if len(args) != 0:
        idx = args[0]

    out = 0
    #split temp into parts
    checksum = temp[data.size_sequence_chksum + data.size_sequence: data.size_sequence_chksum + data.size_sequence + data.size_checksum]  # size_checksum
    message = temp[data.size_sequence_chksum + data.size_sequence + data.size_checksum:]  # [buffer size - 2*size_checksum - size_sequence] bytes

    checksum = bytes_to_bitstring(checksum)
    if checksum == check_sum(message):
        if idx == 0:  # file name, first message
            data.name = message.decode()
            out = 1
        elif idx == 1:  # error data, second message
            parts = message.decode().split('xxxx')
            err.error_state = int(parts[0])
            err.error_rate = float(parts[1])
            out = 1
        elif message == 'zzzzzzzzzz'.encode():  # last packet, save data
            out = 2
        else:
            data.fullfile.append(message)
            out = 1
    else:
        #error in checksum or data.
        err.data += 1

    return out, data, err  # return a 1 or 0 depending on if data checksum worked and data was saved.


# [SERVER]
# function to save data after it has all been compiled
def deliver_data(file_name, full_file):
    file_parts = file_name.split('.')
    new_file_name = file_parts[0] + '_serverOut.' + file_parts[1]  # create modified filename
    s = open(new_file_name, 'wb')  # open new file

    # iterate through the length of full_file
    for i in range(len(full_file)):
        s.write(full_file[i])  # write each packet to the file

    s.close()  # close file
    print('The server received file', file_name, 'and saved it as',
          new_file_name)  # display what file the server received and the name it saved it as\

########################################################################################################################

# CLIENT & SERVER Functions:
# packages [sequence checksum, sequence num, data checksum, data] in bytes into one variable
def makePacket(sequence, error_rate, error_state, *args):  # *args used to take in data if being used on sender side.  if not returns header only
    # *args must be in data.send_data[i]
    error_this_packet = np.random.binomial(1, float(error_rate))  # binary variable telling us if error or not in this packet
    error_state = int(error_state)
    if len(args) != 0:  # client/ sender
        send_data = args[0]
        if (error_state == 3) and error_this_packet:  # error in data checksum
            packet = bitstring_to_bytes(check_sum(bitstring_to_bytes(sequence))) + bitstring_to_bytes(sequence) + bitstring_to_bytes(createError1bit(check_sum(send_data))) + send_data
        elif (error_state == 2) and error_this_packet:  # error in sequence
            packet = bitstring_to_bytes(check_sum(bitstring_to_bytes(sequence))) + bitstring_to_bytes(createError1bit(sequence)) + bitstring_to_bytes(check_sum(send_data)) + send_data
        else:  # no error
            packet = bitstring_to_bytes(check_sum(bitstring_to_bytes(sequence))) + bitstring_to_bytes(sequence) + bitstring_to_bytes(check_sum(send_data)) + send_data

    else:
        # server / receiver
        if error_this_packet and (error_state == 2):
            packet = bitstring_to_bytes(check_sum(bitstring_to_bytes(sequence))) + bitstring_to_bytes(createError1bit(sequence))
        else:
            packet = bitstring_to_bytes(check_sum(bitstring_to_bytes(sequence))) + bitstring_to_bytes(sequence)  # ack packet with sequence num
        # packet = 2 bytes + 4 bytes
    return packet

# function that takes in data of type 'bytes' and returns a checksum.
def check_sum(input, *args):  # *args meant to be used as [0,1] option to return sequence
    sequence_flag = 0              # set flag for sequence to 0
    if len(args) != 0:
        sequence_flag = args[0]
    total = bin(0)
    sum_size = 16  # must be a factor of buffer size  16, 32, 64, 128, 256
    temp = bit.bitarray()
    temp.frombytes(input)
    if sequence_flag:
        seq_out = bin(int(temp.to01(), 2))[2:]
    for i in range(int(len(temp) / sum_size)):  # for each sum_size bit block
        this_check = temp[(i * sum_size):(i * sum_size + sum_size)]
        decimal = int(this_check.to01(), 2) # store integer into decimal variable
        total = bin((int(total, 2) + decimal))  # sum all sum_size bit blocks together
    total = total[2:]  # remove the '0b' from the string
    temp = total
    diff = len(total) - sum_size

    new_sum = total
    while diff != 0:
        if diff > 0:
          overflow = new_sum[0:diff]
          new_sum = sum_binary(new_sum[diff:], overflow)
        while len(new_sum) < sum_size:
            new_sum = '0' + new_sum  # add preceding zeros if there aren't any.

        diff = len(new_sum) - sum_size
        temp = new_sum

    output = invert_bits(temp)

    if len(output) != 16:
        print('error in checksum function.  check it out. ')

    if sequence_flag:
        return output, seq_out
    else:
        return output

# inverts the bits of a string of bits
def invert_bits(temp):
    # inversetemp= temp.replace('1','2') #replace 1s with 2s
    # inversetemp= inversetemp.replace('0','1') #replace 0s with 1s
    # inversetemp= inversetemp.replace('2','0') #replace 2s with 0s - completed the inverse conversion

    # alternative option - one-liner
    inversetemp = ''.join(['1' if i == '0' else '0' for i in temp])
    return (inversetemp)

# sums two binary numbers
def sum_binary(binary1, binary2):  # sum two binary strings
    binary_sum = bin(int(binary1, 2) + int(binary2, 2)) #adds gwo binary string and stores into binary_sum
    binary_sum = binary_sum[2:]
    return (binary_sum)

# checks if a checksum matches a given set of data
def check_check_sum(data):
    out = 0
    # compare if data.checksum matches the computed checksum for recieved data
    temp = check_sum(data.tempdata)
    if data.checksum == temp:
        out = 1

    return out  # 1 = good, 0 = bad

# adds error to a string of bits
def bitError(input, errorRate): # [1,2] state and [0.00-1] error rate and checksum or packets
    # find the length of checksum or packets
    temp = bit.bitarray()  # create 'temp' variable of type bit from imported bitarray module
    temp.frombytes(input)  # converts input into bytes and stores into temp
    packet_length = len(temp) # get length of packets of temp
    random_num = np.random.randint(0, packet_length, size=int(float(errorRate)*packet_length), dtype=int) #random integer generated of packet length within 0.00-1 range
    random_num.sort()      # sort number
    i = 0
    for j in range(packet_length):
        if j == random_num[i]:
            i += 1  #index variable for random_num
            # data.packets[i, j] = not data.packets[i, j]
            if temp[j] == '1':    # convert '1' into '0'
                temp[j] = '0'
            else:
                temp[j] = '1'     # else convert '0' into '1'

    output = bitstring_to_bytes(temp.to01())
    return output

# turns a set of bytes to a string of bits
def bytes_to_bitstring(input):
    a = bit.bitarray()      # create 'a' variable of type bit from imported bitarray module
    a.frombytes(input)
    return_string = a.to01()
    return return_string

# turns a string of bits into bytes
def bitstring_to_bytes(a):  # [4] see references
    a = list(a)
    return_bytes = bytes()  # create return_bytes variables of type bytes
    for i in range(len(a)):
        a[i] = int(a[i])
    if (len(a)%8) != 0:
        a = [0] * (8 - (len(a) % 8)) + a  # adding in extra 0 values to make a multiple of 8 bits
    # s = ''.join(str(x) for x in a)[::-1]  # reverses and joins all bits
    num_return_bytes = len(a) / 8 #number of bytes by converting from number of bits
    temp = str()
    for i in range(len(a)):
        temp += str(a[i])
    temp = hex(int(temp, 2))
    if temp[0:2] == '0x':
        temp = temp[2:]
        if (len(temp) % 2) != 0:
            temp = '0' + temp
        return_bytes = return_bytes.fromhex(temp)  # remove '0x' from string
    else:
        if (len(temp) % 2) != 0:
            temp = '0' + temp
        return_bytes = return_bytes.fromhex(temp)  # no '0x' to remove

    while len(return_bytes) < num_return_bytes:
        return_bytes = b'\x00' + return_bytes

    return return_bytes

# conversion from sequence to state
def sequenceToState(sequence, object):
    if sequence == object.sequence0:    # check if packet sequence number equals state 0's sequence
        state = 0                       # if it does, return state = 0 to caller function
    elif sequence == object.sequence1:  # check if packet sequence number equals state 1's sequence
        state = 1                       # if it does, return state = 1 to caller function
    else:                               # all else return state 2 to caller function
        state = 2
    return state

# conversion from state to sequence
def stateToSequence(state, object):
    if state == '0b0' or state == 0:   # if state equals '0b0' or '0', return sequence0 back to caller function
        sequence = object.sequence0
    elif state == '0b1' or state == 1: # else if state equals '0b1' or '1', return sequence1 back to caller function
        sequence = object.sequence1
    else:
        sequence = '00001111'          # else return 00001111 sequence for state 2 to caller function
    return sequence

def createError1bit(data):
    # flip last bit to create error
    b_dict = {'0': '1', '1': '0'}      # flipping bits dictionary, flip 0s to 1s and 1s to 0s
    bitflip = b_dict[data[-1:]]        # perform bitflip to data packet in file
    data1flip = data[:-1] + bitflip    # ignore first character in datap[] and add with bitflip value and store in data1flip
    #print("new corrupted data:", data1flip)
    return data1flip

