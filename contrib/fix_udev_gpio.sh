#!/bin/bash
#
# This file will change the user, group and permissions in both the
# /sys/devices/virtual/gpio and /sys/class/gpio path directories.
#
# DO NOT change the order of the commands below, they are optimized so that
# commonly created files and directories are changed first.
#

chown -R debian:gpio /sys/devices/virtual/gpio
chown -R debian:gpio /sys/class/gpio
find /sys/devices/virtual/gpio -type d -exec chmod 2775 {} \;
find /sys/devices/virtual/gpio -name "direction" -exec chmod 0660 {} \;
find /sys/devices/virtual/gpio -name "edge" -exec chmod 0660 {} \;
find /sys/devices/virtual/gpio -name "value" -exec chmod 0660 {} \;

find /sys/devices/virtual/gpio -name "active_low" -exec chmod 0660 {} \;
chmod 0220 /sys/class/gpio/export
chmod 0220 /sys/class/gpio/unexport
find /sys/devices/virtual/gpio -name "uevent" -exec chmod 0660 {} \;
find /sys/devices/virtual/gpio -name "autosuspend_delay_ms" -exec chmod 0660 {} \;
find /sys/devices/virtual/gpio -name "control" -exec chmod 0660 {} \;
