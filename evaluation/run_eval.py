import os 
import json
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from config.settings import cfg
from ragas.metrics import (
  Faithfulness,
  AnswerCorrectness,
  AnswerRelevancy,
  ContextRecall,
  ContextPrecision
)
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI

# Khởi tạo LLM cho Ragas bằng API Key từ config
evaluator_llm = LangchainLLMWrapper(ChatOpenAI(
    model="gpt-4o-mini", 
    api_key=cfg.openai.api_key
))

from chatbot import chatbot
from core.logger import get_logger

log = get_logger('evaluation')

def run_evaluation(dataset_path = 'evaluation/eval_dataset.json'):
  if not os.path.exists(dataset_path):
    log.error(f'Dataset not found at {dataset_path}')
    return
  
  with open(dataset_path, 'r', encoding = 'utf-8') as f:
    samples = json.load(f)
  
  log.info(f'Starting evaluation on {len(samples)} samples')

  results = []

  print("\n" + "-"*60)
  print(f"{'#':>3}  {'Route':<10}  {'Docs':>4}  Question")
  print("-"*60)


  for i, item in enumerate(samples):
    question = item['question']
    ground_truth = item.get('ground_truth', '')

    log.info(f"[{i+1}/{len(samples)}] Processing: {question}")

    response = chatbot.chat(
      question,
      user_id='eval_user',
      session_id=f'eval_{i}',
      save_history=False
    )

    contexts = [doc.text for doc in response.docs] if hasattr(response, 'docs') else []
    route = getattr(response, 'route', 'unknown')
    n_docs = len(contexts)

    # Debug line per sample
    status = '[OK]' if n_docs > 0 else '[--]'
    safe_q = question[:60].encode('ascii', errors='replace').decode('ascii')
    print(f"{status} {i+1:>2}.  route={route:<8}  docs={n_docs:>2}  {safe_q}")

    results.append({
      'question': question,
      'answer': response.answer,
      'retrieved_contexts': contexts,
      'ground_truth': ground_truth
    })

  print("-"*60 + "\n")

  hf_dataset = Dataset.from_list(results)

  log.info('Computing metrics...')

  result = evaluate(
    hf_dataset,
    metrics = [
      Faithfulness(llm=evaluator_llm),
      AnswerCorrectness(llm=evaluator_llm),
      AnswerRelevancy(llm=evaluator_llm),
      ContextRecall(llm=evaluator_llm),
      ContextPrecision(llm=evaluator_llm)
    ]
  )

  df = result.to_pandas()
  output_file = 'evaluation/eval_results.csv'
  df.to_csv(output_file, index = False, encoding = 'utf-8-sig')

  print("\n" + "="*50)
  print("EVALUATION RESULTS SUMMARY")
  print("="*50)
  print(result)
  print("="*50)
  print(f"Detailed results saved to: {output_file}")

if __name__ == "__main__":
  import sys
  sys.path.append(os.getcwd())
  
  run_evaluation()