"""
Module to contains tools for analysis.
Currently ingests the tools from the following python packages:
- coucal
"""
import coucal

from cads_toolbox._inputs_transform import transform_module_inputs

aggregate = transform_module_inputs(coucal.aggregate)

climate = transform_module_inputs(coucal.climate)
