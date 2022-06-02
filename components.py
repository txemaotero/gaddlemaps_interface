import streamlit as st

from utilities import GlobalInformation, represent_molecule, write_and_get_file

from gaddlemaps import Alignment
from gaddlemaps.components import System, Molecule


def add_molecule_component(information: GlobalInformation):
    new_comp = False
    with st.container():
        col_cg, col_aa = st.columns(2)

        mol_cg = None
        with col_cg:
            itp_file = write_and_get_file(
                st.file_uploader(
                    "Upload topology to find molecules in the system (low resolution):",
                    type=["itp", "top"],
                    accept_multiple_files=False,
                    key=f"itp_cg_{len(information.system.different_molecules)}",
                )
            )
            if itp_file is not None:
                information.system.add_ftop(itp_file)
                mol_cg = information.system.different_molecules[-1]
                information.molecule_correspondence[mol_cg.name] = Alignment(start=mol_cg)
                represent_molecule(mol_cg)
        with col_aa:
            if mol_cg is not None:
                aa_gro = write_and_get_file(
                    st.file_uploader(
                        "Upload corresponding high resolution GRO file:",
                        type=["gro"],
                        key=f"gro_aa_{len(information.system.different_molecules)}",
                    )
                )
                aa_itp = write_and_get_file(
                    st.file_uploader(
                        "Upload corresponding high resolution TOPOLOGY file:",
                        type=["top", "itp"],
                        key=f"itp_aa_{len(information.system.different_molecules)}",
                    )
                )
                if aa_gro is not None and aa_itp is not None:
                    mol_aa = Molecule.from_files(aa_gro, aa_itp)
                    # mol_aa = Molecule.from_files(aa_gro.name, aa_itp.name)
                    information.molecule_correspondence[mol_cg.name].end = mol_aa
                    represent_molecule(mol_aa, style={"sphere": {"scale": 0.5}})
                    new_comp = True
        if new_comp:
            restriction_selection(information, mol_cg.name)
    if not new_comp:
        st.warning("To upload more molecules, complete the previous one")
    else:
        add_molecule_component(information)


def restriction_selection(information: GlobalInformation, mol_name: str):
    st.markdown('### OPTIONAL: Select restrictions to the mapping. Same number of selections in both resolutions.')
    st.markdown('__To find the indexes of the atoms you can hover over them in the 3D view__')
    col1, col2 = st.columns(2)
    with col1:
        options = list(range(1, len(information.molecule_correspondence[mol_name].start) + 1)) 
        def update_options():
            st.session_state.options_cg.append(1)

        st.session_state.options_cg = options
        cg_rest = st.multiselect(
            "Select atom index in the low resolution system:",
            st.session_state.options_cg,
            key=f"cg_rest_{mol_name}",
            on_change=update_options
        )
    with col2:
        aa_rest = st.multiselect(
            "Select atom index in the high resolution system:",
            list(range(1, len(information.molecule_correspondence[mol_name].end) + 1)),
            key=f"aa_rest_{mol_name}",
        )
    if len(cg_rest) != len(aa_rest):
        information.errors = True
        st.error("The number of selections must be the same in both resolutions")
    else:
        information.molecule_restrictions[mol_name] = list(zip(cg_rest, aa_rest))


def main_page(information: GlobalInformation):
    # First step: Upload CG system
    with st.container():
        st.markdown(
            '<h2 style="text-align: center;padding-bottom: 30px;">Upload the system to be mapped</h2>',
            unsafe_allow_html=True,
        )
        _, col_upl, _, col_info, _ = st.columns([1, 3, 1, 3, 1])

        with col_upl:
            cg_system_gro = write_and_get_file(
                st.file_uploader("Choose a .gro file with the CG systems", type=["gro"])
            )

        with col_info:
            if cg_system_gro is not None:
                information.cg_system_name = cg_system_gro.name.split("/")[-1].split(".")[0]
                information.system = System(cg_system_gro)
                # information.system = System(cg_system_gro.name)
                st.write("Detected residues:")
                text = """| Resname   | Found |
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
                st.warning(
                    "To continue, you need to upload a .gro file with the system to be mapped"
                )

    # Second step: upload low res topology and high res molecules only if system is defined
    if information.system is not None:
        with st.container():
            st.markdown(
                '<h2 style="text-align: center;padding: 30px;">Molecule Recognition</h2>',
                unsafe_allow_html=True,
            )
            add_molecule_component(information)
        

def align_page(information: GlobalInformation):
    st.markdown('Alignment')