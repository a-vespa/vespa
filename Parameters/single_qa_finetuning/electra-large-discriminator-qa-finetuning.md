Electra Large Discriminator QA Finetuning Parameters
============================================================================================================

Model and parameters used to finetune ELectra QA model


Pre-trained(Language) model
--------------------
```
ELECTRA_large_discriminator
```

Dataset
--------------------
```
SQuAD v2.0
```

QA Finetuning Parameters
--------------------
```
python ${EXAMPLES}/run_squad.py \
  --model_type electra \
  --model_name_or_path google/electra-large-discriminator \
  --do_train \
  --do_eval \
  --train_file ${SQUAD}/train-v2.0.json \
  --predict_file ${SQUAD}/dev-v2.0.json \
  --version_2_with_negative \
  --do_lower_case \
  --num_train_epochs 3 \
  --warmup_steps 306 \
  --weight_decay 0.01 \
  --learning_rate 3e-5 \
  --max_grad_norm 0.5 \
  --adam_epsilon 1e-6 \
  --max_seq_length 512 \
  --doc_stride 128 \
  --per_gpu_train_batch_size 8 \
  --gradient_accumulation_steps 16 \
  --per_gpu_eval_batch_size 128 \
  --fp16 \
  --fp16_opt_level O1 \
  --threads 12 \
  --logging_steps 50 \
  --save_steps 1000 \
  --overwrite_output_dir \
  --output_dir ${MODEL_PATH}
```

System & Software
--------------------
```
Transformers: 2.11.0
PyTorch: 1.5.0
TensorFlow: 2.2.0
Python: 3.8.1
OS/Platform: Linux-5.3.0-59-generic-x86_64-with-glibc2.10
CPU/GPU: Intel i9-9900K / NVIDIA Titan RTX 24GB
```


References
--------------------
* https://huggingface.co/ahotrod/electra_large_discriminator_squad2_512