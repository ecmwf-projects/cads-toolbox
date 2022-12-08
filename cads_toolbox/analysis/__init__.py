import coucal
import xarray as xr

from cads_toolbox.cadsify import cadsify_function


shape_average = cadsify_function(
    coucal.shapes.average, funky = xr.Dataset
)
