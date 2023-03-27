import os
import numpy as np
import matplotlib.pyplot as plt
from labutil.plugins.pwscf import run_qe_pwscf, PWscf_inparam, parse_qe_pwscf_output
from labutil.objects import Struc, Dir, ase2struc, Kpoints, PseudoPotential
from ase.spacegroup import crystal
from ase.io import write
from ase.build import bulk


def make_struc(alat, clat):
    """
    Creates the crystal structure using ASE.
    :param alat: Lattice parameter in angstrom
    :return: structure object converted from ase
    """
    fecell = bulk("Fe", "hcp", a=alat, c=clat)
    # check how your cell looks like
    # write('s.cif', gecell)
    print(fecell, fecell.get_atomic_numbers())
    fecell.set_atomic_numbers([26, 26])
    structure = Struc(ase2struc(fecell))
    print(structure.species)
    vol = fecell.get_volume()
    print(vol)
    return structure


def compute_energy(alat, clat, nk, ecut):
    """
    Make an input template and select potential and structure, and the path where to run
    """
    potname = "Fe.pbe-nd-rrkjus.UPF"
    potpath = os.path.join(os.environ["QE_POTENTIALS"], potname)
    pseudopots = {
        "Fe": PseudoPotential(
            path=potpath, ptype="uspp", element="Fe", functional="GGA", name=potname
        ),
    }
    struc = make_struc(alat=alat, clat = clat)
    kpts = Kpoints(gridsize=[nk, nk, nk], option="automatic", offset=False)
    dirname = "Fe_Vol_{}_ecut_{}_nk_{}".format(alat, ecut, nk)
    runpath = Dir(path=os.path.join(os.environ["WORKDIR"], "Lab4/Problem1", dirname))
    input_params = PWscf_inparam(
        {
            "CONTROL": {
                "calculation": "scf",
                "pseudo_dir": os.environ["QE_POTENTIALS"],
                "outdir": runpath.path,
                "tstress": True,
                "tprnfor": True,
                "disk_io": "none",
            },
            "SYSTEM": {
                "ecutwfc": ecut,
                "ecutrho": ecut * 8,
                "nspin": 1,
                "occupations": "smearing",
                "smearing": "mp",
                "degauss": 0.02,
            },
            "ELECTRONS": {
                "diagonalization": "david",
                "mixing_beta": 0.5,
                "conv_thr": 1e-7,
            },
            "IONS": {},
            "CELL": {},
        }
    )

    output_file = run_qe_pwscf(
        runpath=runpath,
        struc=struc,
        pseudopots=pseudopots,
        params=input_params,
        kpoints=kpts,
        ncpu=2,
    )
    output = parse_qe_pwscf_output(outfile=output_file)
    return output



def lattice_scan():
    nk = 9
    ecut = 30
    alat0 = 2.4639
    clat0 = 3.8789
    volume0 = 20.39363/2
    energy_list = []
    vol_list = np.linspace(1.25,1.75,5)
#     nk_list = [3,4,5,6,7,8,9,10]
#     nk_list = [3,5,7,9,11,13,15,17]
    for vol in vol_list:
        output = compute_energy(alat=vol*alat0, clat =vol*clat0 , ecut=ecut, nk=nk)
        energy_list.append(output["energy"])
        print(output)
    
    
    volume = volume0*vol_list**3
    print(volume)
    print(energy_list)
    plt.plot(volume, energy_list,'.-')
    plt.xlabel('Volumn of Unit Cell(A^3)')
    plt.ylabel('Energy of iron (eV)')
#     plt.title('Convergence for cutoff')
    plt.show()


if __name__ == "__main__":
    # put here the function that you actually want to run
    lattice_scan()
