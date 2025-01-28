# Load necessary libraries
library(ggplot2)
library(dplyr)
library(tidyr)

# Accept genome build and data path from command line arguments
args <- commandArgs(trailingOnly = TRUE)
genome_build <- ifelse(length(args) > 0, args[1], "hg38")
data_path <- ifelse(length(args) > 1, args[2], "src_data/hg38_7giab_allvall_benchmarks_summary.tsv")

# Read the data
data <- read.table(data_path, header = TRUE, sep = "\t")

# Filter to remove NaNs and unnecessary columns
data <- data %>%
  filter(!is.na(Fscore)) %>%
  select(SNPClass, Aligner, SNVCaller, AltId, Fscore, Sensitivity.Recall, Specificity, FDR, PPV, Precision)

# Reshape data to long format for easier plotting
data_long <- data %>%
  pivot_longer(cols = c(Fscore, Sensitivity.Recall, Specificity, FDR, PPV, Precision),
               names_to = "Metric",
               values_to = "Value")

# Create and save standalone plots for each SNPClass
unique_classes <- unique(data_long$SNPClass)

for (class in unique_classes) {
  plot_data <- data_long %>% filter(SNPClass == class)

  for (metric in unique(plot_data$Metric)) {
    metric_data <- plot_data %>% filter(Metric == metric)

    # Generate plot
    p <- ggplot(metric_data, aes(x = interaction(Aligner, SNVCaller), y = Value, color = AltId)) +
      geom_point(size = 1.5, alpha = 0.7) +
      labs(title = paste("Metric:", metric, "| SNP Class:", class, "| Genome Build:", genome_build),
           x = "Aligner-SNV Caller",
           y = metric,
           color = "GIAB Sample") +
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 45, hjust = 1))

    # Save each metric's plot as a PDF
    ggsave(filename = paste0("plot_", genome_build, "_", class, "_", metric, ".pdf"), plot = p, device = "pdf", width = 10, height = 6)
  }
}
