#!/bin/bash

c=$(cat count.txt)
cd ./Scripts
cd ./$c-*
for i in *-submit_*
do
    #echo $i
    bash ./$i
done
echo "This section has been submitted" > finished.txt
cd ../../
echo "$(($c+1))" > count.txt

