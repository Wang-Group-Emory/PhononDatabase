#!/bin/bash
filename="varState.dat"
passed_last_line="All non-Gaussian ED ground state calculations have been completed. Exit now."
if [ -z $2 ] && [ -z $1 ]; then
    exit 0
elif [ -z $2 ] && [ $1 -eq $1 >& /dev/null ]; then
    nums="[$1]"
elif ([ $1 == 'all' ] || [ $1 == 'All' ]) && [ -z $2 ]; then
    nums="*"
elif [ $2 -eq $2 >& /dev/null ] && [ $1 -eq $1 >& /dev/null ]; then
    nums="[$1][$2]"
else
    exit 0
fi
###############
# Currently in 2D/scripts/
for data in $nums-data_g*_gpr*_w*
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
            # Currently in 2D/scripts/results/ktpr/doping
            for file in *
            do
                if [ $(basename $file) == 'mylog' ]
                then
                    last_line=$( tail -n 1 $file )
                    if [ "$last_line" != "$passed_last_line" ]
                    then
                        echo -n 'Rerunning: '; echo $PWD | cut -d'/' -f9-
                        rm varState_dat_most_recent
                        cp $filename varState_dat_most_recent
                        rm $filename
                        cp NGSED_iteration_variables.txt $filename
                        sed -i '$d' $filename
                        truncate -s -1 $filename
                        sbatch cori_NGSED_Obs.sh
                    fi
                fi
            done
        cd ..
        # Currently in 2D/scripts/results/ktpr/
        done
    cd ..
    # Currently in 2D/scripts/results/
    done
cd ..
# Currently in 2D/scripts/
done

