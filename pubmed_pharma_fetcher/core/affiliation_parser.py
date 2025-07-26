"""Parser for identifying pharmaceutical/biotech company affiliations."""

import json
import re
from typing import List, Dict, Tuple, Set
from pathlib import Path


class AffiliationParser:
    """Parser for identifying non-academic authors and company affiliations."""
    
    def __init__(self, config_path: str = None):
        """Initialize the affiliation parser.
        
        Args:
            config_path: Path to companies configuration file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "companies.json"
        
        self.companies_data = self._load_companies_config(config_path)
        self.pharma_companies = set(self.companies_data["pharmaceutical_companies"])
        self.biotech_companies = set(self.companies_data["biotech_companies"])
        self.company_keywords = set(self.companies_data["company_keywords"])
        self.academic_keywords = set(self.companies_data["academic_keywords"])
        
    def _load_companies_config(self, config_path: str) -> Dict:
        """Load companies configuration from JSON file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dictionary containing company lists and keywords
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback to basic configuration if file not found
            return {
                "pharmaceutical_companies": ["Pfizer", "Novartis", "Roche", "Merck"],
                "biotech_companies": ["Genentech", "Amgen", "Biogen", "Moderna"],
                "company_keywords": ["Pharmaceuticals", "Pharma", "Inc.", "Ltd.", "Corp."],
                "academic_keywords": ["University", "College", "Institute", "Hospital"]
            }
    
    def is_non_academic_affiliation(self, affiliation: str) -> bool:
        """Check if an affiliation represents a non-academic institution.
        
        Args:
            affiliation: Author's affiliation string
            
        Returns:
            True if affiliation is non-academic, False otherwise
        """
        if not affiliation:
            return False
            
        affiliation_lower = affiliation.lower()
        
        # First check if it's explicitly academic
        for keyword in self.academic_keywords:
            if keyword.lower() in affiliation_lower:
                return False
        
        # Check for pharmaceutical/biotech companies
        if self._contains_pharma_biotech_company(affiliation):
            return True
            
        # Check for corporate keywords
        for keyword in self.company_keywords:
            if keyword.lower() in affiliation_lower:
                return True
                
        # Check email domain patterns
        if self._has_corporate_email_domain(affiliation):
            return True
            
        return False
    
    def extract_company_names(self, affiliation: str) -> List[str]:
        """Extract pharmaceutical/biotech company names from affiliation.
        
        Args:
            affiliation: Author's affiliation string
            
        Returns:
            List of identified company names
        """
        if not affiliation:
            return []
            
        companies = []
        
        # Check for exact matches with known companies
        all_companies = self.pharma_companies.union(self.biotech_companies)
        for company in all_companies:
            if company.lower() in affiliation.lower():
                companies.append(company)
        
        # Extract potential company names using patterns
        potential_companies = self._extract_company_patterns(affiliation)
        companies.extend(potential_companies)
        
        # Remove duplicates while preserving order
        unique_companies = []
        seen = set()
        for company in companies:
            if company.lower() not in seen:
                unique_companies.append(company)
                seen.add(company.lower())
                
        return unique_companies
    
    def _contains_pharma_biotech_company(self, affiliation: str) -> bool:
        """Check if affiliation contains known pharmaceutical/biotech companies.
        
        Args:
            affiliation: Author's affiliation string
            
        Returns:
            True if contains known companies, False otherwise
        """
        affiliation_lower = affiliation.lower()
        all_companies = self.pharma_companies.union(self.biotech_companies)
        
        for company in all_companies:
            if company.lower() in affiliation_lower:
                return True
                
        return False
    
    def _has_corporate_email_domain(self, affiliation: str) -> bool:
        """Check if affiliation contains corporate email domains.
        
        Args:
            affiliation: Author's affiliation string
            
        Returns:
            True if contains corporate email domains, False otherwise
        """
        # Extract email domains
        email_pattern = r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        domains = re.findall(email_pattern, affiliation.lower())
        
        academic_domains = {'.edu', '.ac.', '.edu.', '.org'}
        
        for domain in domains:
            # Skip academic domains
            if any(academic in domain for academic in academic_domains):
                continue
            # Corporate domains typically end with .com, .net, etc.
            if any(corp in domain for corp in ['.com', '.net', '.biz', '.co.']):
                return True
                
        return False
    
    def _extract_company_patterns(self, affiliation: str) -> List[str]:
        """Extract potential company names using common patterns.
        
        Args:
            affiliation: Author's affiliation string
            
        Returns:
            List of potential company names
        """
        companies = []
        
        # Pattern 1: Company Name + corporate suffix
        pattern1 = r'([A-Z][a-zA-Z\s&]+)(?:Inc\.|Ltd\.|Corp\.|Corporation|Company|Pharmaceuticals|Pharma|Biotech)'
        matches1 = re.findall(pattern1, affiliation)
        companies.extend([match.strip() for match in matches1])
        
        # Pattern 2: Words ending with pharmaceutical/biotech keywords
        pattern2 = r'([A-Z][a-zA-Z\s]+?)(?:Pharmaceuticals|Pharma|Biotech|Biotechnology)'
        matches2 = re.findall(pattern2, affiliation)
        companies.extend([match.strip() for match in matches2])
        
        # Clean up extracted names
        cleaned_companies = []
        for company in companies:
            # Remove common prefixes/suffixes that aren't part of company name
            company = re.sub(r'^(The|At|From)\s+', '', company, flags=re.IGNORECASE)
            company = re.sub(r'\s+(Department|Division|Unit)$', '', company, flags=re.IGNORECASE)
            
            if len(company.strip()) > 2:  # Minimum length check
                cleaned_companies.append(company.strip())
                
        return cleaned_companies
    
    def get_non_academic_authors_info(self, authors: List) -> Tuple[List[str], List[str]]:
        """Extract non-academic authors and their company affiliations.
        
        Args:
            authors: List of Author objects
            
        Returns:
            Tuple of (non_academic_authors, company_affiliations)
        """
        non_academic_authors = []
        company_affiliations = []
        
        for author in authors:
            if self.is_non_academic_affiliation(author.affiliation):
                # Add author name
                author_name = f"{author.first_name} {author.last_name}".strip()
                if author_name:
                    non_academic_authors.append(author_name)
                
                # Extract company names
                companies = self.extract_company_names(author.affiliation)
                company_affiliations.extend(companies)
        
        # Remove duplicates
        unique_authors = list(dict.fromkeys(non_academic_authors))
        unique_companies = list(dict.fromkeys(company_affiliations))
        
        return unique_authors, unique_companies
