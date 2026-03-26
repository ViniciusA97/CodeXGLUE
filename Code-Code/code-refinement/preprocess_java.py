#!/usr/bin/env python3
"""
Preprocess Java code to the tokenized format used by CodeBERT training.

Transforms real Java code into the normalized format:
- Method names → METHOD_1, METHOD_2, ...
- Variable names → VAR_1, VAR_2, ...
- Type names → TYPE_1, TYPE_2, ...
- String literals → STRING_1, STRING_2, ...
- Single line format with spaces around operators
"""

import re
from collections import OrderedDict


class JavaPreprocessor:
    """Preprocessor to tokenize Java code."""
    
    def __init__(self):
        self.method_map = OrderedDict()
        self.var_map = OrderedDict()
        self.type_map = OrderedDict()
        self.string_map = OrderedDict()
        
        self.method_counter = 1
        self.var_counter = 1
        self.type_counter = 1
        self.string_counter = 1
    
    def reset(self):
        """Reset all mappings."""
        self.method_map.clear()
        self.var_map.clear()
        self.type_map.clear()
        self.string_map.clear()
        
        self.method_counter = 1
        self.var_counter = 1
        self.type_counter = 1
        self.string_counter = 1
    
    def normalize_code(self, code):
        """
        Normalize Java code to single line with proper spacing.
        
        Args:
            code: Java code string
            
        Returns:
            Normalized code string
        """
        # Remove comments
        code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove extra whitespace and newlines
        code = ' '.join(code.split())
        
        # Add spaces around operators and punctuation
        code = re.sub(r'([+\-*/%=<>!&|^])', r' \1 ', code)
        code = re.sub(r'([(){}\[\];,.])', r' \1 ', code)
        
        # Fix double operators (==, !=, <=, >=, &&, ||, ++, --, etc.)
        code = re.sub(r'(\+)\s+(\+)', r'\1\2', code)
        code = re.sub(r'(-)\s+(-)', r'\1\2', code)
        code = re.sub(r'(&)\s+(&)', r'\1\2', code)
        code = re.sub(r'(\|)\s+(\|)', r'\1\2', code)
        code = re.sub(r'(=)\s+(=)', r'\1\2', code)
        code = re.sub(r'(!)\s+(=)', r'\1\2', code)
        code = re.sub(r'(<)\s+(=)', r'\1\2', code)
        code = re.sub(r'(>)\s+(=)', r'\1\2', code)
        
        # Clean up multiple spaces
        code = re.sub(r'\s+', ' ', code)
        
        return code.strip()
    
    def tokenize_strings(self, code):
        """Replace string literals with STRING_N tokens."""
        def replace_string(match):
            string_val = match.group(0)
            if string_val not in self.string_map:
                self.string_map[string_val] = f'STRING_{self.string_counter}'
                self.string_counter += 1
            return self.string_map[string_val]
        
        # Match string literals (both single and double quotes)
        code = re.sub(r'"(?:[^"\\]|\\.)*"', replace_string, code)
        code = re.sub(r"'(?:[^'\\]|\\.)*'", replace_string, code)
        
        return code
    
    def tokenize_types(self, code):
        """Replace type names with TYPE_N tokens."""
        # Common Java types to tokenize
        # Keep primitive types and common java.lang types
        primitives = {'int', 'long', 'double', 'float', 'boolean', 'char', 'byte', 'short', 'void'}
        
        # Find custom type names (CamelCase identifiers)
        # Pattern: uppercase letter followed by letters/digits
        pattern = r'\b([A-Z][a-zA-Z0-9]*)\b'
        
        def replace_type(match):
            type_name = match.group(1)
            # Skip if it's a known Java class that should stay
            if type_name in {'String', 'Object', 'System', 'List', 'Map', 'Set'}:
                return type_name
            
            if type_name not in self.type_map:
                self.type_map[type_name] = f'TYPE_{self.type_counter}'
                self.type_counter += 1
            return self.type_map[type_name]
        
        code = re.sub(pattern, replace_type, code)
        
        return code
    
    def tokenize_identifiers(self, code):
        """Replace method and variable names with METHOD_N and VAR_N tokens."""
        
        # Pattern for method calls: identifier followed by (
        method_pattern = r'\b([a-z][a-zA-Z0-9]*)\s*(?=\()'
        
        def replace_method(match):
            method_name = match.group(1)
            if method_name not in self.method_map:
                self.method_map[method_name] = f'METHOD_{self.method_counter}'
                self.method_counter += 1
            return self.method_map[method_name] + ' '
        
        code = re.sub(method_pattern, replace_method, code)
        code = re.sub(r'\s+', ' ', code)  # Clean up spaces
        
        # Pattern for variables: lowercase identifier not followed by (
        var_pattern = r'\b([a-z][a-zA-Z0-9]*)\b(?!\s*\()'
        
        def replace_var(match):
            var_name = match.group(1)
            # Skip keywords
            keywords = {
                'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
                'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw',
                'throws', 'new', 'this', 'super', 'null', 'true', 'false',
                'public', 'private', 'protected', 'static', 'final', 'abstract',
                'synchronized', 'volatile', 'transient', 'native', 'strictfp',
                'class', 'interface', 'enum', 'extends', 'implements', 'package',
                'import', 'int', 'long', 'double', 'float', 'boolean', 'char',
                'byte', 'short', 'void'
            }
            
            if var_name in keywords:
                return var_name
            
            if var_name not in self.var_map:
                self.var_map[var_name] = f'VAR_{self.var_counter}'
                self.var_counter += 1
            return self.var_map[var_name]
        
        code = re.sub(var_pattern, replace_var, code)
        
        return code
    
    def preprocess(self, code):
        """
        Full preprocessing pipeline.
        
        Args:
            code: Java code string
            
        Returns:
            Tokenized code string
        """
        # Reset mappings for each new code
        self.reset()
        
        # Step 1: Normalize to single line with proper spacing
        code = self.normalize_code(code)
        
        # Step 2: Tokenize strings
        code = self.tokenize_strings(code)
        
        # Step 3: Tokenize types
        code = self.tokenize_types(code)
        
        # Step 4: Tokenize methods and variables
        code = self.tokenize_identifiers(code)
        
        return code
    
    def get_mappings(self):
        """Return all token mappings."""
        return {
            'methods': dict(self.method_map),
            'variables': dict(self.var_map),
            'types': dict(self.type_map),
            'strings': dict(self.string_map)
        }


def preprocess_file(input_file, output_file=None):
    """
    Preprocess a Java file.
    
    Args:
        input_file: Path to input Java file
        output_file: Path to output file (optional)
    """
    preprocessor = JavaPreprocessor()
    
    with open(input_file, 'r') as f:
        code = f.read()
    
    tokenized = preprocessor.preprocess(code)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(tokenized + '\n')
        print(f"✅ Preprocessed: {input_file} → {output_file}")
    
    return tokenized, preprocessor.get_mappings()


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Preprocess Java code to tokenized format for CodeBERT',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Preprocess a single file
  python preprocess_java.py input.java -o output.java
  
  # Preprocess and show mappings
  python preprocess_java.py input.java --show-mappings
  
  # Preprocess inline code
  python preprocess_java.py --code "public int sum(int a, int b) { return a + b; }"
        """
    )
    
    parser.add_argument('input_file', nargs='?', help='Input Java file')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('--code', help='Java code string to preprocess')
    parser.add_argument('--show-mappings', action='store_true', 
                       help='Show token mappings')
    
    args = parser.parse_args()
    
    preprocessor = JavaPreprocessor()
    
    if args.code:
        # Process inline code
        tokenized = preprocessor.preprocess(args.code)
        print("\n🐛 ORIGINAL CODE:")
        print(args.code)
        print("\n🤖 TOKENIZED CODE:")
        print(tokenized)
        
        if args.show_mappings:
            print("\n📋 TOKEN MAPPINGS:")
            mappings = preprocessor.get_mappings()
            for category, mapping in mappings.items():
                if mapping:
                    print(f"\n{category.upper()}:")
                    for original, token in mapping.items():
                        print(f"  {original} → {token}")
    
    elif args.input_file:
        # Process file
        tokenized, mappings = preprocess_file(args.input_file, args.output)
        
        print("\n🤖 TOKENIZED CODE:")
        print(tokenized)
        
        if args.show_mappings:
            print("\n📋 TOKEN MAPPINGS:")
            for category, mapping in mappings.items():
                if mapping:
                    print(f"\n{category.upper()}:")
                    for original, token in mapping.items():
                        print(f"  {original} → {token}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
