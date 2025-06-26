#*******************************************************************
# License           : MIT
# File Name         : retro_fsm_object.py
# Description       : Output for each phone
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
import retro_control
import utils
import ringing
import tones
import time
import busio
import digitalio
import bluetooth
import pulsetimer
import dtmf

class MainFSM():

    def __init__(self):
        self.state = 0
        self.past_state = 0
        #self.count = 0
        self.time = 0
        self.uptime = 33
        self.dialtime = 10
        self.machine = 0
        self.pulse_count = 0
        self.event_pressed = False
        self.event_released = False
        self.con_register = 0
        self.ext_flag = False
        self.digit_count = 0
        #bluetooth.bt_fsm.digit_count
        self.complete_timeout = 200
        self.dec_intern = 00

        ringing.ringgenerator.call_register = 0
        ringing.ringgenerator.engaged_register = 0
        tones.tonegenerator.signaltone = [0,0,0,0,0]



    def fsm_print(self):
        #print("STATE3")
        if self.state != self.past_state:
            print("Machine:", self.machine, "State:", self.state)
        if ringing.ringgenerator.past_engaged_register != ringing.ringgenerator.engaged_register:
            print("Engaged Register:", ringing.ringgenerator.engaged_register)

        self.past_state = self.state
        ringing.ringgenerator.past_call_register = ringing.ringgenerator.call_register
        ringing.ringgenerator.past_engaged_register = ringing.ringgenerator.engaged_register

    def fsm_logic(self,machine, event_pressed, event_released):
        self.machine = machine
        bluetooth.bt_fsm.calling_machine = machine
        self.event_pressed = event_pressed
        self.event_released = event_released
        #----------------------------------------------------------
        #State 0: Idle state, wait until soeone lifts receiver
        #or wait until the other party signalizes this phone to ring
        #----------------------------------------------------------
        if self.state == 0:
            #idle state, all tones are turned off

            #Set digit counter to zero
            self.digit_count = 0
            #tones.tonegenerator.signaltone[machine] = "off"
          #  #The destination checks if call register bit is set, then goes to state 8
            if utils.test_bit(ringing.ringgenerator.call_register, machine):
                ringing.ringgenerator.engaged_register = utils.set_bit(ringing.ringgenerator.engaged_register, machine)
                self.state = 8
            #User lifts receiver to make a call
            elif self.event_pressed:
                #The engaged register is set to mark, this line can not be called anymore
                ringing.ringgenerator.engaged_register = utils.set_bit(ringing.ringgenerator.engaged_register, machine)
                #Load dial complete timer
                pulsetimer.pulsetimer.complete_timer[machine] = self.complete_timeout
                #Clear flag detecting ecternal call
                self.ext_flag = False
                if self.machine == 1:
                    tones.tonegenerator.signaltone[machine] = "dial_de"
                elif self.machine == 2:
                    tones.tonegenerator.signaltone[machine] = "dial_us"
                elif self.machine == 3:
                    tones.tonegenerator.signaltone[machine] = "dial_us"
                else:
                    tones.tonegenerator.signaltone[machine] = "dial_ch"

                self.state = 1
            else:
                self.state = 0

#----------------------------------------------------------
# State 1: Loop is closed(high), waiting for dialing pulse_low
#   Error timeout in case somone is not dialing (implement later)
#----------------------------------------------------------
        elif self.state == 1:
            #print("Engaged Register:", ringing.ringgenerator.engaged_register)
            #the FSM watches for the loop to be oepened
            #it then goes to state 13 to count the pulses
            #The timeout_pulse differeniates between a hangup or pulse
            #Here is an unexplainable bug, after a few pulses
            #self.event_released seems not react anymore
            #after about 15 dialed numbers
            if self.event_released:
                self.pulse_count = 0
                tones.tonegenerator.signaltone[machine] = "off"
                self.state = 2
                pulsetimer.pulsetimer.pulse_timer[machine] = 9
            #The complete timeout occurs, when all numbers are dialed after about 3s
            elif (pulsetimer.pulsetimer.complete_timer[machine] == 0) and (self.ext_flag == True):
                #When the complete timeout occurs, the ext_flag can be cleared
                self.ext_flag = False
                #Here the external calls are processed
                #print("Digit Count:", retro_control.extract_number(bluetooth.bt_fsm.digit_memory, bluetooth.bt_fsm.digit_count))
                bluetooth.bt_fsm.bt_connect = machine
                self.state = 15
            elif dtmf.dtmfdecoder.dtmf_flag == True:
                self.state = 3
            else:
                self.state = 1

#----------------------------------------------------------
#State 2: Loop is open,  waiting for dialing pulse to go high
#         Wait  until loop closed. Timeout > 70 ms
#         On timeout go to idle self.state 0 means user hang up
#         Loop Closed before timeout brings it to state 3
#         Dial pulse is incremented
#----------------------------------------------------------
        # count the pulses of the number
        elif self.state == 2:
            if self.event_pressed:
        #The count is incremened
                self.pulse_count = self.pulse_count + 1
                #define a timeout to differenciate between hangup or pulse
                pulsetimer.pulsetimer.pulse_timer[machine] = 9
                self.state = 3
            # if the timeout enters, go to state 0 because user hung up
            elif pulsetimer.pulsetimer.pulse_timer[machine] == 0:
                ringing.ringgenerator.engaged_register = utils.clear_bit(ringing.ringgenerator.engaged_register, machine)
                self.con_register = 0
                self.state = 0
            else:
                self.state = 2

#----------------------------------------------------------
#State 3: After a dialing Pulse(low) FSM waits until pulse
#         goes low again for evtl. next pulse
#         If Timeout the dial is completed
#----------------------------------------------------------
        elif self.state == 3:
            #Wait for loop to go high
            if self.event_released:
                self.state = 2
                pulsetimer.pulsetimer.pulse_timer[machine] = 9

            #When rotary dialer finished (Wählscheibe abgelaufen)
            elif ((pulsetimer.pulsetimer.pulse_timer[machine] == 0) or (dtmf.dtmfdecoder.dtmf_flag) == True):
                print("Pulse Timer:", pulsetimer.pulsetimer.pulse_timer[machine])
                print("DTMF Flag:", dtmf.dtmfdecoder.dtmf_flag)

                if (dtmf.dtmfdecoder.dtmf_flag == True):
                    dtmf.dtmfdecoder.dtmf_flag = False
                    #Store number in array
                    #digit_count is the index into the array
                    #array index increments after every dialed digit
                    bluetooth.bt_fsm.digit_memory[self.digit_count] = int(dtmf.dtmfdecoder.digit)
                    #Digit count is index of array, it starts with 0 and increments after "Wählscheibe abgelaufen"
                    self.digit_count = self.digit_count + 1


                else:
                    bluetooth.bt_fsm.digit_memory[self.digit_count] = self.pulse_count
                    #If source is dtmf, write digit from dtmf decoder in que
                    self.digit_count = self.digit_count + 1
                #After the digit incremented, load the number complete timeout (3s)
                pulsetimer.pulsetimer.complete_timer[machine] = self.complete_timeout
                #Check if number has two digits, and the first number is not a "9"
                #Use a function to extract a number from digit_memory array
                if (self.digit_count == 1):
                    if (retro_control.extract_number(bluetooth.bt_fsm.digit_memory, self.digit_count)[0] == 9):
                        self.ext_flag = True
                        print("External Flag:", self.ext_flag)
                        self.state = 1
                    else:
                        self.state = 1

                elif (self.digit_count == 2) and (self.ext_flag == False):
                    #Enable the ring signal for the device that is calling
                    print("digit count:", self.digit_count)
                    print("digit memory:",bluetooth.bt_fsm.digit_memory)
                    self.dec_intern = retro_control.calc_number(bluetooth.bt_fsm.digit_memory)
                    #print("Internal call to Phone:", self.pulse_count)
                    #print("Digit Memory:", bluetooth.bt_fsm.digit_memory)
                    print("Decimal internal number:", self.dec_intern)
                    #print("Bit:", tones.tonegenerator.directory[self.dec_intern])
                    #print("Engaged Register:", ringing.ringgenerator.engaged_register)
                    #Check if line called is not engaged
                    if utils.test_bit(ringing.ringgenerator.engaged_register, tones.tonegenerator.directory[int(self.dec_intern)]):
                        self.state = 10
                    else:
                        if self.dec_intern == 11: #German phone, German Ring tone
                            tones.tonegenerator.signaltone[machine] = "ring_ge"
                            print("Signal state:" ,tones.tonegenerator.signaltone )
                            #Set connection register of phone 1 to connect to this machine
                            retro_control.fsm1.con_register = machine

                        if self.dec_intern == 12: #German phone, German Ring tone
                            tones.tonegenerator.signaltone[machine] = "ring_ge"
                            #Set connection register of phone 2 to connect to this machine
                            retro_control.fsm2.con_register = machine

                        if self.dec_intern == 13: #German phone, German Ring tone
                            tones.tonegenerator.signaltone[machine] = "ring_gb"
                            #Set connection register of phone 3 to connect to this machine
                            retro_control.fsm3.con_register = machine

                        if self.dec_intern == 14: #German phone, German Ring tone
                            tones.tonegenerator.signaltone[machine] = "ring_ge"
                            #Set connection register of phone 4 to connect to this machine
                            retro_control.fsm4.con_register = machine

                        if (self.dec_intern >= 15 and self.dec_intern <= 89):

                         #German phone, German Ring tone
                            tones.tonegenerator.signaltone[machine] = "announce_1"
                            #Set connection register of phone 4 to connect to this machine
                            retro_control.fsm4.con_register = machine




                        #Now set bit in call_request register
                        ringing.ringgenerator.call_register = utils.set_bit(ringing.ringgenerator.call_register, tones.tonegenerator.directory[self.dec_intern])
                        # set the connection multiplexer to input the other party
                        self.con_register = tones.tonegenerator.directory[self.dec_intern]
                        #print("Origin Machine sets Call Register:",ringing.ringgenerator.call_register)
                        #print("Origin Machine sets engaged Register:",ringing.ringgenerator.engaged_register)
                        self.state = 7
                else:
                    #If there are less then 2 digits continue watching dial pulses
                    #Prepare for next number to be dialed
                    self.pulse_count = 0
                    self.state = 1
            else:
                #Wait for pulse to go high again, if not timeout, rotary completed
                self.state = 3



#----------------------------------------------------------\
#State 7: the party is dialed, it must send a request to the other FSM
#----------------------------------------------------------\
        elif self.state == 7:
            #Caller: sent a request to other party
            #Caller:Stay in this state until the destination clears the bit in the request register
            #then go to State 9
            if not(utils.test_bit(ringing.ringgenerator.call_register, tones.tonegenerator.directory[self.dec_intern])):
                tones.tonegenerator.signaltone[machine] = "off"
                self.state = 9
            #Caller has hangup before call was answered
            elif self.event_released:
                #Turn ring tone of if caller hangs up early
                tones.tonegenerator.signaltone[machine] = "off"
                ringing.ringgenerator.call_register = utils.clear_bit(ringing.ringgenerator.call_register, tones.tonegenerator.directory[self.dec_intern])
                ringing.ringgenerator.engaged_register = utils.clear_bit(ringing.ringgenerator.engaged_register, machine)
                self.con_register = 0
                self.state = 0
            else:
                self.state = 7 #stay in state 7 until confirmation from other party, or hangup
#----------------------------------------------------------
#State 8: The called party rings its device
#
#---------------------------------------------------
        elif self.state == 8:
        #The called station lifts receiver
           # print("Ringing Phone:", self.machine, "Request accepted")
           # print("Ringing Phone:", machine,"Call_Register:", ringing.ringgenerator.call_register)
            utils.set_ring(True, machine)
            #The called party lifts the receiver
            if self.event_pressed:
                #The call register bit is cleared
                ringing.ringgenerator.call_register = utils.clear_bit(ringing.ringgenerator.call_register, machine)
                #print("Cleared call register:", machine,"Call_Register:", ringing.ringgenerator.call_register)
                # Ringing is stopped
                utils.set_ring(False, machine)
                # state 9 is the state in which connection is established
                self.state = 9
                #The caller gave up and cleared the call_register bit
                #he machine which is called, checks its bit in the call register
            elif not(utils.test_bit(ringing.ringgenerator.call_register, machine)):
                #print("State of Call_Register:", ringing.ringgenerator.call_register)
                #print("Directory", tones.tonegenerator.directory[self.dec_intern])
                utils.set_ring(False, machine)
                tones.tonegenerator.signaltone[machine] = "off"
                ringing.ringgenerator.engaged_register = utils.clear_bit(ringing.ringgenerator.engaged_register, machine)
                self.con_register = 0
                self.state = 0
                #Stay here while ringing, as long as call_register bit is set
            else:
                #otherwise go back to idle, means caller gave up
                self.state = 8
#----------------------------------------------------------
#State 9: Phone answered, the connection is established
#----------------------------------------------------------
        elif self.state == 9:
       # When connected phone hangs up first, send bussy signal
            if (self.con_register == 1) and (retro_control.fsm1.con_register == 0):
                    self.state = 11
            elif (self.con_register == 2) and (retro_control.fsm2.con_register == 0):
                    self.state = 11
            elif (self.con_register == 3) and (retro_control.fsm3.con_register == 0):
                    self.state = 11
            elif (self.con_register == 4) and (retro_control.fsm4.con_register == 0):
                    self.state = 11
        # When Phone is hang up
            elif self.event_released:
                tones.tonegenerator.signaltone[machine] = "off"
                ringing.ringgenerator.engaged_register = utils.clear_bit(ringing.ringgenerator.engaged_register, machine)
                #set multiplexer back to 0
                self.con_register = 0
                self.state = 0

#----------------------------------------------------------
#State 10: Engaged
#----------------------------------------------------------
        # Calling phone, engaged
        elif self.state == 10:
            tones.tonegenerator.signaltone[machine] = "engaged"
            if self.event_released:
                tones.tonegenerator.signaltone[machine] = "off"
                ringing.ringgenerator.engaged_register = utils.clear_bit(ringing.ringgenerator.engaged_register, machine)
                self.con_register = 0
                self.state = 0
            else:
                self.state = 10

#----------------------------------------------------------
#State 11: Hangup after call
#----------------------------------------------------------
        # Phone is hung up, not hung up party hears engaged
        elif self.state == 11:
            self.con_register = 0
            tones.tonegenerator.signaltone[machine] = "engaged"
            if self.event_released:
                tones.tonegenerator.signaltone[machine] = "off"
                ringing.ringgenerator.engaged_register = utils.clear_bit(ringing.ringgenerator.engaged_register, machine)
                self.con_register = 0
                #set multiplexer back to 0
                self.state = 0
            else:
                self.state = 11



#----------------------------------------------------------
#State 15: Wait until Bluetooth call is completed
#----------------------------------------------------------
        elif self.state == 15:

            # When Analog Phone was hung up
            if self.event_released:
                #If analog caller hangs up receiver
                #force bluetooth connection bit to false
                bluetooth.bt_fsm.bt_connect = 0
                print("Analog loop opened")
                self.state = 0

            #The bluetooth module removes connect after the call is completed
            # The FSM outputs bussy sign
            elif bluetooth.bt_fsm.bt_connect == 0:
                self.state = 11
            else:
                #print("loop to 15")
                self.state = 15
#----------------------------------------------------------
#State 16: External number is called, wait for other party to answer
#----------------------------------------------------------
        elif self.state == 16:

                self.state = 16



#----------------------------------------------------------
#State 17: Stay in this state as long as call is active
#----------------------------------------------------------
        elif self.state == 17:

                self.state = 17
