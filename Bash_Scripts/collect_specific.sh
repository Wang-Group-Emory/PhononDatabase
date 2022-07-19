#!/bin/bash

mainFolder=`echo Results`
rm -r ./${mainFolder}
mkdir ./${mainFolder}

c=$(cat count.txt)
c=$(($c-1))
cd ./Scripts
for j in  $(seq 1 $c); do
    cd ./$j-*
    echo $PWD
    for i in *-collect_*
    do
        #echo $i
        bash ./$i
    done
cd ..
done