import tempfile
import streamlit as st

from components import main_page
from utilities import (GlobalInformation, represent_molecule_comparative, st_stdout)

# Page style
st.set_page_config(layout="wide")
# Title of the main page
st.title("Gaddle Maps Interface")

information = GlobalInformation()

main_page(information)


if information.errors:
    st.info("Please, check the errors before continuing")
elif information.molecule_correspondence and any(
    (ali.start is not None) and (ali.end is not None)
    for ali in information.molecule_correspondence.values()
):
    st.markdown("---")
    st.markdown("## Align molecules and download the mapped system")

    with st.columns(2)[0]:
        scale_factor = st.slider("Scale factor", min_value=0., max_value=1.0, value=0.5, help="The mapped molecules will be scaled by this factor respect to the closest original bead (recomended 0.5 to avoid molecular overlaps)")
        pressed_align = st.button("Start the alignment and generate the mapped system")
        if pressed_align:
            temp_gro = tempfile.NamedTemporaryFile(suffix=".gro") 
            with st_stdout("success"):
                information.align_molecules()
                print('Calculating exchange maps...')
                information.manager.calculate_exchange_maps(scale_factor)
                print('Generating the mapped system...')
                information.manager.extrapolate_system(temp_gro.name)
                temp_gro.seek(0)
            st.warning('Warning: Once you download the mapped system the alignment will be lost. Make sure in the figures bellow show the correct moleucule overlap before pressing the button.')
            st.download_button('Download extrapolated system', temp_gro.read(), file_name=information.cg_system_name + "_mapped.gro")

# If the alignments are done, show the comparative
if information.manager is not None:
    st.markdown("### Alignment done")
    cols = st.columns(3)
    for index, (mol_name, ali) in enumerate(information.molecule_correspondence.items()):
        with cols[index % 3]:
            st.markdown(f"### {mol_name}")
            represent_molecule_comparative(ali)