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

1. Clone the repository:
