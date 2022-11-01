# Data Science project template

A short description of the project.

## Project Organization

    ├── askanna.yml        <- Configuration file for AskAnna
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    ├── data
    │   ├── input          <- The original, immutable data (dump)
    │   ├── interim        <- Intermediate data sets
    │   └── processed      <- The final prepped data sets for modeling
    │
    ├── docs               <- A Sphinx set up including markdown support (see sphinx-doc.org for details)
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- A location for your project related Jupyter notebooks
    │
    ├── src                <- Source code for use in this project
    │   ├── __init__.py    <- Makes code a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   ├── create_dataset.py
    │   │   └── create_features.py
    │   │
    │   └── models         <- Scripts to train models and then use trained models to serve a result
    │      ├── serve_model.py
    │      └── train_model.py
    │
    ├── .env               <- Environment file for local development
    ├── .gitignore         <- Files or directories that should not be pushed to AskAnna
    └── README.md          <- This document

--------
This data science template is inspired by [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/).
