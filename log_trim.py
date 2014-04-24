import sys
r=open(sys.argv[1], "r")
w=open(sys.argv[2], "w")

while True:
	line = r.readline()
	if line == '':
		break
	w.write(line[:20] + "  " + line[48:])

r.close()
w.close()



#DB54  F1 33     SBC ($33),Y = 0400 @ 0400 = 7F  A:81