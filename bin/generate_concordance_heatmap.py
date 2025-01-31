import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_heatmap(csv_file="variants.csv", metric_col="Fscore"):
    # 1) Read in the CSV
    df = pd.read_csv(csv_file, sep=",")

    # 2) Filter out the rows containing '_gt50' in SNPClass
    df = df[~df['SNPClass'].str.contains('_gt50', na=False)]

    # 3) Create a pipeline identifier: e.g. "bwa2a-clair3"
    df['Pipeline'] = df['Aligner'] + "-" + df['SNVCaller']

    # 4) Choose your metric; default: "Fscore"
    #    (Alternatively: "Sensitivity-Recall", "Precision", etc.)
    metric = metric_col

    # 5) Pivot so rows = Pipeline, columns = SNPClass, values = chosen metric
    heatmap_data = df.pivot_table(
        index='Pipeline',
        columns='SNPClass',
        values=metric,
        aggfunc='mean'  # or 'max', 'min' if relevant
    )

    # 6) Create a color-blind-friendly continuous colormap
    #    - Seaborn has "colorblind" palette, but that’s discrete; for a continuous map,
    #      we can use something from matplotlib that is color-blind friendly.
    #    - Two good continuous, color-blind-friendly cmaps are "mako" or "rocket",
    #      or you can create your own from a colorblind palette.
    cmap = sns.color_palette("mako", as_cmap=True)

    plt.figure(figsize=(10, 8))
    # 7) Draw the heatmap
    #    - `annot=True` to label each cell
    #    - `fmt=".3f"` to format float to 3 decimals
    #    - `cbar_kws={"shrink": 0.8}` to adjust color bar size
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".3f",
        cmap=cmap,
        cbar_kws={"shrink": 0.8},
        linewidths=0.5
    )

    # 8) Rotate x-ticks if needed, to make them readable
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    
    # 9) Improve layout & show
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_heatmap(sys.argv[1], metric_col="Fscore")
