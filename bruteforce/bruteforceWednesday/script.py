import joblib
import sys
from pprint import pprint
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator

def print_model_details(model, indent=0):
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

# pkl_path = 'bruteforce_model.pkl'  # Default path, can be overridden by command line argument  
def main(pkl_path):
    try:
        model = joblib.load(pkl_path)
        print(f"\nLoaded model from: {pkl_path}")
        print_model_details(model)
    except Exception as e:
        print(f"❌ Failed to load model: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python inspect_model_pkl.py <path_to_model.pkl>")
    else:
        main(sys.argv[1])
