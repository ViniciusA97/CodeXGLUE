#!/usr/bin/env python3
"""
Pipeline: Modelo CodeRefinement + LLM Analysis

Fluxo:
1. Recebe código Java com bug
2. Executa modelo treinado para corrigir
3. Envia resultado do modelo + código original para LLM analisar
4. LLM julga se a correção foi correta e explica

Uso:
    python pipeline_model_llm.py --code "public int METHOD_1 ( ) { return null ; }"
    python pipeline_model_llm.py --file examples/sintaxe/1_function_syntax/example1_buggy.java
"""

import os
import sys
import argparse
import subprocess
import tempfile
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERRO: anthropic não instalado. Execute:")
    print("  pip install anthropic")
    sys.exit(1)

import sys

# Adicionar path do code-refinement
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CODE_REFINEMENT_PATH = os.path.join(PROJECT_ROOT, 'Code-Code', 'code-refinement')

if CODE_REFINEMENT_PATH not in sys.path:
    sys.path.insert(0, CODE_REFINEMENT_PATH)

from preprocess_java import JavaPreprocessor
from detokenize_java import JavaDetokenizer


class CodeRefinementPipeline:
    def __init__(self, model_path=None):
        # Usar modelo padrão se não fornecido
        if model_path is None:
            model_path = os.path.join(PROJECT_ROOT, 'pytorch_model.bin')
        
        self.model_path = model_path
        self.code_refinement_path = CODE_REFINEMENT_PATH
        self.model_path = model_path
        self.preprocessor = JavaPreprocessor()
        self.detokenizer = JavaDetokenizer()
        self.client = anthropic.Anthropic()
        
        if not os.path.exists(model_path):
            print(f"ERRO: Modelo não encontrado: {model_path}")
            sys.exit(1)
    
    def run_model(self, buggy_code):
        """Executa o modelo treinado no código com bug."""
        print("\n" + "="*80)
        print("ETAPA 1: Executando Modelo de Code Refinement")
        print("="*80)
        
        print(f"\nCódigo com Bug (input):")
        print(f"   {buggy_code}")
        
        # Preprocessar (tokenizar)
        print(f"\nTokenizando...")
        tokenized = self.preprocessor.preprocess(buggy_code)
        print(f"   {tokenized}")
        
        # Criar arquivos temporários
        with tempfile.TemporaryDirectory() as tmpdir:
            buggy_file = os.path.join(tmpdir, 'input.buggy')
            fixed_file = os.path.join(tmpdir, 'input.fixed')
            output_dir = os.path.join(tmpdir, 'output')
            
            # Escrever arquivo de entrada (dummy para fixed)
            with open(buggy_file, 'w') as f:
                f.write(tokenized)
            with open(fixed_file, 'w') as f:
                f.write(tokenized)  # Dummy, o modelo vai gerar
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Executar modelo
            print(f"\nExecutando modelo...")
            try:
                run_py_path = os.path.join(self.code_refinement_path, 'code', 'run.py')
                result = subprocess.run(
                    ['python3', run_py_path,
                     '--do_test',
                     '--model_type', 'roberta',
                     '--model_name_or_path', 'roberta-base',
                     '--config_name', 'roberta-base',
                     '--tokenizer_name', 'roberta-base',
                     '--load_model_path', self.model_path,
                     '--test_filename', f'{buggy_file},{fixed_file}',
                     '--output_dir', output_dir,
                     '--max_source_length', '256',
                     '--max_target_length', '256',
                     '--beam_size', '5',
                     '--eval_batch_size', '1'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode != 0:
                    print(f"ERRO ao executar modelo:")
                    print(result.stderr)
                    return None
                
                # Ler predição
                pred_file = os.path.join(output_dir, 'test_0.output')
                if not os.path.exists(pred_file):
                    print("ERRO: Arquivo de predição não gerado")
                    print(f"Output dir: {output_dir}")
                    print(f"Arquivos gerados: {os.listdir(output_dir) if os.path.exists(output_dir) else 'Nenhum'}")
                    if result.stderr:
                        print(f"Stderr do modelo: {result.stderr}")
                    return None
                
                with open(pred_file, 'r') as f:
                    tokenized_output = f.read().strip().split('\n')[0]  # Primeira linha
                
                print(f"   Modelo gerou (tokenizado):")
                print(f"   {tokenized_output}")
                
                # Detokenizar
                print(f"\nDetokenizando...")
                self.detokenizer.set_mappings(self.preprocessor.get_mappings())
                detokenized_output = self.detokenizer.detokenize(tokenized_output)
                print(f"   {detokenized_output}")
                
                return detokenized_output
            
            except subprocess.TimeoutExpired:
                print("ERRO: Timeout ao executar modelo (> 5 min)")
                return None
            except Exception as e:
                print(f"ERRO ao executar modelo: {e}")
                return None
    
    def analyze_with_llm(self, buggy_code, model_output, fixed_code=None):
        """Usa LLM para analisar a correção do modelo."""
        print("\n" + "="*80)
        print("ETAPA 2: Análise com LLM (Claude Haiku 4.5)")
        print("="*80)
        
        prompt = f"""Você é um especialista em Java e correção de código. 

Analise a correção feita por um modelo de Machine Learning treinado para corrigir bugs em Java.

CÓDIGO COM BUG (input do modelo):
```java
{buggy_code}
```

CORREÇÃO GERADA PELO MODELO (output):
```java
{model_output}
```

{f'''
ESPERADO (para referência):
```java
{fixed_code}
```
''' if fixed_code else ''}

Por favor, analise:

1. **Correção Correta?** (SIM/NÃO/PARCIAL)
   - A correção resolve o problema?
   - Há novos problemas introduzidos?

2. **Explicação**
   - Qual era o bug original?
   - O que o modelo fez?
   - A lógica está correta?

3. **Mudanças Realizadas** (destacar cada mudança)
   - Tokens adicionados/removidos
   - Operadores modificados
   - Estrutura alterada

4. **Avaliação do Modelo**
   - Força: o que o modelo fez bem
   - Fraqueza: onde falhou

Format sua resposta de forma clara e visual, usando:
- [OK] para sucessos
- [ERRO] para erros
- [AVISO] para avisos
- [MUDANÇA] para mudanças
"""
        
        print("\nChamando Claude para análise...")
        
        try:
            message = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            analysis = message.content[0].text
            return analysis
        
        except Exception as e:
            print(f"ERRO ao chamar Claude: {e}")
            return None
    
    def run_pipeline(self, buggy_code, fixed_code=None):
        """Executa a pipeline completa."""
        print("\n" + "="*80)
        print("PIPELINE: Fine Tuning Model + Revisão com LLM")
        print("="*80)
        
        # Etapa 1: Modelo
        model_output = self.run_model(buggy_code)
        if model_output is None:
            print("\nPipeline falhou na etapa 1 (modelo)")
            return False
        
        # Etapa 2: LLM Analysis
        analysis = self.analyze_with_llm(buggy_code, model_output, fixed_code)
        if analysis is None:
            print("\nPipeline falhou na etapa 2 (LLM)")
            return False
        
        # Exibir resultado
        print("\n" + "="*80)
        print("ETAPA 3: Resultado da Análise")
        print("="*80)
        print(analysis)
        
        print("\n" + "="*80)
        print("PIPELINE CONCLUIDA COM SUCESSO")
        print("="*80 + "\n")
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Pipeline: Code Refinement Model + LLM Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:

  # Com código inline
  python pipeline_model_llm.py --code "public int METHOD_1 ( ) { return null ; }"
  
  # Com arquivo
  python pipeline_model_llm.py --file examples/sintaxe/1_function_syntax/example1_buggy.java
  
  # Com arquivo e esperado (para referência)
  python pipeline_model_llm.py --file buggy.java --expected fixed.java
  
  # Com modelo customizado
  python pipeline_model_llm.py --code "..." --model code/output_small/checkpoint-best-bleu/pytorch_model.bin
        """
    )
    
    parser.add_argument('--code', type=str, help='Código Java com bug (inline)')
    parser.add_argument('--file', type=str, help='Arquivo com código Java com bug')
    parser.add_argument('--expected', type=str, help='Arquivo com código esperado (para referência)')
    parser.add_argument('--model', type=str, default=None,
                       help='Caminho para o modelo treinado (padrão: /pytorch_model.bin na raiz)')
    
    
    args = parser.parse_args()
    
    # Validação de entrada
    if not args.code and not args.file:
        parser.print_help()
        print("\n❌ ERRO: Você deve fornecer --code ou --file")
        sys.exit(1)
    
    if args.code and args.file:
        print("❌ ERRO: Forneça apenas --code OU --file, não ambos")
        sys.exit(1)
    
    # Ler código com bug
    if args.code:
        buggy_code = args.code
    else:
        if not os.path.exists(args.file):
            print(f"❌ ERRO: Arquivo não encontrado: {args.file}")
            sys.exit(1)
        with open(args.file, 'r') as f:
            buggy_code = f.read().strip()
    
    # Ler código esperado (opcional)
    fixed_code = None
    if args.expected:
        if not os.path.exists(args.expected):
            print(f"⚠️ AVISO: Arquivo esperado não encontrado: {args.expected}")
        else:
            with open(args.expected, 'r') as f:
                fixed_code = f.read().strip()
    
    # Criar pipeline e executar
    pipeline = CodeRefinementPipeline(model_path=args.model)
    success = pipeline.run_pipeline(buggy_code, fixed_code)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
