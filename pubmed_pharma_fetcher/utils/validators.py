"""Validation utilities for input and data processing."""

import re
from typing import Optional


class QueryValidator:
    """Validator for PubMed query strings."""
    
    @staticmethod
    def validate_query(query: str) -> tuple[bool, Optional[str]]:
        """Validate PubMed query string.
        
        Args:
            query: Query string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not query or not query.strip():
            return False, "Query cannot be empty"
            
        # Check for minimum length
        if len(query.strip()) < 2:
            return False, "Query must be at least 2 characters long"
            
        # Check for potentially problematic characters
        invalid_chars = ['<', '>', '"', "'", ';', '\\']
        for char in invalid_chars:
            if char in query:
                return False, f"Query contains invalid character: {char}"
                
        return True, None
    
    @staticmethod
    def sanitize_query(query: str) -> str:
        """Sanitize query string for safe API usage.
        
        Args:
            query: Raw query string
            
        Returns:
            Sanitized query string
        """
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query.strip())
        
        # Remove potentially harmful characters but preserve PubMed syntax
        query = re.sub(r'[<>"\'\\;]', '', query)
        
        return query


class FileValidator:
    """Validator for file operations."""
    
    @staticmethod
    def validate_filename(filename: str) -> tuple[bool, Optional[str]]:
        """Validate output filename.
        
        Args:
            filename: Filename to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename:
            return False, "Filename cannot be empty"
            
        # Check for invalid filename characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            if char in filename:
                return False, f"Filename contains invalid character: {char}"
                
        # Ensure .csv extension
        if not filename.lower().endswith('.csv'):
            return False, "Filename must have .csv extension"
            
        return True, None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file operations.
        
        Args:
            filename: Raw filename
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        filename = re.sub(r'[<>:"|?*\\]', '', filename)
        
        # Ensure .csv extension
        if not filename.lower().endswith('.csv'):
            filename += '.csv'
            
        return filename
