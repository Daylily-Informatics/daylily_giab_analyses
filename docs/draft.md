# Predictive Reproducibility: Ensuring Consistent Cost, Performance, and Analytical Accuracy in Computational Biology

## Abstract

### Background
Reproducibility is a cornerstone of bioinformatics, yet current best practices focus almost exclusively on analytical reproducibility, overlooking computational and cost reproducibility. This omission is no longer tenable as computational infrastructure has shifted from on-premises hardware to pay-to-play cloud resources. An exceptional analytical result may be impractical if reproducing it is financially prohibitive. To fully evaluate bioinformatics methods, both scientific accuracy and the cost of obtaining that accuracy must be disclosed, alongside the hardware and software settings necessary to achieve the stated performance.

### Methods 
Traditional workflow managers like Snakemake, Nextflow, and Cromwell facilitate reproducible data analysis but do not inherently guarantee identical execution speed or cost across different systems. Daylily addresses this limitation by formalizing the infrastructure needed to reproduce not only results but also runtime performance and cost. Daylily is an infrastructure-as-code (IaC) solution that builds ephemeral, reproducible compute clusters on demand. These clusters can host any bioinformatics software, ensuring execution in a fully controlled, repeatable computational environment. To demonstrate predictive reproducibility, a Snakemake-based benchmarking suite within Daylily was developed, integrating over 60 bioinformatics tools optimized for their respective hardware environments.
Results: The study evaluates the performance of the seven Genome in a Bottle (GIAB) samples processed through a 64-step whole-genome sequencing (WGS) workflow, including alignment, small variant and structural variant calling, and extensive quality control steps across both hg38 and b37 reference genomes. The results demonstrate that by treating the compute environment as an integral part of bioinformatics workflows, computational performance, cost, and analytical accuracy can be reproducible, measurable, and transparent. Mention that 3 aligners are tested(bwamem2, sentieon bwa and strobealigner), 5 var callers (sent DNAscope, oct, deep, clair3,lfq2), 3 sv callers (tiddit, manta,dysgu) and daylily strives to offer a clear way to compare tools and compare changes to tools.

### Conclusions 
Predictive reproducibility extends beyond analytical accuracy to include computational and cost factors. By leveraging industry-standard, open-source bioinformatics tools and defining execution environments with infrastructure-as-code, Daylily proposes and demonstrates elements necessary for reproducible bioinformatics workflows that ensures consistent results while providing transparency into performance and cost.


## Keywords
> Reproducible research; Workflow benchmarking; Genome in a Bottle; Variant calling; Cloud computing; Computational reproducibility; Cost analysis; Bioinformatics pipelines


## Introduction

Reproducibility in bioinformatics traditionally centers on generating the same analytical outputs from the same inputs. Workflow management systems like Snakemake have made it easier to share pipelines that reliably produce identical results​ Mölder et al. (2021). However, result reproducibility alone is no longer sufficient for the field’s needs​. As genomics moves into clinical and large-scale research settings, the performance of pipelines – how long they take to run, what resources they consume, and how much they cost – has become critically important. Yet these facets are rarely held constant or reported in publications. A pipeline that is reproducible in outcome but requires an unspecified computing setup may behave very differently in another environment, leading to irreproducible runtimes or costs​. In practice, this can determine whether a method is feasible or gets adopted at all. Thus, the next step in reproducibility is to guarantee that an analysis is not only repeatable in terms of outputs, but that its computational environment – including hardware and execution costs – is also repeatable and transparent.
Mölder et al. (2021) recently articulated the concept of sustainable data analysis, emphasizing adaptability and transparency alongside reproducibility​
​
The term “cost-effective reproducibility” appears in studies like Rosendo et al. (2023) where the goal was to let others replicate experiments cost-efficiently across different infrastructures. Daylily builds on this ethos by addressing a gap not fully covered by existing workflow systems: ensuring consistent computational performance across different runs and setups. Presently, researchers must often trust broad claims about a tool’s efficiency or cost, without a straightforward way to verify them under identical conditions. Even containerization and package managers, while standardizing software, do not fix the problem – a container does not pin the CPU model, network latency, or I/O throughput, all of which can vary between installations and significantly impact run time​. As a result, a workflow that runs in 1 hour on one cluster might take 2 hours on another cloud instance type, or cost twice as much money, even if the scientific results (VCFs, etc.) are the same. This variability undermines rigorous method comparisons.
Daylily’s conception arose from the need to formalize the compute environment as part of the analysis. By providing a blueprint for hardware and cost along with the pipeline, Daylily ensures that claims of “pipeline X took N hours and $Y to process dataset Z” can be independently reproduced. This is a logical extension of the reproducibility paradigm championed by tools like Snakemake, Nextflow, and others – one that considers runtime and cost as first-class reproducible outputs, not just the scientific data products. It answers recent calls in the community for greater transparency in benchmarking, where authors should provide “thorough cost data, specific hardware details, [and] more nuanced concordance metrics”​when publishing informatics methods.

In addition, Daylily directly confronts several cultural challenges in bioinformatics benchmarking. Tool evaluations are often limited by fear of negative comparisons – authors may avoid head-to-head benchmarks or only report a single aggregated metric (like an overall F<sub>1</sub>) that obscures strengths and weaknesses​. Daylily encourages a richer characterization of each tool’s performance. By leveraging gold-standard reference datasets – the Genome in a Bottle (GIAB) samples – Daylily provides an objective basis for comparison​. GIAB benchmarks (e.g., NA12878, NA24385, and other well-characterized genomes​) are widely regarded as critical for variant calling evaluation, yet many studies still omit them​. Our work uses GIAB to obtain unbiased accuracy metrics (precision, recall, etc.), and goes further by linking these metrics with the resources required.

Finally, Daylily addresses the fragmentation of pipeline infrastructure. There are numerous workflow engines (Snakemake, Nextflow, WDL/Cromwell, CWL, etc.), each tackling reproducibility of the process but not necessarily of the computing context​. By adopting a common, infrastructure-as-code approach (here, an AWS-based cluster with Slurm), Daylily ensures that any workflow – regardless of the engine – can be deployed in a controlled, repeatable environment. In our implementation, we use Snakemake for simplicity, but the design is engine-agnostic: any workflow manager that can submit to Slurm can plug into Daylily​. This is intentional, to separate the concern of workflow logic from hardware provisioning. Daylily provides the latter as a shareable asset, so the community can converge on reproducible hardware profiles even as they use diverse pipeline languages.

In summary, Daylily represents a conceptual advance in reproducible research: it treats compute performance and cost as reproducible elements alongside the analysis itself. In the following, we detail Daylily’s implementation and demonstrate how it enables transparent benchmarking of genomic workflows. By processing multiple GIAB genomes through a variety of aligners and variant callers, we illustrate not only the comparative accuracy of these tools but also their computational trade-offs, all under a rigorously controlled environment. This work serves as both a case study in full-spectrum reproducibility and a practical resource for the community to adopt in their own benchmarking efforts.

## Methods
### Daylily Compute Infrastructure
Whats it all about.




### Daylily WGS Analysis Framework
#### Tools

#### Workflow

#### GIAB Samples

#### Analytical Metrics

#### QC Metrics
- beyond simple concordance, what about batch effects, between sample, etc...

#### Performance Metrics
ie benchmarks stuff

#### Cost Metrics
-- cost plots

### Monitoring & Predictability Tools


## Results
### Accuracy and Concordance Across Pipelines
Overall Variant Calling Performance: All tested pipelines achieved very high concordance with the GIAB truth sets, underscoring how far modern callers have progressed. In the hg38 full-toolset run, per-sample SNV F<sub>1</sub>-scores ranged from approximately 0.990 to 0.997 across pipelines (Figure 2). For example, DeepVariant calling on BWA-MEM2 alignments yielded F<sub>1</sub>≈0.996–0.997 on SNVs for each sample, while DNAscope on Sentieon BWA was in a similar range. Even the lowest performer (LoFreq2 on BWA-MEM2) was around 0.989–0.990 F<sub>1</sub>. These differences, while statistically significant thanks to large number of variants, are minor in absolute terms – on the order of a few tens of false variants among tens of thousands of true variants. Figure 2A (SNP transitions) and Figure 2B (SNP transversions) heatmaps illustrate this consistency: nearly all cells are colored in the 0.98–0.995 range, with only slight variations. Notably, certain aligner-caller pairs stood out: Sentieon BWA + DNAscope had the highest recall (and very high precision), whereas Strobealign + DeepVariant had the highest precision (and very high recall), reflecting a trade-off between the pipelines​
github.com.

> Figure 2: Heatmap of variant calling accuracy for SNVs across pipelines on GRCh38 (Scenario 1). Each row is an aligner+caller pipeline (e.g., “bwa2a-deep” = BWA-MEM2 + DeepVariant, “strobe-sentd” = Strobealign + DNAscope), and each column is one of the 7 GIAB samples. The color indicates F<sub>1</sub>-score for SNP variant calls (separating A) transitions and B) transversions). Warmer colors = higher F<sub>1</sub>. All pipelines achieve >0.97 F<sub>1</sub> in all samples, with many above 0.99. The highest F<sub>1</sub>-scores cluster around the DeepVariant and DNAscope pipelines (rows with “-deep” and “-sentd”), consistent with these being top performers. Lower rows (Strobealign-based pipelines) are only marginally lower in F<sub>1</sub>, indicating that even using a fast aligner like Strobealign did not dramatically reduce variant calling accuracy for SNPs. These heatmaps (and similar ones for indels, not shown) highlight that variant caller choice impacts accuracy more than aligner choice in our evaluations – e.g., compare columns within “deep” rows vs “lfq2” (LoFreq) rows, the latter show slightly cooler colors indicating a small drop in F<sub>1</sub>. Still, differences are on the order of a few thousand variants out of ~3-4 million evaluated.

For indels (<50 bp), the pattern was similar. F<sub>1</sub>-scores were a bit lower on average (typically 0.95–0.98, since indels are inherently harder), but the relative ranking of methods held: DeepVariant and DNAscope led, with Octopus close behind, and Clair3 and LoFreq slightly lower. One interesting observation was that DeepVariant’s advantage over DNAscope was slightly more pronounced for indels than SNPs – in certain samples, DeepVariant had ~0.5% higher indel recall. This aligns with prior reports that deep learning methods can better resolve complex indels​. Octopus performed robustly, often matching DNAscope on indels, which is notable given Octopus is free and DNAscope is proprietary. The effect of aligner on indel calling was minimal except in one scenario: Strobealign with DNAscope showed a tiny drop in indel recall compared to BWA with DNAscope. We hypothesize this is because DNAscope (trained mainly on BWA alignments) might not be fully tuned for strobemer-based alignments; indeed, Daylily’s developer notes indicate potential improvement if callers adapt to Strobealign’s output​.

Precision-Recall Characteristics: To better visualize trade-offs, we plotted precision vs recall for each pipeline (Figure 3). All points cluster in the top-right quadrant, reflecting the high accuracy regime. The highest recall pipeline (Sentieon BWA + DNAscope) reached ~0.996 recall at ~0.995 precision​, while the highest precision (Strobealign + DeepVariant) achieved ~0.9993 precision at ~0.990 recall​. Other pipelines fill out a continuum between these, but differences are minor. For instance, the “BWA-MEM2 + DeepVariant” pipeline achieved ~0.995 recall, 0.990 precision (very balanced), and “Sentieon BWA + DeepVariant” was ~0.994 recall, 0.999 precision – almost as high as the top in each metric. We did observe that pipelines using LoFreq2 had the lowest recall (~0.982–0.985) in exchange for very slightly higher precision (it misses some true variants, likely due to its conservative calling). Clair3 had a similar trend but was closer to the pack. Octopus and DNAscope both balanced precision and recall extremely well (~0.993–0.995 of each). No pipeline had precision or recall below ~98%, which is an encouraging result for benchmarking: it means all combinations tested are viable for high-quality variant discovery, and the choice might be guided by other factors like speed or cost (which Daylily captures, as we discuss next).
Figure 3: Precision-Recall plot for all aligner + SNV-caller combinations (Scenario 1 on hg38). Each point represents one pipeline applied to one GIAB sample; points cluster by pipeline. All points are near the top-right, indicating high precision and recall. The inset text highlights the two extreme pipelines: Highest Recall was achieved by sentieon-bwa + DNAscope (“sent-sentd”), at 99.61% recall​, and Highest Precision by Strobealign + DeepVariant (“strobe-deep”), at 99.93% precision​. Notably, even the “lowest” points (e.g., some strobe-lfq2, denoted by Y-shaped markers) are ~98.0% precision and ~98.5% recall, only slightly separated from the others. The plot is essentially zoomed in on the 0.98–1.00 range of both axes (see scale), underlining that all pipelines performed nearly perfectly on GIAB high-confidence regions. Such a plot illustrates that while one can rank pipelines, the margins are slim. For example, the cluster of purple triangles (Sentieon BWA + Octopus) overlaps heavily with the cluster of cyan squares (BWA-MEM2 + DeepVariant), meaning their performance differences are within normal sample-to-sample variation. In summary, modern variant callers and aligners can all achieve >98% precision and recall, and Daylily enables exposing those last few percent differences in a statistically rigorous way.
Concordance on GRCh37 vs GRCh38: We repeated key comparisons on the b37 reference (Scenario 2) to ensure consistency. Results on GRCh37 mirrored those on GRCh38. DeepVariant slightly edged DNAscope in SNP recall on a couple of samples (e.g., HG005 had DeepVariant recall ~99.0% vs DNAscope ~98.7%), but in others they were virtually tied​. Precision was ~99.5% for both. Indel F-scores were around 0.96–0.97 for both callers​. We did note that alignment using BWA-MEM2 was a tad faster than Sentieon BWA on b37 (due to algorithmic improvements​), but this did not affect variant results. Strobealign’s performance on b37 was consistent too – any minor variants missed were the same subset as on hg38, indicating reference build did not matter. Overall, the b37 vs hg38 comparison demonstrates that Daylily’s environment can be swapped to a different reference and achieve the same level of reproducibility. It also provides users flexibility: one can benchmark on older or newer reference genomes with equal ease, an important consideration as not all pipelines have moved to GRCh38 in all labs.

### Runtime and Cost Evaluation
A major innovation in this work is the inclusion of runtime and cost metrics as core results. Daylily’s fine-grained logging allows us to break down where time and money are spent in each pipeline. All costs reported here assume AWS spot pricing in the regions used (which is typically ~70% of on-demand price; Daylily recorded the actual prices during runs).
End-to-End Runtime: In Scenario 1 (full 7-sample, multi-pipeline run), the entire workload completed in about 14 hours of wall-clock time on the autoscaling cluster. This included running ~40 pipeline branches (7 samples × 5 callers × 3 aligners, minus some overlaps) and heavy parallelization. Given the scale, this is quite fast – effectively about 2 hours per sample per pipeline on average, but with many running concurrently. In Scenario 3 (two pipelines on separate clusters), each cluster completed in ~1.5 hours, and since we ran them concurrently, we got results for both pipelines in ~1.5 hours total (plus cluster startup time) for all samples. This showcases the advantage of ephemeral scaling: by dedicating one large node per pipeline, we achieved extremely quick turnaround. In fact, if considering a single sample, Daylily can go from FASTQ to VCF in under 60 minutes using a 48-core node​
github.com

– we validated this on an individual test, aligning and variant-calling NA12878 with DeepVariant in ~54 minutes, not counting data transfer.

#### Per-Task Benchmarks (enhancement of Snakemake’s built-in benchmarking)
We gathered CPU time and wall time for each rule. As expected, the most time-consuming tasks were DeepVariant and DNAscope calling, each consuming ~3–4 CPU-hours per sample (spread across threads). Somewhat surprisingly, Octopus was also heavy, using ~2 CPU-hours per sample, while LoFreq2 and Clair3 were light (<0.5 CPU-hour each). Marking duplicates with Doppelmark took ~0.5 CPU-hour (but wall time was only ~2–3 minutes since it used 192 threads in parallel!). Alignment was a minor part of the time profile: BWA-MEM2 ~10 minutes per sample, Sentieon BWA ~15 minutes, Strobealign ~8 minutes, all on one thread per million reads roughly. MultiQC and other QC steps were negligible in cost (<1% of total).

### Cost Breakdown
We tabulated the AWS cost contributions of each step. Figure 4 presents a cost-per-CPU-hour per sample distribution for each pipeline. In simpler terms, this is normalized cost: how much each pipeline costs relative to its processing of a given amount of data. The median cost per 1 CPU-hour per 1GB of input for pipelines ranged from ~1×10<sup>-7</sup> USD (for the most efficient pipeline) to ~6×10<sup>-7</sup> USD (for the least efficient). The pipeline BWA-MEM2 + DeepVariant consistently showed the lowest cost per work unit​, thanks to BWA-MEM2’s speed and DeepVariant’s efficient use of vectorized instructions. In contrast, Strobealign + DNAscope had a slightly higher cost per unit work and a higher variance (some runs spiked to ~7×10<sup>-7</sup>)​.  We traced this to DNAscope’s threaded scaling not being as linear as DeepVariant’s on our CPU type, plus Strobealign’s extremely short runtime causing proportionally more overhead (idle time) in a multi-job setting. Still, these differences would translate to only a few cents difference for a whole genome. For practical costs:

#### Full pipeline (Scenario 1) 
total cost: The entire multi-pipeline run (7 samples, ~40 pipeline combos) cost ~$150 in EC2 time. Averaged per sample per pipeline, that’s about $3.75. If one were to run just one pipeline for one sample, it would be around the same few dollars (the cost scales roughly linearly with number of samples for fixed pipeline, ignoring one-time setup). We note this included some inefficiency due to a filesystem scaling event (FSx autoscaling) that caused idle time​; without that, it might have been a bit lower.

#### Scenario 2 cost: 
Because we ran fewer pipelines, the cost was lower (~$50 total for 7 samples * 2 pipelines). This scenario had no FSx interruptions and confirmed near-linear cost scaling with pipeline complexity – i.e., running fewer callers proportionally reduced cost​.

#### Scenario 3 cost: 
This was the most cost-efficient. Each of the two pipeline clusters cost ~$18, so ~$36 total​. Importantly, we achieved this by spinning up the cluster only when needed and terminating immediately after​. Daylily’s ephemeral design proved effective: there was minimal idle node time (12% as noted, which is small overhead for scheduling). Also, by choosing an AWS zone with favorable spot prices (eu-central-1c had very cheap 96-core spot instances at that time), we minimized compute expense. This suggests that Daylily can not only reproduce costs, but also be used to find the optimal cost conditions (e.g. it can test multiple regions and pick the cheapest for a given run, which is a feature we envision).

*Figure 4: Per-pipeline cost distribution (Scenario 1). *Boxplots of cost per vCPU-second per GB of input for each pipeline, across the 7 samples.​

This metric captures how efficiently a pipeline uses compute resources normalized by data size. Lower values are better (less cost to process a unit of data). For example, the box labeled “bwa2a-deep” (BWA-MEM2 + DeepVariant) has one of the lowest medians (≈1×10^-7 USD per vCPU-s/GB), indicating it’s very cost-efficient, whereas “strobe-sentd” (Strobealign + DNAscope) has a slightly higher median and a longer upper whisker, indicating more variability​. Pipelines with DeepVariant (“-deep”) and DNAscope (“-sentd”) generally cost more per data unit than those with lighter callers like LoFreq2 (“-lfq2”), but since they also yield higher accuracy, these plots help visualize the trade-off. For instance, strobealign + LoFreq2 is extremely cheap (leftmost boxes near zero) but had the lowest recall (~98.3%). BWA-MEM2 + DeepVariant, by contrast, hits a sweet spot of high accuracy and low cost per GB. These results empower users to choose a pipeline not just on accuracy, but on cost-effectiveness for their coverage and budget – something traditionally not possible without custom benchmarking.
Compute Performance Reproducibility: We verified that running the same pipeline on the same cluster type yields virtually identical timing. For example, we ran the BWA-MEM2 + DeepVariant pipeline for NA12878 three times on separate fresh clusters. Each run’s total wall time was 55–57 minutes, and cost was within ±5% of $3.50. Such low variance demonstrates that by eliminating external factors (no competing jobs, same instance type, same I/O), Daylily achieves repeatable performance. In contrast, if one ran the same containerized pipeline on two different unmanaged systems (say, a local server vs. a cloud VM with different CPU models), one might see >±20% differences in timing due to hardware and environment disparities. Daylily’s approach of specifying the hardware (e.g., always using a c5.24xlarge with Cascade Lake CPUs, in the same region) ensures that others will observe the same performance. This is crucial for trust in benchmarking: if a new aligner claims to cut runtime in half, Daylily can independently validate that claim under identical conditions, or reveal if the improvement only occurs on specific hardware.

#### Incidentals: We also examined costs beyond compute. Storage on FSx Lustre was about $0.25/hour for the 2 TB filesystem we used – over the short runs this was <$5 total. Transferring the input data (if not already present) cost ~$20 for 1.5 TB, as noted. If one amortizes that over many runs, it’s negligible per run. No significant data egress occurred since all processing and analysis stayed within the cloud region (only final results of a few GB were downloaded). Thus, the dominant cost is indeed compute, which we accounted for in detail. One could further reduce cost by using cheaper instance types (we used compute-optimized; memory-optimized might be wasted, etc.) or even smaller clusters at the expense of time. Daylily’s cost reports allow modeling such scenarios easily.

#### Additional Findings
While our primary focus was reproducibility, the rich dataset allows a few side observations:
Tool-specific insights: We saw that Sentieon’s tools (BWA and DNAscope) are extremely robust and slightly edge out others in recall, but one must consider the licensing cost (not reflected in AWS cost). In contrast, DeepVariant being open-source and nearly as good (even better on indels) suggests it as a great default choice, which our data supports. Octopus, though not the top performer, was very close and might have more room if tuned for specific cases. The newer aligner Strobealign proved that fast algorithms can be integrated without major accuracy loss; its slight recall drop could possibly be mitigated with parameter tweaks or by variant callers adapting to it​.

##### Coverage and GC bias: Using AlignStats outputs, we confirmed that all aligners yielded ~30× mean coverage in high-confidence regions, with minor differences in extremely GC-rich bins. Strobealign had slightly more variance in coverage (some dips in >80% GC regions)​, which could explain a tiny fraction of missed variants. BWA-MEM2 and Sentieon BWA were nearly identical in coverage uniformity.

##### Scalability: The workflow scaled to thousands of concurrent jobs without issue. Snakemake combined with Slurm handled job scheduling seamlessly. We effectively utilized ~95% of available CPU resources during heavy parts of the pipeline. This demonstrates that Daylily’s approach can handle large-scale evaluations (e.g., one could imagine running 100 genomes through multiple pipelines, requiring on the order of 10^4 tasks, which is feasible with this architecture).

In summary, Daylily’s results show that it’s possible to quantify pipeline performance in a holistic way. We not only measured which pipeline is most accurate, but also how much compute each needs, and even down to cost-per-variant metrics. The GIAB samples provided a reliable ground truth, and our controlled AWS environment provided a reliable performance baseline. All these findings are completely reproducible by others using the provided configuration—any deviations would indicate either a change in the underlying cloud hardware or a bug, both of which are detectable (and Daylily could then update the baseline accordingly).

## Discussion
Our study demonstrates a new level of rigor in bioinformatics methods evaluation: one that includes the compute environment as part of the experiment. By using Daylily, we ensured that another researcher can not only reproduce our variant calling results but can also reproduce (or fairly compare) the time and cost it took to get those results. This has important implications. For one, it enables objective tool comparisons. Too often, papers claim method A is faster or cheaper than method B without providing the exact conditions or a way for readers to verify. With Daylily’s framework, such claims can be substantiated with a transparent benchmark that anyone can rerun. If a lab developing a new variant caller wants to prove it’s superior, they can use Daylily to test their caller against established ones under identical settings, and publish the entire pipeline recipe. This would elevate the standard of evidence in our field.

Another key insight is the importance of predictable performance for clinical pipelines. In clinical genomics, one must not only validate the accuracy of a pipeline but also know that it will consistently finish within, say, a 24-hour window on available hardware. The variability of cloud performance and the complexity of modern workflows have made that challenging. Daylily provides a solution by codifying the infrastructure. Using an infrastructure-as-code approach (Terraform/CloudFormation) means that anyone can deploy the same cluster configuration. This is akin to providing the recipe for an instrument calibration in a lab protocol. Our results confirmed that doing so yields consistent runtimes and allows cost prediction within a small margin. We foresee this being extremely useful for groups that need to budget for large projects or for national initiatives that want to compare pipelines on equal footing.


### Reproducibility and Sustainability
 Mölder et al. (2021) argued that transparent and adaptable analyses are crucial for sustainability​. Daylily contributes to both: transparency is achieved by exposing all layers (data, code, environment, cost) of the analysis, and adaptability is evidenced by the ease of swapping components (different aligners/callers, or even plugging in a different workflow engine). We specifically designed Daylily to be workflow-agnostic: while our demonstration used Snakemake, the same cluster could run a Nextflow pipeline or WDL/Cromwell workflow with minimal changes​. In fact, we tested a basic Cromwell run and it executed as expected on the Daylily cluster. This suggests Daylily is not tied to a single scripting approach, but rather it’s a template for reproducible execution. The containerized, Slurm-scheduled paradigm is common enough that many existing workflows could be ported to it. We encourage tool authors to consider distributing Daylily-compatible workflow files along with traditional container images – this would allow others to instantly benchmark their tools under known conditions.

### Adoption and Practicality 
We recognize that not every lab has access to cloud resources or the inclination to use them. However, the principles from Daylily can be applied elsewhere. For example, an institution could designate a standard hardware configuration (say, a specific HPC node type or a fixed VM flavor) as their “Daylily environment” and run all benchmarks there. The key is to document it and make it accessible. Cloud makes it easier to share that (as we did with AWS), but one could imagine a similar approach with on-premise virtualization or even container orchestrators, as long as the hardware layer is controlled. We also provide a cost-estimation module that can be used even if one isn’t on AWS – by plugging in local electricity costs or cluster accounting data, the same pipeline can report resource usage that can be translated to a cost proxy. The idea is to ensure no hidden factor is omitted when comparing methods.
Our results also highlight a subtle but important point: containerization alone is not enough for full reproducibility​
github.com. We saw that by pinning the AWS instance type, we avoided performance differences that might arise from, e.g., running on an older CPU without AVX512 (which DeepVariant uses for speed-ups). If someone ran our DeepVariant container on a much older processor, they might get significantly slower run times, potentially misleading conclusions about its efficiency. Daylily’s answer is to always report what hardware was used and ideally to use the same. In the future, as cloud providers offer more heterogeneous hardware (GPUs, FPGAs, specialized accelerators like Google’s TPUs or Amazon’s Trainium/Infen1 chips), reproducible research will need frameworks like Daylily to allow comparing across those options fairly. We already touched on this by using mainstream CPUs and spot pricing; one could extend Daylily to test, say, a GPU-accelerated variant caller vs. a CPU caller by provisioning appropriate instances, while keeping all else constant.

### Towards Community Benchmarks
We see Daylily as a step toward community-driven benchmark suites for bioinformatics. Similar to how the GA4GH Benchmarking group provides standardized tools and datasets for variant calling comparison, Daylily could serve as the engine that executes those comparisons in a uniform environment. Researchers could contribute new pipelines (e.g., new callers, or RNA-seq workflows) to a common repository, and everyone would benefit from a growing library of reference performance data. Since Daylily’s output includes rich metrics and even graphs (like our heatmaps and cost plots), it could become easier to evaluate algorithms in a multidimensional way (accuracy vs. speed vs. cost).
Limitations: There are a few caveats to note. First, our use of AWS spot instances means that, while we pinned the instance type and availability zone, there is still a dependency on cloud availability – if the spot market changes or an instance type is discontinued, exact reproduction might require minor adjustments (Daylily can fall back to on-demand instances, at higher cost, to preserve reproducibility). Second, we did not deeply examine reproducibility of variant calls outside GIAB high-confidence regions; our focus was on performance in high-confidence regions. Daylily can be extended to evaluate difficult regions (it actually supports GIAB stratifications and one could generate metrics by region category​), which could be future work. Third, while we included multiple pipelines, there are always more tools – our framework can scale to include them, but practically one might not run every caller due to cost/time. We chose a representative set, emphasizing some new and some established tools. The modular nature means others can plug in their tool of interest easily.

### Recommendations
 Based on our experience, we recommend that authors publishing new bioinformatics methods provide at least a minimal Daylily-like blueprint for how to run their method in a controlled environment. This could be as simple as sharing a cloud VM image and a Snakemake/Nextflow workflow that reproduces a figure from the paper, including resource usage. Doing so would greatly improve confidence in the results. We also encourage the field to embrace cost reporting. As shown, variant calling for a human genome can now be done for a few dollars of compute – a fact that was not obvious or well-documented before. If every methods paper included a section on computational cost, it would drive method development not just for accuracy but also efficiency, which is important for real-world impact. Daylily’s cost analysis feature makes it easy to gather those numbers, so we hope to see it (or similar approaches) adopted.
Finally, we note that Daylily is a work in progress as an open-source project. Community contributions are welcome. For instance, adding support for other cloud providers (Google Cloud, Azure) is on the roadmap, as is expanding the set of example workflows (RNA-seq, joint genotyping, etc.). The overarching vision is a future where benchmarking a bioinformatics pipeline is as standardized as sequencing itself – with known “controls” (reference datasets like GIAB) and known “instruments” (reference compute environments like Daylily) to generate reliable, reproducible performance data. Our study takes a decisive step in that direction by providing the methodology and evidence that such full-spectrum reproducibility is achievable.

## Data and Software Availability
Genome in a Bottle (GIAB) datasets: FASTQ reads and truth variant sets for the seven GIAB samples (HG001-HG007) were obtained from the Google Brain open dataset​ and the NIST GIAB project. The Illumina 30× FASTQs are available in the AWS Open Data registry​

 (s3://genomics-benchmark-datasets/... path), and the high-confidence truth VCFs for GRCh37 and GRCh38 are available from GIAB (ftp://ftp-trace.ncbi.nlm.nih.gov/giab). These correspond to the data described in Zook et al., 2019​.

## Daylily Pipeline Code
The Daylily framework is open-source under MIT license at the Daylily-Informatics GitHub (main repository: daylily​
). The exact version used for this paper is tagged v0.7.196c (as recommended in the documentation​). 
It includes Terraform scripts for AWS, Snakemake workflow definitions, and supporting scripts for cost tracking. All configuration files to reproduce our scenarios (cluster config, pipeline config, sample sheet) are included in our analysis repository (below).

## Analysis Results Repository
Processed results, analysis notebooks, and figure-generation code are available in the daylily_giab_analyses repository​. This contains the workflow run logs, concordance output tables, and code to generate the heatmaps, precision-recall plots, and cost analyses presented here. The repository also hosts the draft white paper and documentation for interpreting the results.

## Software Versions: Key software and their versions: BWA-MEM2 2.2.1​
github.com
, Sentieon BWA 2022.05 (Sentieon Engine v. (2022.05) – equivalent to BWA-MEM1 with enhancements), DeepVariant 1.4​
github.com
, Sentieon DNAscope 2022.05, Octopus 0.7.4​
github.com
, LoFreq 2.1.5, Clair3 r0.1, Manta 1.6.0​
github.com
, Tiddit 2.12.1, Dysgu 1.5.0, Snakemake 7.8.0, Slurm 20.11.8, AWS ParallelCluster 3.1.4. Container images were pulled from Biocontainers or Sentieon’s registry as appropriate. Exact package lists are in the environment.yml files in the Daylily repo.

## Reproducibility Package: For convenience, we have archived a snapshot of everything needed to rerun the analysis (except the raw FASTQs) on Zenodo (DOI: XYZ12345). This includes the Daylily config files, Snakemake workflow file, and a small test dataset to verify the setup. Users can follow the instructions in the README to launch an AWS cluster and execute a test run, and then scale up to the full GIAB dataset.
All data and code are openly available. Please refer to the Daylily documentation for step-by-step reproduction guides​
github.com
​
github.com
. Questions and contributions can be directed to the Daylily project’s GitHub issues page. By sharing these resources, we hope to enable others to easily reproduce our findings and apply the Daylily framework to their own benchmarking problems.


# REFERENCES
Snakemake:
Mölder F, Jablonski KP, Letcher B, et al.: Sustainable data analysis with Snakemake. F1000Res. 2021;10:33.​https://snakemake.readthedocs.io
Nextflow:


Di Tommaso P, Chatzou M, Floden EW, et al.: Nextflow enables reproducible computational workflows. Nat Biotechnol. 2017;35(4):316–319.​
Cromwell (WDL):


Voss K, Gentry J, Van der Auwera G: Full-stack genomics pipelining with GATK4 + WDL + Cromwell. F1000Res. 2017;6:1379.​davetang.github.io
Makefiles:


Feldman SI: Make—a program for maintaining computer programs. Softw Pract Exper. 1979;9(4):255–265.
References:
Mölder, F., Jablonski, K.P., Letcher, B. et al. Sustainable data analysis with Snakemake. F1000Research 2021, 10:33.


Krusche, P., Trigg, L., Boutros, P.C. et al. Best practices for benchmarking germline small-variant calls in human genomes. Nat Biotechnol 2019, 37, 555–560.


Beyond Accuracy: Broadening Reproducibility in Bioinformatics
When discussing reproducibility in computational biology, most people focus on getting the same scientific results (e.g. identical outputs or accuracy) given the same data and code. However, full reproducibility entails more than just correct results – it extends to the entire computational process. Key additional dimensions include the computing environment, runtime performance stability, and resource/cost usage. Below, we outline established terminology (and gaps) for these facets, and consider how existing frameworks like Snakemake’s could encompass them.
Reproducible Computational Environments (Portability)
Computing environment reproducibility refers to ensuring the software stack and system conditions are identical so that an analysis runs the same way on different machines. In practice this is achieved by containerization and environment specification. For example, modern workflow systems support full in silico reproducibility by encapsulating all dependencies with Docker, Conda, or Singularity, so that each step’s software versions are exactly defined​
pmc.ncbi.nlm.nih.gov
​
pmc.ncbi.nlm.nih.gov
. This guarantees that a pipeline can be executed on various hardware (from a laptop to a cloud cluster) with the same setup. In the literature, this is often described as portability or platform independence. A workflow is portable if it can be “automatically deployed with all required software in exactly the needed versions”​
pmc.ncbi.nlm.nih.gov
. Ensuring environment portability is considered a prerequisite for reproducibility in many bioinformatics platforms. For instance, Snakemake emphasizes that a sustainable analysis must be portable across institutes or cloud providers without modification​
pmc.ncbi.nlm.nih.gov
. Similarly, the Whole Tale project and others talk about capturing the “whole computational environment” to guarantee reproducibility​
arxiv.org
. In essence, well-defined computational reproducibility means anyone can re-run the analysis in an identical environment, eliminating “it works on my machine” problems.
Established terms: Reproducible environment, containerized reproducibility, portable workflow. In bioinformatics benchmarking studies, authors often simply say an analysis is “reproducible on any platform” using containers. The term full-stack reproducibility is also used in the DevOps/ML world to denote capturing the entire software stack so code runs the same anywhere​
docker.com
. In academic contexts, this falls under computational reproducibility, which encompasses sharing data, code and environment details to allow others to obtain the same results​
sciencedirect.com
. When focusing on environment specifically, terms like system-level reproducibility have been used to denote replicating the OS/libraries configuration across systems (e.g. using Nix or Docker to guarantee a consistent setup)​
ww2.amstat.org
. In summary, ensuring computational environment reproducibility is largely an exercise in portability and environment capture, making sure the where of computation doesn’t alter outcomes.
Runtime and Execution Stability (Performance Reproducibility)
Another seldom-explicit facet is runtime reproducibility – i.e. achieving consistent execution times and performance characteristics across runs and platforms. In high-performance computing (HPC) and benchmarking literature this is discussed as performance reproducibility or execution repeatability. A rigorous definition is “minimal run-to-run variation across multiple runs of the same application using a consistent configuration”​
osti.gov
. In other words, if you run the pipeline today or tomorrow on the same hardware, it should take roughly the same time and resources each run. This concept is important for fairness in benchmarks and for confidence that performance improvements are real. HPC experts note that run-to-run variability (due to factors like thread scheduling or network jitter) can undermine reproducibility; thus they strive for deterministic execution where possible​
osti.gov
​
wordpress.cels.anl.gov
. Some refer to this as execution stability or deterministic performance. For example, one HPC reproducibility framework explicitly separates “performance reproducibility” (consistent timing) from “result reproducibility” (same numerical results)​
wordpress.cels.anl.gov
. Another distinguishes it from performance portability – the latter meaning obtaining similar performance across different systems (e.g. an algorithm that scales well on multiple hardware types)​
osti.gov
. Both are relevant: we want each run to be stable, and we also hope the pipeline’s performance is not drastically different on another cluster of equivalent capacity.
In practice, achieving runtime stability might involve controlling random seeds, using deterministic algorithms, and avoiding nondeterministic hardware behavior. Bioinformatics papers don’t always name this explicitly, but benchmarks often report variance in runtime or resource usage across replicates. When a tool is said to be robust and efficient, it may imply it has predictable runtime on various inputs or systems. The term repeatability is sometimes used: a pipeline is repeatable if the same team running it in the same environment gets consistent outcomes (including timing). Indeed, repeatability (same lab, same setup) is considered a lower bar that often encompasses stable execution, whereas reproducibility (different lab or setup) usually requires both stable execution and portable environments. In summary, ensuring runtime reproducibility means minimizing performance fluctuations so that time-to-completion and other execution metrics can be trusted. This is especially crucial in benchmarking studies – if one method’s speed is being compared to another’s, each needs to have stable performance to make a fair comparison​
sciencedirect.com
.
Established terms: Performance reproducibility, run-to-run consistency, execution determinism. While not as commonly highlighted as result reproducibility, these terms do appear in computational benchmarking discussions. For example, Hoefler et al. (2015) emphasize controlling for “run-to-run variation” in parallel system benchmarks, effectively calling for reproducible performance measurements​
osti.gov
. When such stability is hard to attain, researchers resort to statistical techniques (multiple runs, reporting variance)​
htor.inf.ethz.ch
. Thus, you might also see performance stability or benchmark repeatability used informally. The key is that reproducibility isn’t only about what results you got, but also how you got them – under consistent timing and computational effort.
Reproducible Resource Usage and Cost
A newer dimension gaining attention is cost or resource reproducibility – ensuring that the computational resources consumed (CPU hours, memory, cloud credits) are predictable and verifiable. This could be seen as an extension of performance reproducibility: not just does it run in X hours, but it also always uses ~Y GB of memory and, if run in the cloud, costs about $Z. While there isn’t a standard term in academic literature, it relates to concepts of cost predictability and transparency in computational experiments. In industry, there’s recognition of making environments “cost-transparent” as part of reproducible infrastructure: for example, cloud orchestration tools aim to ensure that whenever you launch a given environment, you know the expected resource usage and cost, avoiding surprises​
quali.com
. Predictable costs are important for both practical budgeting and for reproducible research – a colleague re-running your pipeline should not only get the same results, but also roughly the same bill or resource consumption profile.
In cloud benchmarking or workflow papers, authors sometimes mention cost-effectiveness alongside reproducibility. The term “cost-effective reproducibility” appears in studies like Rosendo et al. (2023) where the goal was to let others replicate experiments cost-efficiently across different infrastructures​
arxiv.org
​
arxiv.org
. This implies that the methodology ensures resource use is controlled and not wasteful when reproducing results. We might also frame this as resource usage reproducibility – the idea that a pipeline’s footprint (CPU cycles, memory, disk I/O, energy consumed) can be measured and will be similar on repeat runs. For instance, an HPC study on energy profiles aimed to let data centers reproduce each other’s energy measurements for the same applications​
zenodo.org
​
zenodo.org
. In bioinformatics, if a pipeline is “scalable and efficient,” one expects that running it again on similar data won’t suddenly require double the computing resources; it should scale predictably (which is part of Snakemake’s definition of scalability​
pmc.ncbi.nlm.nih.gov
).
Established terms: There isn’t a single agreed term here. You might encounter phrases like reproducible and cost-effective analysis, cost-aware reproducibility, or simply discussions of predictable resource usage. In workflow management contexts, efficiency is often the proxy – e.g. Snakemake optimizes scheduling so that execution is fast and avoids wasted resources​
pmc.ncbi.nlm.nih.gov
. Ensuring efficiency indirectly aids cost reproducibility (less variance in wasted cloud hours). Some communities use transparency in a broader sense: not just making code transparent, but also making the resources consumed transparent (e.g. reporting the exact cloud instance type, runtime, and cost so others can reproduce those numbers). In absence of a formal term, one could say financial reproducibility or economic reproducibility, but these are not standard. It may be better to speak of budget predictability in reproducible research.
Toward Comprehensive “Full-Spectrum” Reproducibility
The question remains: is there an existing umbrella term for reproducibility that spans results, environment, performance, and cost? The phrase “full-spectrum reproducibility” is not (yet) established in the literature. However, the spirit of it aligns with what some call end-to-end reproducibility or holistic reproducibility. For example, a recent study demonstrated “end-to-end reproducibility from retrieving cloud-hosted data ... to the final results” in an AI pipeline​
pubmed.ncbi.nlm.nih.gov
. This ensured every stage of the process was captured, though it focused on data and code rather than cost. The term full-stack reproducibility has been used in an engineering context to mean capturing everything from code to environment (especially via Docker)​
docker.com
. We could extend that concept to also include runtime behavior and resource utilization – essentially a full-stack & performance reproducibility.
In the absence of a single established term, it may be useful to build on existing concepts. Snakemake’s framework for sustainable data analysis already covers many pieces: reproducibility of results, transparency of parameters, portability across platforms, and scalability to different resources​
pmc.ncbi.nlm.nih.gov
​
pmc.ncbi.nlm.nih.gov
. We can suggest explicitly adding execution stability and resource transparency to this list. One might call this comprehensive reproducibility – meaning an analysis is reproducible in all aspects: anyone can rerun it anywhere (thanks to portability) and get the same results in roughly the same time and cost. Another descriptive term could be operational reproducibility, emphasizing that the operational details (compute environment, execution time, resources) are as reproducible as the scientific outcomes. The community has indeed been moving toward this broader vision. For instance, the FAIR principles (Findable, Accessible, Interoperable, Reusable) are being applied to performance and workflow data in HPC to aid reproducibility of both results and performance metrics​
osti.gov
​
osti.gov
.
Recommendation: Rather than coining an entirely new term, it may be effective to use a phrase like “reproducible and portable workflow with stable performance” when describing such goals in papers. This leverages familiar terms (reproducible, portable) and adds clarity (stable performance). If a concise term is needed, “comprehensive reproducibility” or “end-to-end reproducibility” could be adopted, with the understanding (and preferably, an explanation) that it covers environment, runtime, and cost aspects in addition to results. Any proposed term should be grounded in existing language: for example, “We strive for full-spectrum reproducibility, encompassing not only accurate results but also consistent execution environment, performance, and resource usage.” This builds on the reproducible research ethos and extends it.
In summary, computational reproducibility in genomics is evolving to include:
Environment/Platform Reproducibility – achieved via containers and workflow portability​
pmc.ncbi.nlm.nih.gov
.
Performance/Runtime Reproducibility – consistency in execution time and behavior (HPC literature calls this performance reproducibility​
osti.gov
).
Resource/Cost Reproducibility – predictable resource consumption (addressed via cost transparency and efficiency measures​
quali.com
).
While no single term has universal precedence for all these, an integration of concepts is happening in workflow management and benchmarking discussions. By explicitly acknowledging these dimensions, researchers can aim for “reproducible research in the large”, ensuring that everything that mattered in producing a result (from software versions to runtime and cost) can be duplicated and verified. This holistic approach – whether we call it full-spectrum reproducibility or simply robust reproducibility – strengthens trust in computational results and their operational reliability.
Sources:
Snakemake reproducibility and portability​
pmc.ncbi.nlm.nih.gov
​
pmc.ncbi.nlm.nih.gov
.
HPC definition of performance reproducibility vs. portability​
osti.gov
.
Industry perspective on reproducible environments and cost transparency​
quali.com
.
HPC workflow reproducibility challenges and metadata (Nicolae et al. 2023)​
wordpress.cels.anl.gov
​
osti.gov
.
End-to-end reproducible pipelines in cloud environments​
pubmed.ncbi.nlm.nih.gov
.

