# -*- coding: utf-8 -*-
"""
    Main module for the banalysis package.
"""

##### IMPORTS #####
# Standard imports

# Third party imports
from bokeh.io import curdoc

# Local imports
from .dashboard import Dashboard

##### FUNCTIONS #####
def main(doc):
    dashboard = Dashboard(doc)


##### MAIN #####
main(curdoc())
