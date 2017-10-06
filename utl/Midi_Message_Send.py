import mido
import time
import logging


if __name__ == "__main__":

    logging.basicConfig(filename="logfilepython.log", level=logging.DEBUG)
    logging.debug('Starting Midi Message Send Program')

    SmallKeyboard = mido.open_output('IAC Driver Small')
    LargeKeyboard = mido.open_output('IAC Driver Large')

    for SmallIndex in range(24, 48):

        Smallon = mido.Message('note_on', note=SmallIndex)
        Smalloff = mido.Message('note_off', note=SmallIndex)

        print('Sending SmallKey: ' + str(Smallon))
        logging.debug('Sending SmallKey: ' + str(Smallon))
        SmallKeyboard.send(Smallon)
        time.sleep(.5)
        print('Sending SmallKey: ' + str(Smalloff))
        SmallKeyboard.send(Smalloff)

        for LargeIndex in range(20, 90):
            msg = mido.Message('note_on', note=LargeIndex)
            print('Sending Large: ' + str(msg))
            logging.debug('Sending LargeKey: ' + str(msg))
            LargeKeyboard.send(msg)

            time.sleep(.5)
            msg = mido.Message('note_off', note=LargeIndex)
            print('Sending Large: ' + str(msg))
            LargeKeyboard.send(msg)

            time.sleep(3)
