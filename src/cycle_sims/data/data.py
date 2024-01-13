import numpy as np
import sympy
from sympy import sympify

# Get a batch, with only the desired result column selected by name
def get_batch_with_selected_result_column_by_name(dataloader, result_column_name, target_features):
    for batch in dataloader:
        test_cases, results = batch
        selected_results = results[:,:, target_features.index(result_column_name):(target_features.index(result_column_name)+1)]
        return test_cases.numpy().reshape(-1, test_cases.shape[-1]), selected_results.numpy().reshape(-1, selected_results.shape[-1])
    
# Get a batch, specifying an expression over target features
def get_batch_with_selected_result_expression(dataloader, result_expression, target_features):
    # Sympify the expression
    expression = sympify(result_expression)
    # Extract symbols (column names) from the expression
    symbols = expression.free_symbols
    symbol_names = [str(symbol) for symbol in symbols]

    for batch in dataloader:
        test_cases, results = batch

        # Extract the columns from results corresponding to the symbols in the expression
        selected_columns = []
        for symbol_name in symbol_names:
            if symbol_name in target_features:
                index = target_features.index(symbol_name)
                selected_columns.append(results[:, :, index:index+1])
            else:
                raise ValueError(f"Column '{symbol_name}' not found in target_features")

        # Concatenate selected columns along the last dimension
        concatenated_results = np.concatenate(selected_columns, axis=-1)

        # Evaluate the expression for each row
        evaluated_results = np.apply_along_axis(
            lambda row: float(expression.subs({symbol: row[target_features.index(str(symbol))] for symbol in symbols})),
            axis=-1, arr=results
        )

        return test_cases, evaluated_results