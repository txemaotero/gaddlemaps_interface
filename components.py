import tempfile
import streamlit as st
from gaddlemaps import Alignment
from gaddlemaps.components import Molecule, System

from utilities import (
    GlobalInformation,
    represent_molecule,
    represent_molecule_comparative,
    st_stdout,
    write_and_get_file,
)


def upload_system_and_molecules(information: GlobalInformation):
    """
    Loads the first two parts of the mapping (system and molecules)

    Parameters
    ----------
    information : GlobalInformation
        Object containing all the information about the current mapping
    """
    with st.container():
        st.markdown("## 1. Upload the system to be mapped")
        col_upl, _, col_info, _ = st.columns([5, 1, 3, 1])

        with col_upl:
            cg_system_gro = write_and_get_file(
                st.file_uploader(
                    "Choose a .gro file with the system in the initial resolution",
                    type=["gro"],
                )
            )

        with col_info:
            if cg_system_gro is not None:
                information.cg_system_name = cg_system_gro.name.split("/")[-1].split(
                    "."
                )[0]
                information.system = System(cg_system_gro)
                st.write("Detected residues:")
                text = """| Resname   | Number |
| ----------- | ----------- |
"""
                text += "\n".join(
                    [
                        "|" + "|".join([k, str(v)]) + "|"
                        for k, v in information.system.system_gro.composition.items()
                    ]
                )
                st.markdown(text)
            else:
                # Some extra space for alignment
                st.text("\n")
                st.text("\n")
                st.warning(
                    "To continue, you need to upload a .gro file with the system to be mapped"
                )
        st.markdown("----")

    # Second step: upload low res topology and high res molecules only if system is defined
    if information.system is not None:
        with st.container():
            st.markdown("## 2. Molecule recognition")
            st.markdown("""In this step you will be assigning the correspondence
                        between the molecules in the uploaded system and in the
                        final representation. There could be some special cases
                        where this assignment can be tricky. For example, if you
                        want to map a simulation using the __MARTINI__ force field
                        and you have __water__ in the system, remember that each
                        MARTINI water bead corresponds to 4 water molecules.
                        This means that if you want to map those water beads, in
                        you must upload a .gro file with a cluster of 4 water
                        molecules and the topology file with the bonds in those
                        4 molecules. To avoid problems derived from this, we
                        recommend to map the system without water and then,
                        resolvate the system in the final representation to add
                        the missing water molecules. If you are using GROMACS,
                        you can use the `gmx solvate` command to do that.""")
            add_molecule_component(information)


def add_molecule_component(information: GlobalInformation):
    """
    Implements de logic and interface to add new molecules

    Parameters
    ----------
    information : GlobalInformation
        Object containing all the information about the current mapping
    """
    new_comp = False
    warning = False
    with st.container():
        st.markdown(f"### Molecule {len(information.system.different_molecules) + 1}")
        col_cg, col_aa = st.columns(2)

        mol_cg = None
        with col_cg:
            itp_file = write_and_get_file(
                st.file_uploader(
                    "Upload topology to find molecules in the system (initial resolution):",
                    type=["itp", "top"],
                    accept_multiple_files=False,
                    key=f"itp_cg_{len(information.system.different_molecules)}",
                )
            )
            if itp_file is not None:
                information.system.add_ftop(itp_file)
                mol_cg = information.system.different_molecules[-1]
                information.molecule_correspondence[mol_cg.name] = Alignment(
                    start=mol_cg
                )
                # Empty space for alignment
                st.markdown('<p style="height:163px"></p>', unsafe_allow_html=True)
                represent_molecule(mol_cg)
                warning = True
        with col_aa:
            if mol_cg is not None:
                aa_gro = write_and_get_file(
                    st.file_uploader(
                        "Upload the corresponding GRO file with the molecule in the final resolution:",
                        type=["gro"],
                        key=f"gro_aa_{len(information.system.different_molecules)}",
                    )
                )
                aa_itp = write_and_get_file(
                    st.file_uploader(
                        "Upload the corresponding TOPOLOGY file the final resolution:",
                        type=["top", "itp"],
                        key=f"itp_aa_{len(information.system.different_molecules)}",
                    )
                )
                if aa_gro is not None and aa_itp is not None:
                    mol_aa = Molecule.from_files(aa_gro, aa_itp)
                    information.molecule_correspondence[mol_cg.name].end = mol_aa
                    represent_molecule(mol_aa, style={"sphere": {"scale": 0.5}})
                    new_comp = True
                    warning = False
        if new_comp:
            restriction_selection(information, mol_cg.name)
    st.markdown("----")
    if warning:
        st.warning("To upload more molecules, complete the previous one")
    if new_comp:
        add_molecule_component(information)


def restriction_selection(information: GlobalInformation, mol_name: str):
    """
    Implements de logic and interface to add constraints to the mapping

    Parameters
    ----------
    information : GlobalInformation
        Object containing all the information about the current mapping
    mol_name : str
        Name of the molecule to add the constraints
    """
    st.markdown("#### Constraints (Optional)")
    if len(information.system.different_molecules) == 1:
        st.markdown(
            """You can include suggestions that guarantee a correct mapping.
            This is specially useful when working with symmetric molecules. For
            instance, in a linear molecule with a polar head, with one
            constraint joining the head in both resolutions is enough."""
        )
        st.markdown(
            """__Remember__: If you are working with molecules with multiple
            residues (e.g. a protein), the constraints will be generated
            automatically based on the residues sequence so you do not need to
            include them."""
        )
        _, col, _ = st.columns([1, 2, 1])
        with col:
            st.info(
                """__Info__: If you select multiple indexes in a single
                selection box, all the possible pairs of constraints will be
                added. For instance, if you select [1, 2] in the left box and
                [3, 4] in the right one, the [(1, 3), (1, 4), (2, 3), (2, 4)]
                constraints will be added."""
            )
    restrictions: set[tuple[int, int]] = set()
    multiselect_restrictions(information, mol_name, restrictions, 0)
    information.molecule_restrictions[mol_name] = list(restrictions)


def multiselect_restrictions(
    information: GlobalInformation,
    mol_name: str,
    restrictions: set[tuple[int, int]],
    key_index: int,
):
    """
    Adds the widgets to select the constraints to a molecule

    Parameters
    ----------
    information : GlobalInformation
        Object containing all the information about the current mapping
    mol_name : str
        Name of the molecule to add the constraints
    restrictions : set[tuple[int, int]]
        Set of the constraints to add to the molecule
    key_index : int
        Index of the current constraint. It is used to avoid repeated key ids in
        the widgets
    """
    _, col1, col2, _ = st.columns([1, 1, 1, 1])
    with col1:
        cg_rest = st.multiselect(
            "Select atoms indexes in the initial resolution:",
            list(range(len(information.molecule_correspondence[mol_name].start))),
            key=f"cg_rest_{mol_name}_{key_index}",
            help="To find the indexes hover the atoms in the left 3D view",
        )
    with col2:
        aa_rest = st.multiselect(
            "Select atoms indexes in the final resolution:",
            list(range(len(information.molecule_correspondence[mol_name].end))),
            key=f"aa_rest_{mol_name}_{key_index}",
            help="To find the indexes hover the atoms in the right 3D view",
        )
    if cg_rest and aa_rest:
        for cg_index in cg_rest:
            for aa_index in aa_rest:
                restrictions.add((cg_index, aa_index))
        multiselect_restrictions(information, mol_name, restrictions, key_index + 1)


def run_mapping_and_download(information: GlobalInformation):
    """
    Implements the logic to run the mapping and download the results

    Parameters
    ----------
    information : GlobalInformation
        Object containing all the information about the current mapping
    """
    st.markdown("## 3. Perform the mapping")
    st.markdown(
        """Once you have uploaded the molecules to be mapped and their
        corresponding constraints you can proceed with their alignment in both
        resolutions. Due to limitations related with the UI, the extrapolation
        and generation of the final mapped system can not be decoupled from
        this alignment step. That is why you need to specified the scale factor
        at this point."""
    )

    with st.columns(3)[0]:
        scale_factor = st.slider(
            "Scale factor",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            help="The mapped molecules will be scaled by this factor respect to the closest original bead (recommended 0.5 to avoid molecular overlaps)",
        )
        pressed_align = st.button("Align and extrapolate")
    if pressed_align:
        st.markdown("### Backend output")
        st.markdown(
            """The text in the green box bellow is the output from the backend
            process. For each molecule, the computed "distance" (Chi2) between
            its representation in both resolution is displayed. After all the
            molecules are aligned, the exchange maps are computed and the final
            mapped system is generated."""
        )
    with st.columns(2)[0]:
        if pressed_align:
            temp_gro = tempfile.NamedTemporaryFile(suffix=".gro")
            with st_stdout("success"):
                information.align_molecules()
                print("Calculating exchange maps...")
                information.manager.calculate_exchange_maps(scale_factor)
                print("Generating the mapped system...")
                information.manager.extrapolate_system(temp_gro.name)
                temp_gro.seek(0)

    # If the alignments are done, show the comparative
    if information.manager is not None:
        st.markdown("### Alignment visual check")
        st.markdown(
            """In the following representations the result of the alignment is
            shown. The molecules with the lowest number of atoms are plotted
            with transparency on top of the others. Check that the alignment is
            what you expected. If not, you can add or change the constraints
            and try again. If the alignment is correct, you can download the
            mapped system in the next section."""
        )
        cols = st.columns(2)
        for index, (mol_name, ali) in enumerate(
            information.molecule_correspondence.items()
        ):
            with cols[index % 2]:
                st.markdown(f"#### {index + 1}. {mol_name}")
                represent_molecule_comparative(ali)
    st.markdown("----")
    if pressed_align:
        st.markdown("## 4. Download the mapped system")
        st.markdown(
            """If the alignment is correct, you can download the .gro file with
            the mapped system pressing the button below. Note that once you
            press it, the alignment will be lost (due again to limitations of
            the UI) so you will need to perform the alignment again if you
            want to change the scale factor or visualize the molecule overlap
            in the previous section. Do not be surprised by the result if you
            visualize the system and the molecules seem to be wrong. Remember
            that the scale factor is applied to avoid molecule overlaps. Normal
            molecular configurations are restored after a short energy
            minimization simulation (we recommend to use the steepest decent
            algorithm)."""
        )
        st.download_button(
            "Download mapped system",
            temp_gro.read(),
            file_name=information.cg_system_name + "_mapped.gro",
        )
        st.markdown("----")
