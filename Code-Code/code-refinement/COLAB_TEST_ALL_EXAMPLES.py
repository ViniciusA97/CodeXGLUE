import os
import subprocess
from datetime import datetime

os.chdir('/content/CodeXGLUE/Code-Code/code-refinement')

model_path = 'code/output_large/checkpoint-best-bleu/pytorch_model.bin'
if not os.path.exists(model_path):
    print("Modelo nao encontrado. Execute a celula de download do modelo primeiro.")
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
    results_dir = f'test_results_{timestamp}'
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
                 '--model', 'code/output_large/checkpoint-best-bleu/pytorch_model.bin',
                 '--examples-dir', folder],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            with open(output_file_real, 'w', encoding='utf-8') as f:
                f.write(f"TESTE COM TOKENIZACAO/DETOKENIZACAO\n")
                f.write(f"Pasta: {folder_name}\n")
                f.write(f"Data: {timestamp}\n")
                f.write(f"{'='*80}\n\n")
                f.write(result.stdout)
                if result.stderr:
                    f.write(f"\n\nERROS:\n{result.stderr}")
            
            print(f"  test_model_real.py concluido")
            
        except subprocess.TimeoutExpired:
            print(f"  Timeout em test_model_real.py")
            with open(output_file_real, 'w', encoding='utf-8') as f:
                f.write(f"TIMEOUT: Teste excedeu 10 minutos\n")
        except Exception as e:
            print(f"  Erro em test_model_real.py: {e}")
            with open(output_file_real, 'w', encoding='utf-8') as f:
                f.write(f"ERRO: {e}\n")
        
        # test_model.py
        print(f"  Executando test_model.py...")
        try:
            result = subprocess.run(
                ['python3', 'test_model.py', 
                 '--model_path', 'code/output_large/checkpoint-best-bleu/pytorch_model.bin',
                 '--examples_dir', folder],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            with open(output_file_model, 'w', encoding='utf-8') as f:
                f.write(f"TESTE SEM TOKENIZACAO/DETOKENIZACAO\n")
                f.write(f"Pasta: {folder_name}\n")
                f.write(f"Data: {timestamp}\n")
                f.write(f"{'='*80}\n\n")
                f.write(result.stdout)
                if result.stderr:
                    f.write(f"\n\nERROS:\n{result.stderr}")
            
            print(f"  test_model.py concluido")
            
        except subprocess.TimeoutExpired:
            print(f"  Timeout em test_model.py")
            with open(output_file_model, 'w', encoding='utf-8') as f:
                f.write(f"TIMEOUT: Teste excedeu 10 minutos\n")
        except Exception as e:
            print(f"  Erro em test_model.py: {e}")
            with open(output_file_model, 'w', encoding='utf-8') as f:
                f.write(f"ERRO: {e}\n")
    
    # Criar ZIP
    print(f"\nCriando arquivo ZIP...")
    zip_filename = f'test_results_{timestamp}.zip'
    
    try:
        subprocess.run(
            ['zip', '-r', zip_filename, results_dir],
            check=True,
            capture_output=True
        )
        print(f"ZIP criado: {zip_filename}")
    except Exception as e:
        print(f"Erro ao criar ZIP: {e}")
    
    # Download
    print(f"\nIniciando download...")
    from google.colab import files
    
    if os.path.exists(zip_filename):
        files.download(zip_filename)
        print(f"Download concluido: {zip_filename}")
    
    print(f"\nTestes concluidos. Arquivos gerados: {len(os.listdir(results_dir))}")
