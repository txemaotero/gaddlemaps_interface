from io import StringIO
from typing import IO, Optional
from gaddlemaps import Alignment

import py3Dmol
import tempfile

from gaddlemaps.components import Molecule
from stmol import showmol

from streamlit.uploaded_file_manager import UploadedFile

def get_mol_view(
    gro_content: str, width: int = 400, height: int = 400, style: dict = None
) -> py3Dmol.view:
    """
    Takes the content of a .gro file and returns a py3Dmol.view object

    Adds the function to hover over atoms and display their index.

    Parameters
    ----------
    gro_content : str
        The content of a .gro file
    width : int, optional
        The width of the view. The default is 400.
    height : int, optional
        The height of the view. The default is 400.
    style : dict, optional
        The style of the view (input to the setStyle method). The default is
        {'sphere': {}}.

    Returns
    -------
    py3Dmol.view
        The py3Dmol.view object containing the molecules in the .gro file.
    """
    if style is None:
        style = {"sphere": {}}
    view = py3Dmol.view(width=width, height=height)
    view.addModel(gro_content, "gro")
    view.setStyle(style)
    view.center()
    view.zoomTo()
    view.setHoverable(
        {},
        True,
        """function(atom,viewer,event,container) {
                   if(!atom.label) {
                    atom.label = viewer.addLabel(atom.index,{position: atom, backgroundColor: 'mintcream', fontColor:'black'});
                   }}""",
        """function(atom,viewer) { 
                   if(atom.label) {
                    viewer.removeLabel(atom.label);
                    delete atom.label;
                   }
                }""",
    )
    return view


def represent_molecule(
    molecule: Molecule, width: int = 400, height: int = 400, style: dict = None
):
    lines = ["test", f"{len(molecule)}"]
    for atom in molecule:
        atom = atom.copy()
        # atom.position *= 1.1  # convert to angstrom
        lines.append(atom.gro_line(parsed=False))
    lines += ["    0.0000    0.0000    0.0000"]
    gro_content = "\n".join(lines)
    view = get_mol_view(gro_content, width=width, height=height, style=style)
    showmol(view, height=height, width=width)


def write_and_get_file(uploaded_file: Optional[UploadedFile]) -> Optional[StringIO]:
    """
    Takes a file uploaded by streamlit and writes it to a temporary file.

    Parameters
    ----------
    uploaded_file : st.FileUploader or None
        The file uploaded by streamlit. If None, returns None.

    Returns
    -------
    tempfile.NamedTemporaryFile
        The temporary file containing the uploaded file and seeked to the
        beginning.
    """
    if uploaded_file is None:
        return None
    name = uploaded_file.name
    fopen = StringIO(uploaded_file.getvalue().decode("utf-8"))
    fopen.mode = 'r'
    fopen.name = name
    return fopen


class GlobalInformation:
    def __init__(self):
        self.system = None
        self.molecule_correspondence: dict[str, Alignment] = {}
        self.page = 0
    
    def next_page(self):
        self.page += 1
        
    def previous_page(self):
        self.page -= 1