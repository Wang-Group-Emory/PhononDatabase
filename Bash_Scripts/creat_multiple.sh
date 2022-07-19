#!/bin/bash

cd ./Scripts
for dir in */
do
    echo $dir
    cd $dir
    for i in *-creatFolders_*
    do
        #echo $i
        bash ./$i
    done
    cd ..
done