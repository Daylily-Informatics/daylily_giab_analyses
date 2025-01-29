import pandas as pd
import matplotlib.pyplot as plt
import re
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
df["Theoretical_min_cpu_time"] = df["Theoretical_min_cpu_time"].replace([float('inf'), -float('inf')], None)

# Generate raw pre-aggregated boxplots
fig, ax = plt.subplots(figsize=(12, max(8, len(df["rule"].unique()) * 0.3)))
df.boxplot(column="task_cost", by="rule", vert=False, patch_artist=True, ax=ax)
ax.set_xlabel("Task Cost ($)", fontsize=12)
ax.set_ylabel("Rule", fontsize=12)
ax.set_title("Task Cost Across Raw Rules", fontsize=14)
plt.subplots_adjust(left=0.4)
plt.suptitle("")
plt.savefig(f"{args.genome_build}_raw_task_cost.pdf")
plt.close()

# Normalize task names for sharded tasks
def normalize_task_name(task_name):
    match = re.match(r"([^.]+\.[^.]+)\.\d+", task_name)
    return match.group(1) if match else task_name

df["normalized_rule"] = df["rule"].apply(normalize_task_name)

# Aggregate metrics for each sample and normalized rule
aggregated_df = df.groupby(["sample", "normalized_rule"]).agg(
    Total_runtime_user=("s", "sum"),
    Total_runtime_cpu=("cpu_time", "sum"),
    Total_cost=("task_cost", "sum"),
    Avg_cpu_efficiency=("cpu_efficiency", "mean"),
    Avg_task_cost=("task_cost", "mean")
).reset_index()

# Generate aggregated boxplots
fig, ax = plt.subplots(figsize=(12, max(8, len(aggregated_df["normalized_rule"].unique()) * 0.3)))
aggregated_df.boxplot(column="Total_cost", by="normalized_rule", vert=False, patch_artist=True, ax=ax)
ax.set_xlabel("Total Task Cost ($)", fontsize=12)
ax.set_ylabel("Aggregated Rule", fontsize=12)
ax.set_title("Total Task Cost Across Aggregated Rules", fontsize=14)
plt.subplots_adjust(left=0.4)
plt.suptitle("")
plt.savefig(f"{args.genome_build}_aggregated_task_cost.pdf")
plt.close()

# Save aggregated metrics
aggregated_df.to_csv(f"{args.genome_build}_aggregated_task_metrics.csv", index=False)

# Save task cost data
df[["sample", "rule", "task_cost"]].to_csv(f"{args.genome_build}_task_costs.csv", index=False)
