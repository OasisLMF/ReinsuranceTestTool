#!/bin/bash

for d in */ ; do
    diff simple_QS/location.csv "$d/location.csv" > /dev/null
    retval=$? 
    if [ $retval -eq 0 ]; then
    	echo $d
    fi
done