#!/bin/bash
# locations like simple_QS
for d in */ ; do
    diff ../examples_old/simple_QS/location.csv "$d/location.csv" > /dev/null
    retval=$? 
    if [ $retval -eq 0 ]; then
    	echo $d
    	cut -d "," -f1,2,3,22,12,43,44,45,46,47,49,62,61,92,91,67,66,95,94,72,71,98,97,77,76,101,100,82,81,83,84,104,103,87,86,88,89,107,106,58,59 "$d/location.csv" > "$d/location1.csv"
    	paste -d "," "$d/location1.csv" PortNumber.csv > "$d/location_new.csv"
    	sed -i -e 's/CondTag/CondNumber/g' "$d/location_new.csv"
    	rm "$d/location1.csv"
    	cut -d "," -f1,4,65,74,10,186,187,188,206,156,112,113,114,132,82,81,80 "$d/account.csv" > "$d/account_new.csv"
    fi
done

#locations like simple_CXL_port_acc_filter
for d in */ ; do
    diff simple_CXL_port_acc_filter/location.csv "$d/location.csv" > /dev/null
    retval=$? 
    if [ $retval -eq 0 ]; then
    	echo $d
    	cut -d "," -f1,2,3,22,12,43,44,45,46,47,49,62,61,92,91,67,66,95,94,72,71,98,97,77,76,101,100,82,81,83,84,104,103,87,86,88,89,107,106,58,59 "$d/location.csv" > "$d/location1.csv"
    	paste -d "," "$d/location1.csv" PortNumber2.csv > "$d/location_new.csv"
    	sed -i -e 's/CondTag/CondNumber/g' "$d/location_new.csv"
    	rm "$d/location1.csv"
    	cut -d "," -f1,4,65,74,10,186,187,188,206,156,112,113,114,132,82,81,80 "$d/account.csv" > "$d/account_new.csv"
    fi
done

for d in */ ; do
    diff single_lgr_level_fac/location.csv "$d/location.csv" > /dev/null
    retval=$? 
    if [ $retval -eq 0 ]; then
    	echo $d
    	cut -d "," -f1,2,3,22,12,43,44,45,46,47,49,62,61,92,91,67,66,95,94,72,71,98,97,77,76,101,100,82,81,83,84,104,103,87,86,88,89,107,106,58,59 "$d/location.csv" > "$d/location1.csv"
    	paste -d "," "$d/location1.csv" PortNumber.csv > "$d/location_new.csv"
    	sed -i -e 's/CondTag/CondNumber/g' "$d/location_new.csv"
    	rm "$d/location1.csv"
    	cut -d "," -f1,4,65,74,10,186,187,188,206,156,112,113,114,132,82,81,80 "$d/account.csv" > "$d/account_new.csv"
    fi
done

for d in */ ; do
    diff single_lgr_level_PR_all_risks/location.csv "$d/location.csv" > /dev/null
    retval=$? 
    if [ $retval -eq 0 ]; then
    	echo $d
    	cut -d "," -f1,2,3,22,12,43,44,45,46,47,49,62,61,92,91,67,66,95,94,72,71,98,97,77,76,101,100,82,81,83,84,104,103,87,86,88,89,107,106,58,59 "$d/location.csv" > "$d/location1.csv"
    	paste -d "," "$d/location1.csv" PortNumber.csv > "$d/location_new.csv"
    	sed -i -e 's/CondTag/CondNumber/g' "$d/location_new.csv"
    	rm "$d/location1.csv"
    	cut -d "," -f1,4,65,74,10,186,187,188,206,156,112,113,114,132,82,81,80 "$d/account.csv" > "$d/account_new.csv"
    fi
done

for d in */ ; do
    diff single_loc_level_fac/location.csv "$d/location.csv" > /dev/null
    retval=$? 
    if [ $retval -eq 0 ]; then
    	echo $d
    	cut -d "," -f1,2,3,22,12,43,44,45,46,47,49,62,61,92,91,67,66,95,94,72,71,98,97,77,76,101,100,82,81,83,84,104,103,87,86,88,89,107,106,58,59 "$d/location.csv" > "$d/location1.csv"
    	paste -d "," "$d/location1.csv" PortNumber.csv > "$d/location_new.csv"
    	sed -i -e 's/CondTag/CondNumber/g' "$d/location_new.csv"
    	rm "$d/location1.csv"
    	cut -d "," -f1,4,65,74,10,186,187,188,206,156,112,113,114,132,82,81,80 "$d/account.csv" > "$d/account_new.csv"
    fi
done

for d in */ ; do
    diff single_loc_level_PR_loc_filter/location.csv "$d/location.csv" > /dev/null
    retval=$? 
    if [ $retval -eq 0 ]; then
    	echo $d
    	cut -d "," -f1,2,3,22,12,43,44,45,46,47,49,62,61,92,91,67,66,95,94,72,71,98,97,77,76,101,100,82,81,83,84,104,103,87,86,88,89,107,106,58,59 "$d/location.csv" > "$d/location1.csv"
    	paste -d "," "$d/location1.csv" PortNumber.csv > "$d/location_new.csv"
    	sed -i -e 's/CondTag/CondNumber/g' "$d/location_new.csv"
    	rm "$d/location1.csv"
    	cut -d "," -f1,4,65,74,10,186,187,188,206,156,112,113,114,132,82,81,80 "$d/account.csv" > "$d/account_new.csv"
    fi
done

for d in */ ; do
    diff single_loc_level_SS_all_risks_loc/location.csv "$d/location.csv" > /dev/null
    retval=$? 
    if [ $retval -eq 0 ]; then
    	echo $d
    	cut -d "," -f1,2,3,22,12,43,44,45,46,47,49,62,61,92,91,67,66,95,94,72,71,98,97,77,76,101,100,82,81,83,84,104,103,87,86,88,89,107,106,58,59 "$d/location.csv" > "$d/location1.csv"
    	paste -d "," "$d/location1.csv" PortNumber.csv > "$d/location_new.csv"
    	sed -i -e 's/CondTag/CondNumber/g' "$d/location_new.csv"
    	rm "$d/location1.csv"
    	cut -d "," -f1,4,65,74,10,186,187,188,206,156,112,113,114,132,82,81,80 "$d/account.csv" > "$d/account_new.csv"
    fi
done