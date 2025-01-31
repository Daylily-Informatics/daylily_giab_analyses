import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(concordance_path, benchmarks_path, sample_info_path):
    concordance_df = pd.read_csv(concordance_path, sep="\t")
    benchmarks_df = pd.read_csv(benchmarks_path, sep="\t")
    sample_info_df = pd.read_csv(sample_info_path)
    return concordance_df, benchmarks_df, sample_info_df

def process_data(concordance_df, benchmarks_df, sample_info_df):
    concordance_df.rename(columns={"AltId": "SampleID", "Fscore": "Fscore_All",
                                   "Aligner": "aligner", "SNVCaller": "snv_caller",
                                   "Fscore SNPts": "Fscore_SNPts", "Fscore SNPtv": "Fscore_SNPtv"}, inplace=True)
    
    align_tasks = benchmarks_df[benchmarks_df['rule'].str.contains('align', case=False)]
    snv_tasks = benchmarks_df[benchmarks_df['rule'].str.contains('snv|var|call', case=False)]
    
    print("Available columns in benchmarks_df:", benchmarks_df.columns)
    print("Available columns in align_time:", align_tasks.columns)
    print("Available columns in snv_time:", snv_tasks.columns)
    
    align_time = align_tasks.groupby("sample").agg({"cpu_time": "sum", "h:m:s": "sum", "task_cost": "sum"}).reset_index()
    snv_time = snv_tasks.groupby("sample").agg({"cpu_time": "sum", "h:m:s": "sum", "task_cost": "sum"}).reset_index()
    
    align_time.rename(columns={"task_cost": "task_cost_align"}, inplace=True)
    snv_time.rename(columns={"task_cost": "task_cost_snv"}, inplace=True)
    
    sample_info_df.rename(columns={"Sample": "SampleID"}, inplace=True)
    sample_info_df["SampleID"] = sample_info_df["SampleID"].astype(str)
    
    summary_df = concordance_df.merge(align_time, left_on="SampleID", right_on="sample", how="left", suffixes=("", "_align"))
    summary_df = summary_df.merge(snv_time, left_on="SampleID", right_on="sample", how="left", suffixes=("", "_snv"))
    summary_df = summary_df.merge(sample_info_df, on="SampleID", how="left")
    
    print("Final merged dataframe columns:", summary_df.columns)
    
    summary_df["cost_per_vcpu_GB_align"] = summary_df["task_cost_align"] / summary_df["InputFastqGB"]
    summary_df["cost_per_vcpu_GB_snv"] = summary_df["task_cost_snv"] / summary_df["InputFastqGB"]
    
    summary_df = summary_df[["SampleID", "aligner", "snv_caller", "cpu_time_align", "cpu_time_snv",
                             "h:m:s_align", "h:m:s_snv", "Fscore_All", "Fscore_SNPts", "Fscore_SNPtv",
                             "task_cost_align", "task_cost_snv", "cost_per_vcpu_GB_align", "cost_per_vcpu_GB_snv"]]
    return summary_df

def generate_plots(summary_df):
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=summary_df, x="aligner", y="Fscore_All")
    plt.title("F-score Distribution by Aligner")
    plt.xticks(rotation=45)
    plt.show()
    
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=summary_df, x="snv_caller", y="Fscore_All")
    plt.title("F-score Distribution by SNV Caller")
    plt.xticks(rotation=45)
    plt.show()
    
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=summary_df, x="cpu_time_align", y="Fscore_All", hue="aligner")
    plt.title("CPU Time to Align vs. F-score")
    plt.show()
    
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=summary_df, x="cpu_time_snv", y="Fscore_All", hue="snv_caller")
    plt.title("CPU Time to SNV Call vs. F-score")
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Analyze WGS Concordance and Benchmark Data")
    parser.add_argument("concordance_path", help="Path to concordance data file")
    parser.add_argument("benchmarks_path", help="Path to benchmarks file")
    parser.add_argument("sample_info_path", help="Path to sample info file")
    args = parser.parse_args()
    
    concordance_df, benchmarks_df, sample_info_df = load_data(args.concordance_path, args.benchmarks_path, args.sample_info_path)
    summary_df = process_data(concordance_df, benchmarks_df, sample_info_df)
    print(summary_df.to_string(index=False))
    generate_plots(summary_df)

if __name__ == "__main__":
    main()