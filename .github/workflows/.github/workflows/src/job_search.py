name: Job Search Test

on:
  workflow_dispatch:

jobs:
  search-jobs:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install requests

      - name: Run job search
        run: |
          python src/job_search.py
