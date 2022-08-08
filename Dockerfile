FROM continuumio/miniconda3

WORKDIR /src/cads-toolbox

COPY environment.yml /src/cads-toolbox/

RUN conda install -c conda-forge gcc python=3.10 \
    && conda env update -n base -f environment.yml

COPY . /src/cads-toolbox

RUN pip install --no-deps -e .
