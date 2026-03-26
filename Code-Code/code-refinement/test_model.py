#!/usr/bin/env python3
"""
Script para testar o modelo treinado de Code Refinement com exemplos reais de Java.

Uso:
    python test_model.py --model_path code/output_small/checkpoint-best-bleu/pytorch_model.bin
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def normalize_java_code(code):
    """
    Normaliza código Java para o formato esperado pelo modelo.
    Remove comentários e formata para uma linha.
    """
    # Remover comentários
    lines = [line.strip() for line in code.split('\n') 
             if line.strip() and not line.strip().startswith('//')]
    
    # Juntar em uma linha
    normalized = ' '.join(lines)
    
    # Substituir múltiplos espaços por um único
    normalized = ' '.join(normalized.split())
    
    return normalized

def prepare_test_files(examples_dir):
    """
    Prepara arquivos de teste a partir dos exemplos em Java.
    """
    examples_path = Path(examples_dir)
    
    # Encontrar todos os arquivos buggy
    buggy_files = sorted(examples_path.glob('*_buggy.java'))
    
    if not buggy_files:
        print(f"❌ Nenhum arquivo *_buggy.java encontrado em {examples_dir}")
        return None, None
    
    buggy_codes = []
    fixed_codes = []
    example_names = []
    
    for buggy_file in buggy_files:
        # Ler código bugado
        with open(buggy_file, 'r') as f:
            buggy_code = f.read()
        
        # Ler código corrigido correspondente
        fixed_file = buggy_file.parent / buggy_file.name.replace('_buggy.java', '_fixed.java')
        if fixed_file.exists():
            with open(fixed_file, 'r') as f:
                fixed_code = f.read()
        else:
            fixed_code = buggy_code  # Usar o mesmo se não houver correção
        
        # Normalizar códigos
        buggy_normalized = normalize_java_code(buggy_code)
        fixed_normalized = normalize_java_code(fixed_code)
        
        buggy_codes.append(buggy_normalized)
        fixed_codes.append(fixed_normalized)
        example_names.append(buggy_file.stem.replace('_buggy', ''))
    
    # Criar arquivos temporários
    buggy_file_path = 'test_examples.buggy'
    fixed_file_path = 'test_examples.fixed'
    
    with open(buggy_file_path, 'w') as f:
        f.write('\n'.join(buggy_codes))
    
    with open(fixed_file_path, 'w') as f:
        f.write('\n'.join(fixed_codes))
    
    print(f"✅ Preparados {len(buggy_codes)} exemplos para teste")
    
    return buggy_file_path, fixed_file_path, example_names, buggy_codes, fixed_codes

def run_inference(model_path, buggy_file, fixed_file, output_dir='./test_output'):
    """
    Executa inferência usando o modelo treinado.
    """
    print("\n🤖 Executando inferência...")
    
    # Criar diretório de output
    os.makedirs(output_dir, exist_ok=True)
    
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
        '--max_source_length', '128',
        '--max_target_length', '128',
        '--beam_size', '3',
        '--eval_batch_size', '1'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Inferência concluída!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na inferência: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def display_results(example_names, buggy_codes, fixed_codes, output_file):
    """
    Exibe os resultados da inferência de forma formatada.
    """
    if not os.path.exists(output_file):
        print(f"❌ Arquivo de output não encontrado: {output_file}")
        return
    
    with open(output_file, 'r') as f:
        predictions = f.readlines()
    
    print("\n" + "="*80)
    print("📊 RESULTADOS DO TESTE")
    print("="*80)
    
    acertos = 0
    total = len(example_names)
    
    for i, (name, buggy, fixed, pred) in enumerate(zip(example_names, buggy_codes, fixed_codes, predictions), 1):
        pred = pred.strip()
        fixed = fixed.strip()
        
        print(f"\n{'─'*80}")
        print(f"EXEMPLO {i}: {name}")
        print('─'*80)
        
        print("\n🐛 CÓDIGO COM BUG:")
        print(f"   {buggy}")
        
        print("\n✅ CORREÇÃO ESPERADA:")
        print(f"   {fixed}")
        
        print("\n🤖 CORREÇÃO DO MODELO:")
        print(f"   {pred}")
        
        # Verificar se acertou
        if pred == fixed:
            print("\n✅ ACERTOU! Correção 100% correta!")
            acertos += 1
        else:
            print("\n⚠️  Diferente da esperada")
            # Mostrar diferenças
            if len(pred) != len(fixed):
                print(f"   Tamanho: esperado={len(fixed)}, predito={len(pred)}")
    
    print("\n" + "="*80)
    print("📈 ESTATÍSTICAS FINAIS")
    print("="*80)
    print(f"  Total de exemplos: {total}")
    print(f"  Acertos exatos: {acertos} ({acertos/total*100:.1f}%)")
    print(f"  Diferenças: {total-acertos} ({(total-acertos)/total*100:.1f}%)")
    print("="*80)

def main():
    parser = argparse.ArgumentParser(description='Testar modelo de Code Refinement')
    parser.add_argument('--model_path', 
                       default='code/output_small/checkpoint-best-bleu/pytorch_model.bin',
                       help='Caminho para o modelo treinado')
    parser.add_argument('--examples_dir', 
                       default='examples',
                       help='Diretório com exemplos de código Java')
    parser.add_argument('--output_dir',
                       default='./test_output',
                       help='Diretório para salvar outputs')
    
    args = parser.parse_args()
    
    print("🚀 TESTADOR DE MODELO - CODE REFINEMENT")
    print("="*80)
    
    # Verificar se o modelo existe
    if not os.path.exists(args.model_path):
        print(f"❌ Modelo não encontrado: {args.model_path}")
        print("\n💡 Dica: Execute o treinamento primeiro ou ajuste o caminho do modelo")
        return 1
    
    print(f"✅ Modelo encontrado: {args.model_path}")
    
    # Preparar arquivos de teste
    result = prepare_test_files(args.examples_dir)
    if result is None:
        return 1
    
    buggy_file, fixed_file, example_names, buggy_codes, fixed_codes = result
    
    # Executar inferência
    if not run_inference(args.model_path, buggy_file, fixed_file, args.output_dir):
        return 1
    
    # Exibir resultados
    output_file = os.path.join(args.output_dir, 'test_0.output')
    display_results(example_names, buggy_codes, fixed_codes, output_file)
    
    # Limpar arquivos temporários
    try:
        os.remove(buggy_file)
        os.remove(fixed_file)
    except:
        pass
    
    print("\n✅ Teste concluído!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
