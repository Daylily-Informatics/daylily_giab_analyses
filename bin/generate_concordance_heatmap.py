import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

def plot_heatmap(csv_file="variants.csv", metric_col="Fscore"):
    # 1) Read in the CSV
    df = pd.read_csv(csv_file, sep="\t")

    # 2) Filter out rows containing '_gt50' in SNPClass
    df = df[~df['SNPClass'].str.contains('_gt50', na=False)]

    # 3) Create a pipeline identifier
    df['Pipeline'] = df['Aligner'] + "-" + df['SNVCaller']

    # 4) Iterate over each unique SNPClass
    for snp_class in df['SNPClass'].unique():
        subset_df = df[df['SNPClass'] == snp_class]

        # 5) Pivot table: Pipelines as rows, Samples as columns
        heatmap_data = subset_df.pivot_table(
            index='Pipeline',
            columns='Sample',  # Assuming 'Sample' exists in CSV
            values=metric_col,
            aggfunc='mean'
        )
        vmin = heatmap_data.min().min()

        heatmap_data = heatmap_data.fillna(0)


        # 6) Define color range emphasizing top scores

        vmax = np.percentile(heatmap_data.values, 90)  # Focus on top 0.5%
        print(f"SNPClass: {snp_class}, Min: {vmin}, Max: {vmax}")

        # 7) Use a perceptually uniform colormap with intense contrast at the top
        cmap = sns.color_palette("magma", as_cmap=True)

        # 8) Apply power scaling to emphasize top values
        norm = mcolors.PowerNorm(gamma=1.3, vmin=vmin, vmax=vmax)

        plt.figure(figsize=(12, 8))

        print(f"Max: {vmax}, Min: {vmin}")
        # 9) Draw heatmap
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt=".5f",
            cmap=cmap,
            cbar_kws={"shrink": 0.8},
            linewidths=0.5,
            norm=norm
        )

        # 10) Formatting
        plt.xticks(rotation=45, ha="right")
        plt.yticks(rotation=0)
        plt.title(f"{metric_col} by Pipeline & Sample (SNPClass: {snp_class})")

        plt.tight_layout()

        # 11) Save and show the plot
        plt.savefig(f"heatmap_{snp_class}.png", dpi=300)
        plt.show()

if __name__ == "__main__":
    plot_heatmap(sys.argv[1], metric_col="Fscore")
