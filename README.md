# ELBaselines
This repo is aimed to create baseline results for Entity Linking, by running a text against the state-of-the-art systems for entity linking, using their most standard configuration.

Currently, only one system is supported (AGDISTIS). To run this, use the following command (change python with python3 if your default Python version is 2.x):
```python
python3 run_naf.py GOLD/aida_naf {outputfile}
```

## TODO:
* Running other systems
  * AGDISTIS (Done)
  * Spotlight (Pending)
  * ADEL (Pending)
  * Babelfy (Pending)
* In-depth error analysis:
  * Analyze candidates
  * Compute upperbound
* My system
  * Run on wikinews data
  * Add the 'recency' score
  * NILs where the confidence is low
  * LOTUS encoded candidates
