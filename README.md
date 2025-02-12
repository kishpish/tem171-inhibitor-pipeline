# TEM-171 β-Lactamase Inhibitor Generation Pipeline

The emergence of TEM-171 β-lactamase represents a significant threat to modern antimicrobial therapy due to its ability to hydrolyze an extended spectrum of β-lactam antibiotics. While traditional β-lactamase inhibitors like tazobactam show diminishing efficacy against this enzyme, no true systematic approach exists for developing targeted protein-based inhibitors. Here, I present an integrated computational pipeline for de novo protein design targeting TEM-171, combining quantum-inspired diffusion models with evolutionary optimization. This dual-platform approach employs RFDiffusion for scaffold generation (n=2048) and BindCraft for interface refinement (n=67), guided by AlphaFold2 structural predictions (mean pLDDT score: 93.2) and ProteinMPNN sequence optimization. The designed inhibitor demonstrates exceptional structural stability (RMSD: 1.2-1.5Å) and binding affinity (ΔG: -12.3 kcal/mol) in microsecond-scale molecular dynamics simulations, with force-displacement profiles revealing peak unbinding forces of 1500-1700 kN/mol. The designed inhibitor maintains stable contacts with critical catalytic residues including Ser70 and maintains conformational integrity across varied physiological conditions (pH 6.5-8.0, 298-310K). Beyond the immediate therapeutic application, the generalizable framework demonstrates 38.4s average computation time per design and 94% success rate in generating stable protein-protein interfaces (i_ptm > 0.8), establishing an efficacious pipeline for accelerated therapeutic protein development. These findings not only present a promising candidate for combating TEM-171-mediated resistance, but also provide a wider-scale methodology for addressing emerging therapeutic challenges through rational protein design.

## Pipeline:
This pipeline should serve as a guideline, visualization, and process description. The pipeline relies on several cutting-edge AL/ML tools for protein structure prediction, binder generation, protein analysis, molecular dynamics, docking & simulations, and more. Installation can be complex, so through this pipeline I provide an in-depth overview of all ML tool installations and notebook code I utilized/produced, as well as results that followed.  

## Credits:

Thanks to Dr. Jennifer Madrigal for the structural and crystallographic insight into the structure of the protein, as well as information surrounding basic MD simulations. Thank you to Cianna Calia, for all the help with BindCraft adn RFDiffusion, and the clarification of the exact metrics behind these models. Special thanks to Anish Maddipoti at NVIDIA, for the large support and access to brev.dev credits to run trials.

Extended Credits for the code inspiration and segments to:

  https://github.com/Joseph-Ellaway/Ramachandran_Plotter
  https://github.com/LePingKYXK/PDB_cleaner/blob/master/pdb_cleaner.py
  https://github.com/harryjubb/pdbtools/blob/master/clean_pdb.py
  https://github.com/openmm/pdbfixer
  https://doi.org/10.1021/acs.jcim.1c00998
  https://github.com/pablo-arantes/making-it-rain/issues
  https://www.biorxiv.org/content/10.1101/2024.09.30.615802v1
  https://doi.org/10.1038/s41586-023-06415-8

Prof. Marco A. Deriu (marco.deriu@polito.it)
Lorenzo Pallante (lorenzo.pallante@polito.it)
Eric A. Zizzi (eric.zizzi@polito.it)
Marcello Miceli (marcello.miceli@polito.it)
Marco Cannariato (marco.cannariato@polito.it)

  https://github.com/google-deepmind/alphafold
  https://github.com/google-deepmind/alphafold3
  https://github.com/sokrypton/ColabFold
  https://github.com/openmm/openmm
