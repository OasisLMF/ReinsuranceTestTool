#!/bin/bash

for d in */ ; do
    diff ../examples_old/simple_QS/ri_scope.csv "$d/ri_scope.csv" > /dev/null
    retval=$? 
    if [ $retval -eq 0 ]; then
    	echo $d
    fi
done