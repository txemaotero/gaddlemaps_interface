import streamlit as st
import pandas as pd

from gaddlemaps import Manager, Alignment
from gaddlemaps.components import System, Molecule

from utilities import get_mol_view, write_and_get_file, represent_molecule, GlobalInformation
from components import add_molecule_component, main_page


# Page style
st.set_page_config(layout="wide")
# Title of the main page
st.title("Gaddle Maps Interface")

information = GlobalInformation()

if information.page == 0:
    main_page(information)
elif information.page == 1:
    pass