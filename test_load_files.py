from io import StringIO
import streamlit as st 

from gaddlemaps.components import System


fgro = st.file_uploader('Upload GRO file', type=['gro'])
fitp = st.file_uploader('Upload itp file', type=['itp'])

if (fgro is not None) and (fitp is not None):
    name = fgro.name
    fgro = StringIO(fgro.getvalue().decode("utf-8"))
    fgro.mode = 'r'
    fgro.name = name

    name = fitp.name
    fitp = StringIO(fitp.getvalue().decode("utf-8"))
    fitp.mode = 'r'
    fitp.name = name

    system = System(fgro, fitp)
    st.write(system.composition)