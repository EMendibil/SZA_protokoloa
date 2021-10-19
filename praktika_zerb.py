#!/usr/bin/env python3

import socket, os, signal, select, random, threading, time


PORT = 50006
MAX_BUF = 1024
MAX_MEZU = 140
MAX_WAIT = 10


class Timer():
    def __init__(self):
        self.time = MAX_WAIT

    def run(self):
        while True:
            #print(self.time)
            self.time -= 1
            time.sleep(1)
            if(self.time==0):
                break
    def display(self):
        print(self.time)
    
    def get_time(self):
        return self.time

    def reinitialize(self):
        self.time = PROBA_TIME
        

def registerUser(args):
    if len(args) != 2:
        return "parametro desegokia" #ER04
    else:
        datuak = args[1].split("#")
        if len(datuak)>3:
            return "Erabiltzaile izenak eta pasahitzak ezin dute # izan" #ER04
        elif len(datuak)<3:
            return "Parametroak falta dira" #ER03
        else:
            users = []
            emails = []
            open(".users.txt","a")
            with open(".users.txt","r") as users_file:
                for line in users_file:
                    elements=line.split(" ")
                    users.append(elements[0])
                    emails.append(elements[2].strip())
            print(emails)
            if datuak[0] not in users and datuak[2] not in emails:
                f = open(".users.txt","a")
                f.write(datuak[0]+" "+datuak[1]+" "+datuak[2]+'\n')
                f.close()
            elif datuak[0]  in users:
                return "Erabiltzailea dagoeneko existitzen da" #ER06
            else:
                return "Emaila beste erabiltzaile bati dagokio" #ER07
    return "OK"


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

s.bind(('', PORT))

signal.signal(signal.SIGCHLD, signal.SIG_IGN)

while True:
    buf, bez_helb = s.recvfrom(MAX_BUF)
    if not buf:
        continue

    if not os.fork():
        s.close()
        msg = ""
        kodea = random.randint(10000, 99999)
        
        timer = Timer()
        timer_thread=threading.Thread(target=timer.run,daemon=True)
        timer_thread.start()
        
        elkarrizketa = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elkarrizketa.connect(bez_helb)
        while buf:
            splitBuf = buf.decode().split(" ")
            komandoa = splitBuf[0]
            
            print(komandoa)
            
       	    if timer.get_time()==0:
            	kodea = random.randint(10000, 99999)
            	
            	timer = Timer()
            	timer_thread=threading.Thread(target=timer.run,daemon=True)
            	timer_thread.start()
            	msg="Kodea expiratu da, berria lortu ID komandoa erabiliz"
            if komandoa == "ID":
            	msg=str(kodea)        
            elif komandoa == "RG":
                msg=registerUser(splitBuf)      
            else:
            	msg="Komando ezezaguna"
            elkarrizketa.send(msg.encode())
            jasoa, _, _ = select.select([elkarrizketa], [], [], 100)
            if not jasoa:
                print("Itxoite denbora maximoa ({} s.) agortuta. Bezeroa bukatutzat jo da.".format(MAX_WAIT))
                break
            buf = elkarrizketa.recv(MAX_BUF)
        elkarrizketa.close()
        exit(0)
s.close()
