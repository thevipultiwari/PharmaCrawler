"""Core modules for PubMed pharmaceutical paper fetcher.

This package contains the core functionality for fetching papers from PubMed,
parsing author affiliations, and processing data for export.
"""

from .pubmed_client import PubMedClient, Paper, Author
from .affiliation_parser import AffiliationParser
from .data_processor import DataProcessor

__all__ = [
    "PubMedClient",
    "Paper",
    "Author", 
    "AffiliationParser",
    "DataProcessor"
]
