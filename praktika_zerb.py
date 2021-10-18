#!/usr/bin/env python3

import socket, os, signal, select, random

PORT = 50006
MAX_BUF = 1024
MAX_MEZU = 140
MAX_WAIT = 999


def registerUser(args):
    if len(args) != 2:
        print("parametro desegokia")
        elkarrizketa.send("Parametro desegokia".encode()) #ER04
    else:
        datuak = args[1].split("#")
        if len(datuak)>3:
            elkarrizketa.send("Erabiltzaile izenak eta pasahitzak ezin dute # izan".encode()) #ER04
        elif len(datuak)<3:
            elkarrizketa.send("Parametroak falta dira".encode()) #ER03
        else:
            users = []
            emails = []
            open(".users.txt","a")
            with open(".users.txt","r") as users_file:
                for line in users_file:
                    elements=line.split(" ")
                    users.append(elements[0])
                    emails.append(elements[2])
            if datuak[0] not in users and datuak[2] not in emails:
                f = open(".users.txt","a")
                f.write(datuak[0]+" "+datuak[1]+" "+datuak[2]+'\n')
                f.close()
            elif datuak[0]  in users:
                print("Erabiltzailea dagoeneko existitzen da") #ER06
            else:
                print("Emaila beste erabiltzaile bati dagokio") #ER07


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

s.bind(('', PORT))

signal.signal(signal.SIGCHLD, signal.SIG_IGN)

while True:
    buf, bez_helb = s.recvfrom(MAX_BUF)
    if not buf:
        continue

    if not os.fork():
        s.close()
        kodea = random.randint(10000, 99999)
        print(kodea)
        elkarrizketa = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elkarrizketa.connect(bez_helb)
        while buf:
            splitBuf = buf.decode().split(" ")
            print(splitBuf)
            elkarrizketa.send(buf)
            if splitBuf[0] == "RG":
                registerUser(splitBuf)
            if splitBuf[0] == "ID":
                elkarrizketa.send(str(kodea).encode())
            #jasoa, _, _ = select.select([elkarrizketa], [], [], 10)
            #if not jasoa:
            #    print("Itxoite denbora maximoa ({} s.) agortuta. Bezeroa bukatutzat jo da.".format(MAX_WAIT))
            #    break
            buf = elkarrizketa.recv(MAX_BUF)
        elkarrizketa.close()
        exit(0)
s.close()
