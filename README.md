# ELBaselines
This repo is aimed to create baseline results for Entity Linking, by running a text against the state-of-the-art systems for entity linking, using their most standard configuration.

Currently, only one system is supported (AGDISTIS). To run this, use the following command (change python with python3 if your default Python version is 2.x):
python3 run_naf.py GOLD/aida_naf {outputfile}
