#!/usr/bin/env python3
"""
Fix real Java code using the CodeBERT model.

This script:
1. Takes real Java code as input
2. Preprocesses it to tokenized format (METHOD_1, VAR_1, etc.)
3. Runs the model
4. Detokenizes the output back to real Java code
5. Returns the fixed real Java code

The token mappings are preserved to ensure consistency.
"""

import os
import sys
import subprocess
import tempfile
from preprocess_java import JavaPreprocessor
from detokenize_java import JavaDetokenizer


def fix_real_code(java_code, model_path='code/output_small/checkpoint-best-bleu/pytorch_model.bin'):
    """
    Fix real Java code using the model.
    
    Args:
        java_code: Real Java code string
        model_path: Path to trained model
        
    Returns:
        tuple: (tokenized_input, tokenized_output, mappings)
    """
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return None, None, None
    
    # Step 1: Preprocess to tokenized format
    print("🔄 Step 1: Preprocessing Java code to tokenized format...")
    preprocessor = JavaPreprocessor()
    tokenized_input = preprocessor.preprocess(java_code)
    mappings = preprocessor.get_mappings()
    
    print(f"✅ Tokenized: {tokenized_input[:80]}...")
    
    # Step 2: Run model
    print("\n🤖 Step 2: Running model...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write tokenized code
        buggy_file = os.path.join(tmpdir, 'input.buggy')
        fixed_file = os.path.join(tmpdir, 'input.fixed')
        output_dir = os.path.join(tmpdir, 'output')
        
        with open(buggy_file, 'w') as f:
            f.write(tokenized_input + '\n')
        with open(fixed_file, 'w') as f:
            f.write(tokenized_input + '\n')  # Dummy
        
        # Run inference
        cmd = [
            sys.executable, 'code/run.py',
            '--do_test',
            '--model_type', 'roberta',
            '--model_name_or_path', 'roberta-base',
            '--config_name', 'roberta-base',
            '--tokenizer_name', 'roberta-base',
            '--load_model_path', model_path,
            '--test_filename', f'{buggy_file},{fixed_file}',
            '--output_dir', output_dir,
            '--max_source_length', '256',
            '--max_target_length', '256',
            '--beam_size', '5',
            '--eval_batch_size', '1'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # Read output
            output_file = os.path.join(output_dir, 'test_0.output')
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    tokenized_output = f.read().strip()
                
                print("✅ Model generated fix!")
                return tokenized_input, tokenized_output, mappings
            else:
                print("❌ Output file not found")
                return tokenized_input, None, mappings
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running model: {e}")
            if e.stderr:
                print(f"Details: {e.stderr[:500]}")
            return tokenized_input, None, mappings


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Fix real Java code using CodeBERT (with preprocessing)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Fix inline code
  python fix_code_real.py --code 'public int sum(int a, int b) { return a - b; }'
  
  # Fix code from file
  python fix_code_real.py --file mycode.java
  
  # Show token mappings
  python fix_code_real.py --code 'public int sum(int a, int b) { return a - b; }' --show-mappings

The script automatically:
  1. Tokenizes your real Java code
  2. Runs the model
  3. Detokenizes back to real Java code
  
Token mappings are preserved to maintain consistency!
        """
    )
    
    parser.add_argument('--code', help='Java code string to fix')
    parser.add_argument('--file', help='Java file to fix')
    parser.add_argument('--model', default='code/output_small/checkpoint-best-bleu/pytorch_model.bin',
                       help='Path to trained model')
    parser.add_argument('--show-mappings', action='store_true',
                       help='Show token mappings')
    
    args = parser.parse_args()
    
    # Get input code
    if args.code:
        java_code = args.code
    elif args.file:
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            return 1
        with open(args.file, 'r') as f:
            java_code = f.read()
    else:
        parser.print_help()
        return 1
    
    print("="*80)
    print("🔧 JAVA CODE FIXER (with Preprocessing)")
    print("="*80)
    
    print("\n🐛 ORIGINAL CODE:")
    print(java_code)
    print()
    
    # Fix code
    tokenized_input, tokenized_output, mappings = fix_real_code(java_code, args.model)
    
    if tokenized_output:
        print("\n" + "="*80)
        print("📊 RESULTS")
        print("="*80)
        
        print("\n📥 TOKENIZED INPUT:")
        print(tokenized_input)
        
        print("\n📤 TOKENIZED OUTPUT (Fixed):")
        print(tokenized_output)
        
        # Step 3: Detokenize back to real Java
        print("\n🔄 Step 3: Detokenizing back to real Java...")
        detokenizer = JavaDetokenizer(mappings)
        fixed_java = detokenizer.detokenize(tokenized_output)
        
        print("\n" + "="*80)
        print("✨ FINAL RESULT")
        print("="*80)
        
        print("\n🐛 ORIGINAL CODE:")
        print(java_code)
        
        print("\n✅ FIXED CODE:")
        print(fixed_java)
        
        if tokenized_input == tokenized_output:
            print("\n⚠️  Model made no changes (code may already be correct)")
        else:
            print("\n🎉 Model suggested a fix!")
            
            # Show what changed
            if java_code.strip() != fixed_java.strip():
                print("\n📝 Changes:")
                original_words = java_code.split()
                fixed_words = fixed_java.split()
                
                for i, (orig, fixed) in enumerate(zip(original_words, fixed_words)):
                    if orig != fixed:
                        print(f"  Position {i}: '{orig}' → '{fixed}'")
        
        if args.show_mappings and mappings:
            print("\n📋 TOKEN MAPPINGS:")
            for category, mapping in mappings.items():
                if mapping:
                    print(f"\n{category.upper()}:")
                    for original, token in mapping.items():
                        print(f"  {token} = {original}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
