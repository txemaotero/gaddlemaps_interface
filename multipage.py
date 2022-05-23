from typing import Callable
import streamlit as st

class MultiPage: 
    """
    Manages wich sub-apps in the sidebar is showing
    
    Parameters
    ----------
    pages : dict
        A dictionary of pages to be added to the sidebar. The key is the name
        of the page, and the value is the function to be run when the page is
        selected.
    sidebar_title : str
        The title of the sidebar. 
    """
    def __init__(self, pages: dict[str, Callable], sidebar_title: str):
        self.pages = pages
        self.sidebar_title = sidebar_title
    
    def add_page(self, title: str, func: Callable): 
        """
        Add a page to the sidebar.

        Parameters
        ----------
        title : str
            The title of the page.
        func : callable
            The function to be run when the page is selected.
        """
        self.pages[title] = func

    def run(self):
        # Drodown to select the page to run  
        page = st.sidebar.selectbox(
            self.sidebar_title, 
            self.pages.keys(),
        )
        # run the app function 
        self.pages[page]()