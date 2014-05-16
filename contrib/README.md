Install udev File
=================

The installation of the udev file will change the file permissions of /sys/class/gpio and /sys/devices/virtual/gpio to dabian:gpio. You will need to create the gpio group. See below.

 1. `# sudo cp contrib/80-gpio.rules /etc/udev/rules.d/`
 2. `# sudo cp contrib/fix_udev_gpio.sh /bin/`
 3. `# sudo groupadd gpio` # Creates a group named `gpio`.
 4. `# sudo adduser <your username> gpio` # Add yourself to the `gpio` group.
 5. `# sudo reboot` # Reboot the Beagle Bone

After the Beagle Bone comes back up you should see that both directories mentiond above should have owner and group `debian:gpio`.
