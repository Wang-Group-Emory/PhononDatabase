#!/bin/bash
passed_last_line="All non-Gaussian ED ground state calculations have been completed. Exit now."
uncon=0
empt=0
fin=0
num=$(cat count.txt)
folds=()
for x in $(seq 1 $num);
do
    folds+=($x)
done
echo ${folds[@]}
#cur=$((($num)*144))
###############
# Currently in 2D/g-gpr/
cd ./Scripts
for fold in */
do
    for i in ${folds[@]}; do
        if [[ $fold == "$i-"* ]]; then
            #echo $fold $PWD
            cd $fold
            for data in *-data_U*_g*_gpr*_w*
            do
                cd $data
                # Currently in 2D/scripts/results/
                for ktpr in k=*tpr=*
                do
                    cd $ktpr
                    # Currently in 2D/scripts/results/ktpr/
                    for doping in *h
                    do
                        cd $doping
                        for file in *
                        do
                            if [ $(basename $file) == 'mylog' ]
                            then
                                fin=$(($fin+1))
                                last_line=$( tail -n 1 $file )
                                if [ "$last_line" != "$passed_last_line" ]
                                then
                                    uncon=$(($uncon+1))
                                    echo -n 'Unconverged: '
                                    echo $PWD | cut -d'/' -f10-
                                fi

                            elif [ $(basename $file) == 'NGSED_iteration_variables.txt' ]
                            then
                                last_line=$( tail -n 1 $file )
                                if [ ! -s $(basename $file) ]
                                then
                                    empt=$(($empt+1))
                                    echo -n 'Empty: '
                                    echo $PWD | cut -d'/' -f10-
                                fi
                            fi
                        done
                    cd ..
                    done
                cd ..
                done
            cd ..
            done
            cd ..
        fi
    done
#cd ..
done
percun=`echo 100*$uncon/$fin|bc -l`
perempt=`echo 100*$empt/$fin|bc -l`
perfin=`echo 100*$fin/5292|bc -l`
t=$(($uncon+$empt))
tper=`echo 100*$t/$fin|bc -l`
printf "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
printf "\nUnconverged/Total: %i/%i or %.2f%%\n" $uncon $fin $percun
printf "Empty/Total: %i/%i or %.2f%%\n" $empt $fin $perempt
printf "______________________________________\n"
printf "Errors/Total: %i/%i or %.2f%%\n" $t $fin $tper
printf "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
printf "Complete: %i/5292 or %.2f%%\n" $fin $perfin
printf "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
