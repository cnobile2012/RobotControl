#!/bin/bash

# Fix the /sys/devices/virtual/gpio path.
chown -R debian:gpio /sys/devices/virtual/gpio
find /sys/devices/virtual/gpio -type d -exec chmod 2775 {} \;
find /sys/devices/virtual/gpio -name "uevent" -exec chmod 0660 {} \;
find /sys/devices/virtual/gpio -name "autosuspend_delay_ms" -exec chmod 0660 {} \;
find /sys/devices/virtual/gpio -name "control" -exec chmod 0660 {} \;

# Fix the /sys/class/gpio path.
chown -R debian:gpio /sys/class/gpio
chmod 0220 /sys/class/gpio/export
chmod 0220 /sys/class/gpio/unexport
