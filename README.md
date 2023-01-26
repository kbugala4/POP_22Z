# POP_22Z
### Projekt końcowy z przedmiotu [POP] - Przeszukiwanie i Optymalizacja
**Temat**: </br>
Rozwiąż Sudoku przy pomocy algorytmu genetycznego oraz algorytmu ACO (ang. Ant Colony Optimisation). Zaprojektuj eksperymenty numeryczne, w których porównasz działanie obu algorytmów.

## Installation

1. Make sure you have python3 installed in your system. 
2. Clone the repository:
```bash
$ git clone https://github.com/kbugala4/POP_22Z.git
```
2. Navigate to the project directory.
3. Create and activate a virtual environment:
```bash
$ python3 -m venv pop_project
$ source pop_project/bin/activate
```
4. Install the required packages:
```bash
$ pip3 install -r requirements.txt
```
5. Navigate to the */src/reproduce* directory and open one of the following scripts:
- reproduce_ga.py -- use to reproduce one of the genetic algorithms tests, by changing line 12 by inputing chosen parameters file name -- files with params used to reproduce tests are located in the */results/params/ga* directory; run file with the following command:
```bash
$ python3 src/reproduce/reproduce_ga.py
```
- reproduce_aco.py -- use to reproduce one of the ACO tests, also by changing the same line with one of the parameters files located in the */results/params/aco* directory; run file with the following command:
```bash
$ python3 src/reproduce/reproduce_aco.py
```
8. Once you're done working on the project, deactivate the virtual environment:
```bash
$ deactivate
```
