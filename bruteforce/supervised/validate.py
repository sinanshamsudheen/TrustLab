from ydata_profiling import ProfileReport
import pandas as pd

df = pd.read_csv("balanced_synthetic_auth_dataset.csv")
profile = ProfileReport(df, title="Brute-Force Dataset Report", explorative=True)
profile.to_file("report.html")
