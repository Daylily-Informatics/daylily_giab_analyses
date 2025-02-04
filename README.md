
# Daylily Ifx Analysis Framework (GIAB Benchmarking)



# Intention
  > The goal of daylily is to enable more rigorous comparisons of informatics tools by formalizing the compute environment these tools run in, and establishing hardware profiles for tools which will reproduce both accuracy and runtime/cost perofrmance of each tool. This is intended to be a general approach and is not married to any specific toolset (of course AWS is involved. I have not made any design choices which would prevent this work from running outside AWS. AWS does offer the signicant benefit of affording a standardized compute hardware environment anyone who sets up an account may access). I should stress, that by 'compute environment', I mean more than simply offering a container. Containers do not guaruntee hardware perofrmance, and as runtime/cost becomes a significant driver in choosing tooling, we need ways to assert reproducible s/w performance on given hardware. Containers are used throughout daylily, as is conda. I strive to not get too tied to specicif tools. I have three main aims:

## Shift Focus
  Move away from unhelpful debates over “the best” tool and toward evidence-based evaluations. Real use cases dictate tool choice, so let’s make sure relevant data and clear methodologies are accessible—or at least ensure enough detail is published to make meaningful comparisons. Specifically, I wish to move away from scant and overly reductive metrics which fail to describe our tools in as rich detail as they can be. ie:

  > If I am looking for the best possible `recall` in SNV calling, initial data suggestes I might look towards [`sentieon bwa`+`sentieon DNAscope`](https://www.sentieon.com/) ... and interestingly, if I wanted the best possible `precision`, it would be worth investigating [`strobealigner`](https://github.com/ksahlin/strobealign) + `deepvariant` _[REF DATA](results/us_west_2d/all/concordance/pvr/hg38_usw2d-all__All_zoom.png)_. `Fscore` would not be as informative for these more sepcific cases.

# Raise the Bar
  Demand better metrics and documentation in tool publications: thorough cost data, specific and reproducible hardware details, more nuanced concordance metrics, and expansive QC reporting. Half-measures shouldn’t pass as “sufficient.”

# Escape Outdated ‘Best Practices’
  They were helpful at first, but our field is stuck in 2012. We need shareable frameworks that capture both accuracy and cost/runtime for truly reproducible pipeline performance—so we can finally move forward.


> This repo will hold the analsis from reuslts of the first stable release of `daylily` running on 7 GIAB samples. Again, not only to highlight the tools I've chosen, but to highlight this approach.



---
## Data Preview

> [You can find the full GIAB dataset analysis here- WIP](docs/data/overview.md)

### Concordance Metrics (Fscore, Recall, Precision, FDR, PPV, Sensitivity), by Sample, by Pipeline, by Variant Class 
- [All Plots For hg38-usw2d-all](results/us_west_2d/all/concordance/boxplots)
  ![](results/us_west_2d/all/concordance/boxplots/hg38_usw2d-all__All_boxplots.png)

### Heatmaps
- [All Heatmaps For hg38-usw2d-all](results/us_west_2d/all/concordance/heatmaps)

#### SNPts F-scores For 7 30x ILMN GIAB Samples, 3 Aligners, 5 SNV Callers (hg38)

  ![](results/us_west_2d/all/concordance/heatmaps/heatmap_SNPts_hg38_usw2d-all.png)


#### SNPtv F-scores For 7 30x ILMN GIAB Samples, 3 Aligners, 5 SNV Callers (hg38)

  ![](results/us_west_2d/all/concordance/heatmaps/heatmap_SNPtv_hg38_usw2d-all.png)

#### Insertions < 50bp F-scores For 7 30x ILMN GIAB Samples, 3 Aligners, 5 SNV Callers (hg38)

  ![](results/us_west_2d/all/concordance/heatmaps/heatmap_INS_50_hg38_usw2d-all.png)

#### Deletions < 50bp F-scores For 7 30x ILMN GIAB Samples, 3 Aligners, 5 SNV Callers (hg38)

  ![](results/us_west_2d/all/concordance/heatmaps/heatmap_INS_50_hg38_usw2d-all.png)


### Precision vs Recall
- [All PvR For hg38-usw2d-all](results/us_west_2d/all/concordance/pvr)

#### Full Dataset, `All` Variant Classes, All Pipelines

> Best Recall `sentieon bwa`+`sentieon DNAscope` == 0.9961
> Best Precision `strobe aligner`+`deepvariant` == 0.9993

  ![](results/us_west_2d/all/concordance/pvr/hg38_usw2d-all__All.png)

#### 'Zoomed' Dataset, `All` Variant Classes, All Pipelines
  ![](results/us_west_2d/all/concordance/pvr/hg38_usw2d-all__All_zoom.png)

#### Raw Concordance Metrics Dot Plots
  - [results/us_west_2d/all/concordance/raw_metrics](results/us_west_2d/all/concordance/raw_metrics)


### Benchmark Data

#### Total CPU Time Per Task
*note!*: the deepvariant times are artificially long in these data.
![](results/us_west_2d/all/benchmarks/usw2d-all_hg38_aggregated_runtime_cpu.png)

#### EC2 Spot Cost Per Task (All)
*note!*: the deepvariant times are artificially long in these data.
![](results/us_west_2d/all/benchmarks/usw2d-all_hg38_aggregated_task_cost.png)

#### EC2 Spot Cost per Task (targeted)
_these are `euc1c-two` data, and deep variant costs are acurate for the AZ spot price market at that time.
![](results/eu_central_1c/two/benchmarks/euc1c-two_hg38_raw_task_cost.png)

#### Cost per vcpu per GB input fastq
_useful in predicting per-sample analysis costs in advance of starting an ephemeral cluster_
*note!*: the deepvariant times are artificially long in these data.

![](results/us_west_2d/all/meta/hg38_usw2d-all_meta_ana_boxplot_cost_per_vcpu_sec_gb.png)


---

## Overview & Goals

1. **Demonstrate the Utility of Daylily**  
   - **Ephemeral** cluster usage: spin up an AWS cluster only when needed, run your WGS analysis, then tear it down to minimize cost.  
   - Built-in **cost tracking**, **spot instance** usage, and **performance metrics**.  

2. **Promote Rigorous Comparison of Tools**  
   - Typically, WGS comparisons omit cost and raw compute details. **Daylily** captures CPU time, wall time, spot pricing, and cost per vCPU second, among other metrics.  
   - The data produced here can help drive cost estimations for your pipeline in the best availability zone.

3. **Streamlined Data & Results**  
   - All raw data (FASTQs, references, alignstats, etc.) are in `./data/`.  
   - Summaries of runtime, cost, coverage, and variant-caller performance are in `./results/`.  
   - MultiQC reports, F-score heatmaps, boxplots, and more provide a comprehensive overview of pipeline performance.

For information on **installing or configuring** Daylily, please see the [Daylily repository](https://github.com/Daylily-Informatics/daylily). This README focuses on reproducing these analyses and showcasing the results, **not** the low-level setup.

---

## Data Sets & Pipeline Configurations

We analyzed **7 GIAB** samples (Illumina, ~30× coverage) on different references (hg38 or b37) in separate AWS regions/clusters, each with distinct aligners, variant callers, and QC steps.

### 1. `hg38_usw2d-all`  
- **Reference**: hg38  
- **Region**: `us-west-2d`  
- **Tools**:  
  - Aligners: **Sentieon BWA**, **BWA-MEM2**, **Strobealign**  
  - SNV Callers: **Sentieon DNAscope**, **DeepVariant**, **Octopus**, **LoFreq2**, **Clair3**  
  - SV Callers: **Manta**, **Tiddit**, **Dysgu**  
  - QC: MultiQC, alignstats + ~14 other tools.  
- **Note**: A resizing event on FSX caused prolonged task hang times, which **inflated** costs and CPU/wall-time metrics for some runs. Cost/timing insights should be drawn from the `eu-central-1c` datasets or the `b37` dataset below.  

### 2. `b37_usw2d-3x2`  
- **Reference**: b37  
- **Region**: `us-west-2d`  
- **Tools**:  
  - **Three aligners**: Strobealign, Sentieon BWA, BWA-MEM2  
  - **Two SNV Callers**: Sentieon DNAscope, DeepVariant  
  - Additional QC: MultiQC, alignstats  + ~14 other tools.  

### 3. `hg38_euc1c-two`  
- **Reference**: hg38  
- **Region**: `eu-central-1c`  
- **Tools**:  
  - **Cluster A**: Sentieon BWA + Sentieon DNAscope  
  - **Cluster B**: BWA-MEM2 + DeepVariant  
- **Goal**: Show ephemeral cluster usage under *ideal conditions* (with spot pricing and no interruptions). This is effectively a smaller targeted run that can be **combined** for cost/CPU comparisons, emphasizing **Daylily**’s cost management features.  

---

## How to Re-Create These Analyses

### Run A`daylily` Ephemeral Cluster
1. **Obtain Daylily** from [its main repository](https://github.com/Daylily-Informatics/daylily).  
2. **Configure** AWS credentials, references (hg38/b37), and your GIAB FASTQ paths in Daylily’s config.  
3. **Process** GIAB FASTQs On An Ephemeral Cluster >> [detailed step-by-step commands may be found here](docs/creating_dataset.md) << , which will guide you through:
   a. **Launch** of an ephemeral cluster via Daylily 
   b. **Run** the WGS pipeline  
      - Executes the alignment, variant calling, and QC steps  
   c. **Review** the final results in `./results/*`, which is where all files used in the analysis to follow will be found.
4. **Mirror** `Fsx` data back to `S3`.
5. **Delete** the ephemieral cluster.

---

## GIAB Benchmark Analysis

### Files & Directories

Each dataset analyzed here includes:

- **`build_annotation_giab_concordance_mqc.tsv`**  
  Contains SNV caller concordance results (F-scores, etc.) by variant class (SNP transitions/transversions, Indels, etc.).  
- **`build_annotation_benchmarks_summary.tsv`**  
  Summaries of runtime, CPU usage, and spot pricing per task—used to derive cost metrics.  
- **Alignstats** (coverage metrics) and (for the two `us_west_2d` runs) **MultiQC** reports.  
- **Consolidated plots** and **tables** inside each subdirectory.

---

### Analysis & Results

Below, we highlight key plots and observations from the **three** main datasets. Additional figures and tables can be found under each dataset’s `concordance/` and `benchmarks/` subdirectories.

### 1. **`hg38_usw2d-all`** (Full Toolset)

> **Goal**: Explore a **broad** matrix of aligners (3) and SNV callers (5) plus multiple SV callers on the 7 GIAB samples (hg38).  

- **Technical Interruption**: A **resizing** of FSX inflated run times for some tasks, leading to higher computed costs.  
- **Interesting Plots**:  
  - **Cost per vCPU-second per GB** boxplots (see `results/us_west_2d/all/concordance/boxplots/`):  
    <br><img src="results/us_west_2d/all/concordance/boxplots/cost_per_vcpu_sec_gb_boxplot.png" width="400" />
    - *Observation:* BWA-MEM2 + DeepVariant shows relatively lower cost per vCPU-second per GB. Strobealign + DNAscope is comparable, but higher standard deviation.  
  - **F-score Heatmaps** (see `heatmaps/`):  
    <br><img src="results/us_west_2d/all/concordance/heatmaps/snp_fscore_heatmap.png" width="400" />
    - *Observation:* DNAscope and DeepVariant consistently hit high F-scores for SNP transitions and transversions across samples.  
  - **Precision-vs-Recall** (PVR) plots (`pvr/`):  
    <br><img src="results/us_west_2d/all/concordance/pvr/pvr_plot.png" width="400" />
    - *Observation:* Points cluster near top-right for most aligner+caller combos, but we see slight differences in recall for Indels vs. SNPs.  

Despite the FSX interruption, these runs confirm:
- **High baseline accuracy** for widely used pipelines (BWA + DeepVariant, Sentieon bwa mem + Sentieon DNAscope).  
- Potentially **lower cost** solutions with Strobealign, albeit with some variability 
    > _note_: SNV callers are not tuned to expect strobe aligner alignments, and I expect there is significant room for improvement.  Given it's disadvantage, it's performance out of the box is quite encouraging.  

### 2. **`b37_usw2d-3x2`** (Three Aligners × Two Callers)

> **Goal**: Evaluate a smaller matrix (3 aligners × 2 SNV callers) against b37-based GIAB data in `us_west_2d`.  

- **Benchmarks**:  
  - **Faster** alignments with BWA-MEM2 than with older BWA in some tasks.  
  - Slightly **higher coverage** variance with Strobealign.  
- **Concordance**:  
  - **DeepVariant** typically edges out DNAscope in terms of SNP recall on certain GIAB samples, though the difference is small.  
  - Indel F-scores are relatively similar for both.  
- **Costs**:  
  - Overall lower than the `hg38_usw2d-all` set, due to fewer pipeline steps and no major FSX interruptions.  
  - Boxplots in `benchmarks/` show cost scaling with CPU time but remaining within typical spot pricing bounds.  

### 3. **`hg38_euc1c-two`** (Two Minimal Pipelines in `eu_central_1c`)

> **Goal**: Show ideal ephemeral usage for two minimal pipelines on 7 GIAB samples with the hg38 reference:  
> 1) **Sentieon BWA + DNAscope**,  
> 2) **BWA-MEM2 + DeepVariant**.  

- **Separate Clusters**: Each pipeline was run on a separate ephemeral cluster at spot pricing in `eu_central_1c`.  
- **Highlights**:  
  - **Lower overall cost** because the cluster spooled up only for these specific tasks, then shut down.  
  - **Daylily**’s cost-tracking reveals consistent spot pricing across tasks, with minimal idle times.  
- **Comparisons**:  
  - Aligners performed comparably for coverage on these GIAB samples.  
  - **DNAscope** vs. **DeepVariant** differences remain subtle but show up in some variant classes—check `concordance/raw_metrics` for exact precision/recall.  

This dataset underscores **Daylily**’s ephemeral cluster approach. The ability to **create** and **destroy** a cluster quickly, with tasks tracked by cost, was highly effective for controlling expenses.

---

## Additional Figures & Tables

- **`concordance/boxplots/`**  
  Side-by-side boxplots for cost, F-scores, coverage distribution, etc.  
- **`concordance/heatmaps/`**  
  Heatmaps covering per-tool performance across variant classes.  
- **`concordance/pvr/`**  
  Precision vs. Recall (P/R) curves for each pipeline.  
- **`benchmarks/`**  
  Summaries of CPU/wall time per Snakefile rule, cost breakdowns, and spot instance logs.  

Feel free to explore the **raw_metrics** subfolders for CSV/TSV data if you want to do further custom analysis or re-plot these metrics.


---
---

# Case Study

## Select An AZ With Favorable Spot Pricing, Analyze There!

From the [daylily repo](), generate a spot instance pricing report.

```bash
 python bin/check_current_spot_market_by_zones.py --profile $AWS_PROFILE -o ./sentieon_case_study.csv --zones us-west-2a,us-west-2b,us-west-2c,us-west-2d,us-east-1a,ap-south-1a,eu-central-1a,eu-central-1b,eu-central-1c,ca-central-1a,ca-central-1b
 ```
  - [Spot market pricing data](data/sentieon_case_study.tsv).

  ![](docs/images/small_spot_market_report.png)

  > `eu-central-1c` has been among the cheapest and with reasonable stability for a few weeks. Proceed with this AZ to create an ephemeral cluster, run analysis, and clean it up when idle. **see daylily repo docs for how to create and run an ephemeral cluster**.



## BWA MEM2 + DEEPVARIANT // Complete Ephemeral Cluster Cost Analysis _for_ 7 30x GIAB Samples, FASTQ->snv.VCF (bwa mem2, doppelmark, deepvariant)

### $5.90 EC2 Costs per Sample // $6.72 Fully Burdened AWS Ephemeral Cluster Cost per Sample

`daylily` tracks every AWS service involved in creating, running and tearing down ephemeral clusters. Below is the complete cost of running an ephemeral cluster to analyze 7 GIAB 30x fastq files using a `bwa mem2`+`doppelmark duplicates`+`deepvariant` pipeline. In this case, running vs `hg38`.

> This ephemeral cluster was created in AZ `eu-central-1c` as it had a very favorable spot market for the `192vcpu` spot instances daylily relies upon, which cost **~$1.40/hr** at that time. 

> This AZ had quota restrictions on how many spot instances could be run at one time, so it existed for 5hr. 
>   - Fully parallelized without quota restrictions, the cluster would have completed processing in **1h 40m**.

  ![](docs/images/hg38_eu-central-1c_ephemeral_cluster_AWS_complete_costs.jpg)

  - `total AWS cost` (EC2, Fsx, networking, etc) to run this cluster = **$47.05**
    - `total EC2 compute` cost = **$41.50**
      - `active EC2 compute` cost as calculated from [hg38_eu-central-1c_benchmarks.tsv](data/eu_central_1c/hg38_eu-central-1c_benchmarks.tsv) = **$36.33**
      - `idle EC2 compute` cost (`total EC2`-`active EC2`) = **$5.17** (_12% idle_)
        - Idle time are vcpu seconds not actively in use by a job/task. 12% likely represents an upper bound, as this cluster was not running at capacity, and many jobs ran on partially utilized instances. This time can be dialed back by reducing the time threshold to teardown idle spot instances.


## SENTIEON // Complete Ephemeral Cluster Cost Analysis _for_ 7 30x GIAB Samples, FASTQ->snv.VCF (sentieon bwa mem, doppelmark, sentieon DNAscope)

---

## Concluding Thoughts & Next Steps

These three data sets illustrate how **Daylily**:

- **Unifies** alignment, variant calling, SV detection, and QC in a cost effective, highly observable, scalable, rigourously reproducible hardware environment paired with tools optimized for this hardware environment. The magic is more in the approach to hardware-software management than in the workflow itseld (NOTE: daylily can already run `CROMWEL` workflows and it is reasonably trivial to enable other workflow managers)
- **Captures** _&_ **Predicts** cost, CPU, coverage, and F-score metrics **in one place**.  
- **Scales** from smaller targeted runs (`hg38_euc1c-two`) to comprehensive tool comparisons (`hg38_usw2d-all`) and should be able to handle 1000's of genomes in parallel per-cluster (given appropriate quotas and so on).  

**Next Steps**:

1. Integrate final results and plots into a **whitepaper** or preprint (see the [whitepaper sketch](https://github.com/Daylily-Informatics/daylily/tree/main/docs/whitepaper)).  
2. Include additional variant callers (e.g., GPU-accelerated) or references for broader coverage.  
3. Expand cost-estimator logic to automatically recommend an optimal AWS region or instance type based on real-time pricing.

**Questions or Contributions**:  
- Please open an issue or pull request in [this repository](https://github.com/Daylily-Informatics/daylily_giab_analyses).  
- For Daylily-specific usage, see the [main Daylily repo](https://github.com/Daylily-Informatics/daylily).

---

*Last updated: February 2025*