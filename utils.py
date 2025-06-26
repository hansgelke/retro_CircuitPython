import asyncio
import board
import digitalio
import keypad
import pwmio
import retro_control
import retro_fsm_object
import ringing


def test_bit(value, bit):
    mask = 1 << bit
    if (value & mask):
        return True
    else:
        False

def set_bit(value, bit):
    mask = 1 << bit
    value |= mask
    return value

def clear_bit(value, bit):
    mask = 1 << bit
    value &= ~mask
    return value

def set_ring(on, phone):
    if phone == 1:
        ringing.ringgenerator.ringring_1 = on
    elif phone == 2:
        ringing.ringgenerator.ringring_2 = on
    elif phone == 3:
        ringing.ringgenerator.ringring_3 = on
    elif phone == 4:
        ringing.ringgenerator.ringring_4 = on

async def timer(set):
    while True:
        if set == True:
            await asyncio.sleep(5)
            timer_go = True
        else:
            timer_go = False
        await asyncio.sleep(0)
