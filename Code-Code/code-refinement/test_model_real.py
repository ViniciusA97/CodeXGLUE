#!/usr/bin/env python3
"""
Test the model with REAL Java code examples using tokenization/detokenization.

This script:
1. Reads real Java code from examples/ directory
2. Tokenizes it (preprocess)
3. Runs the model
4. Detokenizes back to real Java (detokenize)
5. Compares with expected fix

Usage:
    python test_model_real.py
    python test_model_real.py --examples-dir examples/
"""

import os
import sys
import glob
import subprocess
import tempfile
from pathlib import Path
from preprocess_java import JavaPreprocessor
from detokenize_java import JavaDetokenizer


def test_with_real_code(examples_dir='examples', model_path='code/output_small/checkpoint-best-bleu/pytorch_model.bin'):
    """
    Test model with real Java code examples.
    
    Args:
        examples_dir: Directory containing example files
        model_path: Path to trained model
    """
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return
    
    # Find all buggy examples
    buggy_files = sorted(glob.glob(f'{examples_dir}/example*_buggy.java'))
    
    if not buggy_files:
        print(f"❌ No examples found in {examples_dir}")
        return
    
    print("="*80)
    print("RESULTADOS DO TESTE")
    print("="*80)
    print()
    
    correct = 0
    total = 0
    errors = 0
    
    for buggy_file in buggy_files:
        example_name = os.path.basename(buggy_file).replace('_buggy.java', '')
        fixed_file = buggy_file.replace('_buggy.java', '_fixed.java')
        
        if not os.path.exists(fixed_file):
            print(f"⚠️  Skipping {example_name}: no fixed file")
            continue
        
        total += 1
        
        print("─"*80)
        print(f"EXEMPLO {total}: {example_name}")
        print("─"*80)
        
        # Read files
        with open(buggy_file, 'r') as f:
            buggy_code = f.read().strip()
        with open(fixed_file, 'r') as f:
            expected_code = f.read().strip()
        
        # Remove comments from expected (for comparison)
        expected_clean = '\n'.join([line for line in expected_code.split('\n') 
                                   if not line.strip().startswith('//')])
        
        print(f"\nCODIGO COM BUG:")
        for line in buggy_code.split('\n'):
            print(f"   {line}")
        
        print(f"\nCORRECAO ESPERADA:")
        for line in expected_clean.split('\n'):
            print(f"   {line}")
        
        try:
            # Step 1: Preprocess (tokenize)
            preprocessor = JavaPreprocessor()
            tokenized_buggy = preprocessor.preprocess(buggy_code)
            mappings = preprocessor.get_mappings()
            
            
            # Step 2: Run model
            with tempfile.TemporaryDirectory() as tmpdir:
                buggy_tmp = os.path.join(tmpdir, 'input.buggy')
                fixed_tmp = os.path.join(tmpdir, 'input.fixed')
                output_dir = os.path.join(tmpdir, 'output')
                
                # Write tokenized code
                with open(buggy_tmp, 'w') as f:
                    f.write(tokenized_buggy + '\n')
                with open(fixed_tmp, 'w') as f:
                    f.write(tokenized_buggy + '\n')  # Dummy
                
                # Run model
                cmd = [
                    sys.executable, 'code/run.py',
                    '--do_test',
                    '--model_type', 'roberta',
                    '--model_name_or_path', 'roberta-base',
                    '--config_name', 'roberta-base',
                    '--tokenizer_name', 'roberta-base',
                    '--load_model_path', model_path,
                    '--test_filename', f'{buggy_tmp},{fixed_tmp}',
                    '--output_dir', output_dir,
                    '--max_source_length', '256',
                    '--max_target_length', '256',
                    '--beam_size', '5',
                    '--eval_batch_size', '1'
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
                
                # Read model output
                output_file = os.path.join(output_dir, 'test_0.output')
                if os.path.exists(output_file):
                    with open(output_file, 'r') as f:
                        tokenized_output = f.read().strip()
                    
                    # Step 3: Detokenize back to real Java
                    detokenizer = JavaDetokenizer(mappings)
                    fixed_code = detokenizer.detokenize(tokenized_output)
                    
                    print(f"\nCORRECAO DO MODELO:")
                    for line in fixed_code.split('\n'):
                        print(f"   {line}")
                    
                    # Compare (normalize whitespace)
                    fixed_normalized = ' '.join(fixed_code.split())
                    expected_normalized = ' '.join(expected_clean.split())
                    
                    if fixed_normalized == expected_normalized:
                        print("\nCorreto")
                        correct += 1
                    else:
                        print("\nDiferente da esperada")
                else:
                    print(f"\nErro: arquivo de saida nao encontrado")
                    errors += 1
                    
        except Exception as e:
            print(f"\nErro: {e}")
            errors += 1
        
        print()
    
    # Final statistics
    print("="*80)
    print("ESTATISTICAS FINAIS")
    print("="*80)
    print(f"  Total de exemplos: {total}")
    print(f"  Acertos exatos: {correct} ({100*correct/total if total > 0 else 0:.1f}%)")
    print(f"  Diferencas: {total - correct - errors} ({100*(total-correct-errors)/total if total > 0 else 0:.1f}%)")
    if errors > 0:
        print(f"  Erros: {errors}")
    print("="*80)
    print()
    print("Teste concluido!")
    print()


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test model with real Java code (with tokenization)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Test with default examples directory
  python test_model_real.py
  
  # Test with custom examples directory
  python test_model_real.py --examples-dir my_examples/
  
  # Test with custom model
  python test_model_real.py --model code/output/checkpoint-best/pytorch_model.bin

This script automatically:
  1. Reads real Java code from examples
  2. Tokenizes it (METHOD_1, VAR_1, etc.)
  3. Runs the model
  4. Detokenizes back to real Java
  5. Compares with expected output
        """
    )
    
    parser.add_argument('--examples-dir', default='examples',
                       help='Directory containing example files (default: examples)')
    parser.add_argument('--model', default='code/output_small/checkpoint-best-bleu/pytorch_model.bin',
                       help='Path to trained model')
    
    args = parser.parse_args()
    
    test_with_real_code(args.examples_dir, args.model)


if __name__ == '__main__':
    main()
