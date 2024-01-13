from cycle_sims.ml import model as m_, test as t_
import src.cycle_sims.data as d_

def train_model(dataloader, result_column_name, target_features, degree=2):
    model = m_.NormalizedTransformedPolynomial(degree=degree)
    test_cases, results = d_.get_batch_with_selected_result_column_by_name(dataloader, result_column_name, target_features)
    model.fit(test_cases, results)
    predicted_results, mse, r2 = t_.evaluate(model, (test_cases, results))
    return model, predicted_results, (mse, r2), test_cases, results

def train_model_expression(dataloader, result_expression, target_features, degree=2):
    model = m_.NormalizedTransformedPolynomial(degree=degree)
    test_cases, results = d_.get_batch_with_selected_result_expression(dataloader, result_expression, target_features)
    model.fit(test_cases, results)
    predicted_results, mse, r2 = t_.evaluate(model, (test_cases, results))
    return model, predicted_results, (mse, r2), test_cases, results