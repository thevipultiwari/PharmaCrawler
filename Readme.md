# PubMed Pharmaceutical Paper Fetcher

A Python tool for fetching research papers from PubMed that have authors affiliated with pharmaceutical or biotech companies.

## Overview

This tool searches PubMed using standard query syntax and identifies papers with at least one author from a pharmaceutical or biotechnology company. It exports the results as a CSV file with detailed information about non-academic authors and their company affiliations.

## Features

- **PubMed Integration**: Uses NCBI Entrez API for reliable paper fetching
- **Smart Affiliation Detection**: Identifies pharmaceutical/biotech companies using multiple heuristics
- **Flexible Query Support**: Supports full PubMed query syntax
- **CSV Export**: Structured output with all required fields
- **Command-line Interface**: Easy to use with various options
- **Rate Limiting**: Respects NCBI API guidelines (3 requests/second)

## Installation

### Prerequisites
- Python 3.8 or higher
- Poetry for dependency management

### Setup

1. Clone the repository:git clone https://github.com/thevipultiwari/PharmaCrawler.git
cd PharmaCrawle

2. **Install dependencies using Poetry:**
poetry install

3. **Activate the virtual environment:**
poetry shell

4. **Verify installation:**
get-papers-list --help

## Usage

### Command Line Interface

The tool provides an executable command `get-papers-list` with the following syntax:
get-papers-list "your query" [OPTIONS]

#### Options:
- `-d, --debug`: Print debug information during execution
- `-f, --file FILENAME`: Specify filename to save results (CSV format)
- `--help`: Show help message and exit

#### Examples:

1. **Basic search** (output to console):
get-papers-list "COVID-19 AND vaccine"

2. **Save to file:**
get-papers-list "cancer treatment" --file cancer_papers.csv

3. **Debug mode:**
get-papers-list "diabetes" --debug

4. **Complex PubMed query:**
get-papers-list "(cancer[Title]) AND (2023[PDAT]) AND (pharmaceutical[Affiliation])" --file results.csv --debug

5. **Pharmaceutical-specific search:**
get-papers-list "pharmaceutical AND clinical trial" --debug --file pharma_results.csv


### Output Format

The CSV output contains the following columns:

| Column | Description |
|--------|-------------|
| **PubmedID** | Unique PubMed identifier |
| **Title** | Full paper title |
| **Publication Date** | Publication date (YYYY-MM-DD format) |
| **Non-academic Author(s)** | Names of authors from pharma/biotech companies (semicolon-separated) |
| **Company Affiliation(s)** | Names of pharmaceutical/biotech companies (semicolon-separated) |
| **Corresponding Author Email** | Email of corresponding author or "Not available" |

### Sample Output
PubmedID,Title,Publication Date,Non-academic Author(s),Company Affiliation(s),Corresponding Author Email
36702617,The Infectious Diseases Society of America Guidelines on the Diagnosis of COVID-19: Antigen Testing (January 2023).,2024-06-27,M Hassan Murad,Roche,Not available
35171037,Bean Extract-Based Gargle for Efficient Diagnosis of Active COVID-19 Infection Using Rapid Antigen Tests.,2022-02-16,Sangmin Lee; Duwoon Kim,BioApplications,Not available



### Module Descriptions

#### Core Modules (`pubmed_pharma_fetcher/core/`)

- **`pubmed_client.py`**: Handles all PubMed API interactions using NCBI Entrez. Includes rate limiting, error handling, and data models for papers and authors.

- **`affiliation_parser.py`**: Analyzes author affiliations to identify pharmaceutical and biotech companies using multiple detection methods:
  - Known company database matching
  - Corporate keyword detection
  - Email domain analysis
  - Academic institution exclusion

- **`data_processor.py`**: Processes paper data and handles CSV export with proper formatting and field extraction.

#### Utility Modules (`pubmed_pharma_fetcher/utils/`)

- **`validators.py`**: Input validation and sanitization for queries and filenames to ensure safe API usage and file operations.

#### Configuration (`pubmed_pharma_fetcher/config/`)

- **`companies.json`**: Comprehensive database of pharmaceutical and biotech companies, including major global companies and Indian pharmaceutical companies.

## How It Works

1. **Query Processing**: Validates and sanitizes the input query using PubMed syntax rules
2. **Paper Search**: Uses NCBI Entrez API to search PubMed with proper rate limiting
3. **Detail Fetching**: Retrieves full paper details including author affiliations in batches
4. **Affiliation Analysis**: Identifies non-academic authors using multiple approaches:
   - Known pharmaceutical/biotech company database (500+ companies)
   - Corporate keywords (Inc., Ltd., Corp., Pharmaceuticals, Biotech)
   - Email domain analysis (corporate vs. academic domains)
   - Exclusion of academic institutions (Universities, Hospitals, Research Centers)
5. **Data Export**: Formats results and exports to CSV with all required fields

## Company Detection Logic

### Known Companies Database
The system includes an extensive database of:
- **Major pharmaceutical companies**: Pfizer, Novartis, Roche, Johnson & Johnson, Merck, etc.
- **Biotech companies**: Genentech, Amgen, Moderna, Biogen, etc.
- **Indian pharmaceutical companies**: Sun Pharmaceutical, Lupin, Dr. Reddy's, Cipla, etc.

### Heuristic Detection
- **Corporate suffixes**: Inc., Ltd., Corp., Company, AG, GmbH, SA, plc
- **Industry keywords**: Pharmaceuticals, Pharma, Biotech, Biotechnology
- **Email domains**: Corporate domains (.com, .net) vs. academic (.edu, .ac.uk)

### Academic Institution Exclusion
Filters out academic affiliations containing:
- Universities, Colleges, Institutes
- Hospitals and Medical Centers  
- Research Centers and Laboratories
- Government research institutions

## Dependencies and Tools Used

### Core Dependencies
- **[Biopython](https://biopython.org/)** (^1.81) - NCBI Entrez API access and bioinformatics utilities
- **[Click](https://click.palletsprojects.com/)** (^8.1.0) - Command-line interface framework
- **[Pandas](https://pandas.pydata.org/)** (^2.0.0) - Data manipulation and analysis
- **[Requests](https://docs.python-requests.org/)** (^2.31.0) - HTTP requests for API calls
- **[LXML](https://lxml.de/)** (^4.9.0) - XML parsing for PubMed data
- **[python-dateutil](https://dateutil.readthedocs.io/)** (^2.8.2) - Date parsing utilities

### Development Dependencies
- **[pytest](https://pytest.org/)** (^7.4.0) - Testing framework
- **[Black](https://black.readthedocs.io/)** (^23.0.0) - Code formatting
- **[MyPy](https://mypy.readthedocs.io/)** (^1.5.0) - Static type checking
- **[Flake8](https://flake8.pycqa.org/)** (^6.0.0) - Code linting

### Development Tools and LLM Assistance
This project was built with assistance from:
- **[Perplexity AI](https://www.perplexity.ai/)** - Research assistance, API documentation lookup, and code implementation guidance
- **[Poetry](https://python-poetry.org/)** - Modern dependency management and packaging
- **[Git](https://git-scm.com/)** - Version control system
- **[GitHub](https://github.com/)** - Code hosting and collaboration platform

### External APIs
- **[NCBI Entrez API](https://www.ncbi.nlm.nih.gov/books/NBK25497/)** - PubMed database access

## API Limitations and Considerations

- **Rate Limiting**: Maximum 3 requests per second without API key (automatically handled)
- **Batch Processing**: Processes papers in batches of 50 to respect API limits
- **Email Availability**: Approximately 50% of PubMed papers contain author email addresses
- **Affiliation Quality**: Detection accuracy depends on completeness of PubMed metadata
- **Query Limits**: PubMed has maximum result limits (~10,000 papers per query)

## Performance Characteristics

Based on testing with COVID-19 queries:
- **Search Speed**: ~1-2 seconds for initial query
- **Processing Rate**: ~50 papers per second for affiliation analysis
- **Success Rate**: Successfully identified pharmaceutical affiliations in ~21% of COVID-19 papers
- **Company Detection**: Identified companies like Roche, BioApplications, and others

## Testing

### Run the Test Suite
Run all tests
poetry run pytest

Run with verbose output
poetry run pytest -v

Run specific test files
poetry run pytest tests/test_affiliation_parser.py -v

##Author:
Vipul Tiwari



