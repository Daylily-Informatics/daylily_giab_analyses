import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_best_pipeline_bar(csv_file="variants.csv",
                           metric="Fscore",
                           variant_classes=None,
                           exclude_gt50=True):
    """
    Creates a barplot showing the average performance (across multiple samples)
    for each pipeline in each variant class. 
    This answers: "Which pipeline is best for each variant class?"
    
    :param csv_file: Path to the CSV file
    :param metric: The performance metric column to use (e.g. "Fscore", "Sensitivity-Recall")
    :param variant_classes: List of variant classes to keep (e.g. ["SNPts","SNPtv","INS_50","DEL_50","Indel_50","All"])
    :param exclude_gt50: Whether to exclude rows with SNPClass containing "_gt50".
    """
    # 1) Read CSV
    df = pd.read_csv(csv_file, sep="\t")

    # 2) Optionally exclude classes like *_gt50
    if exclude_gt50:
        df = df[~df['SNPClass'].str.contains('_gt50', na=False)]

    # 3) If user specified a subset of classes, filter to them
    if variant_classes:
        df = df[df['SNPClass'].isin(variant_classes)]

    # 4) Create a "Pipeline" column
    df['Pipeline'] = df['Aligner'] + "-" + df['SNVCaller']

    # 5) Group by (Pipeline, SNPClass), then average across samples
    grouped = df.groupby(["Pipeline", "SNPClass"])[metric].mean().reset_index()

    # 6) For a bar plot with x=variant class, hue=pipeline, y=avg metric:
    plt.figure(figsize=(10, 6))
    sns.barplot(data=grouped,
                x="SNPClass",
                y=metric,
                hue="Pipeline",
                palette="colorblind")  # color-blind-friendly palette

    plt.title(f"Mean {metric} by Pipeline and Variant Class (Aggregated Across Samples)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Example usage: 
    # Show "Fscore" for a few typical classes, ignoring *_gt50
    plot_best_pipeline_bar(
        csv_file=sys.argv[1],
        metric="Fscore",
        variant_classes=["SNPts", "SNPtv", "INS_50", "DEL_50", "Indel_50", "All"],
        exclude_gt50=True
    )
