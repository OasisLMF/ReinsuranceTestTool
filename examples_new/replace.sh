#!/bin/bash
# replace
for d in */ ; do
    mv "$d/location_new.csv" "$d/location.csv" 
    mv "$d/account_new.csv" "$d/account.csv" 
done

