#*******************************************************************
# License           : MIT
# File Name         : tpulsetimer.py
# Description       : Generates timeouts
#                    
# Revision History  :
# Date	19.6.2025	Author 	Hans Gelke		Comments Prototype
# ------------------------------------------------------------------
# 19/06/2025	Hans Gelke	Initial			V0.1
#
#*****************************************************************/

import digitalio
import board
import asyncio


class PulseTimer():
    def __init__(self):
        #This array contains the values of four pulsetimer.pulse_timers
        self.pulse_timer = [0,0,0,0,0]
        #Complete timer determines after a series of numbers was dialed
        self.complete_timer = [0,0,0,0,0]
        self.bt_retry_time = 0
        self.bt_query_time = 0


pulsetimer = PulseTimer()




#four puls timers run in parallel. They are triggered by variables from retro_fsm_object

async def timing_pulse_1():
    while True:
        if pulsetimer.pulse_timer[1] > 0:
            pulsetimer.pulse_timer[1] = pulsetimer.pulse_timer[1] - 1
            await asyncio.sleep(0.01)
        else:
            pulsetimer.pulse_timer[1] = pulsetimer.pulse_timer[1]
        await asyncio.sleep(0)


async def timing_pulse_2():
    while True:
        if pulsetimer.pulse_timer[2] > 0:
            pulsetimer.pulse_timer[2] = pulsetimer.pulse_timer[2] - 1
            await asyncio.sleep(0.01)
        else:
            pulsetimer.pulse_timer[2] = pulsetimer.pulse_timer[2]
        await asyncio.sleep(0)

async def timing_pulse_3():
    while True:
        if pulsetimer.pulse_timer[3] > 0:
            pulsetimer.pulse_timer[3] = pulsetimer.pulse_timer[3] - 1

            await asyncio.sleep(0.01)
        else:
            pulsetimer.pulse_timer[3] = pulsetimer.pulse_timer[3]
        await asyncio.sleep(0)

async def timing_pulse_4():
    while True:
        if pulsetimer.pulse_timer[4] > 0:
            pulsetimer.pulse_timer[4] = pulsetimer.pulse_timer[4] - 1

            await asyncio.sleep(0.01)
        else:
            pulsetimer.pulse_timer[4] = pulsetimer.pulse_timer[4]
        await asyncio.sleep(0)


async def timing_complete_1():
    while True:
        if pulsetimer.complete_timer[1] > 0:
            pulsetimer.complete_timer[1] = pulsetimer.complete_timer[1] - 1
            await asyncio.sleep(0.01)
        else:
            pulsetimer.complete_timer[1] = pulsetimer.complete_timer[1]
        await asyncio.sleep(0)

async def timing_complete_2():
    while True:
        if pulsetimer.complete_timer[2] > 0:
            pulsetimer.complete_timer[2] = pulsetimer.complete_timer[2] - 1
            await asyncio.sleep(0.01)
        else:
            pulsetimer.complete_timer[2] = pulsetimer.complete_timer[2]
        await asyncio.sleep(0)

async def timing_complete_3():
    while True:
        if pulsetimer.complete_timer[3] > 0:
            pulsetimer.complete_timer[3] = pulsetimer.complete_timer[3] - 1
            await asyncio.sleep(0.01)
        else:
            pulsetimer.complete_timer[3] = pulsetimer.complete_timer[3]
        await asyncio.sleep(0)

async def timing_complete_4():
    while True:
        if pulsetimer.complete_timer[4] > 0:
            pulsetimer.complete_timer[4] = pulsetimer.complete_timer[4] - 1
            await asyncio.sleep(0.01)
        else:
            pulsetimer.complete_timer[4] = pulsetimer.complete_timer[4]
        await asyncio.sleep(0)

async def bt_retry_timer():
    while True:
        if pulsetimer.bt_retry_time > 0:
            pulsetimer.bt_retry_time = pulsetimer.bt_retry_time - 1
            #print("Retry counter",pulsetimer.bt_retry_time)
            await asyncio.sleep(0.01)
        else:
            pulsetimer.bt_retry_time = pulsetimer.bt_retry_time
            await asyncio.sleep(0)
        await asyncio.sleep(0)

async def bt_query_timer():
    while True:
        if pulsetimer.bt_query_time > 0:
            pulsetimer.bt_query_time = pulsetimer.bt_query_time - 1
            #print("Retry counter",pulsetimer.bt_retry_time)
            await asyncio.sleep(0.01)
        else:
            pulsetimer.bt_query_time = pulsetimer.bt_query_time
            await asyncio.sleep(0)
        await asyncio.sleep(0)



