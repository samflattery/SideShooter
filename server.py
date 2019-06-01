############################
# Code from Sockets demo for 15112
# changes were made to improve UX
###########################

import socket
import threading
import random
from queue import Queue


multiplayer = input("Do you wish to play on two different computers? [y/n]: ")
while multiplayer.strip() != "y" and multiplayer.strip() != "n":
    multiplayer = input("Please type either 'y' or 'n': ")

PORT = random.randint(60000, 65535)
BACKLOG = 4

if multiplayer == "y":
    HOST = socket.gethostbyname(socket.gethostname())
    print("PORT: " + str(PORT) + "\nHOST: " + HOST)
else:
    HOST = ""
    print("PORT: " + str(PORT))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(BACKLOG)
print("looking for connection...")


def handleClient(client, serverChannel, cID, clientele):
    client.setblocking(1)
    msg = ""
    while True:
        try:
            msg += client.recv(10).decode("UTF-8")
            command = msg.split("\n")
            while (len(command) > 1):
                readyMsg = command[0]
                msg = "\n".join(command[1:])
                serverChannel.put(str(cID) + " " + readyMsg)
                command = msg.split("\n")
        except:
            # we failed
            return


def serverThread(clientele, serverChannel):
    while True:
        msg = serverChannel.get(True, None)
        #print("msg recv: ", msg)
        msgList = msg.split(" ")
        senderID = msgList[0]
        instruction = msgList[1]
        details = " ".join(msgList[2:])
        if (details != ""):
            for cID in clientele:
                if cID != senderID:
                    sendMsg = instruction + " " + senderID + " " + details + "\n"
                    clientele[cID].send(sendMsg.encode())
                    #print("> sent to %s:" % cID, sendMsg[:-1])
        # print()
        serverChannel.task_done()


clientele = dict()
playerNum = 0

serverChannel = Queue(100)
threading.Thread(target=serverThread, args=(clientele, serverChannel)).start()

names = ["Player1", "Player2"]

while True:
    client, address = server.accept()
    # myID is the key to the client in the clientele dictionary
    myID = names[playerNum]
    print(myID, playerNum)
    for cID in clientele:
        print (repr(cID), repr(playerNum))
        clientele[cID].send(("newPlayer %s\n" % myID).encode())
        client.send(("newPlayer %s\n" % cID).encode())
    clientele[myID] = client
    client.send(("myIDis %s \n" % myID).encode())
    print("connection recieved from %s" % myID)
    threading.Thread(target=handleClient, args=(client, serverChannel, myID, clientele)).start()
    playerNum += 1
