#!/usr/bin/env python3

import socket
import os
import signal
import select
import random

PORT = 50006
MAX_BUF = 1024
MAX_MEZU = 140
MAX_WAIT = 60


# Seguratasun-kodea lortzeko metodoa
def id(args):
    user = ""
    if len(args) < 2:
        return "ER03", -1, user #Hautazkoa ez den parametro bat falta da.
    par = args[1]
    if len(par.split("#")) > 2:
        return "ER02", -1, user #Espero ez zen parametroa. Parametro bat jaso da espero ez zen tokian.
    if len(par.split("#")) < 2:
        return "ER03", -1, user #Hautazkoa ez den parametro bat falta da.
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
            kodea = random.randint(10000, 99999)
            msg = f"OK {kodea}#{MAX_WAIT}"
            return msg, kodea, user
        else:
            return "ER08", -1, user #Errore orokorra
    except FileNotFoundError:
        return "ER08", -1, user #Errore orokorra


# Erabiltzaile berri bat erregistratzeko metodoa
def registeruser(args):
    if len(args) != 2:
        return "ER03" #Hautazkoa ez den parametro bat falta da.
    else:
        datuak = args[1].split("#")
        if len(datuak) > 3:
            return "ER04" #Parametroak ez du formatu egokia.
        elif len(datuak) < 3:
            return "ER03" #Hautazkoa ez den parametro bat falta da.
        else:
            existingusers = []
            existingemails = []
            open(".users.txt", "a")
            f = open(".users.txt", "r")
            lines = f.read().split("/n")
            for line in lines:
                if len(line.split(" ")) == 3:
                    existingusers.append(line.split(" ")[0])
                    existingemails.append(line.split(" ")[2])
            if datuak[0] not in existingusers and datuak[2] not in existingemails:
                f = open(".users.txt", "a")
                f.write(datuak[0]+" "+datuak[1]+" "+datuak[2]+'\n')
                f.close()
            elif datuak[0] in existingusers:
                return "ER06" #Erabiltzailea dagoeneko existitzen da
            else:
                return "ER07" #Emaila beste erabiltzaile bati dagokio
    return "OK"


# Jasotako kodea erabiltzaileari dagokion kodea dela ziurtatzeko metodoa
def validatecode(code, args):
    if len(args) < 2:
        return "ER03" #Hautazkoa ez den parametro bat falta da.
    sentcode = args[1].split('#')[0]
    if not sentcode.isnumeric():
        return "ER05" #Segurtasun kode okerra.
    if code == int(sentcode):
        return "OK"
    elif code == -1:
        return "ER11" #Segurtasun kodea iraungita

    else:
        return "ER05" #Segurtasun kode okerra


# Mezua bidaltzeko metodoa
def mezuabidali(param, sender):
    if len(param.split("#")) >= 3:
        splitparam = param.split("#", 2)
        user = splitparam[1]
        mssg = splitparam[2]
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
            return "ER10" #Mezu luzeegia (>140)
    else:
        return "ER03" #Hautazko ez den parametro bat falta da.


# Jasotako mezuak irakurtzeko metodoa
def mezuairakurri(param, user):
    if len(param.split("#")) == 1:
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
    else:
        return "ER03" #Hautazko ez den parametro bat falta da.


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
            kodea = -1
            elkarrizketa = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            elkarrizketa.connect(bez_helb)
            while buf:
                splitBuf = buf.decode().split(" ", 1)
                komandoa = splitBuf[0]
                if komandoa == "ID":
                    if kodea == -1:
                        msg, kodea, usr = id(splitBuf)
                    else:
                        msg = "ER12" #Badago baliozoko kode bat
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
                    if kodea != -1:
                        print(f"Itxoite denbora maximoa ({MAX_WAIT} s.) agortuta. Kodea iraungita.")
                        kodea = -1
                buf = elkarrizketa.recv(MAX_BUF)
            elkarrizketa.close()
            exit(0)
    s.close()
