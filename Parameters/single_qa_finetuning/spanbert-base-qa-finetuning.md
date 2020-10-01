SpanBERT Base QA Finetuning Parameters
=============================================================================================

Model and parameters used to finetune SpanBERT QA model


Pre-trained(Language) model
--------------------
```
SpanBERT Base, Cased
```

Dataset
--------------------
```
SQuAD v2.0
```

QA Finetuning Parameters
--------------------
```
python code/run_squad.py \
  --do_train \
  --do_eval \
  --model spanbert-base-cased \
  --train_file train-v2.0.json \
  --dev_file dev-v2.0.json \
  --train_batch_size 32 \
  --eval_batch_size 32  \
  --learning_rate 2e-5 \
  --num_train_epochs 4 \
  --max_seq_length 512 \
  --doc_stride 128 \
  --eval_metric best_f1 \
  --output_dir squad2_output \
  --version_2_with_negative \
  --fp16
```

References
--------------------
* https://huggingface.co/mrm8488/spanbert-base-finetuned-squadv2