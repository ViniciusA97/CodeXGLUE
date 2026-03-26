#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para corrigir código Java usando o modelo treinado.

Uso:
    # Modo interativo
    python fix_code.py
    
    # Passar código diretamente
    python fix_code.py "public int sum(int a, int b) { return a - b; }"
    
    # Ler de arquivo
    python fix_code.py --file meu_codigo.java
"""

import sys
import os
import argparse
import subprocess
import tempfile
import re


def normalize_java_code(code):
    """Remove comments and normalize Java code."""
    # Remove line comments
    code = re.sub(r'//.*', '', code)
    # Remove block comments
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    # Remove empty lines and extra spaces
    code = ' '.join(code.split())
    return code.strip()


def fix_code(buggy_code, model_path='code/output_small/checkpoint-best-bleu/pytorch_model.bin'):
    """
    Fix Java code using the trained model.
    
    Args:
        buggy_code: String with buggy Java code
        model_path: Path to the trained model
        
    Returns:
        String with fixed code
    """
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"❌ Error: Model not found at {model_path}")
        print("\nMake sure the model is trained and in the correct path.")
        return None
    
    # Normalize code
    normalized_code = normalize_java_code(buggy_code)
    
    if not normalized_code:
        print("❌ Error: Empty code after normalization")
        return None
    
    # Create temporary files
    with tempfile.TemporaryDirectory() as tmpdir:
        buggy_file = os.path.join(tmpdir, 'temp_buggy.java')
        fixed_file = os.path.join(tmpdir, 'temp_fixed.java')
        output_dir = os.path.join(tmpdir, 'output')
        
        # Write buggy code
        with open(buggy_file, 'w') as f:
            f.write(normalized_code + '\n')
        
        # Create empty fixed file (required by the script)
        with open(fixed_file, 'w') as f:
            f.write(normalized_code + '\n')
        
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
            print("🤖 Processing code...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # Read result
            output_file = os.path.join(output_dir, 'test_0.output')
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    fixed_code = f.read().strip()
                return fixed_code
            else:
                print("❌ Error: Output file not found")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running model: {e}")
            if e.stderr:
                print(f"Details: {e.stderr[:500]}")
            return None


def interactive_mode(model_path):
    """Interactive mode to fix code."""
    print("=" * 80)
    print("🔧 JAVA CODE FIXER - Interactive Mode")
    print("=" * 80)
    print("\nType or paste your buggy Java code.")
    print("For multi-line code, end with a line containing only 'END'")
    print("Type 'quit' to exit.\n")
    
    while True:
        print("-" * 80)
        print("📝 Paste your Java code (end with 'END' on a separate line):")
        
        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == 'END':
                    break
                if line.strip().lower() == 'quit':
                    print("\n👋 Goodbye!")
                    return
                lines.append(line)
            except EOFError:
                break
        
        if not lines:
            continue
            
        buggy_code = '\n'.join(lines)
        
        print("\n🐛 BUGGY CODE:")
        print(buggy_code)
        print()
        
        # Fix code
        fixed_code = fix_code(buggy_code, model_path)
        
        if fixed_code:
            print("✅ FIXED CODE:")
            print(fixed_code)
            print()
        else:
            print("❌ Could not fix the code.")
        
        print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Fix Java code using trained model',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:

  # Interactive mode
  python fix_code.py
  
  # Fix inline code
  python fix_code.py "public int sum(int a, int b) { return a - b; }"
  
  # Read from file
  python fix_code.py --file my_code.java
  
  # Specify model path
  python fix_code.py --model code/output/checkpoint-best/pytorch_model.bin "code here"
        """
    )
    
    parser.add_argument(
        'code',
        nargs='?',
        help='Java code to fix (optional, use interactive mode if omitted)'
    )
    
    parser.add_argument(
        '--file', '-f',
        help='Java file to fix'
    )
    
    parser.add_argument(
        '--model', '-m',
        default='code/output_small/checkpoint-best-bleu/pytorch_model.bin',
        help='Path to trained model (default: code/output_small/checkpoint-best-bleu/pytorch_model.bin)'
    )
    
    args = parser.parse_args()
    
    # Mode 1: Read from file
    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ Error: File not found: {args.file}")
            return 1
        
        with open(args.file, 'r') as f:
            buggy_code = f.read()
        
        print("🐛 BUGGY CODE:")
        print(buggy_code)
        print()
        
        fixed_code = fix_code(buggy_code, args.model)
        
        if fixed_code:
            print("✅ FIXED CODE:")
            print(fixed_code)
            
            # Ask if want to save
            try:
                save = input("\n💾 Save fixed code? (y/N): ").strip().lower()
                if save == 'y':
                    output_file = args.file.replace('.java', '_fixed.java')
                    with open(output_file, 'w') as f:
                        f.write(fixed_code)
                    print(f"✅ Saved to: {output_file}")
            except (EOFError, KeyboardInterrupt):
                print()
        
        return 0
    
    # Mode 2: Inline code
    elif args.code:
        print("🐛 BUGGY CODE:")
        print(args.code)
        print()
        
        fixed_code = fix_code(args.code, args.model)
        
        if fixed_code:
            print("✅ FIXED CODE:")
            print(fixed_code)
        
        return 0
    
    # Mode 3: Interactive
    else:
        try:
            interactive_mode(args.model)
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        
        return 0


if __name__ == '__main__':
    sys.exit(main())
