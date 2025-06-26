# License           : MIT
# File Name         : dtmf.py
# Description       : Controlling Software DTMF Decoder
#                    
# Revision History  :
# Date	19.6.2025	Author 	Hans Gelke		Comments Prototype
# ------------------------------------------------------------------
# 19/06/2025	Hans Gelke	Initial			V0.1
#
import digitalio
import board
import time
import asyncio

import array            # These libraries will handle the nitty-gritty
import math             # details of reading in the incoming audio and
import analogbufio      # doing the math to detect our tones.


sampleRate=8000                                 # These variables set up the
bufferLength = 96                               # analog audio input buffer
buffer = array.array("B", [0] * bufferLength)   # on Pin 28 with analogbufio.
audioBuffer = analogbufio.BufferedIn(board.GP27,# We need only 96 samples(12ms)
                         sample_rate=sampleRate)# to identify our tones.

highFreqs    =    [1209,1336,1477]      # Here, I've laid out the tones
lowFreqs  = [697,#   1    2    3        # as they appear on the
             770,#   4    5    6        # standard 12-button keypad, to
             852,#   7    8    9        # show the relationship between
             941]#   *    0    #        # the tones and digits. But they
                                        # are both just ordinary lists.
targetFreqs = lowFreqs + highFreqs
threshold = 2e5                       ### Threshold may need to be adjusted
dtmfDigits = [                          # up to reduce false positives and
    ['1', '2', '3'],                    # down to increase sensitivity.
    ['4', '5', '6'],                    # 2e5 is scientific notation for
    ['7', '8', '9'],                    # the number 200000. dtmfDigits
    ['*', '0', '#']]                    # holds each digit as a string.


def checkTone():                    # This function is responsible for calling
    dtmfdecoder.digit = goertzel()              # the goertzel function. If the goertzel
    if not dtmfdecoder.digit:                   # returns a digit, this function will call
        return 0                 # goertzel again 2x, to double then triple
    else:                           # check the result. The double check takes
        for _ in range(2):          # 30ms to complete, meaning we can detect
            verify = goertzel()     # "standard Whelen timing" with 40ms tones,
            if verify != dtmfdecoder.digit:     # 20ms gaps. But, false positives may occur
                return 0         # in noisy signals. The 3rd check finishes
    return dtmfdecoder.digit                    # within 50ms, plenty fast for hand dialing

def goertzel():                   # This goertzel algo uses only ints for speed.
    audioBuffer.readinto(buffer)  # First thing we do: record our 96 samples.
    if max(buffer) < 100:#max=128 # If the signal isn't loud enough to be a
        return None               # DTMF tone, we bail early. Otherwise, we
    magnitudes = []               # get to do some math I don't understand:
    for target_frequency in targetFreqs:
        k = int(0.5 + ((bufferLength * target_frequency) // sampleRate))
        w_real = int(2 * math.cos(2 * math.pi * k / bufferLength) * (1 << 14))
        w_imag = int(math.sin(2 * math.pi * k / bufferLength) * (1 << 14))

        s = 0               # Seriously, I have no idea what is going
        s_prev = 0          # on in this part of the code. Didnt write it.
        s_prev2 = 0         # Luckily we dont need to know it to use it!

        for sample in buffer:
            s = sample + ((w_real * s_prev) >> 14) - s_prev2
            s_prev2 = s_prev
            s_prev = s

        magnitude = (s_prev2 * s_prev2) + (s_prev * s_prev) - ((w_real * s_prev * s_prev2) >> 14)
        magnitudes.append(magnitude)

    max_low_magnitude = max(magnitudes[:4])
    max_high_magnitude = max(magnitudes[4:])
    low_index = magnitudes.index(max_low_magnitude)
    high_index = magnitudes.index(max_high_magnitude) - 4

    if max_low_magnitude > threshold and max_high_magnitude > threshold:
        return dtmfDigits[low_index][high_index] # Finally, if the above math
    else:                                         # hears two valid tones, we
        return None                               # return the matching digit!

class DtmfDecoder():
    def __init__(self):
        self.dtmf_flag = False
        self.digit = None
        self.last_digit = None

dtmfdecoder = DtmfDecoder()


async def dtmf_decoder():
    while True:                     # This is the small bit of logic that prints
        dtmfdecoder.digit = checkTone()             # If we get a digit back from checkTone,
        if dtmfdecoder.digit:                       # we check if it matches the previous digit
            if dtmfdecoder.digit != dtmfdecoder.last_digit:      # detected. If it does, we turn on the LED.
                                   # we print it. The effect is the LED flashes
                print(dtmfdecoder.digit)            # while the digit is held, but it's printed
                dtmfdecoder.dtmf_flag = True
        dtmfdecoder.last_digit = dtmfdecoder.digit
        await asyncio.sleep(0.3)


