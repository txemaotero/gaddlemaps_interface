import streamlit as st
import py3Dmol
from stmol import showmol
import tempfile

from gaddlemaps.components import System

from multipage import MultiPage

def test_app():
    st.markdown("## Test page")

def get_mol_view(gro_content, width=400, height=400):
    view = py3Dmol.view(width=width, height=height)
    view.addModel(gro_content, 'gro')
    view.setStyle({'sphere': {}})
    view.center()
    view.zoomTo()
    view.setHoverable({},True, '''function(atom,viewer,event,container) {
                   if(!atom.label) {
                    atom.label = viewer.addLabel(atom.index,{position: atom, backgroundColor: 'mintcream', fontColor:'black'});
                   }}''',
               '''function(atom,viewer) { 
                   if(atom.label) {
                    viewer.removeLabel(atom.label);
                    delete atom.label;
                   }
                }''')
    return view

def write_and_get_fname(uploaded_file):
    suff = uploaded_file.name.split('.')[-1]
    temp = tempfile.NamedTemporaryFile(suffix='.' + suff)
    text = uploaded_file.read()
    temp.write(text)
    temp.seek(0)
    return temp

st.set_page_config(layout="wide")

# Create an instance of the app 
app = MultiPage({"Test page": test_app}, "Select a page")

# Title of the main page
st.title("Gaddle Maps Interface")

# The main app
app.run()