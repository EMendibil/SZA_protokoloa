#!/usr/bin/env python3

import socket, sys

PORT = 50006
MAX_BUF = 1024

if len( sys.argv ) != 2:
	print( "Erabilera: {} <Zerbitzari izena | IPv4 helbidea>".format( sys.argv[0] ) )
	exit( 1 )

zerb_helb = (sys.argv[1], PORT)

s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

mezua = input( "Sartu bidali nahi duzun mezua (hutsa bukatzeko):\n" )
if not mezua:
	exit( 0 )
s.sendto( mezua.encode(), zerb_helb )

buf, zerb_helb2 = s.recvfrom( MAX_BUF )
print( buf.decode() )

s.connect( zerb_helb2 )

while True:
	mezua = input()
	if not mezua:
		break
	s.send( mezua.encode() )
	buf = s.recv( MAX_BUF )
	if(mezua[:2]=="RD"):
		if "ER" not in buf.decode():
			""""
			print(buf.decode())
			buf = s.recv(MAX_BUF)
			print(buf.decode())
			"""
			mezuak = int (buf.decode().split(" ")[1])
			while buf:
				buf = s.recv(MAX_BUF)
				print(buf.decode())
		else:
			print(buf.decode())

	else:
		print( buf.decode() )
s.send( b"" )
s.close()
