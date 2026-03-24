# 🚀 Code Refinement - Fine-Tuning com Google Colab

## ✅ Este fork já está corrigido e pronto para uso!

### Correções aplicadas:
- ✅ `AdamW` importado de `torch.optim` (compatível com transformers 5.x)
- ✅ Atributo `torchscript` corrigido com `getattr()` (compatível com RobertaConfig atual)

---

## 📋 Como usar no Google Colab

### 1. Acesse o Google Colab
https://colab.research.google.com

### 2. Configure a GPU (IMPORTANTE!)
- Menu: `Runtime` → `Change runtime type`
- Hardware accelerator: Selecione `T4 GPU` ou `GPU`
- Clique em `Save`

### 3. Execute as células abaixo

---

## 📦 Célula 1: Instalação e Clone

```python
# Instalar dependências
!pip install -q transformers torch scikit-learn

# Clonar o repositório corrigido (substitua YOUR_USERNAME pelo seu usuário do GitHub)
!git clone https://github.com/YOUR_USERNAME/CodeXGLUE.git
%cd CodeXGLUE/Code-Code/code-refinement

print("✅ Setup completo!")
```

---

## 🔍 Célula 2: Verificar GPU e Dados

```python
import torch

# Verificar GPU
if torch.cuda.is_available():
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"   Memória: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
else:
    print("⚠️ GPU não disponível!")

# Verificar dados
print("\n📊 Dataset SMALL:")
!wc -l data/small/train.buggy-fixed.buggy data/small/valid.buggy-fixed.buggy data/small/test.buggy-fixed.buggy
```

---

## 🚀 Célula 3: Fine-Tuning (2-3 horas)

```python
%cd code

!python run.py \
    --do_train \
    --do_eval \
    --model_type roberta \
    --model_name_or_path microsoft/codebert-base \
    --config_name roberta-base \
    --tokenizer_name roberta-base \
    --train_filename ../data/small/train.buggy-fixed.buggy,../data/small/train.buggy-fixed.fixed \
    --dev_filename ../data/small/valid.buggy-fixed.buggy,../data/small/valid.buggy-fixed.fixed \
    --output_dir ./output_small \
    --max_source_length 256 \
    --max_target_length 256 \
    --beam_size 5 \
    --train_batch_size 16 \
    --eval_batch_size 16 \
    --learning_rate 5e-5 \
    --train_steps 100000 \
    --eval_steps 5000

print("✅ Treinamento concluído!")
```

---

## 🧪 Célula 4: Inferência

```python
!python run.py \
    --do_test \
    --model_type roberta \
    --model_name_or_path roberta-base \
    --config_name roberta-base \
    --tokenizer_name roberta-base \
    --load_model_path ./output_small/checkpoint-best-bleu/pytorch_model.bin \
    --dev_filename ../data/small/valid.buggy-fixed.buggy,../data/small/valid.buggy-fixed.fixed \
    --test_filename ../data/small/test.buggy-fixed.buggy,../data/small/test.buggy-fixed.fixed \
    --output_dir ./output_small \
    --max_source_length 256 \
    --max_target_length 256 \
    --beam_size 5 \
    --eval_batch_size 16

print("✅ Inferência concluída!")
```

---

## 📊 Célula 5: Avaliação

```python
%cd ..

!python evaluator/evaluator.py \
    -ref data/small/test.buggy-fixed.fixed \
    -pre code/output_small/test_0.output

print("\n📈 Esperado: BLEU ~77.42, Acc ~16.4%")
```

---

## 💾 Célula 6: Download do Modelo

```python
import os
from google.colab import files

checkpoint_path = 'code/output_small/checkpoint-best-bleu'

if os.path.exists(checkpoint_path):
    !zip -r model_trained.zip code/output_small/checkpoint-best-bleu/
    files.download('model_trained.zip')
    print("✅ Download iniciado!")
else:
    print("⚠️ Modelo não encontrado. Verifique se o treinamento terminou.")
```

---

## ☁️ Célula 7 (Opcional): Salvar no Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')

!cp -r code/output_small /content/drive/MyDrive/code_refinement_model

print("✅ Modelo salvo no Drive: MyDrive/code_refinement_model")
```

---

## 💡 Ajustes Opcionais

### Para treino mais rápido (teste):
```python
--train_steps 10000      # ao invés de 100000
--eval_steps 2000        # ao invés de 5000
```

### Se ficar sem memória GPU:
```python
--train_batch_size 8     # ao invés de 16
--eval_batch_size 8      # ao invés de 16
```

### Para dataset MEDIUM:
```python
--train_filename ../data/medium/train.buggy-fixed.buggy,../data/medium/train.buggy-fixed.fixed
--dev_filename ../data/medium/valid.buggy-fixed.buggy,../data/medium/valid.buggy-fixed.fixed
```

---

## 📚 Referências

- **Paper:** [An empirical study on learning bug-fixing patches](https://arxiv.org/pdf/1812.08693.pdf)
- **CodeBERT:** [microsoft/codebert-base](https://huggingface.co/microsoft/codebert-base)
- **CodeXGLUE:** [GitHub Repository](https://github.com/microsoft/CodeXGLUE)

---

**🎉 Pronto! Basta fazer o commit deste fork e usar no Colab!**
