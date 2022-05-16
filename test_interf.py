from io import StringIO
import streamlit as st
import py3Dmol
from stmol import showmol
from gaddlemaps.components import SystemGro


def get_mol_view(gro_content, width=400, height=400):
    view = py3Dmol.view(width=width, height=height)
    view.addModel(gro_content, 'gro')
    view.setStyle({'stick': {}})
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

st.title('GaddleMaps Interface')

cg_system_gro = st.file_uploader("Choose a .gro file with the CG systems", type=["gro"])

if cg_system_gro is not None:
    # gro_content = cg_system_gro.getvalue().decode("utf-8")
    # system = SystemGro(cg_system_gro.name)
    st.write(cg_system_gro.__dict__)
    # view = get_mol_view(gro_content)
    # showmol(view, height=400, width=400)