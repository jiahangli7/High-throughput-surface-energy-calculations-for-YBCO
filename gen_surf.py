from pymatgen.analysis.adsorption import *
from pymatgen.core.surface import Slab, SlabGenerator, generate_all_slabs, Structure, Lattice, ReconstructionGenerator
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.core.structure import Structure
from pymatgen.ext.matproj import MPRester
from matplotlib import pyplot as plt
from pymatgen.io.vasp.inputs import Poscar
import os


mpr = MPRester('TifC7AaCt035HrCAFLx1i30ZjXt0NJMd')

print("Please enter the max miller index:")
a = int(input("max miller index a:"))

outputfile = f"symeteric_25_{a}"
os.makedirs(outputfile, exist_ok=True)


mp_id = "mp-20674"
struct = mpr.get_structure_by_material_id(mp_id)
struct = SpacegroupAnalyzer(struct).get_conventional_standard_structure()


all_slabs = generate_all_slabs(struct, a, 25, 16, symmetrize=True)

print(
    "%s unique slab structures have been found for a max Miller index"
    % (len(all_slabs))
)

max_step = 0

for n,slab in enumerate(all_slabs):
    print(slab.miller_index)
    slab.make_supercell([[1, 0, 0],
                          [0, 1, 0],
                          [0, 0, 1]])

    ouc = slab.oriented_unit_cell
    miller_index_str = ''.join(str(x) for x in slab.miller_index)
    folder_path = os.path.join(outputfile, miller_index_str)
    os.makedirs(folder_path, exist_ok=True)
    filename = os.path.join(folder_path, f"POSCAR-{n}")
    oucname = os.path.join(folder_path, f"POSCAR-0")
    open(filename, 'w').write(str(Poscar(slab)))
    open(oucname, 'w').write(str(Poscar(ouc)))
    
    max_steps = max(max_step, n)
    
print(
    "Notice some Miller indices are repeated. Again, this is due to there being more than one termination"
)

print("the total number of slab is:", max_steps + 1)
