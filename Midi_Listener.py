import mido

inport = mido.open_input('IAC Driver Bus 1')
while True:
    msg = inport.receive()
    print msg
