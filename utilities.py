import sys
from contextlib import contextmanager
from io import StringIO
from typing import Optional

import py3Dmol
import streamlit as st
from gaddlemaps import Alignment, Manager
from gaddlemaps.components import Molecule
from stmol import showmol
from streamlit.scriptrunner import get_script_run_ctx
from streamlit.uploaded_file_manager import UploadedFile

Restrictions = dict[str, Optional[list[tuple[int, int]]]]


def get_mol_view(
    gro_content: str,
    width: int = 400,
    height: int = 400,
    style: dict = None,
    view: Optional[py3Dmol.view] = None,
) -> py3Dmol.view:
    """
    Takes the content of a .gro file and returns a py3Dmol.view object

    Adds the function to hover atoms and display their index.

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
    if view is None:
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
    molecule: Molecule,
    width: int = 616,
    height: int = 400,
    style: dict = None,
    return_showmol=True,
    view: Optional[py3Dmol.view] = None,
) -> Optional[py3Dmol.view]:
    """
    Takes a Molecule (gaddlemaps object) and returns a py3Dmol.view object

    Adds the function to hover atoms and display their index.

    Parameters
    ----------
    Molecule : gaddlemaps.components.Molecule
        The object with the molecule to be represented.
    width : int, optional
        The width of the view. The default is 616 which correspond to half
        column when the browser is maximized.
    height : int, optional
        The height of the view. The default is 400.
    style : dict, optional
        The style of the view (input to the setStyle method). The default is
        {'sphere': {}}.
    return_showmol : bool, optional
        If True None is returned and the generated view is displayed. Else, the
        view is returned. The default is True.
    view : py3Dmol.view, optional
        The view to be used to represent the molecule. The default is None,
        which means that a new view is created.

    Returns
    -------
    py3Dmol.view or None
        The py3Dmol.view object containing the molecules in the .gro file.
    """
    lines = ["test", f"{len(molecule)}"]
    for atom in molecule:
        atom = atom.copy()
        lines.append(atom.gro_line(parsed=False))
    lines += ["    0.0000    0.0000    0.0000"]
    gro_content = "\n".join(lines)
    view = get_mol_view(gro_content, width=width, height=height, style=style, view=view)
    if return_showmol:
        showmol(view, height=height, width=width)
        return None
    else:
        return view


def represent_molecule_comparative(
    align: Alignment, width: int = 616, height: int = 400
):
    """
    Represents the molecular overlap between start and end of align

    Parameters
    ----------
    align : gaddlemaps.Alignment
        The alignment object with the start and end molecules to be
        represented.
    width : int, optional
        The width of the view. The default is 616 which correspond to half
        column when the browser is maximized.
    height : int, optional
        The height of the view. The default is 400.

    """
    align.start.resnames = "START"  # type: ignore
    align.end.resnames = "END"  # type: ignore
    view1 = represent_molecule(
        align.end, width=width, height=height, return_showmol=False
    )
    view = represent_molecule(align.start, view=view1, return_showmol=False)
    assert isinstance(view, py3Dmol.view)
    view.setStyle({"resn": "START"}, {"sphere": {"scale": 1.5, "opacity": 0.7}})
    view.setStyle({"resn": "END"}, {"sphere": {"scale": 0.5}})
    showmol(view, height=height, width=width)


def write_and_get_file(uploaded_file: Optional[UploadedFile]) -> Optional[StringIO]:
    """
    Takes a file uploaded by streamlit converts it to a StringIO

    It also adds some attributes such as the mode and name that are needed to
    load gaddlemaps objects.

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
    fopen.mode = "r"  # type: ignore
    fopen.name = name
    return fopen


class GlobalInformation:
    """
    Class that stores global information about the current mapping.
    """

    def __init__(self):
        self.system = None
        self.molecule_correspondence: dict[str, Alignment] = {}
        self.molecule_restrictions: Restrictions = {}
        self.errors = False
        self.manager = None
        self.cg_system_name = ""

    def init_manager(self):
        """
        Initializes the manager with the loaded molecules and system.
        """
        self.manager = Manager(self.system)
        self.manager.molecule_correspondence = self.molecule_correspondence

    def align_molecules(self):
        """
        Aligns the molecules in the manager.
        """
        if self.manager is None:
            self.init_manager()
        self.manager.align_molecules(restrictions=self.molecule_restrictions)


@contextmanager
def st_redirect(src, dst):
    """
    Redirects the terminal output to the streamlit app.
    """
    placeholder = st.empty()
    output_func = getattr(placeholder, dst)

    with StringIO() as buffer:
        old_write = src.write

        def new_write(b):
            if get_script_run_ctx():
                buffer.write(b + "")
                all_lines = buffer.getvalue().split("\n")
                try:
                    index = all_lines.index("Calculating exchange maps...")
                    lines, end = all_lines[:index], all_lines[index:]
                except ValueError:
                    lines, end = all_lines, []

                headers, chis = lines[0::4], lines[2::4]
                value = "\n\n".join(
                    [
                        i + "\n\n" + (j.split("\r")[-1] if j else "Chi2")
                        for i, j in zip(headers, chis)
                    ]
                )
                output_func(value + "\n\n" + "\n\n".join(end) + "")
            else:
                old_write(b)

        try:
            src.write = new_write
            yield
        finally:
            src.write = old_write


@contextmanager
def st_stdout(dst):
    """
    This will show the prints
    """
    with st_redirect(sys.stdout, dst):
        yield
