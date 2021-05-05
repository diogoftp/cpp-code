# cpp-code
This repository contains code developed during the development of the paper "On the Transition of Legacy Networks to SDN - An Analysis on the Impact of Deployment Time, Number, and Location of Controllers"

## Data sets used

The two data sets included were taken from [Knowledge-Defined Networking Training Datasets](https://knowledgedefinednetworking.org/)

NSFNet is a 14-node topology

GEANT2 is a 24-node topology

## Requirements

[Python3](https://www.python.org/)

## Usage

Install python dependencies in the project directory

    $ python -m pip install -r requirements.txt

To run the optimization separately:

    $ python optimization.py dataset_name N T

To run the highest eccentricity node separately:

    $ python highest_eccentricity_node.py dataset_name N T

To run the highest load node separately:

    $ python highest_load_node.py dataset_name N T

To run the most connected node separately:

    $ python most_connected_node.py dataset_name N T

To run the four algorithms for both topologies and save the results to a file, run:

    $ python results.py output_file number_of_repetitions

## Additional configuration

The max load and max latency constraints can be configured inside each file. The name of the variables are CMAX and LMAX, respectively

To change the load scenario, choose one line and uncomment the other on file functions.py:

Uncomment line 20 for worst case scenario

Uncomment line 22 for best case scenario

### Authors:<br/>
Diogo Pontes (diogo.the@aluno.unb.br)<br/>
Marcos Caetano (mfcaetano@unb.br)<br/>
Geraldo Filho (geraldof@unb.br)<br/>
Lisandro Granville (granville@inf.ufrgs.br)<br/>
Marcelo Marotta (marcelo.marotta@unb.br)<br/>