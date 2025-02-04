
---
---
# A WIP and EXPERIMENT In Drafting A Paper W/Chatgpt
---
---
# Draft Introduction/Summary for Daylily

*Note: I have embedded comments/suggestions in double parentheses “((…))” for your consideration.*


# Introduction

Modern bioinformatics pipelines have become increasingly complex, yet the community often struggles with *consistent*, *transparent*, and *reproducible* assessments of, and comparisons among the many tools available. A growing challenge in reporoducibility is reporducible computation time(and thus cost), which is a now necessary factor in assessing any informatics tools. Challenges stem from a variety of sources: the rapidly evolving hardware landscape (ranging from commodity CPUs to specialized GPUs and proprietary accelerators), paywalled or hybrid-licensed software that impedes broad adoption, heterogeneous hardware environments, competing cloud compute provider ecosystems, and an over-reliance on outdated "best practices" (which I argue, have lagged in large part because comparing tools, and by extension, comparing iterations of pipelines, has been so fraught. These issues create an environment where comparing performance—both in terms of *accuracy* and *cost*—is more difficult than it needs to be. `daylily` offers an approach to assert reproducible accuracy/outputs of tools as well as reproducible computation/cost performance.

Compounding this problem is the tendency to focus solely on final, often overly reductive, accuracy metrics (such as aggregated F1 scores) without fully evaluating more sensitive metrics more appropriate to context-specific use cases, say precision or recall, time-to-result, and detailed runtime costs. Moreover, many supposedly reproducible pipelines fail to yield reproducible *performance* when deployed in different compute environments. Although containerization and robust workflow managers have brought greater consistency to outputs, they do not guarantee identical runtimes or costs. In clinical and large-scale research settings, such cost variability can be a deciding factor in which tools or workflows are ultimately adopted.

**Daylily** is designed to address these gaps by offering a *reproducible, cost-aware, and hardware-explicit* framework for end-to-end bioinformatics analyses—from raw data to variant calls—with emphasis on **transparency**, **consistency**, and **benchmarking**. It leverages infrastructure-as-code to provision standardized compute resources, ties in rigorous cost-tracking at every stage, and simplifies tool comparisons using widely accepted reference datasets (notably the 7 **Genome in a Bottle** (GIAB) samples). 

In this paper, we demonstrate Daylily in action by processing the 7 GIAB samples (using 30× Illumina data provided by the Google Brain project) with **3 different aligners** (including the new Strobe aligner). The resulting mapped data are then passed through **5 SNV callers**, **3 SV callers**, and **N QC tools** to produce a detailed set of variant-calling and quality-control metrics. This approach enables a *clear, formal comparison* of accuracy and runtime across multiple pipelines. By standardizing both software versions and compute hardware, we achieve genuinely reproducible results—covering the full spectrum of runtime performance, cost, and variant-calling accuracy.

Through these analyses, we illustrate how Daylily can serve as a blueprint for developing, benchmarking, and deploying bioinformatics workflows in a manner that is truly transparent and reproducible, and we invite the community to explore and contribute to this evolving platform.

## Introduction

High-throughput sequencing (HTS) technologies have revolutionized clinical genomics by enabling rapid and cost-effective generation of massive volumes of data. Yet, the process of selecting, comparing, and deploying the computational tools required to transform raw sequence data into biologically and clinically actionable findings remains extraordinarily challenging. Tools such as sequence aligners (e.g., BWA-MEM [(Li 2013)](#ref-li2013), BWA-MEM2 [(Vasimuddin et al. 2019)](#ref-vasimuddin2019), minimap2 [(Li 2018)](#ref-li2018)), small variant callers (e.g., DeepVariant [(Poplin et al. 2018)](#ref-poplin2018), GATK [(McKenna et al. 2010)](#ref-mckenna2010), Octopus [(Cooke et al. 2021)](#ref-cooke2021)), structural variant callers (e.g., Manta [(Chen et al. 2016)](#ref-chen2016)), and workflow executors (e.g., Snakemake [(Köster & Rahmann 2012)](#ref-koster2012), Nextflow [(Di Tommaso et al. 2017)](#ref-ditommaso2017)) are heavily used but rarely evaluated under standardized, transparent conditions. **Daylily** is designed to address this gap by offering a reproducible, cost-aware, and hardware-explicit framework for end-to-end bioinformatics analyses—from raw data to variant calls—with emphasis on transparency, consistency, and benchmarking.

((Comment: In this paragraph, I tried to give a high-level introduction and also weave in specific tool references. Let me know if the tone or length is appropriate.))

---

## Rationale and Challenges

1. **Lack of Transparent and Standardized Benchmarks**  
   For many tool developers and researchers, there is a perceived fear that head-to-head comparisons could “look bad” if their tool underperforms on certain metrics. Consequently, many publications and workflows either omit direct comparisons or use simplified/obscure metrics like an aggregated F-score that glosses over context-specific performance (e.g., tool “X” may have excellent precision but middling overall F1, or vice versa).  
   - Such practices limit the field’s ability to thoroughly assess which tool is optimal for a specific use case.  
   - **Genome in a Bottle** (GIAB) reference datasets [(Zook et al. 2019)](#ref-zook2019) represent a comprehensive standard for small variant detection in various genomes (e.g., NA12878, NA24385, etc.), yet many published comparisons fail to include these critical benchmarks.  
   - **((Suggestion: Possibly give a brief overview of the GIAB sample set here, if space allows, to emphasize why it’s so crucial.))**

2. **Inconsistent and Often Irreproducible Cost and Runtime Assessments**  
   Reproducible results in terms of variant calling or alignment accuracy alone have become easier to achieve through containerization and improved workflow management. However, reproducibility of *runtime* and *cost* remains elusive. For many labs, the computational resources needed to run a pipeline can vastly affect whether a particular tool is viable, particularly if it requires specialized hardware such as GPUs or proprietary accelerators like Dragen.  
   - Even open-source workflows may be prohibitively expensive in certain cloud environments if the hardware is not explicitly accounted for in the design.  
   - **((Comment: Here you might add an example illustrating how two identical pipelines can have very different costs depending on instance types or ephemeral storage costs.))**

3. **Over-Reliance on “Best Practices” That Quickly Become Obsolete**  
   Despite rapid advances in algorithms and hardware, the field often clings to “best practices” from leading institutions or tool authors, even when such practices are not rigorously updated or benchmarked. While frameworks like GATK were once considered the “gold standard,” many studies have demonstrated improved or more targeted accuracy with newer approaches. Without a transparent comparative ecosystem, “best practices” can remain static for years.  
   - **((Comment: The statement regarding “best practices” being potentially unethical in clinical settings might need to be phrased carefully, depending on the audience’s tolerance for strong language.))**

4. **Divergent Workflow Managers and Cluster/Container Complexities**  
   Snakemake, Nextflow, CWL, and many other workflow engines each have passionate advocates. In truth, these managers mostly address reproducibility of *outputs* (i.e., ensuring the same commands are run on the same data). They do not inherently guarantee reproducible performance in terms of runtime or cost, especially in dynamic scheduling or container-orchestrated environments.  
   - **Daylily** leverages the powerful features of Snakemake [(Köster & Rahmann 2012)](#ref-koster2012) but keeps the door open for alternative systems by providing an infrastructure-as-code approach for cluster provisioning, job scheduling, and cost tracking.

5. **Need for Explicit Hardware Selection and Infrastructure-as-Code**  
   Historically, each laboratory or institution maintained a unique (sometimes “snowflake”) high-performance computing cluster, making it difficult to reproduce analyses outside that environment. Now, cloud computing offers on-demand scaling, but also introduces a bewildering array of hardware and service options—some open, some proprietary.  
   - Daylily provides a consistent hardware environment (built on AWS using infrastructure-as-code with Terraform and Slurm) that researchers can instantiate and tear down repeatedly with minimal effort.  
   - By eschewing deeply proprietary add-ons (where possible) and focusing on Slurm-based scheduling, Daylily aims to preserve a level of hardware agnosticism, thereby facilitating reproducibility on non-cloud or other cloud platforms.  
   - **((Suggestion: If you intend for Daylily to be easily portable to GCP or Azure in the future, consider clarifying any known dependencies that might need reconfiguration.))**

6. **Persistent Cost Tracking and Analysis**  
   A key innovation in Daylily is integrating cost analysis (and potentially real-time cost gating) directly into the workflow. In many bioinformatics projects, cost is an afterthought, but it can be the decisive factor in clinical and research contexts. Daylily’s design ensures that cost data are collected alongside runtime and accuracy metrics, enabling users to optimize not only for performance but also for budget.  
   - **((Comment: You might detail the mechanism for real-time cost gating here—e.g., hooking into AWS billing APIs or Slurm job costing.))**

7. **Reliance on a Shared Filesystem Approach**  
   Many genomic tools (e.g., MultiQC, structural variant callers) rely on scanning a common filesystem for outputs and intermediate files. Kubernetes-based solutions can complicate such workflows unless a parallel filesystem or distributed volume is overlaid to mimic a shared resource. Daylily’s emphasis on Slurm and AWS FSx for Lustre addresses these workflow needs cleanly, leveraging high-performance parallel I/O while mirroring data to S3 for persistence.

---

## The Daylily Framework

**Daylily** is an open source blueprint that integrates the following components into a cohesive, reproducible system:

- **Infrastructure**: Automated provisioning of an AWS-based Slurm cluster using Terraform, including FSx for Lustre as the shared, high-performance filesystem.  
- **Workflow**: A Snakemake-based analysis pipeline that can be extended or swapped out for other managers, enabling flexible tool integration and versioning.  
- **Cost and Runtime Monitoring**: Built-in hooks to track compute costs (per job, per instance type) and runtime metrics.  
- **Benchmarks and Standards**: Inclusion of GIAB datasets [(Zook et al. 2019)](#ref-zook2019) for robust variant-calling comparisons, along with recommended standard metrics (precision, recall, F1, etc.) to capture both global and subset-specific performance (e.g., calling accuracy in difficult genomic regions).  
- **Reproducibility**: Container-based runtime for tool versions plus pinned AWS machine images ensure that performance benchmarks can be re-created and validated by external parties.  

((Comment: If you like, you can expand on each bullet with more details. I kept them concise here.))

---

## Conclusion

Daylily aspires to foster a culture of open, rigorous tool assessment in clinical genomics. By tying together reproducible hardware environments, robust cost and runtime monitoring, standardized benchmarking datasets, and community-driven workflow frameworks, it directly addresses a longstanding need for clarity and accountability in bioinformatics tool selection. We invite the community to explore, critique, and contribute to Daylily’s roadmap, ensuring that future developments in genomic data analysis are both *innovative* and *transparent*.

((Comment: Feel free to adjust the closing paragraph’s tone and emphasis. You might also add a final note about how to get involved, link to your GitHub, or mention future directions.))

---

## References

<a id="ref-li2013"></a>  
Li, H. (2013). Aligning sequence reads, clone sequences and assembly contigs with BWA-MEM. *arXiv preprint arXiv:1303.3997*.

<a id="ref-vasimuddin2019"></a>  
Vasimuddin, Md., Misra, S., Li, H., & Aluru, S. (2019). Efficient Architecture-Aware Acceleration of BWA-MEM for Multicore Systems. *arXiv preprint arXiv:1907.12992*.

<a id="ref-li2018"></a>  
Li, H. (2018). Minimap2: pairwise alignment for nucleotide sequences. *Bioinformatics*, 34(18), 3094-3100.

<a id="ref-poplin2018"></a>  
Poplin, R., Menozzi, V., Decap, D. et al. (2018). A universal SNP and small-indel variant caller using deep neural networks. *Nature Biotechnology*, 36, 983-987.

<a id="ref-mckenna2010"></a>  
McKenna, A., Hanna, M., Banks, E. et al. (2010). The Genome Analysis Toolkit: a MapReduce framework for analyzing next-generation DNA sequencing data. *Genome Research*, 20, 1297–1303.

<a id="ref-cooke2021"></a>  
Cooke, D. P., Waring, J., & Sealfon, R. S. (2021). Octopus: Improving population-level variant calling using partial-phase information. *Nature Communications*, 12, 6617.

<a id="ref-chen2016"></a>  
Chen, X., Schulz-Trieglaff, O., Shaw, R. et al. (2016). Manta: rapid detection of structural variants and indels for germline and cancer sequencing. *Bioinformatics*, 32(8), 1220-1222.

<a id="ref-ditommaso2017"></a>  
Di Tommaso, P., Chatzou, M., Floden, E. et al. (2017). Nextflow enables reproducible computational workflows. *Nature Biotechnology*, 35, 316–319.

<a id="ref-koster2012"></a>  
Köster, J. & Rahmann, S. (2012). Snakemake—a scalable bioinformatics workflow engine. *Bioinformatics*, 28(19), 2520–2522.

<a id="ref-zook2019"></a>  
Zook, J. M., Catoe, D., McDaniel, J. et al. (2019). An open resource for accurately benchmarking small variant and reference calls. *Nature Biotechnology*, 37, 561–566.
