#@title Binder design settings
#@title Binder design settings
# @markdown ---
# @markdown Enter path where to save your designs. We recommend to save on Google drive so that you can continue generating at any time.
design_path = "/content/drive/MyDrive/BindCraft/7QOR()/" # @param {"type":"string","placeholder":"/content/drive/MyDrive/BindCraft/PDL1/"}

# @markdown Enter the name that should be prefixed to your binders (generally target name).
binder_name = "7QOR" # @param {"type":"string","placeholder":"PDL1"}

# @markdown The path to the .pdb structure of your target. Can be an experimental or AlphaFold2 structure. We recommend trimming the structure to as small as needed, as the whole selected chains will be backpropagated through the network and can significantly increase running times.
starting_pdb = "/Users/krishivpotluri/Downloads/7qor.cif" # @param {"type":"string","placeholder":"/content/bindcraft/example/PDL1.pdb"}

# @markdown Which chains of your PDB to target? Can be one or multiple, in a comma-separated format. Other chains will be ignored during design.
chains = "A" # @param {"type":"string","placeholder":"A,C"}

# #markdown
target_hotspot_residues = "S70, K73, H153, E171, E104, E239, S242, R243, M270, N274" # @param {"type":"string","placeholder":""}

# @markdown What is the minimum and maximum size of binders you want to design? Pipeline will randomly sample different sizes between these values.
lengths = "70,150" # @param {"type":"string","placeholder":"70,150"}

# @markdown How many binder designs passing filters do you require?
number_of_final_designs = 100 # @param {"type":"integer","placeholder":"100"}
# @markdown ---
# @markdown Enter path on your Google drive (/content/drive/MyDrive/BindCraft/[binder_name].json) to previous target settings to continue design campaign. If left empty, it will use the settings above and generate a new settings json in your design output folder.
load_previous_target_settings = "" # @param {"type":"string","placeholder":""}
# @markdown ---

if load_previous_target_settings:
    target_settings_path = load_previous_target_settings
else:
    lengths = [int(x.strip()) for x in lengths.split(',') if len(lengths.split(',')) == 2]

    if len(lengths) != 2:
        raise ValueError("Incorrect specification of binder lengths.")

    settings = {
        "design_path": design_path,
        "binder_name": binder_name,
        "starting_pdb": starting_pdb,
        "chains": chains,
        "target_hotspot_residues": target_hotspot_residues,
        "lengths": lengths,
        "number_of_final_designs": number_of_final_designs
    }

    target_settings_path = os.path.join(design_path, binder_name+".json")
    os.makedirs(design_path, exist_ok=True)

    with open(target_settings_path, 'w') as f:
        json.dump(settings, f, indent=4)

currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Binder design settings updated at: {currenttime}")
print(f"New .json file with target settings has been generated in: {target_settings_path}")


#@title Advanced settings
# @markdown ---
# @markdown Which binder design protocol to run? Default is recommended. "Beta-sheet" promotes the design of more beta sheeted proteins, but requires more sampling. "Peptide" is optimised for helical peptide binders.
design_protocol = "Default" # @param ["Default","Beta-sheet","Peptide"]
# @markdown What interface design method to use?. "AlphaFold2" is the default, interface is generated by AlphaFold2. "MPNN" uses soluble MPNN to optimise the interface, but majority of residues still originate from AlphaFold2.
interface_protocol = "AlphaFold2" # @param ["AlphaFold2","MPNN"]
# @markdown What target template protocol to use? "Default" allows for limited amount flexibility. "Masked" allows for greater target flexibility on both sidechain and backbone level, but might result in reduced experimental success rates.
template_protocol = "Default" # @param ["Default","Masked"]
# @markdown ---

if design_protocol == "Default":
    design_protocol_tag = "default_4stage_multimer"
elif design_protocol == "Beta-sheet":
    design_protocol_tag = "betasheet_4stage_multimer"
elif design_protocol == "Peptide":
    design_protocol_tag = "peptide_3stage_multimer"
else:
    raise ValueError(f"Unsupported design protocol")

if interface_protocol == "AlphaFold2":
    interface_protocol_tag = ""
elif interface_protocol == "MPNN":
    interface_protocol_tag = "_mpnn"
else:
    raise ValueError(f"Unsupported interface protocol")

if template_protocol == "Default":
    template_protocol_tag = ""
elif template_protocol == "Masked":
    template_protocol_tag = "_flexible"
else:
    raise ValueError(f"Unsupported template protocol")

advanced_settings_path = "/content/bindcraft/settings_advanced/" + design_protocol_tag + interface_protocol_tag + template_protocol_tag + ".json"

currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Advanced design settings updated at: {currenttime}")



#@title Filters
# @markdown ---
# @markdown Which filters for designs to use? "Default" are recommended, "Peptide" are for the design of peptide binders, "Relaxed" are more permissive but may result in fewer experimental successes, "Peptide_Relaxed" are more permissive filters for non-helical peptides, "None" is for benchmarking.
filter_option = "Peptide" # @param ["Default", "Peptide", "Relaxed", "Peptide_Relaxed", "None"]
# @markdown ---

if filter_option == "Default":
    filter_settings_path = "/content/bindcraft/settings_filters/default_filters.json"
elif filter_option == "Peptide":
    filter_settings_path = "/content/bindcraft/settings_filters/peptide_filters.json"
elif filter_option == "Relaxed":
    filter_settings_path = "/content/bindcraft/settings_filters/relaxed_filters.json"
elif filter_option == "Peptide_Relaxed":
    filter_settings_path = "/content/bindcraft/settings_filters/peptide_relaxed_filters.json"
elif filter_option == "None":
    filter_settings_path = "/content/bindcraft/settings_filters/no_filters.json"
else:
    raise ValueError(f"Unsupported filter type")

currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Filter settings updated at: {currenttime}")

# @title Import functions and settings
from bindcraft.functions import *

args = {"settings":target_settings_path,
        "filters":filter_settings_path,
        "advanced":advanced_settings_path}

# Check if JAX-capable GPU is available, otherwise exit
check_jax_gpu()

# perform checks of input setting files
settings_path, filters_path, advanced_path = (args["settings"], args["filters"], args["advanced"])

### load settings from JSON
target_settings, advanced_settings, filters = load_json_settings(settings_path, filters_path, advanced_path)

settings_file = os.path.basename(settings_path).split('.')[0]
filters_file = os.path.basename(filters_path).split('.')[0]
advanced_file = os.path.basename(advanced_path).split('.')[0]

### load AF2 model settings
design_models, prediction_models, multimer_validation = load_af2_models(advanced_settings["use_multimer_design"])

### perform checks on advanced_settings
bindcraft_folder = "colab"
advanced_settings = perform_advanced_settings_check(advanced_settings, bindcraft_folder)

### generate directories, design path names can be found within the function
design_paths = generate_directories(target_settings["design_path"])

### generate dataframes
trajectory_labels, design_labels, final_labels = generate_dataframe_labels()

trajectory_csv = os.path.join(target_settings["design_path"], 'trajectory_stats.csv')
mpnn_csv = os.path.join(target_settings["design_path"], 'mpnn_design_stats.csv')
final_csv = os.path.join(target_settings["design_path"], 'final_design_stats.csv')
failure_csv = os.path.join(target_settings["design_path"], 'failure_csv.csv')

create_dataframe(trajectory_csv, trajectory_labels)
create_dataframe(mpnn_csv, design_labels)
create_dataframe(final_csv, final_labels)
generate_filter_pass_csv(failure_csv, args["filters"])

currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Loaded design functions and settings at: {currenttime}")


#@title Initialise PyRosetta

####################################
####################################
####################################
### initialise PyRosetta
pr.init(f'-ignore_unrecognized_res -ignore_zero_occupancy -mute all -holes:dalphaball {advanced_settings["dalphaball_path"]} -corrections::beta_nov16 true -relax:default_repeats 1')


#@title Run BindCraft!
####################################
###################### BindCraft Run
####################################
#@title Run BindCraft with Google Drive Upload
####################################
###################### BindCraft Run
####################################

import os
import sys
from google.colab import drive
from Bio.PDB import PDBParser, PDBIO
from Bio.PDB.Structure import Structure

# Mount Google Drive
drive.mount('/content/drive')

# Create the directory structure
!mkdir -p /content/bindcraft/example/

# Define paths
drive_path = '/content/drive/MyDrive/WindCraft/7qor-pdb-bundle1.pdb'  # Path to your file in Drive
input_path = '/content/bindcraft/example/7qor-pdb-bundle1.pdb'

# Copy file from Drive to working directory
!cp "{drive_path}" "{input_path}"

# Verify file copy
if os.path.exists(input_path):
    file_size = os.path.getsize(input_path)
    print(f"File copied successfully. Size: {file_size} bytes")
    
    # Print first few lines for verification
    print("\nFirst few lines of the file:")
    !head -n 5 {input_path}
else:
    raise FileNotFoundError(f"Failed to copy file from Drive")

# Update target settings with your parameters
target_settings = {
    "binder_name": "7QOR",
    "starting_pdb": input_path,
    "chains": "A",  # Modify this according to your target chain
    "target_hotspot_residues": "",
    "number_of_final_designs": 3,
    "lengths": [70, 150]
}

# Function to clean and renumber PDB
def clean_and_renumber_pdb(pdb_file_path, output_file_path):
    try:
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure(target_settings["binder_name"], pdb_file_path)
        
        # Renumber residues
        residue_number = 1
        for model in structure:
            for chain in model:
                for residue in chain:
                    residue.id = (' ', residue_number, residue.id[2])
                    residue_number += 1
                    
        # Save structure
        io = PDBIO()
        io.set_structure(structure)
        io.save(output_file_path)
        print("Successfully cleaned and renumbered PDB file")
        
    except Exception as e:
        print(f"Error processing PDB file: {str(e)}")
        raise

# Clean and renumber the uploaded file
cleaned_pdb_path = f'/content/bindcraft/example/{target_settings["binder_name"]}_cleaned.pdb'
clean_and_renumber_pdb(input_path, cleaned_pdb_path)

# Update target_settings with cleaned PDB path
target_settings["starting_pdb"] = cleaned_pdb_path

# Verify the cleaned file
if os.path.exists(cleaned_pdb_path):
    print(f"Cleaned PDB file created successfully at: {cleaned_pdb_path}")
else:
    raise FileNotFoundError("Failed to create cleaned PDB file")

script_start_time = time.time()
trajectory_n = 1
accepted_designs = 0
rejected_designs = 0


### start design loop
while True:
    ### check if we have the target number of binders
    final_designs_reached = check_accepted_designs(design_paths, mpnn_csv, final_labels, final_csv, advanced_settings, target_settings, design_labels)

    if final_designs_reached:
        # stop design loop execution
        break

    ### check if we reached maximum allowed trajectories
    max_trajectories_reached = check_n_trajectories(design_paths, advanced_settings)

    if max_trajectories_reached:
        break

    ### Initialise design
    # measure time to generate design
    trajectory_start_time = time.time()

    # generate random seed to vary designs
    seed = int(np.random.randint(0, high=999999, size=1, dtype=int)[0])

    # sample binder design length randomly from defined distribution
    samples = np.arange(min(target_settings["lengths"]), max(target_settings["lengths"]) + 1)
    length = np.random.choice(samples)

    # load desired helicity value to sample different secondary structure contents
    helicity_value = load_helicity(advanced_settings)

    # generate design name and check if same trajectory was already run
    design_name = target_settings["binder_name"] + "_l" + str(length) + "_s"+ str(seed)
    trajectory_dirs = ["Trajectory", "Trajectory/Relaxed", "Trajectory/LowConfidence", "Trajectory/Clashing"]
    trajectory_exists = any(os.path.exists(os.path.join(design_paths[trajectory_dir], design_name + ".pdb")) for trajectory_dir in trajectory_dirs)

    if not trajectory_exists:
        print("Starting trajectory: "+design_name)

        ### Begin binder hallucination
        trajectory = binder_hallucination(design_name, target_settings["starting_pdb"], target_settings["chains"],
                                            target_settings["target_hotspot_residues"], length, seed, helicity_value,
                                            design_models, advanced_settings, design_paths, failure_csv)
        trajectory_metrics = copy_dict(trajectory.aux["log"]) # contains plddt, ptm, i_ptm, pae, i_pae
        trajectory_pdb = os.path.join(design_paths["Trajectory"], design_name + ".pdb")

        # round the metrics to two decimal places
        trajectory_metrics = {k: round(v, 2) if isinstance(v, float) else v for k, v in trajectory_metrics.items()}

        # time trajectory
        trajectory_time = time.time() - trajectory_start_time
        trajectory_time_text = f"{'%d hours, %d minutes, %d seconds' % (int(trajectory_time // 3600), int((trajectory_time % 3600) // 60), int(trajectory_time % 60))}"
        print("Starting trajectory took: "+trajectory_time_text)
        print("")

        # Proceed if there is no trajectory termination signal
        if trajectory_metrics['terminate'] == "":
            # Relax binder to calculate statistics
            trajectory_relaxed = os.path.join(design_paths["Trajectory/Relaxed"], design_name + ".pdb")
            pr_relax(trajectory_pdb, trajectory_relaxed)

            # define binder chain, placeholder in case multi-chain parsing in ColabDesign gets changed
            binder_chain = "B"

            # Calculate clashes before and after relaxation
            num_clashes_trajectory = calculate_clash_score(trajectory_pdb)
            num_clashes_relaxed = calculate_clash_score(trajectory_relaxed)

            # secondary structure content of starting trajectory binder and interface
            trajectory_alpha, trajectory_beta, trajectory_loops, trajectory_alpha_interface, trajectory_beta_interface, trajectory_loops_interface, trajectory_i_plddt, trajectory_ss_plddt = calc_ss_percentage(trajectory_pdb, advanced_settings, binder_chain)

            # analyze interface scores for relaxed af2 trajectory
            trajectory_interface_scores, trajectory_interface_AA, trajectory_interface_residues = score_interface(trajectory_relaxed, binder_chain)

            # starting binder sequence
            trajectory_sequence = trajectory.get_seq(get_best=True)[0]

            # analyze sequence
            traj_seq_notes = validate_design_sequence(trajectory_sequence, num_clashes_relaxed, advanced_settings)

            # target structure RMSD compared to input PDB
            trajectory_target_rmsd = unaligned_rmsd(target_settings["starting_pdb"], trajectory_pdb, target_settings["chains"], 'A')

            # save trajectory statistics into CSV
            trajectory_data = [design_name, advanced_settings["design_algorithm"], length, seed, helicity_value, target_settings["target_hotspot_residues"], trajectory_sequence, trajectory_interface_residues,
                                trajectory_metrics['plddt'], trajectory_metrics['ptm'], trajectory_metrics['i_ptm'], trajectory_metrics['pae'], trajectory_metrics['i_pae'],
                                trajectory_i_plddt, trajectory_ss_plddt, num_clashes_trajectory, num_clashes_relaxed, trajectory_interface_scores['binder_score'],
                                trajectory_interface_scores['surface_hydrophobicity'], trajectory_interface_scores['interface_sc'], trajectory_interface_scores['interface_packstat'],
                                trajectory_interface_scores['interface_dG'], trajectory_interface_scores['interface_dSASA'], trajectory_interface_scores['interface_dG_SASA_ratio'],
                                trajectory_interface_scores['interface_fraction'], trajectory_interface_scores['interface_hydrophobicity'], trajectory_interface_scores['interface_nres'], trajectory_interface_scores['interface_interface_hbonds'],
                                trajectory_interface_scores['interface_hbond_percentage'], trajectory_interface_scores['interface_delta_unsat_hbonds'], trajectory_interface_scores['interface_delta_unsat_hbonds_percentage'],
                                trajectory_alpha_interface, trajectory_beta_interface, trajectory_loops_interface, trajectory_alpha, trajectory_beta, trajectory_loops, trajectory_interface_AA, trajectory_target_rmsd,
                                trajectory_time_text, traj_seq_notes, settings_file, filters_file, advanced_file]
            insert_data(trajectory_csv, trajectory_data)

            if advanced_settings["enable_mpnn"]:
                # initialise MPNN counters
                mpnn_n = 1
                accepted_mpnn = 0
                mpnn_dict = {}
                design_start_time = time.time()

                ### MPNN redesign of starting binder
                mpnn_trajectories = mpnn_gen_sequence(trajectory_pdb, binder_chain, trajectory_interface_residues, advanced_settings)

                # whether to hard reject sequences with excluded amino acids
                if advanced_settings["force_reject_AA"]:
                    restricted_AAs = set(advanced_settings["omit_AAs"].split(','))
                    mpnn_sequences = [{'seq': mpnn_trajectories['seq'][n][-length:], 'score': mpnn_trajectories['score'][n], 'seqid': mpnn_trajectories['seqid'][n]}
                        for n in range(advanced_settings["num_seqs"])
                        if not any(restricted_AA in mpnn_trajectories['seq'][n] for restricted_AA in restricted_AAs)]
                else:
                    mpnn_sequences = [{'seq': mpnn_trajectories['seq'][n][-length:], 'score': mpnn_trajectories['score'][n], 'seqid': mpnn_trajectories['seqid'][n]}
                        for n in range(advanced_settings["num_seqs"])]

                # sort MPNN sequences by lowest MPNN score
                mpnn_sequences.sort(key=lambda x: x['score'])

                # add optimisation for increasing recycles if trajectory is beta sheeted
                if advanced_settings["optimise_beta"] and float(trajectory_beta) > 15:
                    advanced_settings["num_recycles_validation"] = advanced_settings["optimise_beta_recycles_valid"]

                ### Compile prediction models once for faster prediction of MPNN sequences
                clear_mem()
                # compile complex prediction model
                complex_prediction_model = mk_afdesign_model(protocol="binder", num_recycles=advanced_settings["num_recycles_validation"], data_dir=advanced_settings["af_params_dir"],
                                                            use_multimer=multimer_validation)
                complex_prediction_model.prep_inputs(pdb_filename=target_settings["starting_pdb"], chain=target_settings["chains"], binder_len=length, rm_target_seq=advanced_settings["rm_template_seq_predict"],
                                                    rm_target_sc=advanced_settings["rm_template_sc_predict"])

                # compile binder monomer prediction model
                binder_prediction_model = mk_afdesign_model(protocol="hallucination", use_templates=False, initial_guess=False,
                                                            use_initial_atom_pos=False, num_recycles=advanced_settings["num_recycles_validation"],
                                                            data_dir=advanced_settings["af_params_dir"], use_multimer=multimer_validation)
                binder_prediction_model.prep_inputs(length=length)

                # iterate over designed sequences
                for mpnn_sequence in mpnn_sequences:
                    mpnn_time = time.time()

                    # compile sequences dictionary with scores and remove duplicate sequences
                    if mpnn_sequence['seq'] not in [v['seq'] for v in mpnn_dict.values()]:
                        # generate mpnn design name numbering
                        mpnn_design_name = design_name + "_mpnn" + str(mpnn_n)
                        mpnn_score = round(mpnn_sequence['score'],2)
                        mpnn_seqid = round(mpnn_sequence['seqid'],2)

                        # add design to dictionary
                        mpnn_dict[mpnn_design_name] = {'seq': mpnn_sequence['seq'], 'score': mpnn_score, 'seqid': mpnn_seqid}

                        # save fasta sequence
                        if advanced_settings["save_mpnn_fasta"] is True:
                            save_fasta(mpnn_design_name, mpnn_sequence['seq'], design_paths)

                        ### Predict mpnn redesigned binder complex using masked templates
                        mpnn_complex_statistics, pass_af2_filters = masked_binder_predict(complex_prediction_model,
                                                                                        mpnn_sequence['seq'], mpnn_design_name,
                                                                                        target_settings["starting_pdb"], target_settings["chains"],
                                                                                        length, trajectory_pdb, prediction_models, advanced_settings,
                                                                                        filters, design_paths, failure_csv)

                        # if AF2 filters are not passed then skip the scoring
                        if not pass_af2_filters:
                            print(f"Base AF2 filters not passed for {mpnn_design_name}, skipping interface scoring")
                            continue

                        # calculate statistics for each model individually
                        for model_num in prediction_models:
                            mpnn_design_pdb = os.path.join(design_paths["MPNN"], f"{mpnn_design_name}_model{model_num+1}.pdb")
                            mpnn_design_relaxed = os.path.join(design_paths["MPNN/Relaxed"], f"{mpnn_design_name}_model{model_num+1}.pdb")

                            if os.path.exists(mpnn_design_pdb):
                                # Calculate clashes before and after relaxation
                                num_clashes_mpnn = calculate_clash_score(mpnn_design_pdb)
                                num_clashes_mpnn_relaxed = calculate_clash_score(mpnn_design_relaxed)

                                # analyze interface scores for relaxed af2 trajectory
                                mpnn_interface_scores, mpnn_interface_AA, mpnn_interface_residues = score_interface(mpnn_design_relaxed, binder_chain)

                                # secondary structure content of starting trajectory binder
                                mpnn_alpha, mpnn_beta, mpnn_loops, mpnn_alpha_interface, mpnn_beta_interface, mpnn_loops_interface, mpnn_i_plddt, mpnn_ss_plddt = calc_ss_percentage(mpnn_design_pdb, advanced_settings, binder_chain)

                                # unaligned RMSD calculate to determine if binder is in the designed binding site
                                rmsd_site = unaligned_rmsd(trajectory_pdb, mpnn_design_pdb, binder_chain, binder_chain)

                                # calculate RMSD of target compared to input PDB
                                target_rmsd = unaligned_rmsd(target_settings["starting_pdb"], mpnn_design_pdb, target_settings["chains"], 'A')

                                # add the additional statistics to the mpnn_complex_statistics dictionary
                                mpnn_complex_statistics[model_num+1].update({
                                    'i_pLDDT': mpnn_i_plddt,
                                    'ss_pLDDT': mpnn_ss_plddt,
                                    'Unrelaxed_Clashes': num_clashes_mpnn,
                                    'Relaxed_Clashes': num_clashes_mpnn_relaxed,
                                    'Binder_Energy_Score': mpnn_interface_scores['binder_score'],
                                    'Surface_Hydrophobicity': mpnn_interface_scores['surface_hydrophobicity'],
                                    'ShapeComplementarity': mpnn_interface_scores['interface_sc'],
                                    'PackStat': mpnn_interface_scores['interface_packstat'],
                                    'dG': mpnn_interface_scores['interface_dG'],
                                    'dSASA': mpnn_interface_scores['interface_dSASA'],
                                    'dG/dSASA': mpnn_interface_scores['interface_dG_SASA_ratio'],
                                    'Interface_SASA_%': mpnn_interface_scores['interface_fraction'],
                                    'Interface_Hydrophobicity': mpnn_interface_scores['interface_hydrophobicity'],
                                    'n_InterfaceResidues': mpnn_interface_scores['interface_nres'],
                                    'n_InterfaceHbonds': mpnn_interface_scores['interface_interface_hbonds'],
                                    'InterfaceHbondsPercentage': mpnn_interface_scores['interface_hbond_percentage'],
                                    'n_InterfaceUnsatHbonds': mpnn_interface_scores['interface_delta_unsat_hbonds'],
                                    'InterfaceUnsatHbondsPercentage': mpnn_interface_scores['interface_delta_unsat_hbonds_percentage'],
                                    'InterfaceAAs': mpnn_interface_AA,
                                    'Interface_Helix%': mpnn_alpha_interface,
                                    'Interface_BetaSheet%': mpnn_beta_interface,
                                    'Interface_Loop%': mpnn_loops_interface,
                                    'Binder_Helix%': mpnn_alpha,
                                    'Binder_BetaSheet%': mpnn_beta,
                                    'Binder_Loop%': mpnn_loops,
                                    'Hotspot_RMSD': rmsd_site,
                                    'Target_RMSD': target_rmsd
                                })

                                # save space by removing unrelaxed predicted mpnn complex pdb?
                                if advanced_settings["remove_unrelaxed_complex"]:
                                    os.remove(mpnn_design_pdb)

                        # calculate complex averages
                        mpnn_complex_averages = calculate_averages(mpnn_complex_statistics, handle_aa=True)

                        ### Predict binder alone in single sequence mode
                        binder_statistics = predict_binder_alone(binder_prediction_model, mpnn_sequence['seq'], mpnn_design_name, length,
                                                                trajectory_pdb, binder_chain, prediction_models, advanced_settings, design_paths)

                        # extract RMSDs of binder to the original trajectory
                        for model_num in prediction_models:
                            mpnn_binder_pdb = os.path.join(design_paths["MPNN/Binder"], f"{mpnn_design_name}_model{model_num+1}.pdb")

                            if os.path.exists(mpnn_binder_pdb):
                                rmsd_binder = unaligned_rmsd(trajectory_pdb, mpnn_binder_pdb, binder_chain, "A")

                            # append to statistics
                            binder_statistics[model_num+1].update({
                                    'Binder_RMSD': rmsd_binder
                                })

                            # save space by removing binder monomer models?
                            if advanced_settings["remove_binder_monomer"]:
                                os.remove(mpnn_binder_pdb)

                        # calculate binder averages
                        binder_averages = calculate_averages(binder_statistics)

                        # analyze sequence to make sure there are no cysteins and it contains residues that absorb UV for detection
                        seq_notes = validate_design_sequence(mpnn_sequence['seq'], mpnn_complex_averages.get('Relaxed_Clashes', None), advanced_settings)

                        # measure time to generate design
                        mpnn_end_time = time.time() - mpnn_time
                        elapsed_mpnn_text = f"{'%d hours, %d minutes, %d seconds' % (int(mpnn_end_time // 3600), int((mpnn_end_time % 3600) // 60), int(mpnn_end_time % 60))}"


                        # Insert statistics about MPNN design into CSV, will return None if corresponding model does note exist
                        model_numbers = range(1, 6)
                        statistics_labels = ['pLDDT', 'pTM', 'i_pTM', 'pAE', 'i_pAE', 'i_pLDDT', 'ss_pLDDT', 'Unrelaxed_Clashes', 'Relaxed_Clashes', 'Binder_Energy_Score', 'Surface_Hydrophobicity',
                                            'ShapeComplementarity', 'PackStat', 'dG', 'dSASA', 'dG/dSASA', 'Interface_SASA_%', 'Interface_Hydrophobicity', 'n_InterfaceResidues', 'n_InterfaceHbonds', 'InterfaceHbondsPercentage',
                                            'n_InterfaceUnsatHbonds', 'InterfaceUnsatHbondsPercentage', 'Interface_Helix%', 'Interface_BetaSheet%', 'Interface_Loop%', 'Binder_Helix%',
                                            'Binder_BetaSheet%', 'Binder_Loop%', 'InterfaceAAs', 'Hotspot_RMSD', 'Target_RMSD']

                        # Initialize mpnn_data with the non-statistical data
                        mpnn_data = [mpnn_design_name, advanced_settings["design_algorithm"], length, seed, helicity_value, target_settings["target_hotspot_residues"], mpnn_sequence['seq'], mpnn_interface_residues, mpnn_score, mpnn_seqid]

                        # Add the statistical data for mpnn_complex
                        for label in statistics_labels:
                            mpnn_data.append(mpnn_complex_averages.get(label, None))
                            for model in model_numbers:
                                mpnn_data.append(mpnn_complex_statistics.get(model, {}).get(label, None))

                        # Add the statistical data for binder
                        for label in ['pLDDT', 'pTM', 'pAE', 'Binder_RMSD']:  # These are the labels for binder alone
                            mpnn_data.append(binder_averages.get(label, None))
                            for model in model_numbers:
                                mpnn_data.append(binder_statistics.get(model, {}).get(label, None))

                        # Add the remaining non-statistical data
                        mpnn_data.extend([elapsed_mpnn_text, seq_notes, settings_file, filters_file, advanced_file])

                        # insert data into csv
                        insert_data(mpnn_csv, mpnn_data)

                        # find best model number by pLDDT
                        plddt_values = {i: mpnn_data[i] for i in range(11, 15) if mpnn_data[i] is not None}

                        # Find the key with the highest value
                        highest_plddt_key = int(max(plddt_values, key=plddt_values.get))

                        # Output the number part of the key
                        best_model_number = highest_plddt_key - 10
                        best_model_pdb = os.path.join(design_paths["MPNN/Relaxed"], f"{mpnn_design_name}_model{best_model_number}.pdb")

                        # run design data against filter thresholds
                        filter_conditions = check_filters(mpnn_data, design_labels, filters)
                        if filter_conditions == True:
                            print(mpnn_design_name+" passed all filters")
                            accepted_mpnn += 1
                            accepted_designs += 1

                            # copy designs to accepted folder
                            shutil.copy(best_model_pdb, design_paths["Accepted"])

                            # insert data into final csv
                            final_data = [''] + mpnn_data
                            insert_data(final_csv, final_data)

                            # copy animation from accepted trajectory
                            accepted_animation = os.path.join(design_paths["Accepted/Animation"], f"{design_name}.html")
                            if not os.path.exists(accepted_animation):
                                shutil.copy(os.path.join(design_paths["Trajectory/Animation"], f"{design_name}.html"), accepted_animation)

                            # copy plots of accepted trajectory
                            plot_files = os.listdir(design_paths["Trajectory/Plots"])
                            plots_to_copy = [f for f in plot_files if f.startswith(design_name) and f.endswith('.png')]
                            for accepted_plot in plots_to_copy:
                                source_plot = os.path.join(design_paths["Trajectory/Plots"], accepted_plot)
                                target_plot = os.path.join(design_paths["Accepted/Plots"], accepted_plot)
                                if not os.path.exists(target_plot):
                                    shutil.copy(source_plot, target_plot)

                        else:
                            print(f"Unmet filter conditions for {mpnn_design_name}")
                            failure_df = pd.read_csv(failure_csv)
                            special_prefixes = ('Average_', '1_', '2_', '3_', '4_', '5_')
                            incremented_columns = set()

                            for column in filter_conditions:
                                base_column = column
                                for prefix in special_prefixes:
                                    if column.startswith(prefix):
                                        base_column = column.split('_', 1)[1]

                                if base_column not in incremented_columns:
                                    failure_df[base_column] = failure_df[base_column] + 1
                                    incremented_columns.add(base_column)

                            failure_df.to_csv(failure_csv, index=False)
                            shutil.copy(best_model_pdb, design_paths["Rejected"])

                        # increase MPNN design number
                        mpnn_n += 1

                        # if enough mpnn sequences of the same trajectory pass filters then stop
                        if accepted_mpnn >= advanced_settings["max_mpnn_sequences"]:
                            break
                    else:
                        print("Skipping duplicate sequence")

                if accepted_mpnn >= 1:
                    print("Found "+str(accepted_mpnn)+" MPNN designs passing filters")
                else:
                    print("No accepted MPNN designs found for this trajectory.")
                    rejected_designs += 1

                # save space by removing unrelaxed design trajectory PDB
                if advanced_settings["remove_unrelaxed_trajectory"]:
                    os.remove(trajectory_pdb)

                # measure time it took to generate designs for one trajectory
                design_time = time.time() - design_start_time
                design_time_text = f"{'%d hours, %d minutes, %d seconds' % (int(design_time // 3600), int((design_time % 3600) // 60), int(design_time % 60))}"
                print("Design and validation of trajectory "+design_name+" took: "+design_time_text)

            # analyse the rejection rate of trajectories to see if we need to readjust the design weights
            if trajectory_n >= advanced_settings["start_monitoring"] and advanced_settings["enable_rejection_check"]:
                acceptance = accepted_designs / trajectory_n
                if not acceptance >= advanced_settings["acceptance_rate"]:
                    print("The ratio of successful designs is lower than defined acceptance rate! Consider changing your design settings!")
                    print("Script execution stopping...")
                    break

        # increase trajectory number
        trajectory_n += 1

### Script finished
elapsed_time = time.time() - script_start_time
elapsed_text = f"{'%d hours, %d minutes, %d seconds' % (int(elapsed_time // 3600), int((elapsed_time % 3600) // 60), int(elapsed_time % 60))}"
print("Finished all designs. Script execution for "+str(trajectory_n)+" trajectories took: "+elapsed_text)


#@title Consolidate & Rank Designs
#@markdown ---
accepted_binders = [f for f in os.listdir(design_paths["Accepted"]) if f.endswith('.pdb')]

for f in os.listdir(design_paths["Accepted/Ranked"]):
    os.remove(os.path.join(design_paths["Accepted/Ranked"], f))

# load dataframe of designed binders
design_df = pd.read_csv(mpnn_csv)
design_df = design_df.sort_values('Average_i_pTM', ascending=False)

# create final csv dataframe to copy matched rows, initialize with the column labels
final_df = pd.DataFrame(columns=final_labels)

# check the ranking of the designs and copy them with new ranked IDs to the folder
rank = 1
for _, row in design_df.iterrows():
    for binder in accepted_binders:
        target_settings["binder_name"], model = binder.rsplit('_model', 1)
        if target_settings["binder_name"] == row['Design']:
            # rank and copy into ranked folder
            row_data = {'Rank': rank, **{label: row[label] for label in design_labels}}
            final_df = pd.concat([final_df, pd.DataFrame([row_data])], ignore_index=True)
            old_path = os.path.join(design_paths["Accepted"], binder)
            new_path = os.path.join(design_paths["Accepted/Ranked"], f"{rank}_{target_settings['binder_name']}_model{model.rsplit('.', 1)[0]}.pdb")
            shutil.copyfile(old_path, new_path)

            rank += 1
            break

# save the final_df to final_csv
final_df.to_csv(final_csv, index=False)

print("Designs ranked and final_designs_stats.csv generated")



#@title Top 20 Designs
df = pd.read_csv(os.path.join(design_path, 'final_design_stats.csv'))
df.head(20)


#@title Top Design Display
import py3Dmol
import glob
from IPython.display import HTML

#### pymol top design
top_design_dir = os.path.join(design_path, 'Accepted', 'Ranked')
top_design_pdb = glob.glob(os.path.join(top_design_dir, '1_*.pdb'))[0]

# Visualise in PyMOL
view = py3Dmol.view()
view.addModel(open(top_design_pdb, 'r').read(),'pdb')
view.setBackgroundColor('white')
view.setStyle({'chain':'A'}, {'cartoon': {'color':'#3c5b6f'}})
view.setStyle({'chain':'B'}, {'cartoon': {'color':'#B76E79'}})
view.zoomTo()
view.show()



#@title Display animation
import glob
from IPython.display import HTML

#### pymol top design
top_design_dir = os.path.join(design_path, 'Accepted', 'Ranked')
top_design_pdb = glob.glob(os.path.join(top_design_dir, '1_*.pdb'))[0]

top_design_name = os.path.basename(top_design_pdb).split('1_', 1)[1].split('_mpnn')[0]
top_design_animation = os.path.join(design_path, 'Accepted', 'Animation', f"{top_design_name}.html")

# Show animation
HTML(top_design_animation)
