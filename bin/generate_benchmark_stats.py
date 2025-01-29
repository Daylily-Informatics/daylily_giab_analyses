import pandas as pd
import matplotlib.pyplot as plt
import re
import ace_tools as tools
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description="Process Snakemake benchmark data")
parser.add_argument("data_file", type=str, help="Path to the benchmark data file")
parser.add_argument("genome_build", type=str, help="Genome build identifier for output files")
args = parser.parse_args()

# Load the Snakemake benchmark data
df = pd.read_csv(args.data_file, sep="\t")

# Convert relevant columns to numeric where necessary
df["s"] = pd.to_numeric(df["s"], errors="coerce")
df["cpu_time"] = pd.to_numeric(df["cpu_time"], errors="coerce")
df["cpu_efficiency"] = pd.to_numeric(df["cpu_efficiency"], errors="coerce")
df["spot_cost"] = pd.to_numeric(df["spot_cost"], errors="coerce")
df["snakemake_threads"] = pd.to_numeric(df["snakemake_threads"], errors="coerce")
df["nproc"] = pd.to_numeric(df["nproc"], errors="coerce")
df["task_cost"] = pd.to_numeric(df["task_cost"], errors="coerce")

# Calculate theoretical minimum CPU time
df["Theoretical_min_cpu_time"] = df["cpu_time"] / df["cpu_efficiency"]
df["Theoretical_min_cpu_time"].replace([float('inf'), -float('inf')], None, inplace=True)

# Calculate theoretical minimum task cost at the spot bid price
df["Theoretical_min_task_cost_at_spot_bid_price"] = (df["Theoretical_min_cpu_time"] * df["spot_cost"]) / 3600

# Calculate corrected task cost
df["corrected_task_cost"] = df["task_cost"] * (df["snakemake_threads"] / df["nproc"])

# Summarize per sample
summary_df = df.groupby("sample").agg(
    Total_runtime_user=("s", "sum"),
    Total_runtime_cpu=("cpu_time", "sum"),
    Total_cost=("corrected_task_cost", "sum")
).reset_index()
tools.display_dataframe_to_user(name="Sample Summary Metrics", dataframe=summary_df)

# Normalize task names for sharded tasks
def normalize_task_name(task_name):
    match = re.match(r"([^.]+\.[^.]+)\.\d+", task_name)
    return match.group(1) if match else task_name

df["normalized_rule"] = df["rule"].apply(normalize_task_name)

# Aggregate metrics for each sample and normalized rule
aggregated_df = df.groupby(["sample", "normalized_rule"]).agg(
    Total_runtime_user=("s", "sum"),
    Total_runtime_cpu=("cpu_time", "sum"),
    Total_cost=("corrected_task_cost", "sum"),
    Avg_cpu_efficiency=("cpu_efficiency", "mean"),
    Avg_task_cost=("corrected_task_cost", "mean"),
    Theoretical_min_task_cost=("Theoretical_min_task_cost_at_spot_bid_price", "sum")
).reset_index()
tools.display_dataframe_to_user(name="Aggregated Sharded Task Metrics", dataframe=aggregated_df)

# Function to generate improved boxplots and save as PDF
def plot_boxplot(data, column, title, xlabel, ylabel, filename, height_factor=0.3):
    fig, ax = plt.subplots(figsize=(12, max(8, len(data["normalized_rule"].unique()) * height_factor)))
    data.boxplot(column=column, by="normalized_rule", vert=False, patch_artist=True, ax=ax)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.set_yticks(range(len(data["normalized_rule"].unique())))
    ax.set_yticklabels(sorted(data["normalized_rule"].unique()), fontsize=8)
    plt.subplots_adjust(left=0.4)
    plt.suptitle("")
    plt.savefig(f"{args.genome_build}_{filename}.pdf")
    plt.close()

# Generate plots and save them
plot_boxplot(df, "cpu_efficiency", "CPU Efficiency Across Tasks", "CPU Efficiency", "Task (Rule)", "cpu_efficiency")
plot_boxplot(df, "corrected_task_cost", "Corrected Task Cost Across Samples", "Corrected Task Cost ($)", "Task (Rule)", "corrected_task_cost")

# Scatter plot for corrected vs theoretical cost
plt.figure(figsize=(8, 6))
plt.scatter(df["Theoretical_min_task_cost_at_spot_bid_price"], df["corrected_task_cost"], alpha=0.5)
plt.plot([df["corrected_task_cost"].min(), df["corrected_task_cost"].max()], 
         [df["corrected_task_cost"].min(), df["corrected_task_cost"].max()], 'r--')
plt.xlabel("Theoretical Minimum Task Cost ($)", fontsize=12)
plt.ylabel("Corrected Task Cost ($)", fontsize=12)
plt.title("Corrected Actual vs Theoretical Minimum Task Cost", fontsize=14)
plt.grid(True)
plt.savefig(f"{args.genome_build}_cost_comparison.pdf")
plt.close()

tools.display_dataframe_to_user(name="Corrected Task Costs", dataframe=df[["sample", "normalized_rule", "task_cost", "corrected_task_cost"]])
