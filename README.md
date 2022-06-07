Phonon Database
========================
Author: Matt Myers (Clemson University)
------
Update Date: June 6, 2022

## Function of the codes:
This program is split into three main files:

- `options.py` gives the global program options, the choices decide the length and complexity of the run.
  
- `make_database.py` is the main program that takes in the data, filters out directories that lack information, organize the findings into a dictionary, creates desired figures specified in `options.py`, and finally creates the database using __mongoDB__.

- `data_funcs.py` is the program housing all of the functions utilized in the main program. The combination of `options.py` and `datafuncs.py` allow the main program `make_database.py` to run correctly.

## Input and Output
### Options:
`options.py` gives the global program options, the root directory is where the program will look for the data this is the input for `make_database.py`. The subfolders do not matter just the parent folder
```
# Root directory
rootdir = 'C:\\******\\******\\******\\******\\******\\****\\******'

# Options
cmap = True or False
figs = True or False
upload = True or False
```
The options input file contain the optional aspects of the program. The options are boolean so either *True* or *False* would be the choices.

- `cmap` - the option that tells the main program whether to create a colormap or not
- `figs` - the option that tells the main program whether to create doping versus various parameter graphs
- `upload` - the option telling the main program to either upload the information to the database or not. This is helpful for debugging other aspects of the program.
  
### Inputs/Outputs:
`hilbertspace_params.in` sets the basic information about cluster shape, size, dimension, boundary condition, spatial representation, filling and addition restrictions
```
#!bash
Cluster:  8A
ElectronicSiteNumber: 8
Dimension:  2D
Boundary: Periodic
Representation: Momentum
Momentum: 0
Occupancy:  8
#MaxPhononNumber: 5 PhononModeNumber: 2
#PhononMomenta: 0 4
#PhononMomentumOccupancyRestriction: 2 2
#Restrictions: NoDouble
```
The `#` comments out unused options. The Hilbert space input file contain many aspects of information

- `Cluster` - cluster size and name (*required*). It specifies the system size and geometry. The cluster name follows Beth clusters.
- `ElectronicSiteNumber` or `Orbital` number. It specifies the total size * orbital number, or orbital number separately. For example, setting `ElectronicSiteNumber :16` above is equivalent to setting `Orbital: 2`. 
- `Dimension` - the system dimension, 1D or 2D.
- `Boundary` - boundary condition.
- `Representation` - whether the many-body state is written in real or reciprocal space. It can be `Momentum` only when `Boundary` is `Periodic`. 
- `Momentum` specifies the total momentum of the system. It can only be specified when `Boundary` is `Periodic`. 
- `Occupancy` specifies the total electron occupation. The spin up and down occupations can be further specified, e.g. `Occupancy: 8(3,5)`. 



`model_params.in` sets the overall model parameters in the following format
```
#!bash
Hubbard
U= 8        V= 0
t= 1        t'= -0.3     t''= 0.2
```
``spec_params.in`` sets the parameters of non-equilibrium time-domain calculation in the follow format
```
#!bash
SpecType: Sqw   N(q,w)  Raman[B1g]
Frequencies:    wMin= -5    wMax= 5    wDelta= 0.005
```
``timeparams.in`` sets the parameters of non-equilibrium dynamics and spectral calculation in the follow format
```
#!bash
Time: start= 0.05 end= 60 dt= 0.05
Pump: A0= 1.2 w0= 4.4 sigma= 3.0 t0= 19.0
Polarization: x= 1 y= 1
Probe:  sigma= 2.0 
```
Note, the probe type and frequencies are set in ``spec_params.in``
## Compiling and Running
### Compile the code
The compilation is automated in the Makefile:
```
    make EXECUTABLE
```
where the ``EXECUTABLE`` is the target program defined above.

For different machines, one shoud change the definition of compilers and flags. For example, in NERSC where environment has been predefined, one can call ``CC`` as an abstract compiler
```
#!bash
CXX = CC #-std=c++14
FLAGS = -O3 -no-prec-div -static -fp-model fast=2 -xHost -openmp
```
Instead, in TACC one should use specific MPI compiler and ``static`` does not work
```
#!bash
CXX = mpicxx
FLAGS = -O3 -no-prec-div -fp-model fast=2 -xHost -openmp
```
### Dependent libraries
Most of the program is based on Eigen data structure. The ground state calculation (diagonalization) lies in PARPACK dynamic libaray, though an alternative Lanczos class is also provided. The solution of PDE depends on the Odeint libaray in boost.

To compile the code, one should provide the path for Eigen and Boost in the Makefile, together with the link to the dynamics libaray of PARPACK and ARPACK.

Typically, both Eigen and Boost are modules in a supercomputer. One should ``module load eigen`` and ``module load boost`` before compiling the code.  These paths should be provided in the Makefile as
```
#!bash
HEADERLIBS = $(EIGEN3)/eigen3 -I$(BOOST_DIR)/include 
```
The expansion of these paths read as 
```
#!bash
-I/global/common/cori/software/eigen3/3.3.3/include/eigen3 -I/usr/common/software/boost/1.67.0/intel/haswell/include
```
in NERSC (Cori). In contrast, the PARPACK is not necessarily capsulated as a module. If a ``parpack`` module is availabe, one can ``module load parpack`` before compiling the code, and include the paths as
```
OBJLIBS = $(PARPACK)
```
The path reads as
```
-L/usr/common/software/parpack/3.2.0/hsw/intel/lib -larpack -lparpack
```
in NERSC (Cori).

### Run in a supercomputer cluster
A hybrid MPI + OpenMP parallelization has been implemented in the program. To run a hybrid code, please read the instruction of your supercomputer. A typical ``SLURM``submission script looks like (here is the script for NERSC)
```
#!bash
#!/bin/sh
#SBATCH -J JOBNAME
#SBATCH -p debug
#SBATCH --nodes=10
#SBATCH -t 00:15:00
#SBATCH --tasks-per-node=8
#SBATCH --cpus-per-task=8
#SBATCH --constraint=haswell
#SBATCH -e job.err
#SBATCH -o job.out
#SBATCH -V

cd  $SLURM_SUBMIT_DIR
rm job.*
rm *.txt

export OMP_PROC_BIND=true
export OMP_PLACES=threads
export OMP_NUM_THREADS=4
srun ./testNonEquilibriumDynamics >& mylog
```
It is highly recommended to test the parallelization configurations before heavy batch submissions. Timing is embedded in the code, convenient for such test. The MPI communication overhead is typically larger than the shared-memory OpenMP, therefore, maximizing ``OMP_NUM_THREADS`` is recommended for small problems. However, for the construction of Hilbert space, sparse matrix and some observable evaluations, the read/write overhead is also obvious for the shared-memory scheme. A typicall choice of ``OMP_NUM_THREADS`` is about 4-12.

## Architechture of the Program
The general architechture is reflected in the folders. 

The ``Util`` folder contains all global functions, including global classes (MPI related), math functions, string operations and timer. The `LinearAlgebra` folder contains fundamental MPI-based algebra, including the MPI vector operations, MPI eigen-problem solver, MPI linear problem solver, and the Krylov-subspace exponential solver. Both folders are generically designed without physical purposes.

The `PhysDataStruct` folder contains the elementary data structures constitude the exact diagonalization calculation. The main data structures are: 
 
 1. **cluster classes** (including `ClusterReal` and `ClusterReciprocal`) define the geometric relation, size, dimention and symmetries;
 2. **Hilbert space class** (including the basis element `BasisState` and the entire Hilbert-space class `HilbertSpace`) defines the many-body basis, relavant Fock-space operations, and the space-level operations;
 3. **Hamiltonian matrix class** -- template `HamiltonianMatrix`, consistes of the bottom-level matrix decomposition and matrix-vector product, as well as the high-level matrix construction based on Hamiltonian terms;
 4. **many-body state and operations** (including `ManyBodyState`, `ManyBodyOperator` and `VariationalState`) define the wavefunctions and many-body operations. 

The `MeasureEngines` folder contains high-level exact diagonalization calculations of observables, spectroscopies and dynamics. These classes are directly called by the main function to realize (separately or jointly) a physical purpose. The main data structures are: 

 1. **equilibrium engine** (including pure ED `EquilibriumEngine` and variational + ED `EquilibriumVariationalEngine`) sets up the calculation for ground state and low excited states.
 2. **equilibrium spectroscopy engine** (including `EqSpectrum` and `CPTSpectrum`) sets up the calculation of spectroscopies at equilibrium. It relies on `SpectraParams` as an input of spectral type and energy/momentum range.
 3. **nonequilibrium dynamics engine** -- `NonEqTimeEvolution` calculates the time evolution of an initial wave function after applying a pump field. Observable engine is embedded to measure the instantaneous properties.
 4. **nonequilibrium spectroscopy engine** -- `NonEqSpectrum` measures the time-dependent pump-probe spectroscopies. As an extension of both spectroscopy and nonequilibrium dynamics, it takes the input from both wavefunction dynamics and spectral parameters.

Apart from these four main data structures, there are two measurement engines which does not work separately and is embedded in other engines
 1.  **observable engine** -- ``ObservableEngine`` defines all single-time measurements based on any given wavefunctions. The input/output and reduction operations are embedded in this class. The observable engine is called in other measurement engines.
 2. **ensemble engine** (including `EnsembleObservables` and `EnsembleSpectra`) measures ensemble-based properties using multiple excited states.


### Spectral Engines

For example, the `Nqw` option triggers the calculation of dynamical charge structure factor $N(\mathbf{q},\omega)$, defined as
$$
N(\mathbf{q},\omega) = \frac1\pi \mathrm{Im}\langle G | \rho_{-q} \frac1{\mathcal{H} - E_G - \omega - i\delta} \rho_q |G\rangle
$$