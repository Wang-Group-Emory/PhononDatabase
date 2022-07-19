#!/bin/bash
#################
# Setting up
rm -r ./Scripts
mkdir Scripts
cd ./Scripts

#################
# Defining the g-g' plane
g=()
gpr=()
for x in $(seq 0 0.05 1);
do
    g+=($x)
done
for y in $(seq 0 0.05 1);
do
    gpr+=($y)
done
#echo ${gpr[0]}
####################
csmall=12
cbig=1
mkdir $cbig-1-145
cd $cbig-1-145
#echo "$cbig" > foldvar.txt
ccheck=1

for x in ${g[@]};
do
    for y in ${gpr[@]};
    do
        if [ $(expr $(($csmall-12)) % 144) == 0 ] && [ $((csmall-12)) != 0 ]
        then
            cd ..
            cbig=$(($cbig+1))
            if [ $cbig == 37 ]
            then
                mkdir $cbig-$((csmall-10))-5292
                cd $cbig-$((csmall-10))-5292
                #echo "$cbig" > foldvar.txt
            else
                mkdir $cbig-$((csmall-10))-$((csmall+134))
                cd $cbig-$((csmall-10))-$((csmall+134))
                #echo "$cbig" > foldvar.txt
            fi
            ccheck=1
        fi
        echo $x $y $cbig $csmall $ccheck
        python3 ../../creatScript.py $x $y $ccheck $cbig
        #touch test$ccheck.txt
        csmall=$(($csmall+12))
        ccheck=$(($ccheck+1))
    done
done
