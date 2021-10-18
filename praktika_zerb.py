#!/usr/bin/env python3

import socket, os, signal, select

PORT = 50005
MAX_BUF = 1024
MAX_WAIT = 120

s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

s.bind( ('', PORT) )

signal.signal(signal.SIGCHLD, signal.SIG_IGN)
while True:
	buf, bez_helb = s.recvfrom( MAX_BUF )
	if not buf:
		continue
	if not os.fork():
		s.close()
		elkarrizketa = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
		elkarrizketa.connect( bez_helb )
		while buf:
			elkarrizketa.send( buf )
			jasoa, _, _ = select.select( [ elkarrizketa ], [], [], MAX_WAIT )
			if not jasoa:
				print( "Itxoite denbora maximoa ({} s.) agortuta. Bezeroa bukatutzat jo da.".format( MAX_WAIT ) )
				break
			buf = elkarrizketa.recv( MAX_BUF )
		elkarrizketa.close()
		exit( 0 )
s.close()