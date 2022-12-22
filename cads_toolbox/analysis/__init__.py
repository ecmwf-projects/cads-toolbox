"""
Module to contains tools for analysis.
Currently ingests the tools from the following python packages:
- coucal
"""
import coucal

from cads_toolbox.inputs_transform import _transform_module_inputs

aggregate = _transform_module_inputs(coucal.aggregate)

climate = _transform_module_inputs(coucal.climate)
