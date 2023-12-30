import pandas as pd
import re
from collections import defaultdict

def extract_unique_component_names(csv_file_path):
    """
    Extracts a set of unique ComponentNames from a CSV file.

    Parameters:
    csv_file_path (str): The file path to a CSV file.

    Returns:
    set: A set of unique ComponentNames.
    """
    df = pd.read_csv(csv_file_path)
    component_names = set(df['name'].apply(lambda x: x.split('_')[0]))
    return component_names

def extract_parameters_and_values_with_ordering(component_names, csv_file_path):
    """
    For each ComponentName, extracts unique parameter names and their values,
    ensuring that parameter names are correctly identified without including subsequent integer digits.
    Additionally, includes a canonically sorted list of parameter names in the output.

    Parameters:
    component_names (set): A set of ComponentNames.
    csv_file_path (str): The file path to a CSV file.

    Returns:
    dict: A dictionary where each key is a ComponentName and each value is a tuple containing
          two items: a dictionary of parameters and their values, and a list of sorted parameter names.
    """
    df = pd.read_csv(csv_file_path)
    parameters = defaultdict(lambda: (defaultdict(set), []))

    for _, row in df.iterrows():
        component_id = row['name']
        component_name = component_id.split('_')[0]
        if component_name in component_names:
            param_matches = re.findall(r'_(\D+?)(\d+)', component_id)
            param_values = [(param_name, int(param_value)) for param_name, param_value in param_matches]
            for param_name, param_value in param_values:
                parameters[component_name][0][param_name].add(param_value)
            # Sorting parameters by their appearance in the component ID and ensuring uniqueness
            ordered_params = [param_name for param_name, _ in param_values if param_name not in parameters[component_name][1]]
            parameters[component_name][1].extend(ordered_params)

    # Ensuring the ordering of parameters for each component
    for component in parameters:
        parameters[component] = (parameters[component][0], sorted(parameters[component][1], key=lambda x: parameters[component][1].index(x)))

    return parameters

def extract_supported_clock_latencies(csv_file_path):
    """
    Determines all clock latencies for which each ComponentName was simulated.

    Parameters:
    csv_file_path (str): The file path to a CSV file.

    Returns:
    dict: A dictionary where each key is a ComponentName and each value is a sorted
          list of supported clock latencies (as floats).
    """
    df = pd.read_csv(csv_file_path)
    clock_latencies = defaultdict(set)

    for _, row in df.iterrows():
        component_name = row['name'].split('_')[0]
        clock_latency = float(row['critical_path_clock_latency'])
        clock_latencies[component_name].add(clock_latency)

    # Sorting the latencies for each component
    for component in clock_latencies:
        clock_latencies[component] = sorted(clock_latencies[component])

    return clock_latencies

def extract_supported_param_combinations(csv_file_path, component_names, parameters):
    """
    For a given component and clock latency, determines all supported combinations of parameter values.

    Parameters:
    csv_file_path (str): The file path to a CSV file.
    component_names (set): A set of ComponentNames.
    parameters (dict): A dictionary of parameters and their values for each component.

    Returns:
    dict: A dictionary where each key is a tuple (ComponentName, clock_latency) and each value is a
          set of tuples representing supported combinations of parameter values.
    """
    df = pd.read_csv(csv_file_path)
    param_combinations = defaultdict(set)

    for _, row in df.iterrows():
        component_id = row['name']
        component_name = component_id.split('_')[0]
        if component_name in component_names:
            clock_latency = float(row['critical_path_clock_latency'])
            param_values = tuple(int(value) for _, value in re.findall(r'_(\D+?)(\d+)', component_id))
            param_combinations[(component_name, clock_latency)].add(param_values)

    return param_combinations
