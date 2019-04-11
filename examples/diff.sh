#!/bin/bash
# search examples for identical locations file 
for d in */ ; do
    diff ../examples_old/simple_QS/location.csv "$d/location.csv" > /dev/null
    retval=$? 
    if [ $retval -eq 0 ]; then
    	echo $d
    fi
done

