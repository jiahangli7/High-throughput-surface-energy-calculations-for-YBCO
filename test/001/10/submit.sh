#!/bin/bash
#SBATCH --nodes=1
#SBATCH --job-name="vasp"
#SBATCH -o log_%j
#SBATCH -e err_%j
#SBATCH --ntasks-per-node=64
module purge
source ~/vasp544-avx512/env.sh 
mpirun -np 64 /home/u220220935831/vasp544-avx512/bin/vasp_std
