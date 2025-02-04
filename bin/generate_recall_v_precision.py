import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import argparse

def plot_sensitivity_vs_precision(input_file, genome_build, annotation, output_prefix):
    # 1) Read the input TSV file
    df = pd.read_csv(input_file, sep="\t")

    # 2) Filter out rows containing '_gt50' in SNPClass (optional)
    df = df[~df['SNPClass'].str.contains('_gt50', na=False)]

    # 3) Create a pipeline identifier (Aligner-Caller)
    df['Pipeline'] = df['Aligner'] + "-" + df['SNVCaller']

    # 4) Define marker set for pipelines (enough for up to 18 pipelines)
    unique_pipelines = sorted(df["Pipeline"].unique())
    markers = ["o", "s", "D", "^", "v", "<", ">", "p", "H", "*", "X", "|", "_",
               "1", "2", "3", "4", "8"]  # 18 markers
    if len(unique_pipelines) > len(markers):
        raise ValueError(
            f"More unique pipelines ({len(unique_pipelines)}) than markers ({len(markers)}). "
            "Please expand the 'markers' list."
        )
    marker_map = {pipeline: markers[i] for i, pipeline in enumerate(unique_pipelines)}

    # 5) Define color palette for Samples
    samples = sorted(df["Sample"].unique())
    palette = sns.color_palette("husl", len(samples))
    sample_color_map = {sample: palette[i] for i, sample in enumerate(samples)}

    # Helper to add the "top pipeline" text box on the right
    def add_top_pipelines_text(ax, df_sub):
        """
        Find the pipeline with the highest Recall and highest Precision
        in df_sub, then display them + numeric values in a text box
        on the right side of ax.
        """
        if df_sub.empty:
            return

        # Highest recall
        max_rec_idx = df_sub["Sensitivity-Recall"].idxmax()
        max_rec_pipeline = df_sub.loc[max_rec_idx, "Pipeline"]
        max_rec_value = df_sub.loc[max_rec_idx, "Sensitivity-Recall"]

        # Highest precision
        max_prec_idx = df_sub["Precision"].idxmax()
        max_prec_pipeline = df_sub.loc[max_prec_idx, "Pipeline"]
        max_prec_value = df_sub.loc[max_prec_idx, "Precision"]

        txt = (
            f"Highest Recall:\n"
            f"{max_rec_pipeline} ({max_rec_value:.4f})\n\n"
            f"Highest Precision:\n"
            f"{max_prec_pipeline} ({max_prec_value:.4f})"
        )

        ax.text(
            1.02, 0.96,
            txt,
            transform=ax.transAxes,
            va='top', 
            ha='left',
            clip_on=False,
            bbox=dict(facecolor='white', alpha=0.3, edgecolor='none')
        )

    # 6) Loop over each unique SNPClass -> produce TWO scatter plots:
    #    (A) Full range
    #    (B) Zoomed in to top recall & top precision points.
    for snp_class in df["SNPClass"].unique():
        df_sub = df[df["SNPClass"] == snp_class].copy()

        # --------------------------
        # HELPER: Plot function
        # --------------------------
        def create_scatter(ax, title_suffix=""):
            """
            Draw scatter points for df_sub on ax, with legends, etc.
            Return ax so we can add text or further customization.
            """
            # Scatter each point
            for _, row in df_sub.iterrows():
                ax.scatter(
                    row["Sensitivity-Recall"],
                    row["Precision"],
                    color=sample_color_map[row["Sample"]],
                    marker=marker_map[row["Pipeline"]],
                    edgecolors="k",
                    alpha=0.75,
                    s=30  # ~40% smaller than s=50
                )

            # Legends: Pipelines (markers)
            handles_markers = [
                plt.Line2D(
                    [0], [0],
                    marker=marker_map[pipeline],
                    color='w',
                    markerfacecolor='gray',
                    markeredgecolor='k',
                    markersize=8,
                    label=pipeline
                )
                for pipeline in unique_pipelines
            ]
            legend_pipelines = ax.legend(
                handles=handles_markers,
                title="Pipeline (Aligner-VarCaller)",
                loc="lower left",
                fontsize=9,
                frameon=True
            )
            ax.add_artist(legend_pipelines)

            # Legends: Samples (colors)
            handles_samples = [
                plt.Line2D(
                    [0], [0],
                    marker='o',
                    color='w',
                    markerfacecolor=sample_color_map[sample],
                    markeredgecolor='k',
                    markersize=8,
                    label=sample
                )
                for sample in samples
            ]
            legend_samples = ax.legend(
                handles=handles_samples,
                title="Sample",
                loc="upper left",
                fontsize=9,
                frameon=True
            )
            ax.add_artist(legend_samples)

            # Labels & Title
            ax.set_xlabel("Sensitivity (Recall)", fontsize=14)
            ax.set_ylabel("Precision", fontsize=14)
            ax.set_title(
                f"Sensitivity (Recall) vs. Precision\n"
                f"{genome_build}, {annotation} — SNPClass: {snp_class}\n{title_suffix}",
                fontsize=16
            )

            return ax

        # ----------------------------
        # (A) Full-range scatter plot
        # ----------------------------
        figA, axA = plt.subplots(figsize=(10, 7))
        plt.subplots_adjust(right=0.8)

        create_scatter(axA, title_suffix="(Full Range)")
        # Add top pipelines text box
        add_top_pipelines_text(axA, df_sub)

        out_file_full = f"{output_prefix}_{snp_class}.png"
        plt.tight_layout()
        plt.savefig(out_file_full, dpi=300, bbox_inches='tight')
        print(f"Saved: {out_file_full}")
        plt.show()

        # ----------------------------------------
        # (B) Zoomed-in scatter: top recall & prec
        # ----------------------------------------
        # Identify highest recall & highest precision in df_sub
        max_recall_index = df_sub["Sensitivity-Recall"].idxmax() if not df_sub.empty else None
        max_prec_index   = df_sub["Precision"].idxmax() if not df_sub.empty else None

        if max_recall_index is not None and max_prec_index is not None:
            recall_x = df_sub.loc[max_recall_index, "Sensitivity-Recall"]
            recall_y = df_sub.loc[max_recall_index, "Precision"]
            prec_x   = df_sub.loc[max_prec_index,   "Sensitivity-Recall"]
            prec_y   = df_sub.loc[max_prec_index,   "Precision"]

            # Determine bounding rectangle for these 2 points + a small margin
            margin = 0.01
            x_min = max(0.0, min(recall_x, prec_x) - margin)
            x_max = min(1.0, max(recall_x, prec_x) + margin)
            y_min = max(0.0, min(recall_y, prec_y) - margin)
            y_max = min(1.0, max(recall_y, prec_y) + margin)

            figB, axB = plt.subplots(figsize=(10, 7))
            plt.subplots_adjust(right=0.8)

            create_scatter(axB, title_suffix="(Zoomed to top Recall & Precision)")
            axB.set_xlim(x_min, x_max)
            axB.set_ylim(y_min, y_max)
            # Add top pipelines text box
            add_top_pipelines_text(axB, df_sub)

            out_file_zoom = f"{output_prefix}_{snp_class}_zoom.png"
            plt.tight_layout()
            plt.savefig(out_file_zoom, dpi=300, bbox_inches='tight')
            print(f"Saved: {out_file_zoom}")
            plt.show()

    # -------------------------------------------------------------------------
    # Create one boxplot figure *per* SNPClass for 6 metrics:
    # (Fscore, Sensitivity-Recall, Specificity, FDR, PPV, Precision)
    # -------------------------------------------------------------------------
    metrics = [
        ("Fscore",            "F-score"),
        ("Sensitivity-Recall","Recall"),
        ("Specificity",       "Specificity"),
        ("FDR",               "FDR"),
        ("PPV",               "PPV"),
        ("Precision",         "Precision")
    ]

    unique_classes = df["SNPClass"].unique()
    for snp_class in unique_classes:
        df_class = df[df["SNPClass"] == snp_class].copy()

        # Create a figure with 6 subplots (2 rows x 3 cols).
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        axes = axes.flatten()

        for i, (col_name, label) in enumerate(metrics):
            ax = axes[i]

            # Boxplot
            sns.boxplot(
                x="Pipeline",
                y=col_name,
                data=df_class,
                color="white",
                ax=ax
            )
            # Jittered sample dots: solid, size=6
            sns.stripplot(
                x="Pipeline",
                y=col_name,
                data=df_class,
                hue="Sample",
                dodge=True,
                jitter=True,
                marker='o',
                size=3,
                alpha=1.0,
                ax=ax
            )

            # Rotate labels so the label end is right above the tick
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

            # Try setting the y-axis min to Q1 of the "bwa2a-clair3" pipeline, if it exists
            # 1) Filter data to that pipeline
            df_bwa2a = df_class[df_class["Pipeline"] == "bwa2a-clair3"]
            if not df_bwa2a.empty and col_name in df_bwa2a.columns:
                # 2) Get the 25th percentile (Q1)
                q1 = df_bwa2a[col_name].quantile(0.25)
                # 3) Set as the lower y-limit, if q1 is finite
                if pd.notnull(q1):
                    # We'll keep the upper limit automatic
                    ax.set_ylim(q1, None)

            ax.set_title(f"{label}", fontsize=14)
            ax.set_xlabel("Pipeline", fontsize=12)
            ax.set_ylabel(label, fontsize=12)

            # Legend only on the last subplot
            if i == len(metrics) - 1:
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Sample")
            else:
                ax.legend([], [], frameon=False)

        # Overall figure title
        plt.suptitle(
            f"Boxplots for SNPClass: {snp_class}\n{genome_build}, {annotation}",
            fontsize=16
        )

        plt.tight_layout(rect=[0, 0, 1, 0.95])  # leave room for suptitle
        out_file_box = f"{output_prefix}_{snp_class}_boxplots.png"
        plt.savefig(out_file_box, dpi=300, bbox_inches="tight")
        print(f"Saved: {out_file_box}")
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot Sensitivity vs. Precision for WGS pipelines; plus per-SNPClass boxplots (6 metrics)."
    )
    parser.add_argument("-i", "--input", required=True, help="Input concordance TSV file")
    parser.add_argument("-b", "--genomebuild", required=True, help="Genome build")
    parser.add_argument("-a", "--annotation", required=True, help="Annotation")
    parser.add_argument("-o", "--output", required=True,
                        help="Output file prefix. Scatter plots: prefix_SNPClass.png & prefix_SNPClass_zoom.png. Boxplots: prefix_SNPClass_boxplots.png")

    args = parser.parse_args()
    plot_sensitivity_vs_precision(args.input, args.genomebuild, args.annotation, args.output)
