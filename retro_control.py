#*******************************************************************
# License           : MIT
# File Name         : retro_control.py
# Description       : FSM control
#                    
# Revision History  :
# Date	19.6.2025	Author 	Hans Gelke		Comments Prototype
# ------------------------------------------------------------------
# 19/06/2025	Hans Gelke	Initial			V0.1
#
#*****************************************************************/
import time
import asyncio
import board
import digitalio
import utils
import ringing
import bluetooth
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
import pwmio
from retro_fsm_object import MainFSM



hangup_time = True

#Pulling this pin low puts SLICs in Power savings mode
psm = digitalio.DigitalInOut(board.GP15)
psm.direction = digitalio.Direction.OUTPUT
psm.value = True

#loop1 = False
#loop1_del = False

#--------------------------------------------
# Main FSM control
#--------------------------------------------
fsm1 = MainFSM()
fsm2 = MainFSM()
fsm3 = MainFSM()
fsm4 = MainFSM()


async def print_state():
    while True:
        fsm1.fsm_print()
        fsm2.fsm_print()
        fsm3.fsm_print()
        fsm4.fsm_print()
        #bluetooth.bt_fsm.bts_print()
        await asyncio.sleep(0)

async def fsm():

    loop1 = False
    #loop1_pressed = False
    #loop1_released = False
    prev_loop1 = False

    loop2 = False
    #loop2_pressed = False
    #loop2_released = False
    prev_loop2 = False

    loop3 = False
    #loop3_pressed = False
    #loop3_released = False
    prev_loop3 = False

    loop4 = False
    #loop4_pressed = False
    #loop4_released = False
    prev_loop4 = False

    loop1 = Debouncer(DigitalInOut(board.GP5))
    loop2 = Debouncer(DigitalInOut(board.GP4))
    loop3 = Debouncer(DigitalInOut(board.GP8))
    loop4 = Debouncer(DigitalInOut(board.GP12))

    while True:
        # Edge detector for Loop 1
        loop1.update()
        cur_loop1 = loop1.value
        if cur_loop1 == True and prev_loop1 == False:
            bluetooth.bt_fsm.bt_loop1_pressed = True
        elif cur_loop1 == False and prev_loop1 == True:
            bluetooth.bt_fsm.bt_loop1_released = True
        else:
            bluetooth.bt_fsm.bt_loop1_pressed = False
            bluetooth.bt_fsm.bt_loop1_released = False
        prev_loop1 = cur_loop1

        # Edge detector for Loop 2
        loop2.update()
        cur_loop2 = loop2.value
        if cur_loop2 == True and prev_loop2 == False:
            bluetooth.bt_fsm.bt_loop2_pressed = True
        elif cur_loop2 == False and prev_loop2 == True:
            bluetooth.bt_fsm.bt_loop2_released = True
        else:
            bluetooth.bt_fsm.bt_loop2_pressed = False
            bluetooth.bt_fsm.bt_loop2_released = False
        prev_loop2 = cur_loop2

        # Edge detector for Loop 3
        loop3.update()
        cur_loop3 = loop3.value
        if cur_loop3 == True and prev_loop3 == False:
            bluetooth.bt_fsm.bt_loop3_pressed = True
        elif cur_loop3 == False and prev_loop3 == True:
            bluetooth.bt_fsm.bt_loop3_released = True
        else:
            bluetooth.bt_fsm.bt_loop3_pressed = False
            bluetooth.bt_fsm.bt_loop3_released = False
        prev_loop3 = cur_loop3

        # Edge detector for Loop 4
        loop4.update()
        cur_loop4 = loop4.value
        if cur_loop4 == True and prev_loop4 == False:
            bluetooth.bt_fsm.bt_loop4_pressed = True
        elif cur_loop4 == False and prev_loop4 == True:
            bluetooth.bt_fsm.bt_loop4_released = True
        else:
            bluetooth.bt_fsm.bt_loop4_pressed = False
            bluetooth.bt_fsm.bt_loop4_released = False
        prev_loop4 = cur_loop4


    #Call FSM Logic function
        fsm1.fsm_logic(1, (bluetooth.bt_fsm.bt_loop1_pressed), (bluetooth.bt_fsm.bt_loop1_released))
        await asyncio.sleep(0)
        fsm2.fsm_logic(2, (bluetooth.bt_fsm.bt_loop2_pressed), (bluetooth.bt_fsm.bt_loop2_released))
        await asyncio.sleep(0)
        fsm3.fsm_logic(3, (bluetooth.bt_fsm.bt_loop3_pressed), (bluetooth.bt_fsm.bt_loop3_released))
        await asyncio.sleep(0)
        fsm4.fsm_logic(4, (bluetooth.bt_fsm.bt_loop4_pressed), (bluetooth.bt_fsm.bt_loop4_released))
        await asyncio.sleep(0)

        #if ((utils.test_bit(ringing.ringgenerator.engaged_register, 1)) or
         #  (utils.test_bit(ringing.ringgenerator.engaged_register, 2)) or
          # (utils.test_bit(ringing.ringgenerator.engaged_register, 3)) or
           #(utils.test_bit(ringing.ringgenerator.engaged_register, 4))):
            #psm.value = True
            #print("PSM:", psm.value)
        #else:
         #   psm.value = True

def extract_number(phone_number,size):

    print("phone number:",phone_number)
    print("Size:",size)

    index = 0

    fitted_array = [0] * size

    for y in phone_number:
        if index < size:
            if phone_number[index] == 10:
                fitted_array[index] = 0
            else:
                fitted_array[index] = phone_number[index]
            index = index + 1
        else:
            break

    #print("Phone:", fitted_array)
    return fitted_array

def calc_number(number_array):
    phone_number = 10 * number_array[0] + number_array[1]
    print("calculated number:",phone_number)
    return phone_number


