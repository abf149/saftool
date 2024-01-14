from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
import numpy as np

class NormalizedTransformedPolynomial(BaseEstimator, TransformerMixin):
    def __init__(self, degree=2, sqrt=False, lg=True, zero_replace_value=0.0001):
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('preprocessor', PolynomialFeatures(degree=degree, include_bias=True)),
            ('estimator', LinearRegression())
        ])
        self.sqrt = sqrt
        self.lg = lg
        self.degree = degree
        self.zero_replace_value = zero_replace_value

    def fit(self, X, y):
        print(X.shape)
        print(y.shape)
        # Ensure that X and y have the same number of rows
        assert X.shape[0] == len(y), "X and y must have the same number of rows."

        # Create a mask to filter out rows where X or y contains zeros
        non_zero_mask_X = ~np.any(X == 0, axis=1)  # Rows in X that don't contain zero
        non_zero_mask_y = y != 0                  # Elements in y that are not zero
        non_zero_mask = non_zero_mask_X & non_zero_mask_y  # Combine masks

        # Apply the mask
        X_filtered = X[non_zero_mask]
        y_filtered = y[non_zero_mask]

        # Print the number of rows removed
        rows_removed = X.shape[0] - X_filtered.shape[0]
        print(f"Removed {rows_removed} rows containing zeros.")

        # Apply transformation to y
        transformed_y = y_filtered
        if self.sqrt:
            transformed_y = np.sqrt(y_filtered)
        elif self.lg:
            transformed_y = np.log(y_filtered + self.zero_replace_value)

        # Fit the pipeline
        if self.lg:
            self.pipeline.fit(np.log(X_filtered + self.zero_replace_value), transformed_y)
        else:
            self.pipeline.fit(X_filtered, transformed_y)
        return self

    def predict(self, X):
        # Replace zeros in X
        X_replaced = np.where(X == 0, self.zero_replace_value, X)

        # Predict using the pipeline
        if self.lg:
            pipeline_output = self.pipeline.predict(np.log(X_replaced))
        else:
            pipeline_output = self.pipeline.predict(X_replaced)

        # Apply inverse transformation to the output
        if self.sqrt:
            return np.square(pipeline_output)
        elif self.lg:
            return np.exp(pipeline_output)
        else:
            return pipeline_output

'''
class NormalizedTransformedPolynomial(BaseEstimator, TransformerMixin):
    def __init__(self, degree=2, sqrt=False, lg=True):
        # Internal pipeline: input scaler -> polynomial features -> linear regression
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('preprocessor', PolynomialFeatures(degree=degree, include_bias=True)),
            ('estimator', LinearRegression())
        ])
        self.sqrt=sqrt
        self.lg=lg
        self.degree=degree

    def fit(self, X, y):
        # Finding the square root of the y training data
        if self.sqrt:
            sqrt_y = np.sqrt(y)

            # Fitting the internal pipeline to X and sqrt(y)
            self.pipeline.fit(X, sqrt_y)
        elif self.lg:
            # Fitting the internal pipeline to X and log(y)
            self.pipeline.fit(np.log(X+0.0001), np.log(y+0.0001))
        else:
            # Fitting the internal pipeline to X and sqrt(y)
            self.pipeline.fit(X, y)
        return self

    def predict(self, X):
        # Feeding the input to the pipeline and receiving the pipeline output
        pipeline_output=None
        if self.lg:
            pipeline_output = self.pipeline.predict(np.log(X))
        else:
            pipeline_output = self.pipeline.predict(X)

        if self.sqrt:
            # Squaring the pipeline output and returning it
            return np.square(pipeline_output)
        elif self.lg:
            # Taking the exponential of the pipeline output and returning it
            return np.exp(pipeline_output)
        else:
            # Return pipeline output
            return pipeline_output
'''