import streamlit as st

from components import run_mapping_and_download, upload_system_and_molecules
from utilities import GlobalInformation


# Page style
st.set_page_config(page_title="GaddleMaps", page_icon="./imgs/favicon.ico")
st.markdown(
    """
<style>
    .block-container{
        max-width: 80rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.image("./imgs/logo.png", use_column_width=True)

st.title("What is this?")
col1, col2 = st.columns(2)
with col1:
    st.markdown(
        """This web application pretends to be a high level user interface of
        the Gaddle Maps implementation that can be found
        [here](https://github.com/txemaotero/gaddlemaps). If you do not know
        what Gaddle Maps is, please refer to the [original
        paper](https://pubs.acs.org/doi/10.1021/acs.jctc.7b00861). In just
        a few words, Gaddle Maps allows to replace molecules in a simulation
        box in such a way that the replacement is optimally aligned with the
        original molecule. This comes in handy, for instance, when you want to
        convert a simulation with a coarse-grained forcefield into a fully
        atomistic one. The key advantage of the algorithm is that it
        automatically finds the optimal alignment between the initial and final
        representation of the molecules independently of the forcefield,
        molecule type or geometry."""
    )

    st.markdown(
        """This interface will guide you through the whole mapping
            process. First, you will need to upload the coordinates of the
            molecules inside the simulation box in the initial representation.
            Then, you will be required to upload the topology files for each of
            the molecules that you want to map. This will be used to find the
            molecules in the system and to set the existing bonds. You will
            also have to upload the coordinates and the topology files of the
            corresponding molecule in the final representation. You can also
            specify some constraints to guarantee a good alignment. Finally,
            you will be able to start the alignment process and see and
            download the resulting mapped system."""
    )

with col2:
    st.image("./imgs/bilayer.png", use_column_width=True)

st.markdown("# Limitations")

st.markdown(
    """Although this interface considerably facilitates the mapping
process, the following limitations should be taken into account:

- This interface does not offer the same freedom as the python [gaddlemaps
  module](https://github.com/txemaotero/gaddlemaps)
  does.
- This web app uses the slow alignment engine (the one that is not implemented
  in C++) so, if you are trying to map systems with large molecules (e.g.
  proteins), you may want to consider using the gaddlemaps module with the fast
  implementation instead. 
- Here, you are limited to use .gro and .itp (or .top) file formats for the
  coordinates and topology, respectively, while with the python module you can
  implement you own parsers and use different formats. 
- The debugging or error detection can sometimes be quite difficult while with
  the module you have all the control.
  
However, if the above limitations are not a problem, this interface will give
you a very intuitive and visual way to convert your systems between different
molecular representations.
"""
)


st.markdown("# Citing")
st.markdown(
    """Please, if this tool was useful for you, consider citing the [original
publication](https://pubs.acs.org/doi/10.1021/acs.jctc.7b00861). If you
are using LaTeX, you can use the following entry in your .bib file:
"""
)
st.code(
    """
@article{otero2018gaddle,
  title={GADDLE maps: general algorithm for discrete object deformations based on local exchange maps},
  author={Otero-Mato, J. Manuel and Montes-Campos, Hadrian and Calvelo, Martin and Garcia-Fandino, Rebeca and Gallego, Luis J. and Pineiro, Angel and Varela, Luis M.},
  journal={Journal of Chemical Theory and Computation},
  volume={14},
  number={2},
  pages={466--478},
  year={2018},
  publisher={ACS Publications}
}
""",
    language="latex",
)
st.markdown("----")

# Global object to store the information
information = GlobalInformation()

upload_system_and_molecules(information)

if information.errors:
    st.info("Please, check the errors before continuing")
elif information.molecule_correspondence and any(
    (ali.start is not None) and (ali.end is not None)
    for ali in information.molecule_correspondence.values()
):
    run_mapping_and_download(information)

st.markdown("# Do you need help?")
st.markdown("""If you struggle to use this interface or you find any problem or
               bug you can check out the issues section of the repository with [this
               interface](https://github.com/txemaotero/gaddlemaps_interface/issues)
               or the one with the [gaddlemaps python
               module](https://github.com/txemaotero/gaddlemaps/issues) to
               see if anyone else has already experienced the same. If not, you
               can open an issue there and we will try to fix it as soon as
               possible.""")
