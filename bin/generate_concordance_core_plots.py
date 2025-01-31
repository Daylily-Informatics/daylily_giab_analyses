import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Set a color-blind friendly palette globally
sns.set_theme(style="whitegrid", palette="colorblind")

# 1) Load the table into a pandas DataFrame.
#    Replace "variants.csv" with your actual file path.
df = pd.read_csv(sys.argv[1], sep="\t")

# 2) Exclude any rows where `SNPClass` contains "_gt50".
df = df[~df["SNPClass"].str.contains("_gt50")]

# 3) Create a combined "Pipeline" label for easier grouping.
df["Pipeline"] = df["Aligner"] + "-" + df["SNVCaller"]

# 4) Select the variant classes we want to include in the grouped bar plot.
subset_classes = ["SNPts", "SNPtv", "INS_50", "DEL_50", "Indel_50", "All"]
df_subset = df[df["SNPClass"].isin(subset_classes)]

# 5) Group by (Pipeline, SNPClass) to compute mean Fscore across samples
grouped = df_subset.groupby(["Pipeline", "SNPClass"])["Fscore"].mean().reset_index()

# 6) Create a bar plot of mean Fscore by pipeline for those classes
plt.figure(figsize=(10, 6))
# Using the color-blind palette set by sns.set_theme(...)
sns.barplot(data=grouped, x="Pipeline", y="Fscore", hue="SNPClass")
plt.title("Mean Fscore by Aligner+Caller Pipeline (Ignoring _gt50)")
plt.xticks(rotation=45, ha="right")
plt.ylim(0.95, 1.0)  # adjust as needed
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()

# 7) Scatter of Precision vs. Recall for "All" variants
df_scatter = df[df["SNPClass"] == "All"]

plt.figure(figsize=(6, 6))
sns.scatterplot(
    data=df_scatter,
    x="Precision",
    y="Sensitivity-Recall",
    hue="Pipeline",
    style="Pipeline",
    s=100  # adjust point size
)
plt.title("Precision vs. Recall (By Variant Type)")
plt.xlim(0.95, 1.0)  # adjust to your data if needed
plt.ylim(0.95, 1.0)
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()
