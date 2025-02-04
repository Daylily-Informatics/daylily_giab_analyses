#!/usr/bin/env python3

import csv
import sys
import argparse
from collections import defaultdict, namedtuple

# Named tuple or small class to hold aggregated pipeline metrics
PipelineMetrics = namedtuple("PipelineMetrics", [
    "cpu_time",
    "wall_time",
    "cost",
    "avg_cpu_efficiency",
    "num_task_threads"
])

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process pipeline benchmark data and generate summary statistics.")
    parser.add_argument("-b", "--benchmarks", required=True,
                        help="Path to aggregated_task_benchmark_metrics.csv")
    parser.add_argument("-c","--concordance", required=True,
                        help="Path to concordance_results.tsv")
    parser.add_argument("-a", "--alignstats", required=True,
                        help="Path to alignstats.tsv (contains YieldBases, coverage info, etc.)")
    parser.add_argument("-o","--output", required=True,
                        help="Path to output TSV file")
    return parser.parse_args()

def load_alignstats(alignstats_file):
    """
    Load alignstats info keyed by (sample, aligner).

    Expected columns in alignstats_file (TSV-delimited) might include:
      sample, aligner, YieldBases, WgsCoverageMedian, WgsCoverageMean, ...
    Adjust to match your actual column names if different.
    """
    alignstats_data = {}
    with open(alignstats_file, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            sample = "_".join(row["sample"].split('_')[:-1])
            # Construct a key that matches how we combine "sample" and "aligner" in the pipeline sums
            key = (sample, row["aligner"])
        
            # Pull out numeric values safely. You may need to handle missing values or convert them.
            yield_bases = float(row.get("YieldBases", 0.0))
            coverage_median = float(row.get("WgsCoverageMedian", 0.0))
            coverage_mean = float(row.get("WgsCoverageMean", 0.0))
            
            alignstats_data[key] = {
                "YieldBases": yield_bases,
                "WgsCoverageMedian": coverage_median,
                "WgsCoverageMean": coverage_mean
            }
    return alignstats_data

def main(benchmarks_csv, concord_file, alignstats_file, output_file):
    # ----------------------------------------------------------------
    # 1. Read alignstats data (for yield and coverage)
    # ----------------------------------------------------------------
    alignstats_data = load_alignstats(alignstats_file)

    # ----------------------------------------------------------------
    # 2. Read aggregated_task_benchmark_metrics.csv
    #    Aggregate by (sample, aligner, var_caller).
    # ----------------------------------------------------------------
    pipeline_sums = defaultdict(lambda: PipelineMetrics(0.0, 0.0, 0.0, 0.0, 0))

    with open(benchmarks_csv, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sample_raw = row["sample"].split('_DBC0')[0]
            norm_rule = row["normalized_rule"]  # e.g. "bwa2a.deep.concordance" ...
            
            # Convert strings to float safely
            cpu_time  = float(row.get("Total_runtime_cpu", 0.0))
            # Some choose "Total_runtime_user" or "Total_runtime_wall" for "wall_time"
            wall_time = float(row.get("Total_runtime_user", 0.0))
            cost      = float(row.get("Total_cost", 0.0))
            eff       = float(row.get("Avg_cpu_efficiency", 0.0))
            

            # If there's no explicit num_task_threads column, either fix to 1 or parse from rule names
            num_threads = float(row.get("Total_snake_threads", 1.0))

            # A naive way to parse aligner/var_caller from the rule
            parts = norm_rule.split(".")
            if len(parts) < 2:
                aligner = parts[0]
                var_caller = "unknown"
            else:
                aligner = parts[0]
                var_caller = parts[1]

            # canonical key: (sample, aligner, var_caller)
            key = (sample_raw, aligner, var_caller)

            old = pipeline_sums[key]
            new_cpu_time  = old.cpu_time  + cpu_time
            new_wall_time = old.wall_time + wall_time
            new_cost      = old.cost      + cost

            # Weighted average of CPU efficiency
            total_prev_cpu = old.cpu_time
            combined_cpu   = total_prev_cpu + cpu_time
            if combined_cpu > 0:
                weighted_eff = (
                    old.avg_cpu_efficiency * total_prev_cpu + eff * cpu_time
                ) / combined_cpu
            else:
                weighted_eff = eff

            # Use max threads or sum them. We'll just do max for demonstration:
            new_threads = max(old.num_task_threads, num_threads)

            pipeline_sums[key] = PipelineMetrics(
                cpu_time=new_cpu_time,
                wall_time=new_wall_time,
                cost=new_cost,
                avg_cpu_efficiency=weighted_eff,
                num_task_threads=new_threads
            )

    # ----------------------------------------------------------------
    # 3. Read concordance_results.tsv to get F-scores, etc.
    # ----------------------------------------------------------------
    ConcordMetrics = namedtuple("ConcordMetrics", ["fscore","TP","FP","FN"])

    def safe_float(x):
        try:
            return float(x)
        except:
            return 0.0

    concord_data = defaultdict(lambda: dict())  # e.g. concord_data[(sample, aligner, varcaller)][SNPts] -> Fscore

    with open(concord_file, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            snp_class  = row["SNPClass"]   # e.g. SNPts, SNPtv, ...
            # We'll parse the sample similarly:
            sample_name = row["Sample"].split("_DBC0")[0]
            aligner = row.get("Aligner", "NA")
            varcaller = row.get("SNVCaller", "NA")
            fscore_val = safe_float(row.get("Fscore", 0.0))

            # store it:
            key = (sample_name, aligner, varcaller)
            concord_data[key][snp_class] = fscore_val

    # Optionally compute "SNPall" if you have separate SNPts, SNPtv
    for key, class_dict in concord_data.items():
        s_ts = class_dict.get("SNPts", 0.0)
        s_tv = class_dict.get("SNPtv", 0.0)
        if s_ts > 0 and s_tv > 0:
            class_dict["SNPall"] = (s_ts + s_tv) / 2.0
        else:
            class_dict["SNPall"] = max(s_ts, s_tv)

    # ----------------------------------------------------------------
    # 4. Merge all data into a final table
    # ----------------------------------------------------------------
    out_fields = [
        "Sample",
        "aligner",
        "var_caller",
        "cpu_time",
        "wall_time",
        "compute_efficiency",
        "num_task_threads",
        "cost_per_task",
        "per_vcpu_seconds",
        "theoretical_min_cost_per_task",
        "Fscore(all)",
        "Fscore(SNPts)",
        "Fscore(SNPtv)",
        "Fscore(SNPall)",
        "Fscore(INS50)",
        "Fscore(Del50)",
        "Fscore(Indel50)",
        "YieldBases",
        "WgsCoverageMedian",
        "WgsCoverageMean",
        "cost_per_vcpu_sec",
        "cost_per_vcpu_sec_gb"
    ]

    with open(output_file, "w", newline="") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=out_fields, delimiter="\t")
        writer.writeheader()

        for (sample, aligner, varcaller), pm in pipeline_sums.items():
            cpu_time = pm.cpu_time
            wall_time = pm.wall_time
            eff = pm.avg_cpu_efficiency
            cost_per_task = pm.cost
            threads = pm.num_task_threads

            # Some derived fields
            per_vcpu_sec = cpu_time / threads if threads > 0 else cpu_time
            if eff > 0:
                theoretical_min = cost_per_task * (1.0 / eff)
            else:
                theoretical_min = cost_per_task

            # Concordance data
            cdata = concord_data.get((sample, aligner, varcaller), {})
            f_all    = cdata.get("All", 0.0)
            f_snp_ts = cdata.get("SNPts", 0.0)
            f_snp_tv = cdata.get("SNPtv", 0.0)
            f_snpall = cdata.get("SNPall", 0.0)
            f_ins50  = cdata.get("INS_50", 0.0)
            f_del50  = cdata.get("DEL_50", 0.0)
            f_ind50  = cdata.get("Indel_50", 0.0)

            # Alignstats data (YieldBases, coverage, etc.)
            #from IPython import embed; embed()
            
            arow = alignstats_data.get((sample, aligner), {})
            yield_bases = arow.get("YieldBases", 0.0)
            wgs_cov_median = arow.get("WgsCoverageMedian", 0.0)
            wgs_cov_mean = arow.get("WgsCoverageMean", 0.0)

            # If we want to do cost-per-GB calculations using the `YieldBases` from alignstats:
            #sample_gb = yield_bases / 1e9
            denom =  per_vcpu_sec
            if denom > 0.0:
                per_cpv = cost_per_task / denom / threads
            else:
                per_cpv = 0.0

            out_row = {
                "Sample": sample,
                "aligner": aligner,
                "var_caller": varcaller,
                "cpu_time": f"{cpu_time:.2f}",
                "wall_time": f"{wall_time:.2f}",
                "compute_efficiency": f"{eff:.3f}",
                "num_task_threads": str(threads),
                "cost_per_task": f"{cost_per_task:.6f}",
                "per_vcpu_seconds": f"{per_vcpu_sec:.2f}",
                "theoretical_min_cost_per_task": f"{theoretical_min:.6f}",
                "Fscore(all)": f"{f_all:.6f}",
                "Fscore(SNPts)": f"{f_snp_ts:.6f}",
                "Fscore(SNPtv)": f"{f_snp_tv:.6f}",
                "Fscore(SNPall)": f"{f_snpall:.6f}",
                "Fscore(INS50)": f"{f_ins50:.6f}",
                "Fscore(Del50)": f"{f_del50:.6f}",
                "Fscore(Indel50)": f"{f_ind50:.6f}",

                "YieldBases": f"{yield_bases:.0f}",
                "WgsCoverageMedian": f"{wgs_cov_median:.2f}",
                "WgsCoverageMean": f"{wgs_cov_mean:.2f}",

                "cost_per_vcpu_sec": f"{per_cpv:.10f}",
                
                "cost_per_vcpu_sec_gb": f"{per_cpv / (yield_bases/1000000000.0):.20f}"  if yield_bases > 0.0 else -0.1
            }
            writer.writerow(out_row)

if __name__ == "__main__":
    args = parse_arguments()
    main(args.benchmarks, args.concordance, args.alignstats, args.output)
