import streamlit as st

from utilities import GlobalInformation, represent_molecule, write_and_get_file

from gaddlemaps import Alignment
from gaddlemaps.components import System, Molecule


def add_molecule_component(
    system: System, molecule_correspondence: dict[str, Alignment]
):
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
                    key=f"itp_cg_{len(system.different_molecules)}",
                )
            )
            if itp_file is not None:
                system.add_ftop(itp_file.name)
                mol_cg = system.different_molecules[-1]
                molecule_correspondence[mol_cg.name] = Alignment(start=mol_cg)
                represent_molecule(mol_cg)
        with col_aa:
            if mol_cg is not None:
                aa_gro = write_and_get_file(
                    st.file_uploader(
                        "Upload corresponding high resolution GRO file:",
                        type=["gro"],
                        key=f"gro_aa_{len(system.different_molecules)}",
                    )
                )
                aa_itp = write_and_get_file(
                    st.file_uploader(
                        "Upload corresponding high resolution TOPOLOGY file:",
                        type=["top", "itp"],
                        key=f"itp_aa_{len(system.different_molecules)}",
                    )
                )
                if aa_gro is not None and aa_itp is not None:
                    mol_aa = Molecule.from_files(aa_gro.name, aa_itp.name)
                    molecule_correspondence[mol_cg.name].end = mol_aa
                    represent_molecule(mol_aa, style={"sphere": {"scale": 0.5}})
                    new_comp = True
    if not new_comp:
        st.warning("To upload more molecules, complete the previous one")
    else:
        add_molecule_component(system, molecule_correspondence)


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
                information.system = System(cg_system_gro.name)
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
            add_molecule_component(information.system, information.molecule_correspondence)

    if information.molecule_correspondence and any(
        (ali.start is not None) and (ali.end is not None)
        for ali in information.molecule_correspondence.values()
    ):
        st.button("Next Step: Align molecules", on_click=lambda _: information.next_page())