#*******************************************************************
# License           : MIT
# File Name         : main.py
# Description       : Root file
#                    
# Revision History  :
# Date	19.6.2025	Author 	Hans Gelke		Comments Prototype
# ------------------------------------------------------------------
# 19/06/2025	Hans Gelke	Initial			V0.1
#
#*****************************************************************/
import asyncio
import board
#import digitalio
import keypad
import retro_control
import retro_fsm_object
import ringing
import tones
import tone_out_1
import tone_out_2
import tone_out_3
import tone_out_4
import bluetooth
import dtmf
import utils
import digitalio
import busio
import pulsetimer

from retro_fsm_object import MainFSM
from ringing import RingGenerator
#---------------------------------
#Pin initializations for Bluetooth
#---------------------------------
#bt_cmd = digitalio.DigitalInOut(board.GP19)
#bt_cmd.direction = digitalio.Direction.OUTPUT

#bt_int = digitalio.DigitalInOut(board.GP20)
#bt_int.direction = digitalio.Direction.INPUT

#bt_baud = digitalio.DigitalInOut(board.GP21)
#bt_baud.direction = digitalio.Direction.OUTPUT

#bt_pwr = digitalio.DigitalInOut(board.GP22)
#bt_pwr.direction = digitalio.Direction.OUTPUT

#uart = busio.UART(board.GP16, board.GP17, baudrate=115200, timeout=1)

#Power on = true
#bt_pwr.value = True
#baud rate = 115200
#bt_baud.value = True
#command mode: bt_cmd = 0
#bt_cmd.value = False


event = False
state = 0
set_time = 0
time = 0


async def main():

    #nodial_timer_task = asyncio.create_task(retro_control.no_dial_timer())
    print_state_task = asyncio.create_task(retro_control.print_state())
    main_fsm_task = asyncio.create_task(retro_control.fsm())
    ring_pwm1_task = asyncio.create_task(ringing.ring_pwm1())
    ring_pwm2_task = asyncio.create_task(ringing.ring_pwm2())
    ring_pwm3_task = asyncio.create_task(ringing.ring_pwm3())
    ring_pwm4_task = asyncio.create_task(ringing.ring_pwm4())
    dtmf_task = asyncio.create_task(dtmf.dtmf_decoder())
    tone_task_1 = asyncio.create_task(tone_out_1.toneout_1())
    tone_task_2 = asyncio.create_task(tone_out_2.toneout_2())
    tone_task_3 = asyncio.create_task(tone_out_3.toneout_3())
    tone_task_4 = asyncio.create_task(tone_out_4.toneout_4())
    bluetooth_task = asyncio.create_task(bluetooth.bluetooth_fsm())
    pulsetimer_task_1 = asyncio.create_task(pulsetimer.timing_pulse_1())
    pulsetimer_task_2 = asyncio.create_task(pulsetimer.timing_pulse_2())
    pulsetimer_task_3 = asyncio.create_task(pulsetimer.timing_pulse_3())
    pulsetimer_task_4 = asyncio.create_task(pulsetimer.timing_pulse_4())
    completetimer_task_1 = asyncio.create_task(pulsetimer.timing_complete_1())
    completetimer_task_2 = asyncio.create_task(pulsetimer.timing_complete_2())
    completetimer_task_3 = asyncio.create_task(pulsetimer.timing_complete_3())
    completetimer_task_4 = asyncio.create_task(pulsetimer.timing_complete_4())
    bt_retry_timer_task = asyncio.create_task(pulsetimer.bt_retry_timer())
    bt_query_timer_task = asyncio.create_task(pulsetimer.bt_query_timer())



    await asyncio.gather(main_fsm_task,
                        print_state_task,
                        ring_pwm1_task,
                        ring_pwm2_task,
                        ring_pwm3_task,
                        ring_pwm4_task,
                        tone_task_1,
                        tone_task_2,
                        tone_task_3,
                        tone_task_4,
                        dtmf_task,
                        bluetooth_task,
                        pulsetimer_task_1,
                        pulsetimer_task_2,
                        pulsetimer_task_3,
                        pulsetimer_task_4,
                        completetimer_task_1,
                        completetimer_task_2,
                        completetimer_task_3,
                        completetimer_task_4,
                        bt_retry_timer_task,
                        bt_query_timer_task
                        )


asyncio.run(main())
