# daylily_giab_analyses

# `daylily` version `0.7.160`
Used to create these reuslts

## S3 Full Data Set
- LINK


## Cluster Creation

### Determine Most Cost Effective Region
```bash
conda activate DAYCLI

export AWS_PROFILE=daylily

./bin/check_current_spot_market_by_zones.py --profile $AWS_PROFILE -o ./day_clu_cost_predictions.tsv

```

Will produce cost estimate details for the specified availability zones. For example:

~[](docs/images/cost_predictions.png)


### Run Complete `daylily` WGS Analysis


#### Genome Build `hg38`

```bash

```


#### Genome Build `b37`

```bash

```
