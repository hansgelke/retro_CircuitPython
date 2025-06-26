#*******************************************************************
# License           : MIT
# File Name         : tones.py
# Description       : determines Signaltones for each phone
#                    
# Revision History  :
# Date	19.6.2025	Author 	Hans Gelke		Comments Prototype
# ------------------------------------------------------------------
# 19/06/2025	Hans Gelke	Initial			V0.1
#
#*****************************************************************/
import digitalio
import board
import tonegeneration
import asyncio
#import tone_out_1
#import tone_out_2
from audiopwmio import PWMAudioOut
#from audiocore import RawSample
import audiomixer


class ToneGenerator():
    def __init__(self):
        self.dial = 0  #the number of each tone corresponds to the machine 00 = no tone
        self.call = 0
        self.engaged = 0
        self.signaltone = [0,0,0,0,0]
        self.cad_ring_gb = [(0.4,1),(0.2,0),(0.4,1), (2,0)]
        self.cad_ring_ge = [(1,1),(2,0)]
        self.cad_ring_us = [(1,1),(2,0)]
        self.cad_engaged_de = [(0.480,1),(0.480,0)]
        self.cad_dial_de = [(0.200,1),(0.300,0),(0.700,1),(0.800,0)]
        self.cad_dial_us = [(0.100,1),(0.200,0),(0.800,1),(0.200,0)]
        #Assigns phone numbers to hardware machine
        #number           0 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19
        self.directory = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,]


tonegenerator = ToneGenerator()

#tonegenerator_1 = tonegeneration.ToneGeneration()
#tonegenerator_2 = tonegeneration.ToneGeneration()
#tonegenerator_3 = tonegeneration.ToneGeneration()







