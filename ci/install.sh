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

# Install dependencies
if [ "$CIRCLE_NODE_INDEX" = "0" ]; then
    # python3.6, pweave from git/master
    pip install -q matplotlib
    pip install git+ssh://git@github.com/mpastell/Pweave.git
elif [ "$CIRCLE_NODE_INDEX" = "1" ]; then
    # python3.5, latest pweave 0.30
    conda install -q matplotlib pandoc
    pip install -q pweave
else
    # python2.7, legacy pweave 0.25 :(
    conda install -q matplotlib
    pip install -q pweave==0.25
fi

# Bring Spyder dependencies (install/uninstall Spyder)
if [ "$CIRCLE_NODE_INDEX" = "0" ]; then
    pip install -q spyder
    pip uninstall -q -y spyder
else
    conda install -q spyder
    conda remove -q -y spyder
fi

# Install Spyder from the 3.x branch
mkdir spyder-source && cd spyder-source
wget -q https://github.com/spyder-ide/spyder/archive/3.x.zip && unzip -q 3.x.zip
cd spyder-3.x
python setup.py install > /dev/null

# Come back to the initial parent directory and install spyder-reports
cd ../../
python setup.py install --single-version-externally-managed --record=record.txt > /dev/null
