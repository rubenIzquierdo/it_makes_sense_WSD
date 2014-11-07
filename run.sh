#!/bin/bash

root=`dirname $0`

#Setting the output to be ili-wn30 synsets instead of sensekeys
$root/call_ims.py -ili30
