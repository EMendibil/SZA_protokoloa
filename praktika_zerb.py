#!/usr/bin/env python3

import socket, os, signal, select, random


PORT = 50006
MAX_BUF = 1024
MAX_MEZU = 140
MAX_WAIT = 60


def id(args):
    user = ""
    # timer_thread = None
    if len(args) < 2:
        return "ER03", -1, user, # timer_thread
    par = args[1]
    if len(par.split("#")) > 2:
        return "ER02", -1, user, # timer_thread
    if len(par.split("#")) < 2:
        return "ER03", -1, user, # timer_thread
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
            # timer_thread = threading.Thread(target=timer.run, daemon=True)
            # timer_thread.start()
            kodea = random.randint(10000, 99999)
            msg = f"OK {kodea}#{MAX_WAIT}"
            return msg, kodea, user, # timer_thread
        else:
            return "ER08", -1, user, # timer_thread
    except FileNotFoundError:
        return "ER08", -1, user, # timer_thread


def registeruser(args):
    if len(args) != 2:
        return "ER03" #Parametro desegokia
    else:
        datuak = args[1].split("#")
        if len(datuak) > 3:
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


def validatecode(code, args):
    if len(args) < 2:
        return "ER03"
    sentcode = args[1].split('#')[0]
    if not sentcode.isnumeric():
        return "ER05"
    if code == int(sentcode):
        return "OK"
    elif code == -1:
        return "ER11"
    else:
        return "ER05" #Segurtasun kode okerra


def mezuabidali(param, sender):
    if len(param.split("#")) >= 3:
        splitparam = param.split("#", 2)
        print(splitparam)
        user = splitparam[1]
        mssg = splitparam[2]
        print(mssg)
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
    else:
        return "ER03" #Hautazko ez den parametro bat falta da


def mezuairakurri(param, user):
    if len(param.split("#")) == 1:
        response = []
        try:
            file = open(f".{user}.txt")
            mezuak = file.read().split("\n")
            response.append(f"OK {len(mezuak)-1}")
            response = response + mezuak[:-1]
            print(response)
            return response
        except FileNotFoundError:
            response.append("OK 0")
            print(response)
            return response
    else:
        return "ER03"


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
        # timer = Timer()
        kodea = -1
        elkarrizketa = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elkarrizketa.connect(bez_helb)
        while buf:
            splitBuf = buf.decode().split(" ", 1)
            komandoa = splitBuf[0]
            if komandoa == "ID":
                if kodea == -1:
                    msg, kodea, usr = id(splitBuf)  # , timer_thread
                else:
                    msg = "ER12"
            elif komandoa == "RG":
                msg = registeruser(splitBuf)
            elif komandoa in ["MS", "RD", "XT"]:
                    kodestatus = validatecode(kodea, splitBuf)
                    if kodestatus == "OK":
                        if komandoa == "MS":
                            msg = mezuabidali(splitBuf[1], usr)
                        elif komandoa == "RD":
                            msg = mezuairakurri(splitBuf[1], usr)
                        elif komandoa == "XT":
                            kodea = -1
                            msg = "OK"
                    else:
                        msg = kodestatus
            else:
                msg = "ER01"  # Komando ezezaguna
            if "ER" not in msg:
                if komandoa == "RD":
                    for mezua in msg:
                        elkarrizketa.send(mezua.encode())
                else:
                    elkarrizketa.send(msg.encode())
            else:
                elkarrizketa.send(msg.encode())
            jasoa, _, _ = select.select([elkarrizketa], [], [], MAX_WAIT)
            if not jasoa:
                print(f"Itxoite denbora maximoa ({MAX_WAIT} s.) agortuta. Bezeroa bukatutzat jo da.")
                kodea = -1
            buf = elkarrizketa.recv(MAX_BUF)
            print(len(buf))
        elkarrizketa.close()
        exit(0)
s.close()
