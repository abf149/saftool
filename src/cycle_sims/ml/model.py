from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
import numpy as np

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

    def fit(self, X, y):
        # Finding the square root of the y training data
        if self.sqrt:
            sqrt_y = np.sqrt(y)

            # Fitting the internal pipeline to X and sqrt(y)
            self.pipeline.fit(X, sqrt_y)
        elif self.lg:
            # Fitting the internal pipeline to X and log(y)
            self.pipeline.fit(np.log(X), np.log(y))
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