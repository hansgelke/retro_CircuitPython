# Configuring U-Boot

There are two use cases for use to fiddle with U-Boot:

1. Switching between booting the root filesystem from the SD card and over NFS.
1. Settings the `maxcpus=1` boot argument for the scheduling lab.

For these purposes, we override the boot script and assemble our own bootargs for the kernel.

## Understanding the Raspberry Pi Boot Process

(This is a section of an online article ([source][rpi-boot-proc-article]), copied here in case the link ever becomes dead.
You may continue reading the [next section](#boot-arguments).)

More traditional embedded systems contain on-board flash memory mapped at the reset vector.
Upon reset, the CPU will start loading instructions beginning at the reset vector.
In these systems, U-Boot is normally flashed into non-volatile memory at the reset vector.
The on-board flash may also include an environment variable space, the Linux kernel and filesystem.

To reduce cost, the Raspberry Pi (with the exception of the compute module) omits any on-board non-volatile memory.
Rather, a SD/MMC card slot is provided for this purpose.
This also offers convenience – in some environments – as SD cards are not only cheap, but easy to swap out and upgrade.

The VideoCore GPU is responsible for booting the Broadcom BCM283x system on a chip (SoC), contained on the Raspberry Pi.
The SoC will boot up with its main ARM processor held in reset.

The VideoCore GPU loads the first stage bootloader from a ROM embedded within the SoC.
This extremely simple first stage bootloader is designed to load the second stage bootloader from a FAT32 or FAT16 filesystem located on the SD Card.

The second stage bootloader – bootcode.bin – is executed on the VideoCore GPU and loads the third stage bootloader – start.elf.
Both these bootloaders are closed firmware, available as binary blobs from Broadcom.

The third stage bootloader – start.elf – is where all the action happens.
It starts by reading config.txt, a text file containing configuration parameters for both the VideoCore (Video/HDMI modes, memory, console frame buffers etc) and the Linux Kernel (load addresses, device tree, UART/console baud rates etc).

Once the config.txt file has been parsed, the third stage bootloader will load cmdline.txt – a file containing the kernel command line parameters to be passed to the kernel and kernel.img – the Linux kernel.
Both are loaded into shared memory allocated to the ARM processor.
Once complete, the third stage bootloader will release the ARM processor from reset.
Your kernel should now start booting.

Hence, the Linux kernel can be booted without the need of U-Boot.
However, as indicated U-Boot provides many useful tools for developing and debugging embedded systems such as loading a newly compiled kernel via TFTP over the network for testing.
This eliminates the slow and painful process of copying the Kernel to SD Card between each tweak and compilation.

## Boot arguments

Here are the default ones (with a bit of formatting):

```
bootargs = \
    coherent_pool=1M \
    8250.nr_uarts=1 \
    snd_bcm2835.enable_headphones=0 \
    snd_bcm2835.enable_hdmi=0 \
    smsc95xx.macaddr=DC:A6:32:CD:A3:87 \
    vc_mem.mem_base=0x3ec00000 \
    vc_mem.mem_size=0x40000000 \
    dwc_otg.lpm_enable=0 \
    console=ttyS0,115200 \
    root=/dev/mmcblk0p2 \
    rootfstype=ext4 \
    rootwait
```

(If you are updating the labs, please check if the default bootargs changed and update here accordingly.)

Here's if, why and how each one of these is relevant to us.
Also refer to the [relevant kernel documentation][kernel-docs-command-line-params].

### Preserved default boot arguments

| boot argument        | explanation                                  |
| -------------------- | -------------------------------------------- |
| coherent_pool=1M     | irrelevant                                   |
| 8250.nr_uarts=1      | we need one UART                             |
| smsc95xx.macaddr     | sets mac address, irrelevant                 |
| vc_mem.mem_base      | [added by GPU firmware][vc_mem-forum-thread] |
| vc_mem.mem_size      | [added by GPU firmware][vc_mem-forum-thread] |
| dwc_otg.lpm_enable=0 | [disalbes LPM support][vc_mem-forum-thread]  |
| console=ttyS0,115200 | console via serial port, default baud rate   |
| rootfstype=ext4      | same on SD card and via NFS                  |
| rootwait             | wait indefinitely for root device to show up |

### Changed boot arguments

| boot argument       | explanation                              |
| ------------------- | ---------------------------------------- |
| root=/dev/mmcblk0p2 | rootfs location, change to mount via NFS |

### Unsure!

| boot argument                 | explanation                        |
| ----------------------------- | ---------------------------------- |
| snd_bcm2835.enable_headphones | may need to change for audio labs? |
| snd_bcm2835.enable_hdmi       | may need to change for audio labs? |

### Added boot arguments

| boot argument | explanation                                                    |
| ------------- | -------------------------------------------------------------- |
| root=/dev/nfs | /dev/nfs is a virtual device, make kernel mount rootfs via NFS |
| nfsroot       | configure rootfs mount via NFS. more details below.            |
| ip=dhcp       | use DHCP to configure IP routing table for NFS                 |
| rw            | mount root device read-write on boot                           |
| maxcpus=1     | disable all cores but one for scheduling lab                   |

#### nfsroot

Find detailed information on this argument in the [kernel documentation][kernel-docs-nfsroot-cmd-line].
The value we are using is `nfsroot=192.168.0.100:/srv/rpi_rootfs,v3,tcp`.
Server IP, the location of the rootfs on the server and `tcp` as the protocol should be clear.
`v3` is the version of NFS to use.
`v4` exists, but most sources I found online use `v3` as default.
I'm not aware of a concrete benefit to us of using `v4` instead.

## Boot script

The default boot script is in [`meta-raspberry/recipes-bsp/rpi-u-boot-scr`][default-boot-scr].
It is overridden by our own [boot script][custom-boot-scr].

The script reads two environment variables for user customization:

| variable    | possible values                              |
| ----------- | -------------------------------------------- |
| `BOOT_MODE` | `SD`, `NFS` or emtpy, which defaults to `SD` |
| `MAX_CPUS`  | `1` or emtpy, which means activate all cores |

## Booting the kernel via TFTP

This is not implemented.
The kernel is not rebuilt often in the labs,
so having to flash the SD card for that is not too much trouble.
Also, there were many networking issues in the past.
It may be considered to implement this again.

[rpi-boot-proc-article]: https://www.beyondlogic.org/compiling-u-boot-with-device-tree-support-for-the-raspberry-pi/
[kernel-docs-command-line-params]: https://www.kernel.org/doc/html/v6.1/admin-guide/kernel-parameters.html
[vc_mem-forum-thread]: https://forums.raspberrypi.com/viewtopic.php?t=266990
[dwc_otg-forum-thread]: https://raspberrypi.stackexchange.com/a/1887
[kernel-docs-nfsroot-cmd-line]: https://www.kernel.org/doc/html/v6.1/admin-guide/nfs/nfsroot.html#kernel-command-line
[default-boot-scr]: https://github.com/agherzan/meta-raspberrypi/blob/master/recipes-bsp/rpi-u-boot-scr/files/boot.cmd.in
[custom-boot-scr]: /meta-mc2/recipes-bsp/rpi-u-boot-scr/files/boot.cmd.in
