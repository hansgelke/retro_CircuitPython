#*******************************************************************
# License           : MIT
# File Name         : tone_out_1.py
# Description       : Output for each phone
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
import tones
import audiomp3

from audiopwmio import PWMAudioOut

# Setup Pins for channel 1
#CHANGE
audio_out = PWMAudioOut(board.GP26)
tonegen = tonegeneration.ToneGeneration()

#CHANGE
phone = 1

#CHANGE
async def toneout_1():
# Main loop
    while True:
        #print("Signal state:" ,tonegenerator.signaltone[2] )
        if tones.tonegenerator.signaltone[phone] == "dial_us":
            sound = 02 #frequencies of dialtone
            tonegen.dialTone(audio_out,sound)

        elif tones.tonegenerator.signaltone[phone] == "announce_1":
            sound = 08
            tonegen.dialTone(audio_out,sound)

        elif tones.tonegenerator.signaltone[phone] == "dial_de":
            sound = 07 #frequencies of dialtone
            for (index,tone) in tones.tonegenerator.cad_dial_de: #cadence
                if tone:
                    tonegen.dialTone(audio_out,sound)
                    await asyncio.sleep(index)
                    audio_out.stop()
                else:
                    await asyncio.sleep(index)
         #print("Signal state:" ,tonegenerator.signaltone[2] )
        elif tones.tonegenerator.signaltone[phone] == "dial_ch":
            sound = 07 #frequencies of dialtone
            tonegen.dialTone(audio_out,sound)

        #print("Signal state:" ,tonegenerator.signaltone[2] )
        elif tones.tonegenerator.signaltone[phone] == "dial_gb":
            sound = 02 #frequencies of dialtone
            tonegen.dialTone(audio_out,sound)



        elif tones.tonegenerator.signaltone[phone] == "ring_ge":
            sound = 00 #frequencies of dialtone
            for (index,tone) in tones.tonegenerator.cad_ring_ge: #cadence
                if tone:
                    tonegen.dialTone(audio_out,sound)
                    await asyncio.sleep(index)
                    audio_out.stop()
                else:
                    await asyncio.sleep(index)

        elif tones.tonegenerator.signaltone[phone] == "ring_gb":
            sound = 00 #frequencies of dialtone
            for (index,tone) in tones.tonegenerator.cad_ring_gb: #cadence
                if tone:
                    tonegen.dialTone(audio_out,sound)
                    await asyncio.sleep(index)
                    audio_out.stop()
                else:
                    await asyncio.sleep(index)

        elif tones.tonegenerator.signaltone[phone] == "ring_us":
            sound = 00 #frequencies of dialtone
            for (index,tone) in tones.tonegenerator.cad_ring_us: #cadence
                if tone:
                    tonegen.dialTone(audio_out,sound)
                    await asyncio.sleep(index)
                    audio_out.stop()
                else:
                    await asyncio.sleep(index)

        elif tones.tonegenerator.signaltone[phone] == "engaged":
            sound = 00 #frequencies of dialtone
            for (index,tone) in tones.tonegenerator.cad_engaged_de: #cadence
                if tone:
                    tonegen.dialTone(audio_out,sound)
                    await asyncio.sleep(index)
                    audio_out.stop()
                else:
                    await asyncio.sleep(index)
        else:
            audio_out.stop()

        await asyncio.sleep(0)






