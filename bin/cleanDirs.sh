#!/bin/bash
#
# Clean the dir tree of backup and compiled files before doing a checkin.
#
# CVS/SVN Keywords
#------------------------------
# $Author: cnobile $
# $Date: 2010-10-05 12:28:39 -0400 (Tue, 05 Oct 2010) $
# $Revision: 26 $
# ------------------------------
#

REGEX="(^.*.pyc$)|(^.*.wsgic$)|(^.*~$)|(.*#$)" #|(.*\.log((.*)(\d)+)?)"
CMD="find . -regextype posix-egrep -regex $REGEX"

if [ "$1" == "clean" ]; then
    $CMD -exec rm {} \;
else
    $CMD
fi
