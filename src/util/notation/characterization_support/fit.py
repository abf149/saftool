import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.metrics import mean_squared_error
from sympy import symbols, simplify, lambdify
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import itertools
import numpy as np

def polynomial_regression_generalized_v2(data_tuples, column_names, independent_var_names, max_degree=10, overfit=False, show_progress=True):
    """Fit polynomial regression models for given data and return the best models along with scalers."""
    
    # Convert list of tuples into a DataFrame
    data = pd.DataFrame(data_tuples, columns=column_names)

    # Splitting data into training and validation sets
    train_set, test_set = train_test_split(data, test_size=0.2, random_state=42)

    # Features and Targets
    X_train = train_set[independent_var_names]
    X_test = test_set[independent_var_names]
    
    y_energy_train = train_set['energy']
    y_energy_test = test_set['energy']

    y_area_train = train_set['area']
    y_area_test = test_set['area']

    # Standardizing the data
    scaler_X = StandardScaler().fit(X_train)
    X_train_scaled = pd.DataFrame(scaler_X.transform(X_train), columns=independent_var_names)
    X_test_scaled = pd.DataFrame(scaler_X.transform(X_test), columns=independent_var_names)
    
    scaler_energy = StandardScaler().fit(y_energy_train.values.reshape(-1, 1))
    y_energy_train_scaled = scaler_energy.transform(y_energy_train.values.reshape(-1, 1)).ravel()
    y_energy_test_scaled = scaler_energy.transform(y_energy_test.values.reshape(-1, 1)).ravel()
    
    scaler_area = StandardScaler().fit(y_area_train.values.reshape(-1, 1))
    y_area_train_scaled = scaler_area.transform(y_area_train.values.reshape(-1, 1)).ravel()
    y_area_test_scaled = scaler_area.transform(y_area_test.values.reshape(-1, 1)).ravel()
    
    fitted_models = {}
    scalers = {'X': scaler_X, 'energy': scaler_energy, 'area': scaler_area}
    best_degrees = {}
    MSEs = {'energy': [], 'area': []}
    NMSEs = {'energy': [], 'area': []}

    if overfit:
        for target_name, y, y_scaler in zip(
            ['energy', 'area'],
            [data['energy'], data['area']],
            [scaler_energy, scaler_area]
        ):
            y_scaled = y_scaler.transform(y.values.reshape(-1, 1)).ravel()
            poly_features = PolynomialFeatures(degree=max_degree, include_bias=False)
            X_poly = poly_features.fit_transform(pd.DataFrame(scaler_X.transform(data[independent_var_names]), columns=independent_var_names))
            best_model = LinearRegression().fit(X_poly, y_scaled)
            best_degrees[target_name] = max_degree
            fitted_models[target_name] = best_model
    else:
        for target_name, y_train_scaled, y_test_scaled in zip(
            ['energy', 'area'], 
            [y_energy_train_scaled, y_area_train_scaled], 
            [y_energy_test_scaled, y_area_test_scaled]
        ):
            best_mse = float('inf')
            best_degree = 0
            best_model = None
            for degree in range(1, max_degree + 1):
                poly_features = PolynomialFeatures(degree=degree, include_bias=False)
                X_train_poly = poly_features.fit_transform(pd.DataFrame(X_train_scaled, columns=independent_var_names))
                X_test_poly = poly_features.transform(pd.DataFrame(X_test_scaled, columns=independent_var_names))
                
                model = LinearRegression().fit(X_train_poly, y_train_scaled)
                predictions = model.predict(X_test_poly)
                mse = mean_squared_error(y_test_scaled, predictions)
                nmse = mse / mean_squared_error([0]*len(y_test_scaled), y_test_scaled)
                
                MSEs[target_name].append(mse)
                NMSEs[target_name].append(nmse)

                if mse < best_mse:
                    best_mse = mse
                    best_degree = degree
                    best_model = model

            best_degrees[target_name] = best_degree
            fitted_models[target_name] = best_model

    return fitted_models, scalers, best_degrees, MSEs, NMSEs

def polynomial_to_sympy_expression_with_lambda_generalized(model, input_scaler, output_scaler, degree, features):
    """Construct the polynomial symbolic representation and a corresponding lambda function."""
    
    # Define the variables for the model based on feature names
    symbols_list = symbols(features)
    
    # Initialize equation with the intercept
    equation = model.intercept_
    
    # Coefficient index
    idx = 0
    
    # Iterate through the polynomial degrees
    for d in range(1, degree+1):
        for comb in itertools.combinations_with_replacement(symbols_list, d):
            term = np.prod([(sym - input_scaler.mean_[features.index(str(sym))]) / input_scaler.scale_[features.index(str(sym))] for sym in comb])
            equation += model.coef_[idx] * term
            idx += 1
    
    # Apply the inverse scaling transformation symbolically
    equation = equation * output_scaler.scale_[0] + output_scaler.mean_[0]
    
    # Create a lambda function to evaluate the expression
    lambda_func = lambdify(symbols_list, equation, 'numpy')
    
    return str(simplify(equation)), lambda_func

def generate_baseline_estimate_generalized(model, feature_names, feature_values_dict, input_scaler, output_scaler, degree):
    """
    Generate the baseline energy (or area) estimate given a model, feature names, and feature values.
    """

    # Extract the values in the canonical order
    X = [feature_values_dict[name] for name in feature_names]
    
    X_df = pd.DataFrame([X], columns=feature_names)

    # Transform the input data
    X_scaled = pd.DataFrame(input_scaler.transform(X_df), columns=feature_names)

    # Generate polynomial features
    poly_features = PolynomialFeatures(degree=degree, include_bias=False)
    X_poly = poly_features.fit_transform(X_scaled)

    # Predict using the model
    y_scaled_pred = model.predict(X_poly)

    # Inverse transform the prediction to get the unscaled estimate
    y_estimate = output_scaler.inverse_transform(y_scaled_pred.reshape(-1, 1))[0][0]

    return y_estimate

def compare_lambda_with_baseline(fitted_models, lambdas, data_tuples, column_names, independent_var_names, scalers, best_degrees):
    """
    Compare the estimates from the lambda functions with the baseline estimates from the trained models.
    """
    
    # Extract the unscaled input data
    data_df = pd.DataFrame(data_tuples, columns=column_names)
    X_unscaled = data_df[independent_var_names].values
    
    # Calculate predictions using the lambda functions
    lambda_predictions = {
        target: lambdas[target](*X_unscaled.T) for target in ['energy', 'area']
    }

    # Calculate predictions using the generate_baseline_estimate_generalized function
    model_predictions = {}
    for target in ['energy', 'area']:
        model_predictions[target] = [
            generate_baseline_estimate_generalized(
                fitted_models[target], 
                independent_var_names, 
                {name: val for name, val in zip(independent_var_names, x)},
                scalers['X'], 
                scalers[target], 
                best_degrees[target]
            ) for x in X_unscaled
        ]

    # Calculate the mean squared error between lambda predictions and model predictions
    mse_comparison = {
        target: mean_squared_error(lambda_predictions[target], model_predictions[target]) for target in ['energy', 'area']
    }

    return mse_comparison