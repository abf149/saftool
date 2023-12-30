# SAFTools

This is a simple example package. You can use
[GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.

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