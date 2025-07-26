"""Data processor for handling paper data and CSV export."""

import csv
import sys
from typing import List, Dict, Optional
from io import StringIO
from .affiliation_parser import AffiliationParser


class DataProcessor:
    """Processes paper data and exports to CSV format."""
    
    def __init__(self):
        """Initialize the data processor."""
        self.affiliation_parser = AffiliationParser()
        
    def process_papers(self, papers: List) -> List[Dict[str, str]]:
        """Process papers and extract required information.
        
        Args:
            papers: List of Paper objects
            
        Returns:
            List of dictionaries containing processed paper data
        """
        processed_papers = []
        
        for paper in papers:
            # Get non-academic authors and company affiliations
            non_academic_authors, company_affiliations = \
                self.affiliation_parser.get_non_academic_authors_info(paper.authors)
            
            # Skip papers without non-academic authors
            if not non_academic_authors:
                continue
                
            # Find corresponding author email
            corresponding_email = self._extract_corresponding_email(paper.authors)
            
            processed_paper = {
                'PubmedID': paper.pubmed_id,
                'Title': paper.title,
                'Publication Date': paper.publication_date,
                'Non-academic Author(s)': '; '.join(non_academic_authors),
                'Company Affiliation(s)': '; '.join(company_affiliations),
                'Corresponding Author Email': corresponding_email or 'Not available'
            }
            
            processed_papers.append(processed_paper)
            
        return processed_papers
    
    def _extract_corresponding_email(self, authors: List) -> Optional[str]:
        """Extract corresponding author email from authors list.
        
        Args:
            authors: List of Author objects
            
        Returns:
            Email of corresponding author or None
        """
        # First, look for authors explicitly marked as corresponding
        for author in authors:
            if author.is_corresponding and author.email:
                return author.email
                
        # If no explicit corresponding author, look for any email
        for author in authors:
            if author.email:
                return author.email
                
        return None
    
    def export_to_csv(self, processed_papers: List[Dict[str, str]], 
                     filename: Optional[str] = None) -> str:
        """Export processed papers to CSV format.
        
        Args:
            processed_papers: List of processed paper dictionaries
            filename: Output filename, if None returns CSV as string
            
        Returns:
            CSV content as string
        """
        if not processed_papers:
            return "No papers found with pharmaceutical/biotech company affiliations."
            
        fieldnames = [
            'PubmedID',
            'Title', 
            'Publication Date',
            'Non-academic Author(s)',
            'Company Affiliation(s)',
            'Corresponding Author Email'
        ]
        
        # Create CSV content
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator='\n')
        writer.writeheader()
        writer.writerows(processed_papers)
        csv_content = output.getvalue()
        output.close()
        
        # Save to file if filename provided
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    csvfile.write(csv_content)
                print(f"Results saved to {filename}")
            except Exception as e:
                print(f"Error saving to file: {str(e)}", file=sys.stderr)
                
        return csv_content
    
    def print_summary(self, processed_papers: List[Dict[str, str]], 
                     debug: bool = False) -> None:
        """Print summary of processed papers.
        
        Args:
            processed_papers: List of processed paper dictionaries
            debug: Whether to print debug information
        """
        print(f"\nFound {len(processed_papers)} papers with pharmaceutical/biotech affiliations")
        
        if debug and processed_papers:
            print("\nCompany affiliations found:")
            all_companies = set()
            for paper in processed_papers:
                companies = paper['Company Affiliation(s)'].split('; ')
                all_companies.update(comp.strip() for comp in companies if comp.strip())
            
            for company in sorted(all_companies):
                print(f"  - {company}")
                
            print(f"\nSample papers:")
            for i, paper in enumerate(processed_papers[:3]):
                print(f"  {i+1}. {paper['Title'][:80]}...")
