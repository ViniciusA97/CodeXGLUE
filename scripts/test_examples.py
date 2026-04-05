import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Detectar diretório raiz do projeto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Caminhos absolutos
CODE_REFINEMENT_PATH = os.path.join(PROJECT_ROOT, 'Code-Code', 'code-refinement')
MODEL_PATH = os.path.join(PROJECT_ROOT, 'model.bin')

# Mudar para diretório do code-refinement
os.chdir(CODE_REFINEMENT_PATH)

if not os.path.exists(MODEL_PATH):
    print(f"ERRO: Modelo nao encontrado em {MODEL_PATH}")
    print("Coloque o arquivo pytorch_model.bin na raiz do projeto.")
    sys.exit(1)
else:
    # Pastas de sintaxe (9 categorias)
    syntax_folders = [
        'examples/sintaxe/1_function_syntax',
        'examples/sintaxe/2_conditionals',
        'examples/sintaxe/3_variables',
        'examples/sintaxe/4_loops',
        'examples/sintaxe/5_arrays',
        'examples/sintaxe/6_operators',
        'examples/sintaxe/7_strings',
        'examples/sintaxe/8_primitives',
        'examples/sintaxe/9_exceptions'
    ]

    # Pastas contextuais
    contextual_folders = [
        'examples/contextual/simple'
    ]

    example_folders = syntax_folders + contextual_folders

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_dir = os.path.join(CODE_REFINEMENT_PATH, f'test_results_{timestamp}')
    os.makedirs(results_dir, exist_ok=True)

    print(f"Testando {len(example_folders)} pastas de exemplos...")

    for folder in example_folders:
        if not os.path.exists(folder):
            print(f"Pasta {folder} nao encontrada, pulando...")
            continue

        example_count = len([f for f in os.listdir(folder) if f.endswith('_buggy.java')])
        folder_name = folder.replace('examples/', '').replace('/', '_')
        print(f"\n[{folder_name}] {example_count} exemplos")

        output_file_real = f'{results_dir}/{folder_name}_test_real.txt'
        output_file_model = f'{results_dir}/{folder_name}_test_model.txt'

        # test_model_real.py
        print(f"  Executando test_model_real.py...")
        try:
            result = subprocess.run(
                ['python3', 'test_model_real.py',
                 '--model', MODEL_PATH,
                 '--examples-dir', folder],
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode != 0:
                print(f"  [ERRO] test_model_real.py falhou com código {result.returncode}")
                if result.stderr:
                    print(f"  Stderr:\n{result.stderr}")
                if result.stdout:
                    print(f"  Stdout:\n{result.stdout}")

            with open(output_file_real, 'w', encoding='utf-8') as f:
                f.write(f"TESTE COM TOKENIZACAO/DETOKENIZACAO\n")
                f.write(f"Pasta: {folder_name}\n")
                f.write(f"Data: {timestamp}\n")
                f.write(f"Codigo de retorno: {result.returncode}\n")
                f.write(f"{'='*80}\n\n")
                f.write(result.stdout)
                if result.stderr:
                    f.write(f"\n\nERROS:\n{result.stderr}")

            print(f"  test_model_real.py concluido")

        except subprocess.TimeoutExpired:
            print(f"  [ERRO] Timeout em test_model_real.py (excedeu 10 minutos)")
            with open(output_file_real, 'w', encoding='utf-8') as f:
                f.write(f"TIMEOUT: Teste excedeu 10 minutos\n")
        except Exception as e:
            print(f"  [ERRO] Excecao em test_model_real.py: {type(e).__name__}: {e}")
            with open(output_file_real, 'w', encoding='utf-8') as f:
                f.write(f"ERRO: {type(e).__name__}: {e}\n")

        # test_model.py
        print(f"  Executando test_model.py...")
        try:
            result = subprocess.run(
                ['python3', 'test_model.py',
                 '--model_path', MODEL_PATH,
                 '--examples_dir', folder],
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode != 0:
                print(f"  [ERRO] test_model.py falhou com código {result.returncode}")
                if result.stderr:
                    print(f"  Stderr:\n{result.stderr}")
                if result.stdout:
                    print(f"  Stdout:\n{result.stdout}")

            with open(output_file_model, 'w', encoding='utf-8') as f:
                f.write(f"TESTE SEM TOKENIZACAO/DETOKENIZACAO\n")
                f.write(f"Pasta: {folder_name}\n")
                f.write(f"Data: {timestamp}\n")
                f.write(f"Codigo de retorno: {result.returncode}\n")
                f.write(f"{'='*80}\n\n")
                f.write(result.stdout)
                if result.stderr:
                    f.write(f"\n\nERROS:\n{result.stderr}")

            print(f"  test_model.py concluido")

        except subprocess.TimeoutExpired:
            print(f"  [ERRO] Timeout em test_model.py (excedeu 10 minutos)")
            with open(output_file_model, 'w', encoding='utf-8') as f:
                f.write(f"TIMEOUT: Teste excedeu 10 minutos\n")
        except Exception as e:
            print(f"  [ERRO] Excecao em test_model.py: {type(e).__name__}: {e}")
            with open(output_file_model, 'w', encoding='utf-8') as f:
                f.write(f"ERRO: {type(e).__name__}: {e}\n")

    print(f"\n[OK] Testes concluidos!")
    print(f"Resultados salvos em: {results_dir}")
    print(f"Total de arquivos: {len(os.listdir(results_dir))}")
