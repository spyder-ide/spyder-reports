#!/bin/bash

# First convert PY_VERSIONS to an array and then select the python
# version based on the CIRCLE_NODE_INDEX
export PY_VERSIONS=($PY_VERSIONS)
export TRAVIS_PYTHON_VERSION=${PY_VERSIONS[$CIRCLE_NODE_INDEX]}
echo -e "PYTHON = $TRAVIS_PYTHON_VERSION \n============"

git clone git://github.com/astropy/ci-helpers.git > /dev/null
source ci-helpers/travis/setup_conda_$TRAVIS_OS_NAME.sh
export PATH="$HOME/miniconda/bin:$PATH"
source activate test

conda install -q ciocheck -c spyder-ide --no-update-deps

if [ "$CIRCLE_NODE_INDEX" = "0" ]; then
    pip install -q markdown pygments ipython nbformat nbconvert jupyter_client pyqt5 spyder>=3.2 matplotlib
    pip install git+ssh://git@github.com/mpastell/Pweave.git
else
    conda install -q "spyder>=3.2" matplotlib
    pip install -q pweave
fi

python setup.py install --single-version-externally-managed --record=record.txt > /dev/null
