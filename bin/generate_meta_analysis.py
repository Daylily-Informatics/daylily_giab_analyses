#!/usr/bin/env python3

import csv
import sys
from collections import defaultdict, namedtuple

# Named tuple or small class to hold aggregated pipeline metrics
PipelineMetrics = namedtuple("PipelineMetrics", [
    "cpu_time",
    "wall_time",
    "cost",
    "avg_cpu_efficiency",
    "num_task_threads"
])

def main(benchmarks_csv, concord_file, sample_info_file):
    # ----------------------------------------------------------------
    # 1. Read aggregated_task_benchmark_metrics.csv
    #    We will aggregate by (sample, aligner, var_caller).
    #    You can define how you detect “aligner” vs. “var_caller” from the “normalized_rule”.
    # ----------------------------------------------------------------

    aggregated_file = benchmarks_csv #"aggregated_task_benchmark_metrics.csv"
    # Example assumption: "bwa2a.deep" => aligner="bwa2a", var_caller="deep"
    # For tasks like "bwa2a.deep.concordance" or "bwa2a.deep.merge", we want to sum them all
    # into the single job (“bwa2a.deep”).

    # We will store partial sums for each pipeline job in a dict:
    #    pipeline_sums[(sample, aligner, var_caller)] = PipelineMetrics(...)
    pipeline_sums = defaultdict(lambda: PipelineMetrics(0.0, 0.0, 0.0, 0.0, 0))

    # In many pipelines, “num_task_threads” might vary by sub-task.  You could do an average
    # or keep a maximum. For simplicity, we’ll sum up CPU times, costs, etc. and pick one
    # “representative” thread count.  Adjust as needed.
    # Example: keep track of the largest num_task_threads across sub-tasks.

    # Some guess: “Total_runtime_cpu” is CPU-seconds, “Total_runtime_user” or “wall_time” might be the “user” portion.
    # “Avg_task_cost” or “Total_cost” might be the cost for that sub-step.  Adjust logic as needed.
    
    with open(aggregated_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sample_raw = row["sample"]  # e.g. "RIH0_ANA0-HG001-19"
            norm_rule = row["normalized_rule"]  # e.g. "bwa2a.deep.concordance"
            cpu_time  = float(row["Total_runtime_cpu"] or 0.0)
            wall_time = float(row["Total_runtime_user"] or 0.0)  # or whichever you prefer
            cost      = float(row["Total_cost"] or 0.0)
            eff       = float(row["Avg_cpu_efficiency"] or 0.0)
            # we do not see explicit "num_task_threads" columns, so you might store it
            # or parse from your pipeline data. For demonstration, we'll store 1 as placeholder
            # or you can do something like a dictionary of known thread usage per rule:
            num_threads = 1  # or load from your pipeline’s logic

            # parse out aligner, var_caller from “norm_rule”
            # e.g. norm_rule = "bwa2a.deep" or "bwa2a.deep.concordance"
            # A simple way: split by '.' and take the first two segments
            # (Your pipeline might have different naming patterns, so adapt as needed.)
            parts = norm_rule.split(".")
            if len(parts) < 2:
                # e.g. "bwa2a" alone or something else
                aligner = parts[0]
                var_caller = "unknown"
            else:
                aligner = parts[0]  # "bwa2a"
                var_caller = parts[1]  # "deep", "lfq2", etc.

            # canonical key: (sample, aligner, var_caller)
            key = (sample_raw, aligner, var_caller)

            # sum everything
            old = pipeline_sums[key]
            # For "avg_cpu_efficiency", we might keep a simple average or the min, etc.
            # We'll do a weighted average based on CPU_time, or you might just take an
            # average over sub-tasks. Simplify here:
            new_cpu_time  = old.cpu_time  + cpu_time
            new_wall_time = old.wall_time + wall_time
            new_cost      = old.cost      + cost
            # Weighted “eff” or just do an average:
            # Weighted approach: old_avg_eff * old_cpu_time + eff * cpu_time / total_cpu_time
            total_prev_cpu = old.cpu_time
            combined_cpu   = total_prev_cpu + cpu_time
            if combined_cpu > 0:
                weighted_eff = (old.avg_cpu_efficiency * total_prev_cpu + eff * cpu_time) / combined_cpu
            else:
                weighted_eff = eff

            # pick max threads or sum threads or do your own logic
            new_threads = max(old.num_task_threads, num_threads)

            pipeline_sums[key] = PipelineMetrics(
                cpu_time=new_cpu_time,
                wall_time=new_wall_time,
                cost=new_cost,
                avg_cpu_efficiency=weighted_eff,
                num_task_threads=new_threads
            )

    # ----------------------------------------------------------------
    # 2. Read sample_info.csv to get #basecalls (in GB) per sample
    # ----------------------------------------------------------------

    # This file has lines like:
    # Sample,InputFastq_num_basecalls_GB
    # RIH0_ANA0-HG001-19,110,000,000,000   (or do we have commas?)
    # We must parse out the numeric portion. Possibly "110,000,000,000" means 110,000,000,000 basecalls => 110 GB?
    sample_info = {}
    
    with open(sample_info_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            s = row["Sample"]

            raw_val = row["InputFastq_num_basecalls"]
            # raw_val might then be "110000000000"
            # interpret that as basecalls in 'count of bases', i.e. 1.1e11
            # If we want “GB” as “1e9 basecalls”, then 1.1e11 basecalls is 110 “GB”.
            # So do:
            basecalls = float(raw_val)
            # convert to "GB" if 1 GB = 1e9 basecalls:
            gb = basecalls / 1e9
            sample_info[s] = gb

    # ----------------------------------------------------------------
    # 3. Read concordance_results.tsv to get F-scores
    # ----------------------------------------------------------------
    # This file has lines with columns: SNPClass, Sample, Fscore, etc.
    # The user wants Fscore(all), Fscore(SNPts), Fscore(SNPtv), Fscore(SNPall) (which merges SNPts & SNPtv),
    # Fscore(INS50), Fscore(Del50), Fscore(Indel50)
    #
    # We also see that “SNPall” is the combined TS + TV. We can compute a “macro” F-score or a “weighted” F-score
    # depending on the # of actual TS vs. TV calls.  One approach is:
    #
    #    Fscore(SNPall) = 2*TPall / (2*TPall + FPall + FNall)
    #
    # where TPall, FNall, FPall come from the sum of “SNPts” + “SNPtv” lines.  Alternatively, if you only have
    # precomputed Fscore(SNPts) and Fscore(SNPtv), you can do a call-level weighting.  Shown below as a skeleton.

    # We'll store a dictionary: concord[(sample, aligner, var_caller)][class_name] = (Fscore, #TP, #FN, #FP, etc.)
    # Then we can do the final merging.

    ConcordMetrics = namedtuple("ConcordMetrics", ["fscore","TP","FP","FN"])
    # Or store the entire row from the TSV. Adapt to your data.

    # Example function to safely parse a float:
    def safe_float(x):
        try: return float(x)
        except: return 0.0

    # We need to figure out how to parse the row’s “Sample” to get the same (sample, aligner, var_caller).
    # The file shows lines like:
    #    RIH0_ANA0-HG001-19_DBC0_0-bwa2a-deep-All
    # where “bwa2a-deep” is the chunk that identifies aligner=“bwa2a” and var caller=“deep”.
    # So we can parse that substring to match how we aggregated tasks above.

    concord_data = defaultdict(lambda: dict())  # e.g. concord_data[(sample, aligner, varcaller)][SNPts] -> Fscore
    
    with open(concord_file,"r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            # row has SNPClass, Sample, Fscore
            snp_class  = row["SNPClass"]   # e.g. SNPts, SNPtv, ...
            sample_name = row["Sample"] # e.g. "RIH0_ANA0-HG001-19_DBC0_0-bwa2a-deep-All"
            fscore_val      = safe_float(row["Fscore"]) 
            aligner = row["Aligner"]
            varcaller = row["SNVCaller"]
            # parse out sample “RIH0_ANA0-HG001-19” from that big string, and the pipeline “bwa2a-deep”.
            # typically we see something like:   RIH0_ANA0-HG001-19_DBC0_0-bwa2a-deep-SNPts
            # So we can do:
            #   1) split by '-'
            #   2) your sample is "RIH0_ANA0-HG001-19" up to the first big dash section
            #   3) the last chunk might be "bwa2a-deep-SNPts"
            # or simpler: note “_bwa2a-deep-” is in the middle?  We’ll do a quick approach:

            # if you always have "sample_bwa2a-xxx-SNPts" pattern, we can do a regex or just find the substring.
            # Here is a simplified approach:
            # find the pipeline portion:
            #    everything after the last '_' is "bwa2a-deep-SNPts" => we can then parse by splitting further.

            # for safety, you might do something more robust:
            ##splitted = full_sample_str.split("-", maxsplit=1)
            ### splitted[0] = "RIH0_ANA0-HG001-19_DBC0_0"
            ### splitted[1] = "bwa2a-deep-SNPts" ...
            ##if len(splitted)<2:
            ##    continue

            ##right_part = splitted[1]  # e.g. "bwa2a-deep-SNPts"
            # find the last dash => separate pipeline from SNPClass string?
            # or note that row["SNPClass"] is already SNPts, so the right_part might be just "bwa2a-deep"
            ##pipeline_str = right_part.rsplit("-",1)[0] # "bwa2a-deep"
            # parse pipeline_str => aligner="bwa2a", varcaller="deep"
            ##pipe_parts = pipeline_str.split("-")
            ##if len(pipe_parts)<2:
            ##    aligner = pipe_parts[0]
            ##    varcaller = "unknown"
            ##else:
            ##    aligner, varcaller = pipe_parts[0], pipe_parts[1]

            # parse the sample name from splitted[0], which might be “RIH0_ANA0-HG001-19_DBC0_0”
            # or you can just do a prefix approach if needed. Suppose the real sample is “RIH0_ANA0-HG001-19”
            # We might do something like:
            ##left_part = splitted[0]  # e.g. "RIH0_ANA0-HG001-19_DBC0_0"
            # you might have additional “_DBC0_0” etc. We can do:
            # sample_name = left_part.split("_DBC0_")[0]  => "RIH0_ANA0-HG001-19"
            ##sample_name = left_part.split("_DBC")[0]

            # store the fscore
            key = (sample_name, aligner, varcaller)

            # we can store them into a small dictionary:
            concord_data[key][snp_class] = fscore_val

    # after reading all lines, we also want to compute “SNPall” by merging “SNPts” & “SNPtv”.
    # if you have the per-class F-scores plus TPs, FPs, FNs, you can do a real combined F-score.  But if
    # you only have F-scores, you might do a weighted average by # calls.  Or skip if you do not have the
    # TPs.  Shown here as a naive approach that just averages the two if found:
    for key in concord_data:
        d = concord_data[key]
        # For example:
        snts = d.get("SNPts", 0.0)
        sntv = d.get("SNPtv", 0.0)
        # If you have TPs, do real combination.  If not, do a simple average:
        if snts>0.0 and sntv>0.0:
            # naive average
            d["SNPall"] = (snts + sntv)/2.0
        else:
            d["SNPall"] = max(snts, sntv)

    # ----------------------------------------------------------------
    # 4. Merge all data and calculate final fields
    # ----------------------------------------------------------------

    out_fields = [
        "Sample", "aligner", "var_caller",
        "cpu_time", "wall_time", "compute_efficiency",
        "num_task_threads", "cost_per_task", "per_vcpu_seconds",
        "theoretical_min_cost_per_task",
        "Fscore(all)", "Fscore(SNPts)", "Fscore(SNPtv)", "Fscore(SNPall)",
        "Fscore(INS50)", "Fscore(Del50)", "Fscore(Indel50)",
        "per_gb_cost_per_vcpu_sec"
    ]

    writer = csv.DictWriter(sys.stdout, fieldnames=out_fields)
    writer.writeheader()

    # Now iterate pipeline_sums to create the final rows
    for (sample, aligner, varcaller), pm in pipeline_sums.items():
        # some fields
        cpu_time  = pm.cpu_time
        wall_time = pm.wall_time
        eff       = pm.avg_cpu_efficiency
        cost      = pm.cost
        threads   = pm.num_task_threads

        # “cost_per_task” we might define as total cost for that pipeline => so cost.
        cost_per_task = cost

        # per_vcpu_seconds = cpu_time / threads  (from your notes ^1)
        if threads>0:
            per_vcpu_sec = cpu_time / threads
        else:
            per_vcpu_sec = cpu_time

        # “theoretical_min_cost_per_task”: placeholder formula.
        # You could refine it.  For instance:
        #   theoretical_min_cost_per_task = cost_per_task * (1/eff)
        # or cost if the job was at 100% CPU efficiency. Example:
        theoretical_min = cost_per_task * (1.0/eff) if eff>0 else cost_per_task

        # fetch the Fscores from concord_data
        # e.g. Fscore(all), Fscore(SNPts), ...
        cdata = concord_data.get((sample, aligner, varcaller), {})
        f_all    = cdata.get("All", 0.0)       # "All" in the “SNPClass” column
        f_snp_ts = cdata.get("SNPts", 0.0)
        f_snp_tv = cdata.get("SNPtv", 0.0)
        f_snpall = cdata.get("SNPall", 0.0)    # we computed above
        f_ins50  = cdata.get("INS_50", 0.0)
        f_del50  = cdata.get("DEL_50", 0.0)
        f_ind50  = cdata.get("Indel_50", 0.0)

        # “per_gb_cost_per_vcpu_sec”: you want cost / ( #GB basecalls × total_vcpu_seconds )
        # get #GB from sample_info
        sample_gb = sample_info.get(sample, 1.0)  # fallback to 1.0 if unknown
        total_vcpu_seconds = per_vcpu_sec  # or possibly just “cpu_time”?  Decide if you want to multiply by “threads” again
        # The note says “#  ^3: per_gb_cost_per_vcpu_sec: cost per number GB basecalls per vcpu sec ”
        # => cost / ( sample_gb * total_vcpu_seconds )
        denom = sample_gb * total_vcpu_seconds
        if denom>0:
            per_gb_cpv = cost_per_task / denom
        else:
            per_gb_cpv = 0.0

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
            "per_gb_cost_per_vcpu_sec": f"{per_gb_cpv:.8f}"
        }

        writer.writerow(out_row)


if __name__ == "__main__":
    benchmarks_csv=sys.argv[1]
    concordance_tsv=sys.argv[2]
    sample_info_csv=sys.argv[3]
    main(benchmarks_csv, concordance_tsv, sample_info_csv)
