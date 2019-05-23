SET R1, 0x00
ADD R1, R0
cond:
DEC R0
JZ halt
main:
ADD R1, R0
JMP cond
halt:
JMP halt
