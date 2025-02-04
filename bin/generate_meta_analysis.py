#!/usr/bin/env python3

import csv
import sys
import argparse
from collections import defaultdict, namedtuple

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Named tuple to hold aggregated pipeline metrics
PipelineMetrics = namedtuple("PipelineMetrics", [
    "cpu_time",
    "wall_time",
    "cost",
    "avg_cpu_efficiency",
    "num_task_threads"
])

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Process pipeline data, filter out dirsetupunknown, produce summary TSV and two boxplots."
    )
    parser.add_argument("-b", "--benchmarks", required=True,
                        help="Path to aggregated_task_benchmark_metrics.csv")
    parser.add_argument("-c", "--concordance", required=True,
                        help="Path to concordance_results.tsv")
    parser.add_argument("-a", "--alignstats", required=True,
                        help="Path to alignstats.tsv (contains YieldBases, coverage, etc.)")
    parser.add_argument("-o", "--output", required=True,
                        help="Path to output TSV file (plots will be saved alongside)")
    return parser.parse_args()

def load_alignstats(alignstats_file):
    """
    Load alignstats info keyed by (sample, aligner).
    """
    alignstats_data = {}
    with open(alignstats_file, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            # Example: derive sample name by removing the last '_' part
            sample = "_".join(row["sample"].split('_')[:-1])
            aligner = row["aligner"]
            key = (sample, aligner)

            yield_bases = float(row.get("YieldBases", 0.0))
            coverage_median = float(row.get("WgsCoverageMedian", 0.0))
            coverage_mean = float(row.get("WgsCoverageMean", 0.0))
            
            alignstats_data[key] = {
                "YieldBases": yield_bases,
                "WgsCoverageMedian": coverage_median,
                "WgsCoverageMean": coverage_mean
            }
    return alignstats_data

def safe_float(x):
    """Convert x to float, or 0.0 on failure."""
    try:
        return float(x)
    except:
        return 0.0

def load_data(benchmarks_csv, concord_file, alignstats_file):
    """
    1) Parse benchmark CSV, aggregating by (sample, aligner, var_caller).
    2) Parse concordance TSV, store f-scores in dict keyed by (sample, aligner, var_caller).
    3) Parse alignstats, store coverage data in dict keyed by (sample, aligner).
    4) Combine everything into a single list of rows (dicts) suitable for a DataFrame,
       skipping rows where aligner/var_caller is 'dirsetupunknown'.
    """
    # --------------------------------------
    # Load alignstats
    # --------------------------------------
    alignstats_data = load_alignstats(alignstats_file)

    # --------------------------------------
    # Aggregate tasks from benchmarks
    # --------------------------------------
    pipeline_sums = defaultdict(lambda: PipelineMetrics(0, 0, 0, 0, 0))
    with open(benchmarks_csv, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sample_raw = row["sample"].split('_DBC0')[0]
            norm_rule = row["normalized_rule"]

            cpu_time  = safe_float(row.get("Total_runtime_cpu", 0.0))
            # pick your "wall_time" column
            wall_time = safe_float(row.get("Total_runtime_user", 0.0))
            cost      = safe_float(row.get("Total_cost", 0.0))
            eff       = safe_float(row.get("Avg_cpu_efficiency", 0.0))
            num_threads = safe_float(row.get("Total_snake_threads", 1.0))

            parts = norm_rule.split(".")
            if len(parts) < 2:
                aligner = parts[0]
                var_caller = "unknown"
            else:
                aligner = parts[0]
                var_caller = parts[1]

            # -------- Skip if aligner or var_caller is 'dirsetupunknown' --------
            if aligner == "dirsetupunknown" or var_caller == "dirsetupunknown":
                continue

            key = (sample_raw, aligner, var_caller)
            old = pipeline_sums[key]

            new_cpu = old.cpu_time + cpu_time
            new_wall = old.wall_time + wall_time
            new_cost = old.cost + cost

            # Weighted avg of CPU efficiency
            total_prev_cpu = old.cpu_time
            combined_cpu = total_prev_cpu + cpu_time
            if combined_cpu > 0:
                weighted_eff = (
                    old.avg_cpu_efficiency * total_prev_cpu + eff * cpu_time
                ) / combined_cpu
            else:
                weighted_eff = eff

            # We'll just keep the max threads encountered
            new_threads = max(old.num_task_threads, num_threads)

            pipeline_sums[key] = PipelineMetrics(
                cpu_time=new_cpu,
                wall_time=new_wall,
                cost=new_cost,
                avg_cpu_efficiency=weighted_eff,
                num_task_threads=new_threads
            )

    # --------------------------------------
    # Load concordance
    # --------------------------------------
    concord_data = defaultdict(dict)
    with open(concord_file, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            snp_class = row["SNPClass"]  # e.g. SNPts, SNPtv, ...
            sample_name = row["Sample"].split("_DBC0")[0]
            aligner = row.get("Aligner", "NA")
            varcaller = row.get("SNVCaller", "NA")
            fscore_val = safe_float(row.get("Fscore", 0.0))

            # -------- Skip if aligner or var_caller is 'dirsetupunknown' --------
            if aligner == "dirsetupunknown" or varcaller == "dirsetupunknown":
                continue

            key = (sample_name, aligner, varcaller)
            concord_data[key][snp_class] = fscore_val

    # Optionally compute "SNPall" if you have separate SNPts and SNPtv
    for k, class_dict in concord_data.items():
        s_ts = class_dict.get("SNPts", 0.0)
        s_tv = class_dict.get("SNPtv", 0.0)
        if s_ts > 0 and s_tv > 0:
            class_dict["SNPall"] = (s_ts + s_tv) / 2.0
        else:
            class_dict["SNPall"] = max(s_ts, s_tv)

    # --------------------------------------
    # Create final list of row dicts
    # --------------------------------------
    final_rows = []
    for (sample, aligner, varcaller), pm in pipeline_sums.items():
        cpu_time = pm.cpu_time
        wall_time = pm.wall_time
        eff = pm.avg_cpu_efficiency
        cost_per_task = pm.cost
        threads = pm.num_task_threads

        per_vcpu_sec = cpu_time / threads if threads > 0 else cpu_time
        if eff > 0:
            theoretical_min_cost = cost_per_task / eff
        else:
            theoretical_min_cost = cost_per_task

        cdata = concord_data.get((sample, aligner, varcaller), {})
        f_all    = cdata.get("All", 0.0)
        f_snp_ts = cdata.get("SNPts", 0.0)
        f_snp_tv = cdata.get("SNPtv", 0.0)
        f_snpall = cdata.get("SNPall", 0.0)
        f_ins50  = cdata.get("INS_50", 0.0)
        f_del50  = cdata.get("DEL_50", 0.0)
        f_ind50  = cdata.get("Indel_50", 0.0)

        # Alignstats
        alignrow = alignstats_data.get((sample, aligner), {})
        yield_bases = alignrow.get("YieldBases", 0.0)
        wgs_cov_median = alignrow.get("WgsCoverageMedian", 0.0)
        wgs_cov_mean = alignrow.get("WgsCoverageMean", 0.0)

        # cost_per_vcpu_sec
        if per_vcpu_sec > 0:
            cost_per_vcpu_sec = cost_per_task / per_vcpu_sec / threads
        else:
            cost_per_vcpu_sec = 0.0

        # cost_per_vcpu_sec_gb
        if yield_bases > 0:
            cost_per_vcpu_sec_gb = cost_per_vcpu_sec / (yield_bases / 1e9)
        else:
            cost_per_vcpu_sec_gb = 0.0

        rowdict = {
            "Sample": sample,
            "aligner": aligner,
            "var_caller": varcaller,
            "cpu_time": cpu_time,
            "wall_time": wall_time,
            "compute_efficiency": eff,
            "num_task_threads": threads,
            "cost_per_task": cost_per_task,
            "per_vcpu_seconds": per_vcpu_sec,
            "theoretical_min_cost_per_task": theoretical_min_cost,
            "Fscore(all)": f_all,
            "Fscore(SNPts)": f_snp_ts,
            "Fscore(SNPtv)": f_snp_tv,
            "Fscore(SNPall)": f_snpall,
            "Fscore(INS50)": f_ins50,
            "Fscore(Del50)": f_del50,
            "Fscore(Indel50)": f_ind50,
            "YieldBases": yield_bases,
            "WgsCoverageMedian": wgs_cov_median,
            "WgsCoverageMean": wgs_cov_mean,
            "cost_per_vcpu_sec": cost_per_vcpu_sec,
            "cost_per_vcpu_sec_gb": cost_per_vcpu_sec_gb
        }
        final_rows.append(rowdict)

    return final_rows

def write_tsv(rows, output_file):
    """
    Write list of row-dicts to a TSV file, with a consistent field order.
    """
    fields = [
        "Sample", "aligner", "var_caller",
        "cpu_time", "wall_time", "compute_efficiency", "num_task_threads",
        "cost_per_task", "per_vcpu_seconds", "theoretical_min_cost_per_task",
        "Fscore(all)", "Fscore(SNPts)", "Fscore(SNPtv)", "Fscore(SNPall)",
        "Fscore(INS50)", "Fscore(Del50)", "Fscore(Indel50)",
        "YieldBases", "WgsCoverageMedian", "WgsCoverageMean",
        "cost_per_vcpu_sec", "cost_per_vcpu_sec_gb"
    ]
    with open(output_file, "w", newline="") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for row in rows:
            # Convert to string or format as needed
            writer.writerow({fn: row[fn] for fn in fields})

def plot_boxplot_by_pipeline(df, metric, output_tsv):
    """
    Create a boxplot + stripplot of <metric> vs. pipeline.
    Saves to a PNG named like "<output_tsv>_boxplot_<metric>.png".
    """
    df['pipeline'] = df['aligner'] + "-" + df['var_caller']

    # Plot
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='pipeline', y=metric, data=df, showfliers=False)
    sns.stripplot(x='pipeline', y=metric, data=df, hue='Sample',
                  dodge=True, jitter=True, alpha=0.7, size=2)
    plt.xticks(rotation=45, ha='right')
    plt.title(f"{metric} by Pipeline")
    plt.tight_layout()

    out_png = output_tsv.replace(".tsv", f"_boxplot_{metric}.png")
    plt.savefig(out_png)
    plt.close()
    print(f"Saved boxplot: {out_png}")

def main():
    args = parse_arguments()

    # 1) Load and filter data
    rows = load_data(args.benchmarks, args.concordance, args.alignstats)

    # 2) Write final TSV
    write_tsv(rows, args.output)

    # 3) Make DataFrame for plotting
    df = pd.DataFrame(rows)

    # 4) Produce two boxplots
    plot_boxplot_by_pipeline(df, "cost_per_vcpu_sec", args.output)
    plot_boxplot_by_pipeline(df, "cost_per_vcpu_sec_gb", args.output)

if __name__ == "__main__":
    main()
