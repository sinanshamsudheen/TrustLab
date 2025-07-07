#!/usr/bin/env python3
"""
Utility script to inspect a trained model's structure and parameters
"""
import joblib
import sys
import os
from pprint import pprint
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator

# Add project root to path to make imports work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config_loader import Config

# Initialize configuration
config = Config()

def print_model_details(model, indent=0):
    """Print details of a model object"""
    prefix = " " * indent
    print(f"{prefix}Type: {type(model)}")
    
    if isinstance(model, Pipeline):
        print(f"{prefix}Pipeline steps:")
        for name, step in model.named_steps.items():
            print(f"{prefix}- Step: {name}")
            print_model_details(step, indent + 4)
        return

    if isinstance(model, BaseEstimator):
        try:
            print(f"{prefix}Hyperparameters:")
            pprint(model.get_params(), indent=indent + 2)
        except Exception as e:
            print(f"{prefix}Failed to get params: {e}")

    for attr in ['coef_', 'intercept_', 'feature_importances_', 'classes_']:
        if hasattr(model, attr):
            print(f"{prefix}{attr}:")
            pprint(getattr(model, attr), indent=indent + 2)

    if hasattr(model, '__dict__'):
        print(f"{prefix}Attributes:")
        keys = sorted(model.__dict__.keys())
        for key in keys:
            print(f"{prefix}- {key}: {type(model.__dict__[key])}")

def main(pkl_path=None):
    """Inspect a model file"""
    if pkl_path is None:
        pkl_path = config.get('paths.models.bruteforce_model')
        
    try:
        model = joblib.load(pkl_path)
        print(f"\nLoaded model from: {pkl_path}")
        print_model_details(model)
    except Exception as e:
        print(f"❌ Failed to load model: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
