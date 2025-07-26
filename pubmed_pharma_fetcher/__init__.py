"""PubMed Pharmaceutical Paper Fetcher.

A tool for fetching research papers from PubMed that have authors
affiliated with pharmaceutical or biotech companies.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core.pubmed_client import PubMedClient, Paper, Author
from .core.affiliation_parser import AffiliationParser
from .core.data_processor import DataProcessor

__all__ = [
    "PubMedClient",
    "Paper", 
    "Author",
    "AffiliationParser",
    "DataProcessor"
]
