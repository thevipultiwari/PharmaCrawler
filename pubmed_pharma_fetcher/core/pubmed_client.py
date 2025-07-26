"""PubMed API client for fetching research papers."""

import time
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import requests
from Bio import Entrez


@dataclass
class Author:
    """Represents a paper author with affiliation information."""
    first_name: str
    last_name: str
    affiliation: str
    email: Optional[str] = None
    is_corresponding: bool = False


@dataclass
class Paper:
    """Represents a research paper from PubMed."""
    pubmed_id: str
    title: str
    publication_date: str
    authors: List[Author]
    abstract: Optional[str] = None


class PubMedClient:
    """Client for interacting with PubMed API."""
    
    def __init__(self, email: str = "user@example.com", tool: str = "pubmed-pharma-fetcher"):
        """Initialize PubMed client.
        
        Args:
            email: Email for NCBI Entrez API
            tool: Tool name for API identification
        """
        Entrez.email = email
        Entrez.tool = tool
        self.base_delay = 0.34  # To respect 3 requests per second limit
        
    def search_papers(self, query: str, max_results: int = 100) -> List[str]:
        """Search for papers using PubMed query syntax.
        
        Args:
            query: PubMed search query
            max_results: Maximum number of results to return
            
        Returns:
            List of PubMed IDs
        """
        try:
            search_handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=max_results,
                sort="relevance"
            )
            search_results = Entrez.read(search_handle)
            search_handle.close()
            
            time.sleep(self.base_delay)  # Rate limiting
            
            return search_results["IdList"]
            
        except Exception as e:
            raise RuntimeError(f"Failed to search PubMed: {str(e)}")
    
    def fetch_paper_details(self, pubmed_ids: List[str]) -> List[Paper]:
        """Fetch detailed information for papers.
        
        Args:
            pubmed_ids: List of PubMed IDs
            
        Returns:
            List of Paper objects with detailed information
        """
        if not pubmed_ids:
            return []
            
        papers = []
        
        # Process in batches to avoid API limits
        batch_size = 50
        for i in range(0, len(pubmed_ids), batch_size):
            batch_ids = pubmed_ids[i:i + batch_size]
            batch_papers = self._fetch_batch(batch_ids)
            papers.extend(batch_papers)
            
            if i + batch_size < len(pubmed_ids):
                time.sleep(self.base_delay)  # Rate limiting between batches
                
        return papers
    
    def _fetch_batch(self, pubmed_ids: List[str]) -> List[Paper]:
        """Fetch a batch of papers from PubMed.
        
        Args:
            pubmed_ids: List of PubMed IDs for the batch
            
        Returns:
            List of Paper objects
        """
        try:
            fetch_handle = Entrez.efetch(
                db="pubmed",
                id=",".join(pubmed_ids),
                rettype="medline",
                retmode="xml"
            )
            
            records = Entrez.read(fetch_handle)
            fetch_handle.close()
            
            papers = []
            for record in records["PubmedArticle"]:
                paper = self._parse_paper_record(record)
                if paper:
                    papers.append(paper)
                    
            return papers
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch paper details: {str(e)}")
    
    def _parse_paper_record(self, record: Dict[str, Any]) -> Optional[Paper]:
        """Parse a single paper record from PubMed XML.
        
        Args:
            record: Raw paper record from PubMed
            
        Returns:
            Paper object or None if parsing fails
        """
        try:
            medline_citation = record["MedlineCitation"]
            pubmed_id = str(medline_citation["PMID"])
            
            # Extract title
            article = medline_citation["Article"]
            title = str(article["ArticleTitle"])
            
            # Extract publication date
            pub_date = self._extract_publication_date(article)
            
            # Extract authors
            authors = self._extract_authors(article)
            
            # Extract abstract if available
            abstract = None
            if "Abstract" in article and "AbstractText" in article["Abstract"]:
                abstract_parts = article["Abstract"]["AbstractText"]
                if isinstance(abstract_parts, list):
                    abstract = " ".join(str(part) for part in abstract_parts)
                else:
                    abstract = str(abstract_parts)
            
            return Paper(
                pubmed_id=pubmed_id,
                title=title,
                publication_date=pub_date,
                authors=authors,
                abstract=abstract
            )
            
        except Exception as e:
            print(f"Warning: Failed to parse paper record: {str(e)}")
            return None
    
    def _extract_publication_date(self, article: Dict[str, Any]) -> str:
        """Extract publication date from article record.
        
        Args:
            article: Article section of PubMed record
            
        Returns:
            Publication date as string (YYYY-MM-DD format)
        """
        try:
            # Try electronic publication date first
            if "ArticleDate" in article and article["ArticleDate"]:
                date_info = article["ArticleDate"][0]
                year = date_info.get("Year", "")
                month = date_info.get("Month", "01").zfill(2)
                day = date_info.get("Day", "01").zfill(2)
                return f"{year}-{month}-{day}"
            
            # Fall back to journal publication date
            if "Journal" in article and "JournalIssue" in article["Journal"]:
                pub_date = article["Journal"]["JournalIssue"].get("PubDate", {})
                year = pub_date.get("Year", "")
                month = pub_date.get("Month", "01")
                day = pub_date.get("Day", "01")
                
                # Convert month name to number if necessary
                if isinstance(month, str) and not month.isdigit():
                    month_map = {
                        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
                    }
                    month = month_map.get(month[:3], "01")
                
                month = str(month).zfill(2)
                day = str(day).zfill(2)
                return f"{year}-{month}-{day}"
                
        except Exception:
            pass
            
        return "Unknown"
    
    def _extract_authors(self, article: Dict[str, Any]) -> List[Author]:
        """Extract author information from article record.
        
        Args:
            article: Article section of PubMed record
            
        Returns:
            List of Author objects
        """
        authors = []
        
        if "AuthorList" not in article:
            return authors
            
        for author_data in article["AuthorList"]:
            try:
                # Extract names
                last_name = author_data.get("LastName", "")
                first_name = author_data.get("ForeName", "")
                if not first_name:
                    first_name = author_data.get("Initials", "")
                
                # Extract affiliation
                affiliation = ""
                if "AffiliationInfo" in author_data and author_data["AffiliationInfo"]:
                    affiliation = author_data["AffiliationInfo"][0].get("Affiliation", "")
                
                # Check for corresponding author and email
                email = None
                is_corresponding = False
                
                # Look for email in affiliation text
                if affiliation:
                    # Simple email extraction pattern
                    import re
                    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                    email_matches = re.findall(email_pattern, affiliation)
                    if email_matches:
                        email = email_matches[0]
                        is_corresponding = True
                
                author = Author(
                    first_name=first_name,
                    last_name=last_name,
                    affiliation=affiliation,
                    email=email,
                    is_corresponding=is_corresponding
                )
                
                authors.append(author)
                
            except Exception as e:
                print(f"Warning: Failed to parse author: {str(e)}")
                continue
                
        return authors
