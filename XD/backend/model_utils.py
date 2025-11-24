"""
Utility classes for ML model compatibility
"""

class EnhancedFeatureEngineer:
    """
    Dummy class for model loading compatibility
    The actual model (LightGBM) doesn't need this class to make predictions,
    but it's required for unpickling the saved model file
    """
    def __init__(self):
        pass
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return X
    
    def fit_transform(self, X, y=None):
        return self.fit(X, y).transform(X)
