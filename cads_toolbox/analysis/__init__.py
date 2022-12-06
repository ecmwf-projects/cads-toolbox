import numpy
import emohawk
import coucal

#@emhawk_to_format('numpy')
def nanmean(data, *args, **kwargs):
    data = emohawk.open(data).to_numpy()
    return numpy.nanmean(*args, **kwargs)


@emohawk_to_format('xarray')
def climatology_mean(dataarray, *args, **kwargs):
    return coucal.climatology_mean(dataarray, *args, **kwargs)


@emohawk_to_format('xarray', 'geopandas')
def shape_average(dataarray, shape, *args, **kwargs):
    return coucal.shapes.average(dataarray, shape, *args, **kwargs)


shape_average = cadsify_function(
    coucal.shapes.average,
)



@cadsify_function(coucal.shapes.average)
def shape_average(dataarray, shape, *args, **kwargs):
    dataarray = emohawk(dataarray).to_xarray()
    shape = emohawk(shape).to_geopandas()
    return coucal.shapes.average(dataarray, shape, *args, **kwargs)