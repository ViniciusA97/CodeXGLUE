#!/usr/bin/env python3
"""
Detokenize Java code from the tokenized format back to real Java.

This reverses the preprocessing by applying the token mappings back to the code.
Maintains consistency: if METHOD_1 was 'sum', it will be 'sum' again.
"""

import re
from collections import OrderedDict


class JavaDetokenizer:
    """Detokenizer to convert tokenized code back to real Java."""
    
    def __init__(self, mappings=None):
        """
        Initialize detokenizer with mappings.
        
        Args:
            mappings: Dict with 'methods', 'variables', 'types', 'strings' mappings
                     Each mapping is {original_name: token}
        """
        self.reverse_mappings = {
            'methods': {},
            'variables': {},
            'types': {},
            'strings': {}
        }
        
        if mappings:
            self.set_mappings(mappings)
    
    def set_mappings(self, mappings):
        """
        Set token mappings (will be reversed internally).
        
        Args:
            mappings: Dict with forward mappings {original: token}
        """
        # Reverse the mappings: {token: original}
        for category in ['methods', 'variables', 'types', 'strings']:
            if category in mappings:
                self.reverse_mappings[category] = {
                    token: original 
                    for original, token in mappings[category].items()
                }
    
    def detokenize(self, tokenized_code):
        """
        Detokenize code back to real Java.
        
        Args:
            tokenized_code: Tokenized Java code string
            
        Returns:
            Real Java code string
        """
        code = tokenized_code
        
        # Step 1: Replace string tokens
        for token, original in self.reverse_mappings['strings'].items():
            code = code.replace(token, original)
        
        # Step 2: Replace type tokens
        for token, original in self.reverse_mappings['types'].items():
            # Use word boundaries to avoid partial replacements
            code = re.sub(r'\b' + re.escape(token) + r'\b', original, code)
        
        # Step 3: Replace method tokens
        for token, original in self.reverse_mappings['methods'].items():
            code = re.sub(r'\b' + re.escape(token) + r'\b', original, code)
        
        # Step 4: Replace variable tokens
        for token, original in self.reverse_mappings['variables'].items():
            code = re.sub(r'\b' + re.escape(token) + r'\b', original, code)
        
        # Step 5: Clean up formatting (optional - make it more readable)
        code = self.format_java(code)
        
        return code
    
    def format_java(self, code):
        """
        Format Java code to be more readable (optional).
        
        Args:
            code: Java code string
            
        Returns:
            Formatted Java code
        """
        # Remove extra spaces around parentheses and brackets
        code = re.sub(r'\s*\(\s*', '(', code)
        code = re.sub(r'\s*\)\s*', ') ', code)
        code = re.sub(r'\s*\[\s*', '[', code)
        code = re.sub(r'\s*\]\s*', '] ', code)
        code = re.sub(r'\s*\{\s*', ' { ', code)
        code = re.sub(r'\s*\}\s*', ' } ', code)
        code = re.sub(r'\s*;\s*', '; ', code)
        code = re.sub(r'\s*,\s*', ', ', code)
        
        # Fix spacing around operators (keep spaces)
        # Already has spaces, just clean up multiple spaces
        code = re.sub(r'\s+', ' ', code)
        
        return code.strip()


def detokenize_with_mappings(tokenized_code, mappings):
    """
    Convenience function to detokenize with mappings.
    
    Args:
        tokenized_code: Tokenized Java code
        mappings: Token mappings from preprocessing
        
    Returns:
        Real Java code
    """
    detokenizer = JavaDetokenizer(mappings)
    return detokenizer.detokenize(tokenized_code)


def main():
    """Main function for command-line usage."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(
        description='Detokenize Java code back to real format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Detokenize with mappings from JSON file
  python detokenize_java.py --code "public int METHOD_1 ( int VAR_1 ) { ... }" --mappings mappings.json
  
  # Detokenize inline with manual mappings
  python detokenize_java.py --code "public int METHOD_1 ( int VAR_1 , int VAR_2 ) { return VAR_1 + VAR_2 ; }" \\
      --method METHOD_1=sum --var VAR_1=a --var VAR_2=b

Note: Mappings must match the original preprocessing to maintain consistency.
        """
    )
    
    parser.add_argument('--code', required=True, help='Tokenized Java code')
    parser.add_argument('--mappings', help='JSON file with token mappings')
    parser.add_argument('--method', action='append', help='Method mapping (METHOD_1=sum)')
    parser.add_argument('--var', action='append', help='Variable mapping (VAR_1=count)')
    parser.add_argument('--type', action='append', help='Type mapping (TYPE_1=ArrayList)')
    parser.add_argument('--string', action='append', help='String mapping (STRING_1="hello")')
    
    args = parser.parse_args()
    
    # Build mappings
    mappings = {
        'methods': {},
        'variables': {},
        'types': {},
        'strings': {}
    }
    
    # Load from JSON file if provided
    if args.mappings:
        with open(args.mappings, 'r') as f:
            mappings = json.load(f)
    
    # Add manual mappings
    if args.method:
        for mapping in args.method:
            token, original = mapping.split('=')
            mappings['methods'][original] = token
    
    if args.var:
        for mapping in args.var:
            token, original = mapping.split('=')
            mappings['variables'][original] = token
    
    if args.type:
        for mapping in args.type:
            token, original = mapping.split('=')
            mappings['types'][original] = token
    
    if args.string:
        for mapping in args.string:
            token, original = mapping.split('=')
            mappings['strings'][original] = token
    
    # Detokenize
    print("🤖 TOKENIZED CODE:")
    print(args.code)
    print()
    
    detokenized = detokenize_with_mappings(args.code, mappings)
    
    print("🐛 DETOKENIZED CODE:")
    print(detokenized)
    print()
    
    if mappings['methods'] or mappings['variables'] or mappings['types'] or mappings['strings']:
        print("📋 MAPPINGS USED:")
        for category, mapping in mappings.items():
            if mapping:
                print(f"\n{category.upper()}:")
                for original, token in mapping.items():
                    print(f"  {token} → {original}")


if __name__ == '__main__':
    main()
