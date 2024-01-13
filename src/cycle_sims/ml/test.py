import cycle_sims.util.data as d_
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

def evaluate(model, batch):
    """
    Evaluate the given model on a batch of data.

    :param model: An instance of CustomSquaredModel.
    :param batch: A tuple containing test cases and results.
    :return: A tuple containing the model's prediction, the mean squared error, and the r^2 score.
    """
    test_cases, true_results = batch

    # Predicting with the model
    predicted_results = model.predict(test_cases)

    # Calculating Mean Squared Error (MSE)
    mse = mean_squared_error(true_results, predicted_results)

    # Calculating R^2 score
    # Note: This calculation assumes the batch provided is the same batch the model was fitted to.
    r2 = r2_score(true_results, predicted_results)

    # Printing MSE and R^2 score
    print(f"Mean Squared Error (MSE): {mse}")
    print(f"R^2 Score: {r2}")

    return predicted_results, mse, r2

def test_model(model, dataloader, result_column_name, target_features):
    test_cases, results = d_.get_batch_with_selected_result_column_by_name(dataloader, result_column_name, target_features)
    predicted_results, mse, r2 = evaluate(model, (test_cases, results))
    return model, (mse, r2), predicted_results, test_cases, results

def test_model_expression(model, dataloader, result_expression, target_features):
    test_cases, results = d_.get_batch_with_selected_result_expression(dataloader, result_expression, target_features)
    predicted_results, mse, r2 = evaluate(model, (test_cases, results))
    return model, (mse, r2), predicted_results, test_cases, results