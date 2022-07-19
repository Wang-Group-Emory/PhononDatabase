######################################
# Libraries
import numpy as np
import sys
######################################
# Please enter the parameters below
site=16
uval=8
wval=0.2
# We want the entire g-g' plane (0:0.05:1)
gval=sys.argv[1]
gprval=sys.argv[2]
#tpr_vals = [0,-0.1,-0.2,-0.3]
k_vals = [0,2,10]
doping_vals = [2,4]
#k_vals = [2,10]
tpr_vals=[0,-0.3]
#k_vals=1
#doping_vals=1
num=sys.argv[3]
fold=sys.argv[4]
foldprefix = ['creatFolders', 'submit', 'collect']
foldname = [f'{num}-{foldprefix[0]}_w={wval}_g={gval}_gpr={gprval}.sh',
            f'{num}-{foldprefix[1]}_w={wval}_g={gval}_gpr={gprval}.sh',
            f'{num}-{foldprefix[2]}_w={wval}_g={gval}_gpr={gprval}.sh']
######################################
# Functions
def bash_array(vals):
    if type(vals) == int or type(vals) == float:
        return(vals)
    bashlis = '{'
    for val in vals:
        if val == vals[-1]:
            bashlis = f'{bashlis}{val}}}'
            return(bashlis)
        bashlis = f'{bashlis}{val},'
######################################
# Different scripts

######################################
# First case TPR NOT ARRAY
#
######################################

if type(tpr_vals) != list and type(k_vals) == list and type(doping_vals) == list:
    # Display of information
    #print("tpr not an array")
    #print(f'tpr_vals: {tpr_vals} k_vals: {k_vals} doping_vals: {doping_vals}')
    
    # Creating the creatFolders script
    with open(foldname[0], 'w') as cfsh:
        cfsh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
tpr={bash_array(tpr_vals)}
site={site}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{mainFolder}}
mkdir ${{mainFolder}}
cd ${{mainFolder}}
# Currently in 2D/scripts/results/
###############
for kval in {bash_array(k_vals)};do
    momentum=$kval
    ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
    rm -r ${{ktprfolder}}
    mkdir ${{ktprfolder}}
    cd ${{ktprfolder}}
    # Currently in 2D/gpr/scripts/indiv/data/ktpr/
    for di in {bash_array(doping_vals)};do
       doping=`echo $di*2|bc -q`
       filling=`echo $site-$doping|bc -q`
       dnFilling=`echo "($site-$doping)/2"|bc -q`
       upFilling=`echo $filling-$dnFilling|bc -q`
       runFolder=`echo 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
       rm -r ${{runFolder}}
       mkdir  ${{runFolder}}
       cp ../../../../../*.in ./${{runFolder}}
       cp ../../../../../*.config ./${{runFolder}}
       cd ${{runFolder}}
       # Currently in 2D/scripts/results/ktpr/specific
       echo "creating folder ${{runFolder}}"
       cat > ./model_params.in<<EOF
Hubbard-Holstein
U= ${{uval}}      t= 1
g= ${{gval}}      W= ${{wval}}
t'= ${{tpr}}      g'= ${{gprval}}
EOF
cat > ./hilbertspace_params.in <<EOF
Cluster:        ${{site}}A
ElectronicSiteNumber: ${{site}}
Dimension:      2D
Boundary:       Periodic
Representation: Momentum
Momentum: $momentum
Occupancy:      ${{filling}}($upFilling,$dnFilling)
EOF
       echo "params changed"
       cat > ./cori_NGSED_Obs.sh<<EOF
#!/bin/sh
#SBATCH -J U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}_k${{momentum}}_${{doping}}h_tpr${{tpr}}
#SBATCH -A m3706
#SBATCH -p regular
#SBATCH --nodes=4
#SBATCH -t 01:00:00
#SBATCH --tasks-per-node=8
#SBATCH --cpus-per-task=8
#SBATCH --constraint=haswell
#SBATCH -e job.err
#SBATCH -o job.out
#SBATCH --mail-type=fail
#SBATCH --mail-user=mtm9@g.clemson.edu
#SBATCH -V
cd \$SLURM_SUBMIT_DIR

rm job.*
rm *.txt

export OMP_PROC_BIND=true
export OMP_PLACES=threads
export OMP_NUM_THREADS=8
srun ../../../../../../../NGSED_GROUND_OBS >& mylog
wait
EOF
        echo "created script for ${{runFolder}}"
        cd ..
        # Currently in 2D/scripts/results/ktpr/
    done
    cd ..
    # Currently in 2D/scripts/results/
done
        ''')
        cfsh.close()
        
        # Creating the submit script
        with open(foldname[1], 'w') as ssh:
            ssh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
tpr={bash_array(tpr_vals)}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
cd ${{mainFolder}}
###############
for kval in {bash_array(k_vals)};do
    # Currently in 2D/scripts/results/
    echo "k= ${{kval}}, tpr=${{tpr}}"
    ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
    cd ${{ktprfolder}}
    # Currently in 2D/scripts/results/ktpr/
    for di in {bash_array(doping_vals)};do
        doping=`echo $di*2|bc -q`
        cd 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h
            # Currently in 2D/scripts/results/ktpr/specific
            sbatch cori_NGSED_Obs.sh
        cd ..
        # Currently in 2D/scripts/results/ktpr/
    done
    cd ..
    # Currently in 2D/scripts/results/
done
        ''')
        ssh.close()
        
        # Creating the Collection script
        with open(foldname[2], 'w') as csh:
            csh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
tpr={bash_array(tpr_vals)}
# Currently in 2D/scripts/
mainFolder=`echo Results`
cd ../../${{mainFolder}}
# Currently in 2D/scripts/results/
resFolder=`echo nonGaussEDGround2D_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{resFolder}}
mkdir ${{resFolder}}
cd ${{resFolder}}

# Currently in 2D/scripts/results/nonGauss
for kval in {bash_array(k_vals)};do
    kfolder=`echo k=${{kval}}`
    mkdir ${{kfolder}}
    cd ${{kfolder}}
    # Currently in 2D/scripts/results/nonGauss/k=()/
    tprfolder=`echo tpr=${{tpr}}`
    mkdir ${{tprfolder}} 
    cd ${{tprfolder}}
    # Currently in 2D/scripts/results/nonGauss/k=()/tpr=()/
    for di in {bash_array(doping_vals)};do
      doping=`echo $di*2|bc -q`
      mkdir Doping${{doping}}h
      cd Doping${{doping}}h
      # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
      dataFolder=`echo  ../../../../../Scripts/{fold}-*/{num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}/k=${{kval}}tpr=${{tpr}}/2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
      collectFolder=`echo ./resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}}`
      mkdir ${{collectFolder}}

      cp ${{dataFolder}}/mylog  ${{collectFolder}}/
      cp ${{dataFolder}}/NGSED_iteration_observables.txt  ${{collectFolder}}/nonGaussED_eq_observables.txt
      cp ${{dataFolder}}/NGSED_iteration_variables.txt  ${{collectFolder}}/varState.txt
      cp ${{dataFolder}}/hilbertspace_params.in  ${{collectFolder}}/
      cp ${{dataFolder}}/observable_name_list.txt ${{collectFolder}}/observableList.txt
      echo "copied ${{dataFolder}} to ${{collectFolder}}"
      mv resU${{uval}}_g0${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g0${{gval}}_W${{wval}}
      mv resU${{uval}}_g${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g${{gval}}_W${{wval}}
      mv resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g${{gval}}_gpr${{gprval}}_W${{wval}}
      mv resU${{uval}}_g0${{gval}}_gpr0.10_W${{wval}} resU${{uval}}_g0${{gval}}_gpr0.1_W${{wval}}
      cd ..
      # Currently in 2D/scripts/results/nonGauss/kfolder/tprfolder/
    done
    cd ../..
    # Currently in 2D/scripts/results/nonGauss/
done

# Currently in 2D/scripts/results/nonGauss
for kval in {bash_array(k_vals)};do
    kfolder=`echo k=${{kval}}`
    cd ${{kfolder}}
    # Currently in 2D/scripts/results/nonGauss/kfolder
    tprfolder=`echo tpr=${{tpr}}`
    cd ${{tprfolder}}
    # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder
    for di in {bash_array(doping_vals)};do
        doping=`echo $di*2|bc -q`
        cd Doping${{doping}}h
        # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
        mv resU${{uval}}_g00_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0_gpri0${{gprval}}_W${{wval}}
        mv resU${{uval}}_g0.10_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0.1_gpri0${{gprval}}_W${{wval}}
        cd ..
        # Currently in 2D/scripts/results/nonGauss/kfolder/tprfolder/
    done
    cd ../..
    # Currently in 2D/scripts/results/nonGauss/
done
        ''')
        csh.close()

######################################
# 2ND case K NOT ARRAY
#
######################################
elif type(tpr_vals) == list and type(k_vals) != list and type(doping_vals) == list:
    #print("k is not an array")
    #print(f'tpr_vals: {tpr_vals} k_vals: {k_vals} doping_vals: {doping_vals}')
    
    # Creating the creatFolders script
    with open(foldname[0], 'w') as cfsh:
        cfsh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
kval={bash_array(k_vals)}
site={site}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{mainFolder}}
mkdir ${{mainFolder}}
cd ${{mainFolder}}
# Currently in 2D/scripts/results/
###############
momentum=$kval
for tpr in {bash_array(tpr_vals)};do
    ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
    rm -r ${{ktprfolder}}
    mkdir ${{ktprfolder}}
    cd ${{ktprfolder}}
    # Currently in 2D/scripts/results/ktpr/
    for di in {bash_array(doping_vals)};do
       doping=`echo $di*2|bc -q`
       filling=`echo $site-$doping|bc -q`
       dnFilling=`echo "($site-$doping)/2"|bc -q`
       upFilling=`echo $filling-$dnFilling|bc -q`
       runFolder=`echo 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
       rm -r ${{runFolder}}
       mkdir  ${{runFolder}}
       cp ../../../../../*.in ./${{runFolder}}
       cp ../../../../../*.config ./${{runFolder}}
       cd ${{runFolder}}
       # Currently in 2D/scripts/results/ktpr/specific
       echo "creating folder ${{runFolder}}"
       cat > ./model_params.in<<EOF
Hubbard-Holstein
U= ${{uval}}      t= 1
g= ${{gval}}      W= ${{wval}}
t'= ${{tpr}}      g'= ${{gprval}}
EOF
cat > ./hilbertspace_params.in <<EOF
Cluster:        ${{site}}A
ElectronicSiteNumber: ${{site}}
Dimension:      2D
Boundary:       Periodic
Representation: Momentum
Momentum: $momentum
Occupancy:      ${{filling}}($upFilling,$dnFilling)
EOF
   echo "params changed"
   cat > ./cori_NGSED_Obs.sh<<EOF
#!/bin/sh
#SBATCH -J U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}_k${{momentum}}_${{doping}}h_tpr${{tpr}}
#SBATCH -A m3706
#SBATCH -p regular
#SBATCH --nodes=4
#SBATCH -t 01:00:00
#SBATCH --tasks-per-node=8
#SBATCH --cpus-per-task=8
#SBATCH --constraint=haswell
#SBATCH -e job.err
#SBATCH -o job.out
#SBATCH --mail-type=fail
#SBATCH --mail-user=mtm9@g.clemson.edu
#SBATCH -V
cd \$SLURM_SUBMIT_DIR

rm job.*
rm *.txt

export OMP_PROC_BIND=true
export OMP_PLACES=threads
export OMP_NUM_THREADS=8
srun ../../../../../../../NGSED_GROUND_OBS >& mylog
wait
EOF
        echo "created script for ${{runFolder}}"
        cd ..
        # Currently in 2D/scripts/results/ktpr/
    done
    cd ..
    # Currently in 2D/scripts/results/
done
        ''')
        cfsh.close()
        
        # Creating the submit script
        with open(foldname[1], 'w') as ssh:
            ssh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
kval={bash_array(k_vals)}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
cd ${{mainFolder}}
###############
for tpr in {bash_array(tpr_vals)};do
    # Currently in 2D/scripts/results/
    echo "k= ${{kval}}, tpr=${{tpr}}"
    ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
    cd ${{ktprfolder}}
    # Currently in 2D/scripts/results/ktpr/
    for di in {bash_array(doping_vals)};do
        doping=`echo $di*2|bc -q`
        cd 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h
            # Currently in 2D/scripts/results/ktpr/specific
            sbatch cori_NGSED_Obs.sh
        cd ..
        # Currently in 2D/scripts/results/ktpr/
    done
    cd ..
    # Currently in 2D/scripts/results/
done 
        ''')
        ssh.close()
        
        # Creating the Collection script
        with open(foldname[2], 'w') as csh:
            csh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
kval={bash_array(k_vals)}
# Currently in 2D/scripts/
mainFolder=`echo Results`
cd ../../${{mainFolder}}
# Currently in 2D/scripts/results/
resFolder=`echo nonGaussEDGround2D_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{resFolder}}
mkdir ${{resFolder}}
cd ${{resFolder}}

# Currently in 2D/scripts/results/nonGauss
kfolder=`echo k=${{kval}}`
mkdir ${{kfolder}}
cd ${{kfolder}}
# Currently in 2D/scripts/results/nonGauss/k=()/
for tpr in {bash_array(tpr_vals)};do
    tprfolder=`echo tpr=${{tpr}}`
    mkdir ${{tprfolder}} 
    cd ${{tprfolder}}
    # Currently in 2D/scripts/results/nonGauss/k=()/tpr=()/
    for di in {bash_array(doping_vals)};do
      doping=`echo $di*2|bc -q`
      mkdir Doping${{doping}}h
      cd Doping${{doping}}h
      # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
      dataFolder=`echo  ../../../../../Scripts/{fold}-*/{num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}/k=${{kval}}tpr=${{tpr}}/2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
      collectFolder=`echo ./resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}}`
      mkdir ${{collectFolder}}

      cp ${{dataFolder}}/mylog  ${{collectFolder}}/
      cp ${{dataFolder}}/NGSED_iteration_observables.txt  ${{collectFolder}}/nonGaussED_eq_observables.txt
      cp ${{dataFolder}}/NGSED_iteration_variables.txt  ${{collectFolder}}/varState.txt
      cp ${{dataFolder}}/hilbertspace_params.in  ${{collectFolder}}/
      cp ${{dataFolder}}/observable_name_list.txt ${{collectFolder}}/observableList.txt
      echo "copied ${{dataFolder}} to ${{collectFolder}}"
      mv resU${{uval}}_g0${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g0${{gval}}_W${{wval}}
      mv resU${{uval}}_g${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g${{gval}}_W${{wval}}
      mv resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g${{gval}}_gpr${{gprval}}_W${{wval}}
      mv resU${{uval}}_g0${{gval}}_gpr0.10_W${{wval}} resU${{uval}}_g0${{gval}}_gpr0.1_W${{wval}}
      cd ..
      # Currently in 2D/scripts/results/nonGauss/kfolder/tprfolder/
    done
    cd ..
    # Currently in 2D/scripts/results/nonGauss/kfolder/
done

# Currently in 2D/scripts/results/nonGauss
kfolder=`echo k=${{kval}}`
cd ${{kfolder}}
# Currently in 2D/scripts/results/nonGauss/kfolder
for tpr in {bash_array(tpr_vals)};do
    tprfolder=`echo tpr=${{tpr}}`
    cd ${{tprfolder}}
    # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder
    for di in {bash_array(doping_vals)};do
        doping=`echo $di*2|bc -q`
        cd Doping${{doping}}h
        # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
        mv resU${{uval}}_g00_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0_gpri0${{gprval}}_W${{wval}}
        mv resU${{uval}}_g0.10_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0.1_gpri0${{gprval}}_W${{wval}}
        cd ..
        # Currently in 2D/scripts/results/nonGauss/kfolder/tprfolder/
    done
    cd ..
    # Currently in 2D/scripts/results/nonGauss/kfolder/
done
        ''')
        csh.close()

######################################
# 3RD case DOPING NOT ARRAY
#
######################################
elif type(tpr_vals) == list and type(k_vals) == list and type(doping_vals) != list:
    #print("doping is not an array")
    #print(f'tpr_vals: {tpr_vals} k_vals: {k_vals} doping_vals: {doping_vals}')
    
    # Creating the creatFolders script
    with open(foldname[0], 'w') as cfsh:
        cfsh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
site={site}
di={bash_array(doping_vals)}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{mainFolder}}
mkdir ${{mainFolder}}
cd ${{mainFolder}}
# Currently in 2D/scripts/results/
###############
for kval in {bash_array(k_vals)};do
    momentum=$kval
    for tpr in {bash_array(tpr_vals)};do
        ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
        rm -r ${{ktprfolder}}
        mkdir ${{ktprfolder}}
        cd ${{ktprfolder}}
        # Currently in 2D/scripts/results/ktpr/
        doping=`echo $di*2|bc -q`
        filling=`echo $site-$doping|bc -q`
        dnFilling=`echo "($site-$doping)/2"|bc -q`
        upFilling=`echo $filling-$dnFilling|bc -q`
        runFolder=`echo 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
        rm -r ${{runFolder}}
        mkdir  ${{runFolder}}
        cp ../../../../../*.in ./${{runFolder}}
        cp ../../../../../*.config ./${{runFolder}}
        cd ${{runFolder}}
        # Currently in 2D/scripts/results/ktpr/specific
        echo "creating folder ${{runFolder}}"
        cat > ./model_params.in<<EOF
Hubbard-Holstein
U= ${{uval}}      t= 1
g= ${{gval}}      W= ${{wval}}
t'= ${{tpr}}      g'= ${{gprval}}
EOF
cat > ./hilbertspace_params.in <<EOF
Cluster:        ${{site}}A
ElectronicSiteNumber: ${{site}}
Dimension:      2D
Boundary:       Periodic
Representation: Momentum
Momentum: $momentum
Occupancy:      ${{filling}}($upFilling,$dnFilling)
EOF
       echo "params changed"
       cat > ./cori_NGSED_Obs.sh<<EOF
#!/bin/sh
#SBATCH -J U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}_k${{momentum}}_${{doping}}h_tpr${{tpr}}
#SBATCH -A m3706
#SBATCH -p regular
#SBATCH --nodes=4
#SBATCH -t 01:00:00
#SBATCH --tasks-per-node=8
#SBATCH --cpus-per-task=8
#SBATCH --constraint=haswell
#SBATCH -e job.err
#SBATCH -o job.out
#SBATCH --mail-type=fail
#SBATCH --mail-user=mtm9@g.clemson.edu
#SBATCH -V
cd \$SLURM_SUBMIT_DIR

rm job.*
rm *.txt

export OMP_PROC_BIND=true
export OMP_PLACES=threads
export OMP_NUM_THREADS=8
srun ../../../../../../../NGSED_GROUND_OBS >& mylog
wait
EOF
        echo "created script for ${{runFolder}}"
        cd ../..
        # Currently in 2D/scripts/results/
    done
done
        ''')
        cfsh.close()
        
        # Creating the submit script
        with open(foldname[1], 'w') as ssh:
            ssh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
di={bash_array(doping_vals)}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
cd ${{mainFolder}}
###############
for kval in {bash_array(k_vals)};do
    for tpr in {bash_array(tpr_vals)};do
        # Currently in 2D/scripts/results/
        echo "k= ${{kval}}, tpr=${{tpr}}"
        ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
        cd ${{ktprfolder}}
        # Currently in 2D/scripts/results/ktpr/
        doping=`echo $di*2|bc -q`
        cd 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h
            # Currently in 2D/scripts/results/ktpr/specific
            sbatch cori_NGSED_Obs.sh
        cd ../..
        # Currently in 2D/scripts/results/
    done
done
        ''')
        ssh.close()
        
        # Creating the Collection script
        with open(foldname[2], 'w') as csh:
            csh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
di={bash_array(doping_vals)}
# Currently in 2D/scripts/
mainFolder=`echo Results`
cd ../../${{mainFolder}}
# Currently in 2D/scripts/results/
resFolder=`echo nonGaussEDGround2D_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{resFolder}}
mkdir ${{resFolder}}
cd ${{resFolder}}

# Currently in 2D/scripts/results/nonGauss
for kval in {bash_array(k_vals)};do
    kfolder=`echo k=${{kval}}`
    mkdir ${{kfolder}}
    cd ${{kfolder}}
    # Currently in 2D/scripts/results/nonGauss/k=()/
    for tpr in {bash_array(tpr_vals)};do
        tprfolder=`echo tpr=${{tpr}}`
        mkdir ${{tprfolder}} 
        cd ${{tprfolder}}
        # Currently in 2D/scripts/results/nonGauss/k=()/tpr=()/
        doping=`echo $di*2|bc -q`
        mkdir Doping${{doping}}h
        cd Doping${{doping}}h
        # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
        dataFolder=`echo  ../../../../../Scripts/{fold}-*/{num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}/k=${{kval}}tpr=${{tpr}}/2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
        collectFolder=`echo ./resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}}`
        mkdir ${{collectFolder}}

        cp ${{dataFolder}}/mylog  ${{collectFolder}}/
        cp ${{dataFolder}}/NGSED_iteration_observables.txt  ${{collectFolder}}/nonGaussED_eq_observables.txt
        cp ${{dataFolder}}/NGSED_iteration_variables.txt  ${{collectFolder}}/varState.txt
        cp ${{dataFolder}}/hilbertspace_params.in  ${{collectFolder}}/
        cp ${{dataFolder}}/observable_name_list.txt ${{collectFolder}}/observableList.txt
        echo "copied ${{dataFolder}} to ${{collectFolder}}"
        mv resU${{uval}}_g0${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g0${{gval}}_W${{wval}}
        mv resU${{uval}}_g${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g${{gval}}_W${{wval}}
        mv resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g${{gval}}_gpr${{gprval}}_W${{wval}}
        mv resU${{uval}}_g0${{gval}}_gpr0.10_W${{wval}} resU${{uval}}_g0${{gval}}_gpr0.1_W${{wval}}
        cd ..
        # Currently in 2D/scripts/results/nonGauss/kfolder/
    done
    cd ..
    # Currently in 2D/scripts/results/nonGauss/
done

# Currently in 2D/scripts/results/nonGauss
for kval in {bash_array(k_vals)};do
    kfolder=`echo k=${{kval}}`
    cd ${{kfolder}}
    # Currently in 2D/scripts/results/nonGauss/kfolder
    for tpr in {bash_array(tpr_vals)};do
        tprfolder=`echo tpr=${{tpr}}`
        cd ${{tprfolder}}
        # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder
        doping=`echo $di*2|bc -q`
        cd Doping${{doping}}h
        # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
        mv resU${{uval}}_g00_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0_gpri0${{gprval}}_W${{wval}}
        mv resU${{uval}}_g0.10_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0.1_gpri0${{gprval}}_W${{wval}}
        cd ../..
        # Currently in 2D/scripts/results/nonGauss/kfolder/
    done
    cd ..
    # Currently in 2D/scripts/results/nonGauss/
done
        ''')
        csh.close()


######################################
# 4TH case TPR,K NOT ARRAYS
#
######################################
elif type(tpr_vals) != list and type(k_vals) != list and type(doping_vals) == list:
    #print("tpr and k are not arrays")
    #print(f'tpr_vals: {tpr_vals} k_vals: {k_vals} doping_vals: {doping_vals}')
    
    # Creating the creatFolders script
    with open(foldname[0], 'w') as cfsh:
        cfsh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
tpr={bash_array(tpr_vals)}
kval={bash_array(k_vals)}
site={site}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{mainFolder}}
mkdir ${{mainFolder}}
cd ${{mainFolder}}
# Currently in 2D/scripts/results/
###############
momentum=$kval
ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
rm -r ${{ktprfolder}}
mkdir ${{ktprfolder}}
cd ${{ktprfolder}}
# Currently in 2D/scripts/results/ktpr/
for di in {bash_array(doping_vals)};do
   doping=`echo $di*2|bc -q`
   filling=`echo $site-$doping|bc -q`
   dnFilling=`echo "($site-$doping)/2"|bc -q`
   upFilling=`echo $filling-$dnFilling|bc -q`
   runFolder=`echo 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
   rm -r ${{runFolder}}
   mkdir  ${{runFolder}}
   cp ../../../../../*.in ./${{runFolder}}
   cp ../../../../../*.config ./${{runFolder}}
   cd ${{runFolder}}
   # Currently in 2D/scripts/results/ktpr/specific
   echo "creating folder ${{runFolder}}"
   cat > ./model_params.in<<EOF
Hubbard-Holstein
U= ${{uval}}      t= 1
g= ${{gval}}      W= ${{wval}}
t'= ${{tpr}}      g'= ${{gprval}}
EOF
cat > ./hilbertspace_params.in <<EOF
Cluster:        ${{site}}A
ElectronicSiteNumber: ${{site}}
Dimension:      2D
Boundary:       Periodic
Representation: Momentum
Momentum: $momentum
Occupancy:      ${{filling}}($upFilling,$dnFilling)
EOF
       echo "params changed"
       cat > ./cori_NGSED_Obs.sh<<EOF
#!/bin/sh
#SBATCH -J U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}_k${{momentum}}_${{doping}}h_tpr${{tpr}}
#SBATCH -A m3706
#SBATCH -p regular
#SBATCH --nodes=4
#SBATCH -t 01:00:00
#SBATCH --tasks-per-node=8
#SBATCH --cpus-per-task=8
#SBATCH --constraint=haswell
#SBATCH -e job.err
#SBATCH -o job.out
#SBATCH --mail-type=fail
#SBATCH --mail-user=mtm9@g.clemson.edu
#SBATCH -V
cd \$SLURM_SUBMIT_DIR

rm job.*
rm *.txt

export OMP_PROC_BIND=true
export OMP_PLACES=threads
export OMP_NUM_THREADS=8
srun ../../../../../../../NGSED_GROUND_OBS >& mylog
wait
EOF
    echo "created script for ${{runFolder}}"
    cd ..
    # Currently in 2D/scripts/results/ktpr
done
        ''')
        cfsh.close()
        
        # Creating the submit script
        with open(foldname[1], 'w') as ssh:
            ssh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
tpr={bash_array(tpr_vals)}
kval={bash_array(k_vals)}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
cd ${{mainFolder}}
###############
# Currently in 2D/scripts/results/
echo "k= ${{kval}}, tpr=${{tpr}}"
ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
cd ${{ktprfolder}}
# Currently in 2D/scripts/results/ktpr/
for di in {bash_array(doping_vals)};do
    doping=`echo $di*2|bc -q`
    cd 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h
        # Currently in 2D/scripts/results/ktpr/specific
        sbatch cori_NGSED_Obs.sh
    cd ..
    # Currently in 2D/scripts/results/ktpr/
done
        ''')
        ssh.close()
        
        # Creating the Collection script
        with open(foldname[2], 'w') as csh:
            csh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
tpr={bash_array(tpr_vals)}
kval={bash_array(k_vals)}
# Currently in 2D/scripts/
mainFolder=`echo Results`
cd ../../${{mainFolder}}
# Currently in 2D/scripts/results/
resFolder=`echo nonGaussEDGround2D_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{resFolder}}
mkdir ${{resFolder}}
cd ${{resFolder}}

# Currently in 2D/scripts/results/nonGauss
kfolder=`echo k=${{kval}}`
mkdir ${{kfolder}}
cd ${{kfolder}}
# Currently in 2D/scripts/results/nonGauss/k=()/
tprfolder=`echo tpr=${{tpr}}`
mkdir ${{tprfolder}} 
cd ${{tprfolder}}
# Currently in 2D/scripts/results/nonGauss/k=()/tpr=()/
for di in {bash_array(doping_vals)};do
    doping=`echo $di*2|bc -q`
    mkdir Doping${{doping}}h
    cd Doping${{doping}}h
    # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
    dataFolder=`echo  ../../../../../Scripts/{fold}-*/{num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}/k=${{kval}}tpr=${{tpr}}/2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
    collectFolder=`echo ./resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}}`
    mkdir ${{collectFolder}}

    cp ${{dataFolder}}/mylog  ${{collectFolder}}/
    cp ${{dataFolder}}/NGSED_iteration_observables.txt  ${{collectFolder}}/nonGaussED_eq_observables.txt
    cp ${{dataFolder}}/NGSED_iteration_variables.txt  ${{collectFolder}}/varState.txt
    cp ${{dataFolder}}/hilbertspace_params.in  ${{collectFolder}}/
    cp ${{dataFolder}}/observable_name_list.txt ${{collectFolder}}/observableList.txt
    echo "copied ${{dataFolder}} to ${{collectFolder}}"
    mv resU${{uval}}_g0${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g0${{gval}}_W${{wval}}
    mv resU${{uval}}_g${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g${{gval}}_W${{wval}}
    mv resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g${{gval}}_gpr${{gprval}}_W${{wval}}
    mv resU${{uval}}_g0${{gval}}_gpr0.10_W${{wval}} resU${{uval}}_g0${{gval}}_gpr0.1_W${{wval}}
    cd ..
    # Currently in 2D/scripts/results/nonGauss/kfolder/tprfolder/
done
cd ../..

# Currently in 2D/scripts/results/nonGauss
kfolder=`echo k=${{kval}}`
cd ${{kfolder}}
# Currently in 2D/scripts/results/nonGauss/kfolder
tprfolder=`echo tpr=${{tpr}}`
cd ${{tprfolder}}
# Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder
for di in {bash_array(doping_vals)};do
    doping=`echo $di*2|bc -q`
    cd Doping${{doping}}h
    # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
    mv resU${{uval}}_g00_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0_gpri0${{gprval}}_W${{wval}}
    mv resU${{uval}}_g0.10_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0.1_gpri0${{gprval}}_W${{wval}}
    cd ..
    # Currently in 2D/scripts/results/nonGauss/kfolder/tprfolder/
done
        ''')
        csh.close()

######################################
# 5TH case TPR,DOPING NOT ARRAYS
#
######################################
elif type(tpr_vals) != list and type(k_vals) == list and type(doping_vals) != list:
    #print("tpr and doping are not arrays")
    #print(f'tpr_vals: {tpr_vals} k_vals: {k_vals} doping_vals: {doping_vals}')
    
    # Creating the creatFolders script
    with open(foldname[0], 'w') as cfsh:
        cfsh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
tpr={bash_array(tpr_vals)}
di={bash_array(doping_vals)}
site={site}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{mainFolder}}
mkdir ${{mainFolder}}
cd ${{mainFolder}}
# Currently in 2D/scripts/results/
###############
for kval in {bash_array(k_vals)};do
    momentum=$kval
    ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
    rm -r ${{ktprfolder}}
    mkdir ${{ktprfolder}}
    cd ${{ktprfolder}}
    # Currently in 2D/scripts/results/ktpr/
    doping=`echo $di*2|bc -q`
    filling=`echo $site-$doping|bc -q`
    dnFilling=`echo "($site-$doping)/2"|bc -q`
    upFilling=`echo $filling-$dnFilling|bc -q`
    runFolder=`echo 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
    rm -r ${{runFolder}}
    mkdir  ${{runFolder}}
    cp ../../../../../*.in ./${{runFolder}}
    cp ../../../../../*.config ./${{runFolder}}
    cd ${{runFolder}}
    # Currently in 2D/scripts/results/ktpr/specific
    echo "creating folder ${{runFolder}}"
    cat > ./model_params.in<<EOF
Hubbard-Holstein
U= ${{uval}}      t= 1
g= ${{gval}}      W= ${{wval}}
t'= ${{tpr}}      g'= ${{gprval}}
EOF
cat > ./hilbertspace_params.in <<EOF
Cluster:        ${{site}}A
ElectronicSiteNumber: ${{site}}
Dimension:      2D
Boundary:       Periodic
Representation: Momentum
Momentum: $momentum
Occupancy:      ${{filling}}($upFilling,$dnFilling)
EOF
       echo "params changed"
       cat > ./cori_NGSED_Obs.sh<<EOF
#!/bin/sh
#SBATCH -J U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}_k${{momentum}}_${{doping}}h_tpr${{tpr}}
#SBATCH -A m3706
#SBATCH -p regular
#SBATCH --nodes=4
#SBATCH -t 01:00:00
#SBATCH --tasks-per-node=8
#SBATCH --cpus-per-task=8
#SBATCH --constraint=haswell
#SBATCH -e job.err
#SBATCH -o job.out
#SBATCH --mail-type=fail
#SBATCH --mail-user=mtm9@g.clemson.edu
#SBATCH -V
cd \$SLURM_SUBMIT_DIR

rm job.*
rm *.txt

export OMP_PROC_BIND=true
export OMP_PLACES=threads
export OMP_NUM_THREADS=8
srun ../../../../../../../NGSED_GROUND_OBS >& mylog
wait
EOF
        echo "created script for ${{runFolder}}"
    cd ../..
    # Currently in 2D/scripts/results/
done
        ''')
        cfsh.close()
        
        # Creating the submit script
        with open(foldname[1], 'w') as ssh:
            ssh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
tpr={bash_array(tpr_vals)}
di={bash_array(doping_vals)}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
cd ${{mainFolder}}
###############
for kval in {bash_array(k_vals)};do
    # Currently in 2D/scripts/results/
    echo "k= ${{kval}}, tpr=${{tpr}}"
    ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
    cd ${{ktprfolder}}
    # Currently in 2D/scripts/results/ktpr/
    doping=`echo $di*2|bc -q`
    cd 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h
        # Currently in 2D/scripts/results/ktpr/specific
        sbatch cori_NGSED_Obs.sh
    cd ../..
    # Currently in 2D/scripts/results/
done
        ''')
        ssh.close()
        
        # Creating the Collection script
        with open(foldname[2], 'w') as csh:
            csh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
tpr={bash_array(tpr_vals)}
di={bash_array(doping_vals)}
# Currently in 2D/scripts/
mainFolder=`echo Results`
cd ../../${{mainFolder}}
# Currently in 2D/scripts/results/
resFolder=`echo nonGaussEDGround2D_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{resFolder}}
mkdir ${{resFolder}}
cd ${{resFolder}}

# Currently in 2D/scripts/results/nonGauss
for kval in {bash_array(k_vals)};do
    kfolder=`echo k=${{kval}}`
    mkdir ${{kfolder}}
    cd ${{kfolder}}
    # Currently in 2D/scripts/results/nonGauss/k=()/
    tprfolder=`echo tpr=${{tpr}}`
    mkdir ${{tprfolder}} 
    cd ${{tprfolder}}
    # Currently in 2D/scripts/results/nonGauss/k=()/tpr=()/
    doping=`echo $di*2|bc -q`
    mkdir Doping${{doping}}h
    cd Doping${{doping}}h
    # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
    dataFolder=`echo  ../../../../../Scripts/{fold}-*/{num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}/k=${{kval}}tpr=${{tpr}}/2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
    collectFolder=`echo ./resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}}`
    mkdir ${{collectFolder}}

    cp ${{dataFolder}}/mylog  ${{collectFolder}}/
    cp ${{dataFolder}}/NGSED_iteration_observables.txt  ${{collectFolder}}/nonGaussED_eq_observables.txt
    cp ${{dataFolder}}/NGSED_iteration_variables.txt  ${{collectFolder}}/varState.txt
    cp ${{dataFolder}}/hilbertspace_params.in  ${{collectFolder}}/
    cp ${{dataFolder}}/observable_name_list.txt ${{collectFolder}}/observableList.txt
    echo "copied ${{dataFolder}} to ${{collectFolder}}"
    mv resU${{uval}}_g0${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g0${{gval}}_W${{wval}}
    mv resU${{uval}}_g${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g${{gval}}_W${{wval}}
    mv resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g${{gval}}_gpr${{gprval}}_W${{wval}}
    mv resU${{uval}}_g0${{gval}}_gpr0.10_W${{wval}} resU${{uval}}_g0${{gval}}_gpr0.1_W${{wval}}
    cd ../../..
    # Currently in 2D/scripts/results/nonGauss/
done

# Currently in 2D/scripts/results/nonGauss
for kval in {bash_array(k_vals)};do
    kfolder=`echo k=${{kval}}`
    cd ${{kfolder}}
    # Currently in 2D/scripts/results/nonGauss/kfolder
    tprfolder=`echo tpr=${{tpr}}`
    cd ${{tprfolder}}
    # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder
    doping=`echo $di*2|bc -q`
    cd Doping${{doping}}h
    # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
    mv resU${{uval}}_g00_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0_gpri0${{gprval}}_W${{wval}}
    mv resU${{uval}}_g0.10_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0.1_gpri0${{gprval}}_W${{wval}}
    cd ../../..
    # Currently in 2D/scripts/results/nonGauss/
done
        ''')
        csh.close()

######################################
# 6TH case K,DOPING NOT ARRAYS
#
######################################
elif type(tpr_vals) == list and type(k_vals) != list and type(doping_vals) != list:
    #print("k and doping are not arrays")
    #print(f'tpr_vals: {tpr_vals} k_vals: {k_vals} doping_vals: {doping_vals}')
    
    # Creating the creatFolders script
    with open(foldname[0], 'w') as cfsh:
        cfsh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
kval={bash_array(k_vals)}
di={bash_array(doping_vals)}
site={site}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{mainFolder}}
mkdir ${{mainFolder}}
cd ${{mainFolder}}
# Currently in 2D/scripts/results/
###############
momentum=$kval
for tpr in {bash_array(tpr_vals)};do
    ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
    rm -r ${{ktprfolder}}
    mkdir ${{ktprfolder}}
    cd ${{ktprfolder}}
    # Currently in 2D/scripts/results/ktpr/
    doping=`echo $di*2|bc -q`
    filling=`echo $site-$doping|bc -q`
    dnFilling=`echo "($site-$doping)/2"|bc -q`
    upFilling=`echo $filling-$dnFilling|bc -q`
    runFolder=`echo 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
    rm -r ${{runFolder}}
    mkdir  ${{runFolder}}
    cp ../../../../../*.in ./${{runFolder}}
    cp ../../../../../*.config ./${{runFolder}}
    cd ${{runFolder}}
    # Currently in 2D/scripts/results/ktpr/specific
    echo "creating folder ${{runFolder}}"
    cat > ./model_params.in<<EOF
Hubbard-Holstein
U= ${{uval}}      t= 1
g= ${{gval}}      W= ${{wval}}
t'= ${{tpr}}      g'= ${{gprval}}
EOF
cat > ./hilbertspace_params.in <<EOF
Cluster:        ${{site}}A
ElectronicSiteNumber: ${{site}}
Dimension:      2D
Boundary:       Periodic
Representation: Momentum
Momentum: $momentum
Occupancy:      ${{filling}}($upFilling,$dnFilling)
EOF
   echo "params changed"
   cat > ./cori_NGSED_Obs.sh<<EOF
#!/bin/sh
#SBATCH -J U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}_k${{momentum}}_${{doping}}h_tpr${{tpr}}
#SBATCH -A m3706
#SBATCH -p regular
#SBATCH --nodes=4
#SBATCH -t 01:00:00
#SBATCH --tasks-per-node=8
#SBATCH --cpus-per-task=8
#SBATCH --constraint=haswell
#SBATCH -e job.err
#SBATCH -o job.out
#SBATCH --mail-type=fail
#SBATCH --mail-user=mtm9@g.clemson.edu
#SBATCH -V
cd \$SLURM_SUBMIT_DIR

rm job.*
rm *.txt

export OMP_PROC_BIND=true
export OMP_PLACES=threads
export OMP_NUM_THREADS=8
srun ../../../../../../../NGSED_GROUND_OBS >& mylog
wait
EOF
    echo "created script for ${{runFolder}}"
    cd ../..
    # Currently in 2D/scripts/results/
done
        ''')
        cfsh.close()
        
        # Creating the submit script
        with open(foldname[1], 'w') as ssh:
            ssh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
kval={bash_array(k_vals)}
di={bash_array(doping_vals)}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
cd ${{mainFolder}}
###############
for tpr in {bash_array(tpr_vals)};do
    # Currently in 2D/scripts/results/
    echo "k= ${{kval}}, tpr=${{tpr}}"
    ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
    cd ${{ktprfolder}}
    # Currently in 2D/scripts/results/ktpr/
    doping=`echo $di*2|bc -q`
    cd 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h
        # Currently in 2D/scripts/results/ktpr/specific
        sbatch cori_NGSED_Obs.sh
    cd ../..
    # Currently in 2D/scripts/results/
done
        ''')
        ssh.close()
        
        # Creating the Collection script
        with open(foldname[2], 'w') as csh:
            csh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
kval={bash_array(k_vals)}
di={bash_array(doping_vals)}
# Currently in 2D/scripts/
mainFolder=`echo Results`
cd ../../${{mainFolder}}
# Currently in 2D/scripts/results/
resFolder=`echo nonGaussEDGround2D_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{resFolder}}
mkdir ${{resFolder}}
cd ${{resFolder}}

# Currently in 2D/scripts/results/nonGauss
kfolder=`echo k=${{kval}}`
mkdir ${{kfolder}}
cd ${{kfolder}}
# Currently in 2D/scripts/results/nonGauss/k=()/
for tpr in {bash_array(tpr_vals)};do
    tprfolder=`echo tpr=${{tpr}}`
    mkdir ${{tprfolder}} 
    cd ${{tprfolder}}
    # Currently in 2D/scripts/results/nonGauss/k=()/tpr=()/
    doping=`echo $di*2|bc -q`
    mkdir Doping${{doping}}h
    cd Doping${{doping}}h
    # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
    dataFolder=`echo  ../../../../../Scripts/{fold}-*/{num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}/k=${{kval}}tpr=${{tpr}}/2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
    collectFolder=`echo ./resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}}`
    mkdir ${{collectFolder}}

    cp ${{dataFolder}}/mylog  ${{collectFolder}}/
    cp ${{dataFolder}}/NGSED_iteration_observables.txt  ${{collectFolder}}/nonGaussED_eq_observables.txt
    cp ${{dataFolder}}/NGSED_iteration_variables.txt  ${{collectFolder}}/varState.txt
    cp ${{dataFolder}}/hilbertspace_params.in  ${{collectFolder}}/
    cp ${{dataFolder}}/observable_name_list.txt ${{collectFolder}}/observableList.txt
    echo "copied ${{dataFolder}} to ${{collectFolder}}"
    mv resU${{uval}}_g0${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g0${{gval}}_W${{wval}}
    mv resU${{uval}}_g${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g${{gval}}_W${{wval}}
    mv resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g${{gval}}_gpr${{gprval}}_W${{wval}}
    mv resU${{uval}}_g0${{gval}}_gpr0.10_W${{wval}} resU${{uval}}_g0${{gval}}_gpr0.1_W${{wval}}
    cd ../..
    # Currently in 2D/scripts/results/nonGauss/kfolder/
done

# Currently in 2D/scripts/results/nonGauss
kfolder=`echo k=${{kval}}`
cd ${{kfolder}}
# Currently in 2D/scripts/results/nonGauss/kfolder
for tpr in {bash_array(tpr_vals)};do
    tprfolder=`echo tpr=${{tpr}}`
    cd ${{tprfolder}}
    # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder
    doping=`echo $di*2|bc -q`
    cd Doping${{doping}}h
    # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
    mv resU${{uval}}_g00_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0_gpri0${{gprval}}_W${{wval}}
    mv resU${{uval}}_g0.10_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0.1_gpri0${{gprval}}_W${{wval}}
    cd ../..
    # Currently in 2D/scripts/results/nonGauss/kfolder/
done
        ''')
        csh.close()

######################################
# 7TH case NONE ARRAYS
#
######################################
elif type(tpr_vals) != list and type(k_vals) != list and type(doping_vals) != list:
    #print("None are arrays")
    #print(f'tpr_vals: {tpr_vals} k_vals: {k_vals} doping_vals: {doping_vals}')
    
    # Creating the creatFolders script
    with open(foldname[0], 'w') as cfsh:
        cfsh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
tpr={bash_array(tpr_vals)}
di={bash_array(doping_vals)}
kval={bash_array(k_vals)}
site={site}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{mainFolder}}
mkdir ${{mainFolder}}
cd ${{mainFolder}}
# Currently in 2D/scripts/results/
###############
momentum=$kval
ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
rm -r ${{ktprfolder}}
mkdir ${{ktprfolder}}
cd ${{ktprfolder}}
# Currently in 2D/scripts/results/ktpr/
doping=`echo $di*2|bc -q`
filling=`echo $site-$doping|bc -q`
dnFilling=`echo "($site-$doping)/2"|bc -q`
upFilling=`echo $filling-$dnFilling|bc -q`
runFolder=`echo 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
rm -r ${{runFolder}}
mkdir  ${{runFolder}}
cp ../../../../../*.in ./${{runFolder}}
cp ../../../../../*.config ./${{runFolder}}
cd ${{runFolder}}
# Currently in 2D/scripts/results/ktpr/specific
echo "creating folder ${{runFolder}}"
cat > ./model_params.in<<EOF
Hubbard-Holstein
U= ${{uval}}      t= 1
g= ${{gval}}      W= ${{wval}}
t'= ${{tpr}}      g'= ${{gprval}}
EOF
cat > ./hilbertspace_params.in <<EOF
Cluster:        ${{site}}A
ElectronicSiteNumber: ${{site}}
Dimension:      2D
Boundary:       Periodic
Representation: Momentum
Momentum: $momentum
Occupancy:      ${{filling}}($upFilling,$dnFilling)
EOF
       echo "params changed"
       cat > ./cori_NGSED_Obs.sh<<EOF
#!/bin/sh
#SBATCH -J U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}_k${{momentum}}_${{doping}}h_tpr${{tpr}}
#SBATCH -A m3706
#SBATCH -p regular
#SBATCH --nodes=4
#SBATCH -t 01:00:00
#SBATCH --tasks-per-node=8
#SBATCH --cpus-per-task=8
#SBATCH --constraint=haswell
#SBATCH -e job.err
#SBATCH -o job.out
#SBATCH --mail-type=fail
#SBATCH --mail-user=mtm9@g.clemson.edu
#SBATCH -V
cd \$SLURM_SUBMIT_DIR

rm job.*
rm *.txt

export OMP_PROC_BIND=true
export OMP_PLACES=threads
export OMP_NUM_THREADS=8
srun ../../../../../../../NGSED_GROUND_OBS >& mylog
wait
EOF
echo "created script for ${{runFolder}}"

        ''')
        cfsh.close()
        
        # Creating the submit script
        with open(foldname[1], 'w') as ssh:
            ssh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
tpr={bash_array(tpr_vals)}
di={bash_array(doping_vals)}
kval={bash_array(k_vals)}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
cd ${{mainFolder}}
###############
# Currently in 2D/scripts/results/
echo "k= ${{kval}}, tpr=${{tpr}}"
ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
cd ${{ktprfolder}}
# Currently in 2D/scripts/results/ktpr/
doping=`echo $di*2|bc -q`
cd 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h
    # Currently in 2D/scripts/results/ktpr/specific
    sbatch cori_NGSED_Obs.sh

        ''')
        ssh.close()
        
        # Creating the Collection script
        with open(foldname[2], 'w') as csh:
            csh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
tpr={bash_array(tpr_vals)}
di={bash_array(doping_vals)}
kval={bash_array(k_vals)}
# Currently in 2D/scripts/
mainFolder=`echo Results`
cd ../../${{mainFolder}}
# Currently in 2D/scripts/results/
resFolder=`echo nonGaussEDGround2D_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{resFolder}}
mkdir ${{resFolder}}
cd ${{resFolder}}

# Currently in 2D/scripts/results/nonGauss
kfolder=`echo k=${{kval}}`
mkdir ${{kfolder}}
cd ${{kfolder}}
# Currently in 2D/scripts/results/nonGauss/k=()/
tprfolder=`echo tpr=${{tpr}}`
mkdir ${{tprfolder}} 
cd ${{tprfolder}}
# Currently in 2D/scripts/results/nonGauss/k=()/tpr=()/
doping=`echo $di*2|bc -q`
mkdir Doping${{doping}}h
cd Doping${{doping}}h
# Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
dataFolder=`echo  ../../../../../Scripts/{fold}-*/{num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}/k=${{kval}}tpr=${{tpr}}/2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
collectFolder=`echo ./resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}}`
mkdir ${{collectFolder}}

cp ${{dataFolder}}/mylog  ${{collectFolder}}/
cp ${{dataFolder}}/NGSED_iteration_observables.txt  ${{collectFolder}}/nonGaussED_eq_observables.txt
cp ${{dataFolder}}/NGSED_iteration_variables.txt  ${{collectFolder}}/varState.txt
cp ${{dataFolder}}/hilbertspace_params.in  ${{collectFolder}}/
cp ${{dataFolder}}/observable_name_list.txt ${{collectFolder}}/observableList.txt
echo "copied ${{dataFolder}} to ${{collectFolder}}"
mv resU${{uval}}_g0${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g0${{gval}}_W${{wval}}
mv resU${{uval}}_g${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g${{gval}}_W${{wval}}
mv resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g${{gval}}_gpr${{gprval}}_W${{wval}}
mv resU${{uval}}_g0${{gval}}_gpr0.10_W${{wval}} resU${{uval}}_g0${{gval}}_gpr0.1_W${{wval}}

# Currently in 2D/scripts/results/nonGauss
kfolder=`echo k=${{kval}}`
cd ${{kfolder}}
# Currently in 2D/scripts/results/nonGauss/kfolder
tprfolder=`echo tpr=${{tpr}}`
cd ${{tprfolder}}
# Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder
doping=`echo $di*2|bc -q`
cd Doping${{doping}}h
# Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
mv resU${{uval}}_g00_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0_gpri0${{gprval}}_W${{wval}}
mv resU${{uval}}_g0.10_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0.1_gpri0${{gprval}}_W${{wval}}
        ''')
        csh.close()

######################################
# 8TH case ALL ARRAYS
#
######################################
else:
    # Display of information
    #print("All are arrays")
    #print(f'tpr_vals: {tpr_vals} k_vals: {k_vals} doping_vals: {doping_vals}')
    
    # Creating the creatFolders script
    with open(foldname[0], 'w') as cfsh:
        cfsh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
site={site}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{mainFolder}}
mkdir ${{mainFolder}}
cd ${{mainFolder}}
# Currently in 2D/scripts/results/
###############
for kval in {bash_array(k_vals)};do
    momentum=$kval
    for tpr in {bash_array(tpr_vals)};do
        ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
        rm -r ${{ktprfolder}}
        mkdir ${{ktprfolder}}
        cd ${{ktprfolder}}
        # Currently in 2D/scripts/results/ktpr/
        for di in {bash_array(doping_vals)};do
           doping=`echo $di*2|bc -q`
           filling=`echo $site-$doping|bc -q`
           dnFilling=`echo "($site-$doping)/2"|bc -q`
           upFilling=`echo $filling-$dnFilling|bc -q`
           runFolder=`echo 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
           rm -r ${{runFolder}}
           mkdir  ${{runFolder}}
           cp ../../../../../*.in ./${{runFolder}}
           cp ../../../../../*.config ./${{runFolder}}
           cd ${{runFolder}}
           # Currently in 2D/scripts/results/ktpr/specific
           echo "creating folder ${{runFolder}}"
           cat > ./model_params.in<<EOF
Hubbard-Holstein
U= ${{uval}}      t= 1
g= ${{gval}}      W= ${{wval}}
t'= ${{tpr}}      g'= ${{gprval}}
EOF
cat > ./hilbertspace_params.in <<EOF
Cluster:        ${{site}}A
ElectronicSiteNumber: ${{site}}
Dimension:      2D
Boundary:       Periodic
Representation: Momentum
Momentum: $momentum
Occupancy:      ${{filling}}($upFilling,$dnFilling)
EOF
       echo "params changed"
       cat > ./cori_NGSED_Obs.sh<<EOF
#!/bin/sh
#SBATCH -J U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}_k${{momentum}}_${{doping}}h_tpr${{tpr}}
#SBATCH -A m3706
#SBATCH -p regular
#SBATCH --nodes=4
#SBATCH -t 01:00:00
#SBATCH --tasks-per-node=8
#SBATCH --cpus-per-task=8
#SBATCH --constraint=haswell
#SBATCH -e job.err
#SBATCH -o job.out
#SBATCH --mail-type=fail
#SBATCH --mail-user=mtm9@g.clemson.edu
#SBATCH -V
cd \$SLURM_SUBMIT_DIR

rm job.*
rm *.txt

export OMP_PROC_BIND=true
export OMP_PLACES=threads
export OMP_NUM_THREADS=8
srun ../../../../../../../NGSED_GROUND_OBS >& mylog
wait
EOF
            echo "created script for ${{runFolder}}"
            cd ..
            # Currently in 2D/scripts/results/ktpr/
        done
        cd ..
        # Currently in 2D/scripts/results/
    done
done
        ''')
        cfsh.close()
        
        # Creating the submit script
        with open(foldname[1], 'w') as ssh:
            ssh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
# Currently in 2D/scripts/
mainFolder=`echo {num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}`
cd ${{mainFolder}}
###############
for kval in {bash_array(k_vals)};do
    for tpr in {bash_array(tpr_vals)};do
        # Currently in 2D/scripts/results/
        echo "k= ${{kval}}, tpr=${{tpr}}"
        ktprfolder=`echo k=${{kval}}tpr=${{tpr}}`
        cd ${{ktprfolder}}
        # Currently in 2D/scripts/results/ktpr/
        for di in {bash_array(doping_vals)};do
            doping=`echo $di*2|bc -q`
            cd 2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h
                # Currently in 2D/scripts/results/ktpr/specific
                sbatch cori_NGSED_Obs.sh
            cd ..
            # Currently in 2D/scripts/results/ktpr/
        done
        cd ..
        # Currently in 2D/scripts/results/
    done
done
        ''')
        ssh.close()
        
        # Creating the Collection script
        with open(foldname[2], 'w') as csh:
            csh.write(f'''\
#!/bin/bash
uval={uval}
wval={wval}
gval={gval}
gprval={gprval}
# Currently in 2D/scripts/
mainFolder=`echo Results`
cd ../../${{mainFolder}}
# Currently in 2D/scripts/results/
resFolder=`echo nonGaussEDGround2D_g${{gval}}_gpr${{gprval}}_w${{wval}}`
rm -r ${{resFolder}}
mkdir ${{resFolder}}
cd ${{resFolder}}
# Currently in 2D/scripts/results/nonGauss
for kval in {bash_array(k_vals)};do
    kfolder=`echo k=${{kval}}`
    mkdir ${{kfolder}}
    cd ${{kfolder}}
    # Currently in 2D/scripts/results/nonGauss/k=()/
    for tpr in {bash_array(tpr_vals)};do
        tprfolder=`echo tpr=${{tpr}}`
        mkdir ${{tprfolder}} 
        cd ${{tprfolder}}
        # Currently in 2D/scripts/results/nonGauss/k=()/tpr=()/
        for di in {bash_array(doping_vals)};do
          doping=`echo $di*2|bc -q`
          mkdir Doping${{doping}}h
          cd Doping${{doping}}h
          # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
          dataFolder=`echo  ../../../../../Scripts/{fold}-*/{num}-data_U${{uval}}_g${{gval}}_gpr${{gprval}}_w${{wval}}/k=${{kval}}tpr=${{tpr}}/2D_U${{uval}}g${{gval}}gpr${{gprval}}W${{wval}}_${{doping}}h`
          collectFolder=`echo ./resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}}`
          mkdir ${{collectFolder}}

          cp ${{dataFolder}}/mylog  ${{collectFolder}}/
          cp ${{dataFolder}}/NGSED_iteration_observables.txt  ${{collectFolder}}/nonGaussED_eq_observables.txt
          cp ${{dataFolder}}/NGSED_iteration_variables.txt  ${{collectFolder}}/varState.txt
          cp ${{dataFolder}}/hilbertspace_params.in  ${{collectFolder}}/
          cp ${{dataFolder}}/observable_name_list.txt ${{collectFolder}}/observableList.txt
          echo "copied ${{dataFolder}} to ${{collectFolder}}"
          mv resU${{uval}}_g0${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g0${{gval}}_W${{wval}}
          mv resU${{uval}}_g${{gval}}_gpri00_W${{wval}}  resU${{uval}}_g${{gval}}_W${{wval}}
          mv resU${{uval}}_g${{gval}}_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g${{gval}}_gpr${{gprval}}_W${{wval}}
          mv resU${{uval}}_g0${{gval}}_gpr0.10_W${{wval}} resU${{uval}}_g0${{gval}}_gpr0.1_W${{wval}}
          cd ..
          # Currently in 2D/scripts/results/nonGauss/kfolder/tprfolder/
        done
        cd ..
        # Currently in 2D/scripts/results/nonGauss/kfolder/
    done
    cd ..
    # Currently in 2D/scripts/results/nonGauss/
done

# Currently in 2D/scripts/results/nonGauss
for kval in {bash_array(k_vals)};do
    kfolder=`echo k=${{kval}}`
    cd ${{kfolder}}
    # Currently in 2D/scripts/results/nonGauss/kfolder
    for tpr in {bash_array(tpr_vals)};do
        tprfolder=`echo tpr=${{tpr}}`
        cd ${{tprfolder}}
        # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder
        for di in {bash_array(doping_vals)};do
            doping=`echo $di*2|bc -q`
            cd Doping${{doping}}h
            # Currently in 2D/scripts/results/nonGauss/Kfolder/tprfolder/SpecificDoping
            mv resU${{uval}}_g00_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0_gpri0${{gprval}}_W${{wval}}
            mv resU${{uval}}_g0.10_gpri0${{gprval}}_W${{wval}} resU${{uval}}_g0.1_gpri0${{gprval}}_W${{wval}}
            cd ..
            # Currently in 2D/scripts/results/nonGauss/kfolder/tprfolder/
        done
        cd ..
        # Currently in 2D/scripts/results/nonGauss/kfolder/
    done
    cd ..
    # Currently in 2D/scripts/results/nonGauss/
done
        ''')
        csh.close()

