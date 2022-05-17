from io import StringIO
import streamlit as st
import py3Dmol
from stmol import showmol
import tempfile
from gaddlemaps.components import System


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


st.title('GaddleMaps Interface')

cg_system_gro = st.file_uploader("Choose a .gro file with the CG systems", type=["gro"])

if cg_system_gro is not None:
    sys_gro_name = write_and_get_fname(cg_system_gro)
    system = System(sys_gro_name.name)
    st.write(system.system_gro.composition)
    # view = get_mol_view(gro_content)
    # showmol(view, height=400, width=400)
    itp_files = st.file_uploader("Upload topologies to recognize molecules", type=["itp", "top"], accept_multiple_files=True)
    for itp in itp_files:
        fopen = write_and_get_fname(itp)
        system.add_ftop(fopen.name)
    st.write(system.composition)
    for mol in system.different_molecules:
        lines = ['test', f'{len(mol)}']
        lines += [a.gro_line(parsed=False) for a in mol] + ['    0.0000    0.0000    0.0000']
        print(lines)
        gro_content = '\n'.join(lines)
        view = get_mol_view(gro_content)
        showmol(view, height=400, width=400)