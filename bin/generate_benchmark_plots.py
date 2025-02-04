import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description="Process Snakemake benchmark data and generate plots")
parser.add_argument("data_file", type=str, help="Path to the benchmark data file")
parser.add_argument("genome_build", type=str, help="Genome build identifier for output files")
parser.add_argument("identifier", type=str, help="Human-readable identifier for output file names")
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
#df["theoretical_min_cost"] = df["task_cost"] * (1-df["cpu_efficiency"])



# Extract HG00# sample identifier
df["HG_sample"] = df["sample"].str.extract(r'(HG\d+)')

# Normalize task names for sharded tasks
def normalize_task_name(task_name):
    match = re.match(r"([^.]+\.[^.]+)\.\d+", task_name)
    return match.group(1) if match else task_name

df["normalized_rule"] = df["rule"].apply(normalize_task_name)

# Aggregate metrics for each sample and normalized rule
aggregated_df = df.groupby(["sample", "normalized_rule"]).agg(
    Total_runtime_user=("s", "sum"),
    Total_runtime_cpu=("cpu_time", lambda x: (x * df.loc[x.index, "snakemake_threads"]).sum()),  # Multiply before summing
    Total_cost=("task_cost", "sum"),
    Total_snake_threads=("snakemake_threads", "sum"),
    Avg_cpu_efficiency=("cpu_efficiency", "mean"),
    Avg_task_cost=("task_cost", "mean")
).reset_index()

# Compute Runtime_cpu_per_vcpu
aggregated_df["Runtime_cpu_per_vcpu"] = aggregated_df["Total_runtime_cpu"] / aggregated_df["Total_snake_threads"]

# Generate raw pre-aggregated boxplots with overlayed dots
plt.figure(figsize=(12, max(8, len(df["rule"].unique()) * 0.3)))
sns.boxplot(x="task_cost", y="rule", data=df, palette="pastel")
sns.stripplot(x="task_cost", y="rule", data=df, hue="HG_sample", dodge=True, jitter=True, size=4, alpha=0.7)
plt.xlabel("Task Cost ($)", fontsize=12)
plt.ylabel("Rule", fontsize=12)
plt.title("Task Cost Across Raw Rules", fontsize=14)
plt.legend(title="Sample", loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=5, frameon=False, fontsize=10)
plt.tight_layout()
plt.savefig(f"{args.identifier}_{args.genome_build}_raw_task_cost.png", dpi=300, bbox_inches='tight')
plt.close()

# Generate aggregated boxplots with overlayed dots
plt.figure(figsize=(12, max(8, len(aggregated_df["normalized_rule"].unique()) * 0.3)))
sns.boxplot(x="Total_cost", y="normalized_rule", data=aggregated_df, palette="pastel")
sns.stripplot(x="Total_cost", y="normalized_rule", data=aggregated_df, hue="sample", dodge=True, jitter=True, size=4, alpha=0.7)
plt.xlabel("Total Task Cost ($)", fontsize=12)
plt.ylabel("Aggregated Rule", fontsize=12)
plt.title("Total Task Cost Across Aggregated Rules", fontsize=14)
plt.legend(title="Sample", loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=5, frameon=False, fontsize=10)
plt.tight_layout()
plt.savefig(f"{args.identifier}_{args.genome_build}_aggregated_task_cost.png", dpi=300, bbox_inches='tight')
plt.close()



# Save aggregated metrics
aggregated_df.to_csv(f"{args.identifier}_{args.genome_build}_aggregated_task_metrics.csv", index=False)

# Save task cost data
df[["sample", "rule", "task_cost", "HG_sample"]].to_csv(f"{args.identifier}_{args.genome_build}_task_costs.csv", index=False)
