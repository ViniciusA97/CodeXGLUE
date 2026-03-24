#!/bin/bash
# Script para teste rápido do treinamento (10k steps ao invés de 100k)
# Use este script para validar que tudo está funcionando antes do treino completo

echo "🚀 Iniciando Teste Rápido de Fine-Tuning (10k steps)..."
echo "================================================"

cd "$(dirname "$0")/code"

python run.py \
    --do_train \
    --do_eval \
    --model_type roberta \
    --model_name_or_path microsoft/codebert-base \
    --config_name roberta-base \
    --tokenizer_name roberta-base \
    --train_filename ../data/small/train.buggy-fixed.buggy,../data/small/train.buggy-fixed.fixed \
    --dev_filename ../data/small/valid.buggy-fixed.buggy,../data/small/valid.buggy-fixed.fixed \
    --output_dir ./output_small_test \
    --max_source_length 128 \
    --max_target_length 128 \
    --beam_size 3 \
    --train_batch_size 4 \
    --eval_batch_size 4 \
    --learning_rate 5e-5 \
    --train_steps 10000 \
    --eval_steps 2000

echo ""
echo "✅ Teste concluído!"
echo "📁 Modelo salvo em: ./code/output_small_test/"
