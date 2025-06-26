#*******************************************************************
# License           : MIT
# File Name         : ringing.py
# Description       : PWMs for ringing
#                    
# Revision History  :
# Date	19.6.2025	Author 	Hans Gelke		Comments Prototype
# ------------------------------------------------------------------
# 19/06/2025	Hans Gelke	Initial			V0.1
#
#*****************************************************************/
import asyncio
import board
import digitalio
import keypad
import pwmio
import time
import tones


ringing1 = digitalio.DigitalInOut(board.GP3)
ringing1.direction = digitalio.Direction.OUTPUT
ringing1.value = False
ringing2 = digitalio.DigitalInOut(board.GP2)
ringing2.direction = digitalio.Direction.OUTPUT
ringing2.value = False
ringing3 = digitalio.DigitalInOut(board.GP7)
ringing3.direction = digitalio.Direction.OUTPUT
ringing3.value = False
ringing4 = digitalio.DigitalInOut(board.GP11)
ringing4.direction = digitalio.Direction.OUTPUT
ringing4.value = False


pwm1 = pwmio.PWMOut(board.GP1, frequency=20, duty_cycle=65535)
pwm2 = pwmio.PWMOut(board.GP0, frequency=20, duty_cycle=65535)
pwm3 = pwmio.PWMOut(board.GP6, frequency=20, duty_cycle=65535)
pwm4 = pwmio.PWMOut(board.GP14, frequency=20, duty_cycle=65535)


class RingGenerator():
    def __init__(self):
        self.ringring_1 = False
        self.ringring_2 = False
        self.ringring_3 = False
        self.ringring_4 = False
        self.call_register = 0
        self.past_call_register = 0

        self.engaged_register = 0
        self.past_engaged_register = 0


ringgenerator = RingGenerator()

async def ring_pwm1():

    while True:
        #print("Ring Flag:",ringgenerator.ringring)

        if ringgenerator.ringring_1 == True:

        #if True:
            for (index,tone) in tones.tonegenerator.cad_ring_ge:
                if tone:
                    ringing1.value = True
                    await asyncio.sleep(0.01)
                    pwm1.duty_cycle = 32767
                    await asyncio.sleep(index)
                else:
                    #The duty cycle determines if the PWM AG1171 F/R signal is high or low when not
                    # in use. The F/R pin should be high when not in use = 65535
                    pwm1.duty_cycle = 65535
                    #delay makes sure high voltage is decayed after toggling F/R
                    await asyncio.sleep(0.2)
                    ringing1.value = False
                    await asyncio.sleep(index)
                await asyncio.sleep(0)
        else:
            pwm1.duty_cycle = 65535
            ringing1.value = False
            await asyncio.sleep(0)



async def ring_pwm2():

    while True:
        #print("Ring Flag:",ringgenerator.ringring)

        if ringgenerator.ringring_2 == True:
        #if True:
            for (index,tone) in tones.tonegenerator.cad_ring_ge:
                if tone:
                    ringing2.value = True
                    await asyncio.sleep(0.01)
                    pwm2.duty_cycle = 32767
                    await asyncio.sleep(index)
                else:
                    pwm2.duty_cycle = 65535
                    #delay makes sure high voltage is decayed after toggling F/R
                    await asyncio.sleep(0.2)
                    ringing2.value = False
                    await asyncio.sleep(index)
                await asyncio.sleep(0)
        else:
            pwm2.duty_cycle = 65535
            ringing2.value = False
            await asyncio.sleep(0)


async def ring_pwm3():

    while True:
        #print("Ring Flag:",ringgenerator.ringring)

        if ringgenerator.ringring_3 == True:
        #if True:
            for (index,tone) in tones.tonegenerator.cad_ring_gb:
                if tone:
                    ringing3.value = True
                    await asyncio.sleep(0.01)
                    pwm3.duty_cycle = 32767
                    await asyncio.sleep(index)
                else:
                    pwm3.duty_cycle = 65535
                    #delay makes sure high voltage is decayed after toggling F/R
                    await asyncio.sleep(0.2)
                    ringing3.value = False
                    await asyncio.sleep(index)
                await asyncio.sleep(0)
        else:
            pwm3.duty_cycle = 65535
            ringing3.value = False
            await asyncio.sleep(0)


async def ring_pwm4():

    while True:
        #print("Ring Flag:",ringgenerator.ringring)

        if ringgenerator.ringring_4 == True:
        #if True:
            for (index,tone) in tones.tonegenerator.cad_ring_gb:
                if tone:
                    ringing4.value = True
                    await asyncio.sleep(0.01)
                    pwm4.duty_cycle = 32767
                    await asyncio.sleep(index)
                else:
                    # duty cycle 65535 pulls f/R permanently high
                    pwm4.duty_cycle = 65535
                    #delay makes sure high voltage is decayed after toggling F/R
                    await asyncio.sleep(0.2)
                    ringing4.value = False
                    await asyncio.sleep(index)
                await asyncio.sleep(0)
        else:
            pwm4.duty_cycle = 65535
            ringing4.value = False
            await asyncio.sleep(0)

