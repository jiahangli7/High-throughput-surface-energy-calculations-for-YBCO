import os
import math
import numpy as np

def read_basic(folder_path, POS_path):
    energy = None
    N = None
    if os.path.exists(folder_path):
        with open(folder_path, 'r') as file:
            lines = file.readlines()
            lines.reverse()
            energy = None
            for line in lines:
                if 'free  energy   TOTEN' in line:
                    energy = float(line.split()[-2].strip())
                    break
       
    line_count = 0                
    if os.path.exists(POS_path):
        with open(POS_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line_count += 1
                if line_count == 7:
                    num_line = line.split()
                    N = sum(float(num) for num in num_line)       
    return energy, N

def surf_area_from_poscar(poscar_path):
    a = None
    b = None
    gamma = None

    if os.path.exists(poscar_path):
        with open(poscar_path, 'r') as file:
            lines = file.readlines()
            v1 = np.array([float(x) for x in lines[2].split()])
            v2 = np.array([float(x) for x in lines[3].split()])
            v3 = np.array([float(x) for x in lines[4].split()])
            a = np.linalg.norm(v1)
            b = np.linalg.norm(v2)
            gamma = np.degrees(np.arccos(np.dot(v1, v2) / (a * b)))
    return a, b, gamma

def calculate_surface_energy(E_slab1, E_slab2, E_bulk, n, A):
    gamma_value = (E_slab1 + E_slab2 - n * E_bulk) / (4 * A) * 16.022
    return gamma_value

folder_values = {}

current_dir = os.getcwd()

for root, dirs, files in os.walk(current_dir):
    for dir_name in dirs:
        subdir_path = os.path.join(root, dir_name)
        bulk_path = os.path.join(subdir_path, 'bulk')
        
        if os.path.exists(bulk_path) and os.path.isdir(bulk_path):
            print("Bulk folder path:", bulk_path)
            base_path = os.path.join(bulk_path,'OUTCAR')
            pos_path = os.path.join(bulk_path,'POSCAR')
            Ebulk, N0 = read_basic(base_path, pos_path)
            print("Ebulk N0 is: ", Ebulk, N0)
            Ebulk0 = Ebulk
            print("E0 is: ", Ebulk0) 

            slab_dirs = []
            for sub_dir in os.listdir(subdir_path):
                slab_path = os.path.join(subdir_path, sub_dir)
                if os.path.isdir(slab_path) and sub_dir != 'bulk':
                    slab_dirs.append(slab_path)

            for i in range(len(slab_dirs)):
                for j in range(i + 1, len(slab_dirs)):
                    slab1_path = slab_dirs[i]
                    slab2_path = slab_dirs[j]
                    poscar1_path = os.path.join(slab1_path, 'POSCAR')
                    poscar2_path = os.path.join(slab2_path, 'POSCAR')
                    outcar1_path = os.path.join(slab1_path, 'OUTCAR')
                    outcar2_path = os.path.join(slab2_path, 'OUTCAR')

                    Eslab1, N1 = read_basic(outcar1_path, poscar1_path)
                    Eslab2, N2 = read_basic(outcar2_path, poscar2_path)

                    if Eslab1 is None or Eslab2 is None:
                        print(f"Skipping pair ({slab1_path}, {slab2_path}) due to missing energy data.")
                        continue

                    if N0 > 0 and (N1 + N2) % N0 == 0:
                        n = (N1 + N2) / N0
                        a, b, gamma = surf_area_from_poscar(poscar1_path)
                        A = a * b * math.sin(np.radians(gamma))

                        gamma_value = calculate_surface_energy(Eslab1, Eslab2, Ebulk0, n, A)
                        if gamma_value is not None:
                           folder_values[(dir_name, sub_dir)] = gamma_value
                           print(f"slab1: {slab1_path}, slab2: {slab2_path}, gamma(J/m2): {gamma_value}")
                        else:
                           print(f"Skipping pair ({slab1_path}, {slab2_path}) due to calculation error.")

                        folder_values[(dir_name, sub_dir)] = gamma_value

                        print(f"slab1: {slab1_path}, slab2: {slab2_path}, gamma(J/m2): {gamma_value}")

with open("surface_values.txt", "w") as file:
    for folder_name, value in folder_values.items():
        file.write(f"{folder_name}: {value:.4f} J/m2\n")
print("surface_values.txt done!")