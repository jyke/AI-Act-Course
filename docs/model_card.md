---
license: mit
language:
- en
datasets:
- iris
metrics:
- accuracy
- f1
pipeline_tag: tabular-classification
tags:
- sklearn
- random-forest
- iris
- classification
---

# Model Card — Iris Flower Classifier

## Model Details

- **Model name**: Iris Flower Classifier
- **Author**: Liora
- **Date**: 2026-06-22
- **Version**: 1.0
- **Model type**: `RandomForestClassifier` (scikit-learn), 100 estimators, `random_state=42`
- **License**: MIT

## Intended Use

### Intended use cases

The model predicts the species of an Iris flower (`setosa`, `versicolor`, or `virginica`) from four measurements: sepal length and width, and petal length and width.

It is intended for learning, technical demonstrations, supervised-classification exercises, and ML pipeline experiments.

### Out-of-scope use

- Not intended for production: robustness testing, cross-validation, and regulatory review have not been performed.
- Not intended for high-impact decisions or medical, legal, or commercial use.
- Not expected to generalize to real-world data: the training dataset is small, clean, and not representative of varied field conditions.

## Factors (Facteurs)

1. **Input feature distribution**: Training measurements come from a small, homogeneous dataset. A shift in measurement protocol or atypical specimens may reduce performance.
2. **Class balance**: Iris contains 50 examples per class. Performance under real-world class imbalance has not been evaluated; a skewed distribution could favor the majority class.

## Metrics (Métriques)

For this multiclass task, accuracy is reported alongside per-class precision, recall, and F1. Macro averages give equal weight to each class.

Results on the 30-example test split (`test_size=0.2`, `random_state=42`):

| Class | Precision | Recall | F1-score | Support |
|---|---:|---:|---:|---:|
| setosa | 1.00 | 1.00 | 1.00 | 10 |
| versicolor | 1.00 | 1.00 | 1.00 | 9 |
| virginica | 1.00 | 1.00 | 1.00 | 11 |
| **Accuracy** |  |  | **1.00** | **30** |
| Macro average | 1.00 | 1.00 | 1.00 | 30 |
| Weighted average | 1.00 | 1.00 | 1.00 | 30 |

An accuracy of 1.00 on this small, well-separated benchmark does not indicate expected performance on field data.

## Training Data (Données d'entraînement)

- **Dataset**: Iris flower dataset (Fisher, 1936)
- **Source**: `sklearn.datasets.load_iris()`
- **Total size**: 150 examples; 120 used for training (80%)
- **Features**: `sepal length (cm)`, `sepal width (cm)`, `petal length (cm)`, and `petal width (cm)`
- **Target**: flower species (`setosa`, `versicolor`, `virginica`)
- **Preprocessing**: none; no missing values or normalization are used for this random forest.
- **Known limitations**: the dataset is small and historically collected at one location (Gaspé Peninsula, Canada); it does not represent global botanical diversity.

## Evaluation Data (Données d'évaluation)

- **Source**: held-out partition of the same Iris dataset
- **Size**: 30 examples (20% of the dataset)
- **Split**: `train_test_split(test_size=0.2, random_state=42)`; a reproducible random split
- **Preprocessing**: none
- **Limitation**: evaluation on a split from the same dataset does not establish generalization to new data. No external benchmark was used.

## Quantitative Analyses (Analyses quantitatives)

The test results are identical across the three classes: precision, recall, and F1-score are each 1.00, with supports of 10 (`setosa`), 9 (`versicolor`), and 11 (`virginica`). This is consistent with the strong class separation in this benchmark. It is not evidence of general robustness; errors and class-level disparities may arise for morphologically similar specimens or data collected under different conditions.

## Ethical Considerations (Considérations éthiques)

The model classifies flowers, not people, so it has no direct human-subject impact in its intended educational use. Using it for consequential scientific or commercial decisions would be inappropriate without further validation. The dataset's single historical collection context and balanced class counts may fail to represent natural variation in geography, climate, season, and species frequency.

## Caveats and Recommendations (Limites et recommandations)

- **Small dataset (150 observations)**: do not generalize from this evaluation alone. Validate on a larger and more diverse dataset.
- **Single train/test split**: the reported metrics come from one split. Use 5- or 10-fold cross-validation for a more stable performance estimate before any applied use.
- **Limited real-world representativeness**: test on specimens collected across regions, seasons, and measurement protocols before using the model in an applied setting.
- **No post-deployment monitoring**: if used on ongoing data, monitor input distributions for data drift and reassess performance.

## Reproducibility

- **Training script**: `train.py`
- **Dataset loader**: `sklearn.datasets.load_iris()`
- **Split**: `train_test_split(test_size=0.2, random_state=42)`
- **Estimator**: `RandomForestClassifier(n_estimators=100, random_state=42)`
- **Git commit (git_sha)**: unavailable; this directory is not inside a Git repository.
- **MLflow run ID**: N/A (not used in this chapter)
- **Dataset hash**: N/A (not recorded in this chapter)
