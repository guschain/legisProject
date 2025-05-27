# 🇵🇹 Parlamento Data Pipeline

This project automates the daily retrieval of open data from the official Portuguese Parliament “Dados Abertos” portal. The data is programmatically downloaded, parsed, and stored as clean .csv files for further use.

# 📦 What it collects

The scraper retrieves and processes three main categories of parliamentary data:

* **Iniciativas Legislativas** - Details on proposed legislation, voting records, and parliamentary decisions.

* **Atividades Parlamentares** - Includes interventions, presence records, and other activity logs.

* **Informação Base** - Reference data such as parties, deputies, legislatures — essential for linking activity and vote records to individuals and affiliations.

# 🔁 Daily Automation

A GitHub Actions workflow runs every day at 03:00 UTC, regenerating the .csv files and uploading them as assets to the latest release (latest-data). These are available for use without bloating the Git repository.

# 🔧 Future: ETL and Dataset Publishing

The next phase will perform ETL (Extract, Transform, Load) steps to:

* **Merge the three data sources**

* **Clean and normalize fields**

* **Build structured datasets that allow analysis like:**

    1. Party-level vote alignment
    2. Alignment between different parties
    3. Legislative throughput per legislature
    4. Vote outcomes


The result will be a unified dataset per legislature period, suitable for direct analysis or import into visualization platforms.

# 📁 How to Use the Data

You can programmatically download the latest raw CSVs from the release:

gh release download latest-data --pattern '*.csv' --dir data --clobber

Or use them directly in Python:

import pandas as pd

df = pd.read_csv(
    "https://github.com/guschain/legisProject/releases/download/latest-data/AtividadesXVI_json_txt.csv"
)

# 💡 Motivation

This project aims to support political data transparency, reproducible research, and civic tech initiatives by making raw legislative data easier to access and use.

# 📄 License

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.txt) – see the LICENSE file for details.
