#!/usr/bin/env python3

import socket, os, signal, select, random, threading
from time import sleep


PORT = 50006
MAX_BUF = 1024
MAX_MEZU = 140
MAX_WAIT = 10


class Timer:
    def __init__(self):
        self.time = MAX_WAIT

    def run(self):
        while True:
            # print(self.time)
            self.time -= 1
            sleep(1)
            if self.time == 0:
                break

    def display(self):
        print(self.time)
    
    def get_time(self):
        return self.time


def id(args, timer):
    par = args[1]
    if len(par.split("#")) != 2:
        return "ER02", -1
    user = par.split("#")[0]
    password = par.split("#")[1]
    try:
        file = open(".users.txt")
        lines = file.read().split("\n")
        exist = False
        for line in lines:
            if line.split(" ")[0] == user:
                if line.split(" ")[1] == password:
                    exist = True
                break

        if exist:
            timer_thread = threading.Thread(target=timer.run, daemon=True)
            timer_thread.start()
            kodea = random.randint(10000, 99999)
            msg = f"OK {kodea}#{MAX_WAIT}"
            return msg, kodea
        else:
            return "ER08", -1
    except FileNotFoundError:
        return "ER08", -1




def registeruser(args):
    if len(args) != 2:
        return "ER04" #Parametro desegokia
    else:
        datuak = args[1].split("#")
        if len(datuak)>3:
            return "ER04" #Erabiltzaile izenak eta pasahitzak ezin dute # izan
        elif len(datuak)<3:
            return "ER03" #Parametroak falta dira
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
            elif datuak[0] in users:
                return "ER06" #Erabiltzailea dagoeneko existitzen da
            else:
                return "ER07" #Emaila beste erabiltzaile bati dagokio
    return "OK"


def validatecode(code, sentcode):
    if code == sentcode:
        return "OK"
    elif code == -1:
        return "Not valid"
    else:
        return "ER05" #Segurtasun kode okerra


def mezuabidali(info, sender):
    if len(info) == 2:
        user = info[0]
        mssg = info[1]
        if len(mssg.encode()) <= 140:
            file = open(f".users.txt")
            lines = file.read().split("\n")
            exist = False
            for line in lines:
                if line.split(" ")[0] == user:
                    exist = True
                    break
            if exist:
                file = open(f".{user}.txt", "a")
                file.write(f"{sender}#{mssg}\n")
                file.close()
                return "OK"
            else:
                return "ER09" #Erabiltzaile ezezaguna
        else:
            return "ER10" #Mezuluzeegia
    elif len(info) < 2:
        return "ER03" #Hautazko ez den parametro bat falta da
    else:
        return "ER02" #Espero ez zen parametroa. Parametro bat jaso da espero ez zen tokian


def mezuairakurri(user):
    response = []
    try:
        file = open(f".{user}.txt")
        mezuak = file.read().split("\n")
        response.append(f"OK {len(mezuak)-1}")
        response = response + mezuak[:-1]
        return response
    except FileNotFoundError:
        response.append("OK 0")
        return response


if __name__ == "__main__":

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
            usr = ""
            timer = Timer()
            kodea = -1

            # kodea = random.randint(10000, 99999)
            #
            # timer = Timer()
            # timer_thread = threading.Thread(target=timer.run, daemon=True)
            # timer_thread.start()

            elkarrizketa = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            elkarrizketa.connect(bez_helb)
            while buf:
                splitBuf = buf.decode().split(" ")
                komandoa = splitBuf[0]

                # print(komandoa)

                if timer.get_time() == 0:

                    # kodea = random.randint(10000, 99999)
                    # timer = Timer()
                    # timer_thread=threading.Thread(target=timer.run, daemon=True)
                    # timer_thread.start()
                    # msg="Kodea expiratu da, berria lortu ID komandoa erabiliz"

                    kodea = -1
                    timer = Timer()

                if komandoa == "ID" and kodea != -1:
                    msg, kodea = id(splitBuf, timer)
                elif komandoa == "RG":
                    msg = registeruser(splitBuf)
                elif komandoa in ["MS", "RD", "XT"]:
                    kodestatus = validatecode(kodea, splitBuf[1].split('#')[0])
                    if kodestatus == "OK":
                        if komandoa == "MS":
                            msg = mezuabidali([splitBuf[1].split('#')[1], splitBuf[1].split('#')[2]], usr)
                        elif komandoa == "RD":
                            if len(splitBuf) != 1:
                                msg = "ER02" #Espero ez zen parametroa. Parametro bat jaso da espero ez zen tokian
                            else:
                                msg = mezuairakurri(usr)
                        elif komandoa == "XT":
                            kodea = -1
                            msg = "OK"
                    elif kodestatus == "Not valid":
                        continue
                        #TODO
                        # Kodea ez da baliozkoa, erantzun bat eman behar da zerbitzaritik?

                    else:
                        msg = kodestatus

                else:
                    msg = "ER01" #Komando ezezaguna
                if komandoa == "RD":
                    if len(msg) > 1:
                        for mezua in msg:
                            elkarrizketa.send(mezua.encode())
                    else:
                        elkarrizketa.send(msg[0].encode())
                else:
                    elkarrizketa.send(msg.encode())
                jasoa, _, _ = select.select([elkarrizketa], [], [], 100)
                if not jasoa:
                    print(f"Itxoite denbora maximoa ({MAX_WAIT} s.) agortuta. Bezeroa bukatutzat jo da.")
                    break
                buf = elkarrizketa.recv(MAX_BUF)
            elkarrizketa.close()
            exit(0)
    s.close()
