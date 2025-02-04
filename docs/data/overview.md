# ALL DATA FILES

- [data](../../data)


# ALL RESULTS FILES

- [results](../../results)


# Daylily Framework Pipelines Data Sets

## How To Reproduce Data Used In The Following Analysis
- [Steps to reproduce generating the results used here](docs/creating_dataset.md).


---

## References
`daylily` relies on a [S3 bucket](https://github.com/Daylily-Informatics/daylily?tab=readme-ov-file#daylily-references-public-reference-bucket) which contains all necessary refrences, bioinformatics tool artifacts, genomic annotations, giab fastqs, etc.

---

## Data Types

### Raw Data
_available upon request, until I have these files available in a cost effective way_

- Available: all files produced by [`daylily`](https://github.com/Daylily-Informatics/daylily) (aligner BAM, snv+sv VCFs, logs, etc).


### QC Data (multiqc)
A large number of QC tools are used to offer insight into each workflow. These tools are aggregated into a final html reports with `multiqc`.

> Ephemeral cluster cost monitoring is fully integrated with `daylily`, down to the task/job level. QC reports include a header with summary info re:costs to run a given analysis (more detailed cost reporting to be integrated into multiqc).
>
> ![](docs/images/b37_mqc_cost_stats.png)

### Alignstats Data
[Alignstats](https://github.com/jfarek/alignstats) is a tool which calculates extensive (*163*!) metrics for BAM/CRAM files. 

- [hg38_us-west-2d_alignstats](data/us_west_2d/hg38_7giab_us-west-2d_alignstats.tsv)
- [b37_us-west-2d_alignstats](data/us_west_2d/b37_7giab_us-west-2d_alignstats.tsv)
- _Alignstats was not run for `eu-central-1c`, but is expected to be exactly the same as `hg38_us-west-2d` above_.


### Concordance Data (for both `hg38` and `b37`)
`daylily` automatically will caclulate concordrance metrics for each sample for which there has been a truthset `vcf` specified.

The following annotations/metrics are presented in the concordance results file:
    > - SNPClass	
    > - Sample	
    > - TgtRegionSize	
    > - TN	
    > - FN
    > - TP	
    > - FP	
    > - Fscore	
    > - Sensitivity-Recall	
    > - Specificity	
    > - FDR	
    > - PPV	
    > - Precision	

SNPClass segments stats per sample as (categories defined by `bcfstats`):
  > - All
  > - SNPts
  > - SNPtv
  > - Ins_50
  > - Ins_gt50
  > - Del_50
  > - Del_gt50
  > - Indel_50
  > - Indel_gt50

With the GIABid, aligner and snv caller annotated as well.

### Benchmark + Cost Data

Spot instance compute benchmark metrics are tracked per-task, including spot instance type details and the cost to run each task.  The benchmark summary file includes the following columns:

  > - sample	
  > - rule	
  > - s	
  > - h:m:s	
  > - max_rss	
  > - max_vms	
  > - max_uss	
  > - max_pss	
  > - io_in	
  > - io_out	
  > - mean_load	
  > - cpu_time	
  > - hostname	
  > - ip	
  > - nproc	
  > - cpu_efficiency	
  > - instance_type	
  > - region_az	
  > - spot_cost	
  > - snakemake_threads	
  > - task_cost


---

## Summary Data Available

### hg38

#### `us-west-2d`
**This region-az was chosen for expediency vs cheapest spot market cost**

> `daylily` relies almost exclusively on `192 vcpu` instances. At the time this workflow was executed, the harmonic mean of spot prices for these instances was ~$3.60/hr. I chose this AZ b/c I have a far greater spot instance quota to run in this region.

All 7 GIAB 30x google brain Illumina reads were processed via complete `daylily` WGS analysis framework. All FASTQs were mapped with 3 aligners (`sentieon bwa`, `bwa mem2` & `strobe aligner`). Each BAM was SNC called with 5 variant callers (`Sentieon DNAscope`, `deepvariant`, `octopus`, `clair3`, `lofreq2`), and SVs called with three SV callers (`manta`, `tiddit`, `dysgu`). Finally, ~ 14 QC tools were executed and each workflow run captured in a single multiqc report.


##### Concordance Data

- [hg38_us-west-2d_concordance.tsv](data/us-west-2d/hg38_7giab_us-west-2d_giab_concordance_mqc.tsv)

##### Benchmark & Cost Data

- [hg38_us-west-2d_benchmarks.tsv](data/us-west-2d/hg38_7giab_us-west-2d_benchmarks_summary.tsv)

##### QC (multiqc) Reports
_download these `html` files and open in a new browser_

- [hg38 Multiqc Report](data/us-west-2d/qc_data/hg38_us-west-2d_DAY_final_multiqc.html) _note: cost data summary is borked_



#### `eu-central-1c`
**This region-az was chosen as one of the cheapest spot markets**

To demonstrate running in a different, very cheap AZ, only `bwa mem2` and `deepvariant` were run on all 7 GIAB samples.

> The harmonic mean cost of running in this AZ was ~$1.5/hour. *note:* the lowest spot pricing I have seen is ~0.80/hr for these instance types.

##### Concordance Data

- [eu-central_concordance.tsv](data/eu_central-1c/hg38_eu-central-1c_giab_concordances.tsv)

##### Benchmark & Cost Data

- [eu-central_benchmarks.tsv]](data/eu_central-1c/hg38_eu-central-1c_benchmarks.tsv)

##### QC (multiqc) Reports
_QC tools not run for this data set_


### b37
In the interest of saving $, I only ran the winning pipelines from the `hg38` trials. Aligners (`sentieon bwa` & `bwa mem2`) & SNV callers (`sentieon DNAscope` and `deepvariant`). All QC tools were executed and a multiqc report produced.

> Spot instance costs ~$3.60/hr.

#### `us-west-2d`
**The b37 analysis was queued up in parallel with the `hg38` jobs, and all run on the same ephemeral cluster in the same region$**

- [data files here](data/us-west-2d)

##### Concordance Data

- [us-west-2d_b37_benchmarks.tsv](data/us-west-2d/b37_7giab_us-west-2c_benchmarks_summary.tsv)

##### Benchmark & Cost Data

- [us-west-2d_b37_concordance.tsv](data/us-west-2d/b37_7giab_us-west-2c_benchmarks_summary.tsv)



##### QC (multiqc) Reports
_download these `html` files and open in a new browser_

- [b37 Multiqc Report](data/us-west-2d/qc_data/b37_us-west-2d_DAY_final_multiqc.html)


# Concordance Analysis 


## Producing Plots 

[see installing CONDA env here](docs/creating_dataset.md)

```bash

conda activate DAYGIAB
mkdir -p results/{us_west_2d/{all,3x2},eu_central_1c/two}/{concordance/{boxplots,pvr,raw_metrics,heatmaps},benchmarks,meta}

# Base Concordance Metrics
Rscript bin/generate_concordance_plots.R hg38 data/us_west_2d/hg38_7giab_us-west-2d_giab_concordance_mqc.tsv usw2d-all

Rscript bin/generate_concordance_plots.R b37 data/us_west_2d/b37_7giab_us-west-2d_3x2_giab_concordance_mqc.tsv usw2d-3x2

Rscript bin/generate_concordance_plots.R hg38 data/eu_central_1c/hg38_eu-central-1c_mem2-sent-combo_giab_concordance.tsv euc1c-two


mv plot_hg38_usw2d-all_* results/us_west_2d/all/concordance/raw_metrics
mv plot_hg38_euc1c-two_* results/eu_central_1c/two/concordance/raw_metrics
mv plot_b37_usw2d-3x2_* results/us_west_2d/3x2/concordance/raw_metrics


# HEATMAPS
python bin/generate_concordance_heatmap.py data/us_west_2d/hg38_7giab_us-west-2d_giab_concordance_mqc.tsv hg38 usw2d-all
 
python bin/generate_concordance_heatmap.py data/us_west_2d/b37_7giab_us-west-2d_3x2_giab_concordance_mqc.tsv b37 usw2d-3x2

python bin/generate_concordance_heatmap.py data/eu_central_1c/hg38_eu-central-1c_mem2-sent-combo_giab_concordance.tsv hg38 euc1c-two


mv heatmap_*usw2d-all* results/us_west_2d/all/concordance/heatmaps
mv heatmap_*usw2d-3x2* results/us_west_2d/3x2/concordance/heatmaps
mv heatmap_*euc* results/eu_central_1c/two/concordance/heatmaps


# Benchmarks Cost/Runtime
python bin/generate_benchmark_plots.py data/us_west_2d/hg38_7giab_us-west-2d_benchmarks_summary.tsv hg38 usw2d-all
 
python bin/generate_benchmark_plots.py data/us_west_2d/b37_7giab_us-west-2d_3x2_benchmarks_summary.tsv b37 usw2d-3x2

python bin/generate_benchmark_plots.py data/eu_central_1c/hg38_eu-central-1c_mem2-sent-combo_benchmarks.tsv hg38 euc1c-two

mv euc1c-two_hg38_* results/eu_central_1c/two/benchmarks
mv usw2d-all_* results/us_west_2d/all/benchmarks
mv usw2d-3x2_* results/us_west_2d/3x2/benchmarks


# Precision vs Recall & Boxplots

python bin/generate_recall_v_precision.py -b hg38 -a usw2d-all -i data/us_west_2d/hg38_7giab_us-west-2d_giab_concordance_mqc.tsv -o ./hg38_usw2d-all_
python bin/generate_recall_v_precision.py -b b37 -a usw2d-3x2 -i data/us_west_2d/b37_7giab_us-west-2d_3x2_giab_concordance_mqc.tsv -o ./b37_usw2d-3x2_

mv *usw2d-all*box* results/us_west_2d/all/concordance/boxplots
mv *usw2d-all* results/us_west_2d/all/concordance/pvr

mv *usw2d-3x2l*box* results/us_west_2d/3x2/concordance/boxplots
mv *usw2d-3x2* results/us_west_2d/3x2/concordance/pvr


python bin/generate_recall_v_precision.py -b hg38 -a euc1c-two -i data/eu_central_1c/hg38_eu-central-1c_mem2-sent-combo_giab_concordance.tsv -o ./hg38_euc1c-two_
mv *box* results/eu_central_1c/two/concordance/boxplots
mv *png results/eu_central_1c/two/concordance/pvr


# Meta Analysis

python bin/generate_meta_analysis.py -b results/us_west_2d/all/benchmarks/usw2d-all_hg38_aggregated_task_metrics.csv -c data/us_west_2d/hg38_7giab_us-west-2d_giab_concordance_mqc.tsv -a data/us_west_2d/hg38_7giab_us-west-2d_alignstats.tsv -o hg38_usw2d-all_meta_ana.tsv

python bin/generate_meta_analysis.py -b results/us_west_2d/3x2/benchmarks/usw2d-3x2_b37_aggregated_task_metrics.csv -c data/us_west_2d/b37_7giab_us-west-2d_3x2_giab_concordance_mqc.tsv -a data/us_west_2d/b37_7giab_us-west-2d_3x2_alignstats.tsv -o b37_usw2d-3x2_meta_ana.tsv

python bin/generate_meta_analysis.py -b results/eu_central_1c/two/benchmarks/euc1c-two_hg38_aggregated_task_metrics.csv -c data/eu_central_1c/hg38_eu-central-1c_mem2-sent-combo_giab_concordance.tsv -a data/us_west_2d/hg38_7giab_us-west-2d_alignstats.tsv -o hg38_euc1c-two_meta_ana.tsv

mv *usw2d-all* results/us_west_2d/all/meta
mv *usw2d-3x2* results/us_west_2d/3x2/meta

mv *euc1c* results/eu_central_1c/two/meta

# WHEW!

```
