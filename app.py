import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_completeness(df):
    num_cells = df.size
    num_non_null_cells = df.count().sum()
    return (num_non_null_cells / num_cells) * 100

def calculate_accuracy(df):
    num_cells = df.size
    num_non_missing_cells = num_cells - df.isnull().sum().sum()
    return (num_non_missing_cells / num_cells) * 100

def calculate_consistency(df):
    num_rows = df.shape[0]
    num_duplicates = df.duplicated().sum()
    return 100 - (num_duplicates / num_rows) * 100

def evaluate_csv_file(file_path):
    try:
        # Use lazy evaluation with yield
        df_iterator = pd.read_csv(file_path, chunksize=1000, encoding='utf-8')
        
        # Calculate metrics
        completeness_values = []
        accuracy_values = []
        consistency_values = []
        
        for df_chunk in df_iterator:
            completeness_values.append(calculate_completeness(df_chunk))
            accuracy_values.append(calculate_accuracy(df_chunk))
            consistency_values.append(calculate_consistency(df_chunk))
        
        completeness = sum(completeness_values) / len(completeness_values)
        accuracy = sum(accuracy_values) / len(accuracy_values)
        consistency = sum(consistency_values) / len(consistency_values)
        
        # Generate report
        report = {
            "file_path": file_path,
            "completeness": completeness,
            "accuracy": accuracy,
            "consistency": consistency
        }

        # Plotting
        metrics = ["Completeness", "Accuracy", "Consistency"]
        metric_values = [completeness, accuracy, consistency]

        sns.set(style="whitegrid")
        plt.figure(figsize=(8, 4))
        sns.barplot(x=metrics, y=metric_values)
        plt.title("Data Quality Metrics")
        plt.xlabel("Metrics")
        plt.ylabel("Percentage")
        plt.savefig("C:/Users/ageu/Documents/AppProjects/dqc_app/static/graph.png")

        return report

    except FileNotFoundError:
        logger.error("File not found. Please provide a valid file path.")
        return None
    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "csv_file" not in request.files:
            logger.error("No file uploaded.")
            return render_template("index.html", error="No file uploaded.")
        
        csv_file = request.files["csv_file"]
        if csv_file.filename == "":
            logger.error("No file selected.")
            return render_template("index.html", error="No file selected.")

        csv_file.save("C:/Users/ageu/Documents/AppProjects/dqc_app/static/uploaded.csv")
        return redirect(url_for("evaluate"))

    return render_template("index.html")

@app.route("/evaluate", methods=["GET"])
def evaluate():
    csv_filename = "C:/Users/ageu/Documents/AppProjects/dqc_app/static/uploaded.csv"
    report = evaluate_csv_file(csv_filename)
    if report is None:
        return render_template("result.html", error="Error occurred while evaluating the CSV file.")

    return render_template("result.html", report=report)

if __name__ == "__main__":
    app.run(debug=True)
