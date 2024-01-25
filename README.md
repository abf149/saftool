# SAFTools

Please cite Git repo via the following DOI: 10.5281/zenodo.10568496

[Additional documentation (WIP)](https://saftools.readthedocs.io/en/latest/)

SAFTools is a software suite for inferring and sizing Sparse Acceleration Feature (SAF) microarchitecture, starting from an architecture specification and a declarative description of SAF optimizations. The input specifications are expected in the [Sparseloop](https://sparseloop.mit.edu/) configuration file format.

SAFTools allows you to quickly figure out what microarchitecture may be required to exploit tensor zero-sparsity in a hardware accelerator. SAFTools also facilitates design-space exploration over the space of possible microarchitectures. This can be done with the user writing any RTL ("pre-RTL".)

* **SAFinfer** - Perform *taxonomic inference*, in order to infer a hierarchical SAF microarchitecture topology for each SAF in the Sparseloop config
    * The hierarchical topology has two key levels of abstraction
    * High-level SAF microarchitecture blocks - sparse-format-agnostic netlist representing the implementation of each SAF
    * Low-level SAF microarchitecture topology - each high-level block is associated with an lower-level implementation, which is a netlist of interconnected SAF microarchitecture primitives. SAFinfer automatically customizes this implementation topology based on sparse representation format and other surrounding design considerations.
* **SAFmodel** - (1) perform *scale inference* to size the scale parameters for each SAF microarchitecture primitive. (2) export pre-RTL Accelergy analytical models of SAF microarchitecture components.
* A typical workflow will utilize SAFinfer and SAFmodel in sequence, in order to infer and size a SAF microarchitecture and then export Accelergy models.
* **SAFsearch** -
    * Sometimes a SAF microarchitecture implementation topology has *free parameters* which SAFinfer cannot infer based on sparse representation format or surrounding design details
    * Free parameters represent a design-exploration space, in which the user can explore tradeoffs without breaking the design.
    * **SAFsearch** implements an automated search loop over free parameters. Each design-point is a combination of free parameter values. Each inner-loop iteration calls SAFinfer and injects free parameter values corresponding to the particular design-point, then calls SAFmodel to perform scale inference (model export is disabled by SAFsearch to speed up the search process)
    * SAFsearch returns a list of the top-K design-points, ranked by a user-specified objective function.
* **RTL library** - SAFmodel models pull energy/area metrics from a CSV table of RTL characterization results. The RTL library contains the original RTL which was characterized. Parameterized RTL is implemented in the Chisel HDL and then transformed to Verilog for a variety of parameter-value combinations.

SAFTools is an artifact associated with the masters thesis "Microarchitecture Categorization and Pre-RTL
Analytical Modeling for Sparse Tensor Accelerators" (Feldman, 2024.)

## Quickstart

**Install**:

```
cd saftools/src
python3 -m pip uninstall saftools
python3 -m pip install -e saftools
```

**SAFInfer**:
```
safinfer -i src/ref_input/ -q src/ref_input/safinfer_settings.yaml -o src/ref_output/ -L
```

**SAFModel**:
```
safmodel -T src/ref_output/new_arch.yaml -a src/ref_input/arch.yaml -s src/ref_input/sparseopts.yaml -c src/ref_input/compound_components.yaml -U src/ref_input/safmodel_settings.yaml  -r src/ref_output/arch_w_SAF.yaml -k   src/ref_output/ -L
```

**SAFSearch**:
```
safsearch -L -a src/ref_input/arch.yaml -A src/ref_output/arch_w_SAF.yaml -c src/ref_input/compound_components.yaml -k   src/ref_output/  -s src/ref_input/sparseopts.yaml -S src/ref_input/safmodel_settings.yaml -q src/ref_input/safinfer_settings.yaml -Q src/ref_input/safsearch_settings.yaml -T src/ref_output/new_arch.yaml -b src/ref_output/bindings.yaml
```

## Build docs

1. From the top-level directory, run

```
sphinx-apidoc -o docs .
```

2. From the docs directory, run

```
./make_html
```

## SAF microarchitecture YAML scripting frameworks

This work introduces two YAML scripting frameworks, taxoscript and modelscript, for users to define custom SAF microarchitecture components.

* **Taxoscript** - Framework for defining low-level SAF microarchitecture primitives and high-level SAF microarchitecture blocks
* **Modelscript** - Framework for
    1. Defining low-level primitive action-energy/area models in terms of RTL characterized metrics
    1. Defining compound models of high-level SAF microarchitecture blocks, composed from primitive models

## Overview of directory structure

```
src/ # Source directory
|-- accelergy/ # Accelergy resources directory
||
||-- data/
|||
|||-- primitives_table.csv # RTL characterization table.
|||
|||-- # Note: SAFmodel exports SAF microarchitecture models to primitives_ERT_ART.pkl in this directory
|||
||-- estimation_plugins/
|||
|||-- saf_primitives_estimator.py # SAFTools Accelergy estimator plugin for Accelergy.
|||
||-- primitive_component_libs/
|||
|||-- # Note: SAFmodel exports Accelergy primitive descriptions to saf_primitives.lib.yaml in this directory
|||
|-- case_studies/ # Case-studies from (Feldman, 2024)
||
||-- saf_attributes/
||
|||-- saf_attributes.ipynb # Top-level case-study Jupyter notebook
||
|
|-- cycle_sims/ # Cycle-accurate SAF microarchitecture primitive simulators (for training analytical models)
||
||-- fit_model_to_cycle_accurate_sim.ipynb # Google Colab notebook which runs cycle-accurate
||
||-- components/
|||
|||-- isectbd/ # Bidirectional intersection cycle-accurate simulators
||||
||||-- units/
|||||
|||||-- ideal.py # Ideal zero-cyle intersection unit sim
|||||
|||||-- two_finger.py # ExTensor-like two-finger intersection unit sim
|||||
|||||-- skip_ahead.py # ExTensor-like optimized/"skip-ahead" intersection unit sim
|||||
|||||-- direct_map.py # "Direct-mapped" intersection unit sim
|||||
||||
||||-- data/
||||
||||-- harness/ # Test-harness for simulating fiber intersection with intersection units
||||
|||
||
||-- data/
||
||-- ml/ # Resources for training a classical ML model to predict intersection unit match throughput
||
||-- viz/ # Resources for visualizing cycle-accurate simulator and modeling results
||
|
|-- core/ # SAFTools core functionality - Sparseloop parsing frontends, SAF microarchitecture abstractions, char. table parsing
|
|-- export/ # SAFmodel functionality to dump Accelergy models
|
|-- hw/ # RTL and characterization
||
||-- chisel/ # Chisel RTL
|||
|||-- main/ # Chisel SAF microarchitecture primitive RTL implementations
|||
|||-- test/ # Chisel testbench code
|||
|||-- verilog/ # Chisel-to-verilog export directory
|||
||
|
|-- script_parser/ # Taxoscript and modelscript parsers
||
||--taxo_parser_core.py # Taxoscript parser top-level file
||
||-- model_parser_core.py # Modelscript parser top-level file
||
|
|-- saflib/ # SAF microarchitecture script
||
||-- microarchitecture/
|||
|||-- taxoscript/ # Taxoscript definitions of SAF microarchitecture components
|||
|||-- modelscript/ # Modelscript model definitions for SAF microarchitecture components
|||
||
||-- architecture/ # Taxoscript models of architectural buffer stubs
||
|
|-- search/ # Support for SAFsearch design-space exploration capabilities
|
|-- solver/ # Taxonomic inference & scale inference solvers
|
|-- safinfer.py # SAFinfer CLI wrapper
|
|-- safmodel.py # SAFmodel CLI wrapper
|
|-- safsearch.py # SAFsearch CLI wrapper
|
|
|-- make_prim.sh # Automate RTL characterization
|

docs/ # Docs build directory
```