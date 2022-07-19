#!/bin/bash

c=$(cat count.txt)
cd ./Scripts
cd ./$c-*
for i in *-collect_*
do
    echo $i
    #bash ./$i
done