#*******************************************************************
# License           : MIT
# File Name         : tonegeneration.py
# Description       : Tonegenerator
#                    
# Revision History  :
# Date	19.6.2025	Author 	Hans Gelke		Comments Prototype
# ------------------------------------------------------------------
# 19/06/2025	Hans Gelke	Initial			V0.1
#
#*****************************************************************/

import digitalio
import board
import time
import asyncio
import audiomp3

# We'll need these to generate our sine waves
import math
import array

# These libraries handle our audio needs
from audiopwmio import PWMAudioOut
from audiocore import RawSample
import audiomixer



class ToneGeneration():

    def __init__(self):
        self.sample_rate = 31000

    #sampleRate = 31000

    # This function accepts a frequency in Hz
    # and returns a playable RawSample
    def generateTone(self,frequency):
        samples = self.sample_rate // frequency
        buffer = array.array("h", [0] * samples)
        # The ugly bit below fills the buffer with our wave
        for i in range(samples):
            # Calculate the angle for this sample in radians
            angle = 2 * math.pi * i / samples
            # Calculate the sine value, scale to the range of
            # int16 then stick it back in the buffer
            buffer[i] = int(math.sin(angle) * 32767)
        tone = RawSample(buffer, sample_rate=self.sample_rate)
        return tone

    #def generateAnouncement(self):
       #



# This function sets volume for both voices,
# then starts playing both tones in a loop
    def dialTone(self,audio, sound):
        mp3 = audiomp3.MP3Decoder("kein_anschluss.mp3")
        #vdata = open("kein_anschluss.wav", "rb")
        #see below to play wav
        #wav = audiocore.WaveFile(vdata)

        mixer = audiomixer.Mixer(buffer_size=1024, voice_count=2,
            sample_rate = 31000, channel_count=1,
            bits_per_sample=16, samples_signed=True)
        if sound == 00:
            tone_0 = self.generateTone(440)
            tone_1 = self.generateTone(480)
        elif sound == 01:
            tone_0 = self.generateTone(400)
            tone_1 = self.generateTone(450)
        elif sound == 02:
            tone_0 = self.generateTone(350)
            tone_1 = self.generateTone(440)
        elif sound == 03:
            tone_0 = self.generateTone(350)
            tone_1 = self.generateTone(450)
        elif sound == 07:
            tone_0 = self.generateTone(425)
            tone_1 = self.generateTone(425)
        elif sound == 08:
            if not audio.playing:
                audio.play(mp3)


        if not audio.playing:
            audio.play(mixer)
            mixer.voice[0].level = .2
            mixer.voice[1].level = .2
            if sound == 07:
                mixer.voice[1].level = 0
            else:
                mixer.voice[1].level = .2

            mixer.voice[0].play(tone_0, loop=True)
            mixer.voice[1].play(tone_1, loop=True)



