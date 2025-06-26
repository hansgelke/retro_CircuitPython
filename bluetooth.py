# License           : MIT
# File Name         : bluetooth.py
# Description       : Controlling RN52 Bluetooth module
#                    
# Revision History  :
# Date	19.6.2025	Author 	Hans Gelke		Comments Prototype
# ------------------------------------------------------------------
# 19/06/2025	Hans Gelke	Initial			V0.1

import time
import digitalio
import board
import busio
import asyncio
import tones
import retro_fsm_object
import retro_control
import pulsetimer
import utils
import ringing

bt_cmd = digitalio.DigitalInOut(board.GP19)
bt_cmd.direction = digitalio.Direction.OUTPUT

bt_int = digitalio.DigitalInOut(board.GP20)
bt_int.direction = digitalio.Direction.INPUT

bt_baud = digitalio.DigitalInOut(board.GP21)
bt_baud.direction = digitalio.Direction.OUTPUT

bt_pwr = digitalio.DigitalInOut(board.GP22)
bt_pwr.direction = digitalio.Direction.OUTPUT

uart = busio.UART(board.GP16, board.GP17, baudrate=115200, timeout=0)

#Power on = true////////////////////////////////////////////////////////
bt_pwr.value = True
#baud rate = 115200
bt_baud.value = True
#command mode: bt_cmd = 0
bt_cmd.value = False


class BlueTooth():
    def __init__(self):
        self.state = 0
        self.past_state = 0
        self.bt_connect = 0
        self.calling_machine = 0
        self.digit_memory = [0]*25
        self.bt_digit_count = 0
        self.bt_retry_timeout = 600
        self.bt_query_timeout = 50
        self.bt_loop1_pressed = False
        self.bt_loop1_released = False
        self.bt_loop2_pressed = False
        self.bt_loop2_released = False
        self.bt_loop3_pressed = False
        self.bt_loop3_released = False
        self.bt_loop4_pressed = False
        self.bt_loop4_released = False

    def bts_print(self):
        if self.state != self.past_state:
            print("BT_FSM:", "State:", self.state )
        self.past_state = self.state


#-----------------------------------------------------------
#   Bluetooth FSM State 0:
#   - Waits until bt_connect Flag from main FSM is set
#   - Loops until BT module is connected to iphone
#   - evtl. implement a timeout and a message "Connect iphone"
#-------------------------------------------------------------

    def bt_fsm_logic(self):
        if self.state == 0:
            #If retry timer is expired, check if BT is still connected
            if pulsetimer.pulsetimer.bt_retry_time == 0:
                self.state = 5
            else:
                self.state = 0



#-----------------------------------------------------------
#   Bluetooth FSM State 1:
#   Dials the number handed down from Main FSM
#-------------------------------------------------------------
        elif self.state == 1:
            if bt_fsm.bt_connect == 1:
                self.bt_digit_count = retro_control.fsm1.digit_count
            elif bt_fsm.bt_connect == 2:
                self.bt_digit_count = retro_control.fsm2.digit_count
            elif bt_fsm.bt_connect == 3:
                self.bt_digit_count = retro_control.fsm3.digit_count
            elif bt_fsm.bt_connect == 4:
                self.bt_digit_count = retro_control.fsm4.digit_count
            else:
                self.bt_digit_count = retro_control.fsm4.digit_count
            #print("Dialing Number:", retro_control.fsm4.digit_memory)
            #Enable in case of debugging: p_number = "A,0444800686\n"
            index = 0
            fitted_array = [0] * (self.bt_digit_count - 1)
            for y in fitted_array:
                if index < self.bt_digit_count - 1:
                    if self.digit_memory[index+1] == 10:
                        fitted_array[index] = 0
                    else:
                        fitted_array[index] = self.digit_memory[index+1]
                    index = index + 1
                else:
                    break

            prefix = "A,"
            postfix = "\n"

            number_string = ''.join(map(str, fitted_array))
            strings_to_join = [prefix, number_string, postfix]
            p_number = "".join(strings_to_join)
            print("Sent to BT:", p_number)
            #Uncomment below to avoid dialing number during debug
            uart.write(bytes(p_number,"ascii"))
            #immediate read, to eliminate message AOK from buffer
            data = uart.readline
            pulsetimer.pulsetimer.bt_query_time = self.bt_query_timeout
            self.state = 2

#-----------------------------------------------------------
#   Bluetooth FSM State 2:
#   - Checks if number was accepted by iphone
#   (outgoing call established)
#   - Loop until call is established evtl. implement a timeout
#-------------------------------------------------------------
        elif self.state == 2:
            if bt_fsm.bt_connect == 0:
                cmd = "E\n" #Terminate a call
                uart.write(bytes(cmd,"ascii"))
                self.state = 0
            else:
                if pulsetimer.pulsetimer.bt_query_time == 0:
                    pulsetimer.pulsetimer.bt_query_time = self.bt_query_timeout
                    cmd = "q\n" #query bt module status
                    s1 = "04" #outgoing call established
                    uart.write(bytes(cmd,"ascii"))
                    data = uart.readline()  # Read a line from UART
                    if data:  # Ensure data is not Nonet
                        ascii_string = data.decode("ascii")
                        if ascii_string[2:4] == s1:
                            #print("call established", ascii_string[2:4])
                            #tones.tonegenerator.signaltone[self.calling_machine] = "ring_gb"
                            pulsetimer.pulsetimer.bt_query_time = self.bt_query_timeout
                            self.state = 3
                        else:
                            #print("Call not established, wait", ascii_string[2:4])
                            self.state = 2
                else:
                    self.state = 2
#-----------------------------------------------------------
#   Bluetooth FSM State 3:
#   Wait here if recepient lifted the receiver
#-------------------------------------------------------------
        elif self.state == 3:
            if bt_fsm.bt_connect == 0:
                cmd = "E\n" #Terminate a call
                uart.write(bytes(cmd,"ascii"))
                self.state = 0
            else:
                if pulsetimer.pulsetimer.bt_query_time == 0:
                    pulsetimer.pulsetimer.bt_query_time = self.bt_query_timeout
                    cmd = "q\n" #query bt module status
                    s1 = "06" #active call, recipient lifted receiver
                    uart.write(bytes(cmd,"ascii"))
                    data = uart.readline()  # Read a line from UART
                    if data:  # Ensure data is not Nonet
                        ascii_string = data.decode("ascii")
                        if ascii_string[2:4] == s1:
                            #print("Call active", ascii_string[2:4])
                            #tones.tonegenerator.signaltone[self.calling_machine] = "stop"
                            pulsetimer.pulsetimer.bt_query_time = self.bt_query_timeout
                            tones.tonegenerator.signaltone[bt_fsm.bt_connect] = "off"

                            self.state = 4
                        else:
                            #print("Waiting for call to be accepted", ascii_string[2:4])
                            #self.state = 3
                            #evtl implement tiemout if callee does not answer
                            self.state = 3
                    else:
                        self.state = 3
#-----------------------------------------------------------
#   Bluetooth FSM State 4:
#   The call is active, wait until the recipient hangs up
#-------------------------------------------------------------

        elif self.state == 4:
            if bt_fsm.bt_connect == 0:
                cmd = "E\n" #Terminate a call
                uart.write(bytes(cmd,"ascii"))
                self.state = 0
            else:
                if pulsetimer.pulsetimer.bt_query_time == 0:
                    pulsetimer.pulsetimer.bt_query_time = self.bt_query_timeout
                    cmd = "q\n" #query bt module status
                    s1 = "03" #Hang Up
                    uart.write(bytes(cmd,"ascii"))
                    data = uart.readline()  # Read a line from UART
                    if data:  # Ensure data is not Nonet
                        #print("State 4 data", data)
                        ascii_string = data.decode("ascii")
                        if ascii_string[2:4] == s1:
                            #print("Network terminated", ascii_string[2:4])
                            bt_fsm.bt_connect = 0
                            self.state = 0
                    else:
                        self.state = 4
                else:
                    self.state = 4

#-----------------------------------------------------------
#   Bluetooth FSM State 5: Check periodically if BT connected
#-------------------------------------------------------------

        elif self.state == 5:
            cmd = "q\n"
            s1 = "03"
            #s2 =
            uart.write(bytes(cmd,"ascii"))
            data = uart.readline()  # Reads line until n
            #print("Data:", data)
            self.state = 7
            if data:  # Ensure data is not Nonet
                ascii_string = data.decode("ascii")
                if ascii_string[2:4] == s1:
                    #print("iphone connected", ascii_string[2:4])
                    #tones.tonegenerator.signaltone[self.calling_machine] = "dial_de"
                    pulsetimer.pulsetimer.bt_retry_time = self.bt_retry_timeout
                    self.state = 7
                else:
                    #print("Error, iphone not connected", ascii_string[2:4])
                    pulsetimer.pulsetimer.bt_retry_time = self.bt_retry_timeout
                    self.state = 6
                    #temporär to stop looping
            else:
                self.state = 5

#-----------------------------------------------------------
#   Bluetooth FSM State 6: Bluetooth is not connected
#-------------------------------------------------------------

        elif self.state == 6:
            #It got into this state, because BT is not connected
            #Wait in this state until timer is exppired and retry connection check
            if pulsetimer.pulsetimer.bt_retry_time == 0:
                pulsetimer.pulsetimer.bt_retry_time = self.bt_retry_timeout
                self.state = 5
            else:
                #Otherwise stay here until timer expired
                self.state = 6


#-----------------------------------------------------------
#   Bluetooth FSM State 7:
#   If in this state, the BT Module is connected to tge phone
#-------------------------------------------------------------

        elif self.state == 7:
            #print("Retry counter", pulsetimer.pulsetimer.bt_retry_time)
            #It got into this state, because BT is connected
            #If connection is requested, go to state 1
            if pulsetimer.pulsetimer.bt_query_time == 0:
                pulsetimer.pulsetimer.bt_query_time = self.bt_query_timeout
                cmd = "q\n" #query bt module status
                s1 = "05" #someone calls mobile number
                uart.write(bytes(cmd,"ascii"))
                data = uart.readline()  # Read a line from UART
                if data:  # Ensure data is not Nonet
                    ascii_string = data.decode("ascii")
                    if ascii_string[2:4] == s1:
                        #print("Incoming Call requested", ascii_string[2:4])
                        #tones.tonegenerator.signaltone[self.calling_machine] = "stop"
                        pulsetimer.pulsetimer.bt_query_time = self.bt_query_timeout
                        #Call phone 4
                        ringing.ringgenerator.call_register = utils.set_bit(ringing.ringgenerator.call_register, 4)
                        self.con_register = 4
                        self.state = 8
                    else:
                        #print("Waiting for call to be accepted", ascii_string[2:4])
                        #self.state = 3
                        #evtl implement tiemout if callee does not answer
                        self.state = 7

            #If one of the phones requests to call outside (bt_connect 1-4)
            elif bt_fsm.bt_connect > 0:
                tones.tonegenerator.signaltone[bt_fsm.bt_connect] = "ring_ge"
                self.state = 1
            elif pulsetimer.pulsetimer.bt_retry_time == 0:
                pulsetimer.pulsetimer.bt_retry_time = self.bt_retry_timeout
                self.state = 5
            else:
                #Otherwise stay here and wait for bt_connect to become true until timer expired
                self.state = 7

#-----------------------------------------------------------
#   Bluetooth FSM State 8:
#   An external Call is requested, wait until called phone lifts receiver
#-------------------------------------------------------------
        elif self.state == 8:
            #The calle Party lifts receiver
            if self.bt_loop4_pressed:
                #The call register bit of phone 4 is cleared
                ringing.ringgenerator.call_register = utils.clear_bit(ringing.ringgenerator.call_register, 4)
                #print("Cleared call register:", machine,"Call_Register:", ringing.ringgenerator.call_register)
                # Ringing is stopped
                utils.set_ring(False, 4)
                #Accept incoming call
                cmd = "c\n" # Accept incoming call
                uart.write(bytes(cmd,"ascii"))
                data = uart.readline()
                print("Data after accepting call:", data)
                # in state 9 is the connection is established
                self.state = 9
            else:
                self.state = 8

#-----------------------------------------------------------
#   Bluetooth FSM State 9:
#   The call is established, wait until hung up again
#-------------------------------------------------------------
        elif self.state == 9:
        # Check if Network phone has hangup
            if pulsetimer.pulsetimer.bt_query_time == 0:
                pulsetimer.pulsetimer.bt_query_time = self.bt_query_timeout
                cmd = "q\n" #query bt module status
                s1 = "03" #Hang Up
                uart.write(bytes(cmd,"ascii"))
                data = uart.readline()  # Read a line from UART
                if data:  # Ensure data is not Nonet
                    ascii_string = data.decode("ascii")
                    if ascii_string[2:4] == s1:
                        print("Network terminated on icoming call", ascii_string[2:4])
                        self.state = 0
                        #Here main fsm4 sends a bussy signal
                        retro_control.fsm4.state = 11
                    else:
                        self.state = 9
                else:
                    self.state = 9
        # When Analog Phone is hang up
            elif self.bt_loop4_released:
                cmd = "E\n" # Terminate active call
                uart.write(bytes(cmd,"ascii"))
                data = uart.readline()
                print("Data after hanging up:", data)

                ringing.ringgenerator.engaged_register = utils.clear_bit(ringing.ringgenerator.engaged_register, 4)
                self.state = 0
            else:
                self.state = 9


bt_fsm = BlueTooth()

async def bluetooth_fsm():

    bt_connect = False
    #increase speaker Volume
    cmd = "SS,0F\n" #query bt module status
    uart.write(bytes(cmd,"ascii"))



    while True:
         #calls FSM logic, hands down signal connect
         #Connect active when MainFsm requests connection to BT
        bt_fsm.bt_fsm_logic()
        await asyncio.sleep(0)

