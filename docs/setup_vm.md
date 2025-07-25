# Setting up a VM

These are instructions to prepare a VM for students to use in the labs.
First, go through the process of setting up a fresh Ubuntu VM.
Skip the unattended installation, I don't trust VirtualBox.
(user: mc2, password: mc2)

## General settings

Be nice to the students and make Ubuntu a little less unbearable:
- dark mode
- auto-hide dock
- fix disgusting terminal color scheme (Profiles > Unnamed):
  - Text > Terminal Bell NO
  - Colors:
    - Text and Background Color:
      - Use colors from system theme NO
      - Built-in schemes "White on black"
    - Palette
      - Built-in schemes: GNOME
      - Show bold text in bright colors YES

## Install Guest additions

The guest additions are necessary for mounting shared folders, which is the fastest way to copy over data like the build cache.

Download the ISO for your precise VirtualBox version [here][virtual-box-download].
Mount the ISO to the VM via Devices > Optical drives > Choose a disk drive.
Once mounted, execute `autorun.sh` from within the VM.
Restart the virtual machine for it to take effect.

## Keyboard & Clipboard

- Add the Swiss German Keyboard and make it default
- Enable Drag&Drop in VM Settings

## VM settings

### Network

Add the ethernet adapter for the Raspberry Pi as a second bridged adapter.

### USB

- Select the USB 3.0 Controller
- Add the UART device for the serial connection.

## Run the setup scripts

Next, you need the source code of this repository inside the VM.
It is recommended to use a shared folder, which you can set up in the settings of your virtual machine.

To get around any permissions shenanigans, copy the scripts somewhere else on the filesystem and change the owner to mc2 (`chown -R mc2:mc2 ./host_setup/*`).

Check `env.sh` to see if you're happy with the configuration.
Run the scripts: `./host_setup/main.sh`.

## Populate the build cache

For quick development and testing, you probably want to just copy over the cache you already have.
Use a shared folder for that.
For the final VM built for the students, it is recommended to delete the existing cache and make a new one with a single build.
This should ensure the cache is only as large as it needs to be.
Remeber that the default location of the cache is `~/sstate-cache`.

```sh
cd ~
mkdir sstate-cache
sudo su
cp -R /media/sf_sstate-cache/* sstate-cache/
chown -R mc2:mc2 /home/mc2/sstate-cache/
```

The `sstate-cache` does not include downloaded sources and compilation cache of the kernel.
These are required for the kernel module lab.
Fetch and compile as much as possible to spare the students from having to do it during the labs:

```sh
bitbake linux-raspberrypi -c do_compile_kernelmodules
```

## Cleanup

Once you're done, remember to remove stuff like:
- mc2-labs repo
- ssh-keys

One more thing: In order to get a small OVA file, unused blocks should be set uo 0. THe easieast way for this, create a big file with zeros until SSD is full, then delete it:
- sudo dd if=/dev/zero of=/bigemptyfile; sudo rm -rf /bigemptyfile

That's it!

[virtual-box-download]: https://download.virtualbox.org/virtualbox
