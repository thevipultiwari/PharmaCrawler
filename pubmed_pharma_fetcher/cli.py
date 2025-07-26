"""Command line interface for PubMed pharmaceutical paper fetcher."""

import sys
import click
from typing import Optional

from .core.pubmed_client import PubMedClient
from .core.data_processor import DataProcessor
from .utils.validators import QueryValidator, FileValidator


@click.command()
@click.argument('query', required=True)
@click.option('-d', '--debug', is_flag=True, 
              help='Print debug information during execution')
@click.option('-f', '--file', 'output_file', 
              help='Specify the filename to save the results')
def main(query: str, debug: bool, output_file: Optional[str]):
    """Fetch PubMed papers with pharmaceutical/biotech company affiliations.
    
    QUERY: PubMed search query using standard PubMed syntax
    
    Examples:
    
      get-papers-list "COVID-19 AND vaccine"
      
      get-papers-list "cancer treatment" --file results.csv
      
      get-papers-list "diabetes" --debug
    """
    
    print("=== ACTUAL CLI MAIN ENTERED ===")
    print(f"Arguments received: query={query}, debug={debug}, file={output_file}")
    
    try:
        # Validate and sanitize query
        is_valid, error_msg = QueryValidator.validate_query(query)
        if not is_valid:
            click.echo(f"Error: {error_msg}", err=True)
            sys.exit(1)
            
        query = QueryValidator.sanitize_query(query)
        
        # Validate output file if provided
        if output_file:
            is_valid, error_msg = FileValidator.validate_filename(output_file)
            if not is_valid:
                click.echo(f"Error: {error_msg}", err=True)
                sys.exit(1)
            output_file = FileValidator.sanitize_filename(output_file)
        
        if debug:
            click.echo(f"Searching PubMed for: {query}")
            if output_file:
                click.echo(f"Output will be saved to: {output_file}")
        
        # Initialize components
        pubmed_client = PubMedClient()
        data_processor = DataProcessor()
        
        # Search for papers
        if debug:
            click.echo("Searching for papers...")
            
        paper_ids = pubmed_client.search_papers(query, max_results=100)
        
        if not paper_ids:
            click.echo("No papers found for the given query.")
            return
            
        if debug:
            click.echo(f"Found {len(paper_ids)} papers, fetching details...")
        
        # Fetch paper details
        papers = pubmed_client.fetch_paper_details(paper_ids)
        
        if debug:
            click.echo(f"Successfully fetched details for {len(papers)} papers")
        
        # Process papers to find pharmaceutical/biotech affiliations
        processed_papers = data_processor.process_papers(papers)
        
        if not processed_papers:
            click.echo("No papers found with pharmaceutical/biotech company affiliations.")
            return
        
        # Export results
        csv_content = data_processor.export_to_csv(processed_papers, output_file)
        
        # Print results to console if no file specified
        if not output_file:
            click.echo(csv_content)
        
        # Print summary
        data_processor.print_summary(processed_papers, debug)
        
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user.", err=True)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR CAUGHT: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
