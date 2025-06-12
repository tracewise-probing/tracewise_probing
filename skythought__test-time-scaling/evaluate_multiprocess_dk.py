from datasets import load_dataset
import sys
from functools import partial
import importlib.util
import dspy
import numpy as np
from tqdm import tqdm
import os
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
from collections import Counter

from live_code_bench_program import (
    generate_tests_repeat,
    post_process_code,
    has_test_type,
    NaiveCodeGenerator,
    NaiveCodeGeneratorNoDSPy,
    CodeGeneratorWithSelfDebug,
    generate_tests_for_one_example,
)
import random
from datetime import datetime
from live_code_bench_execute import check_correctness, check_correctness_oracle

import json
import base64
import zlib
import pickle
import scipy.stats as stats
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
from util import name_map

from pprint import pprint 
from dspy.utils.callback import BaseCallback
from dspy import Prediction
from contextlib import nullcontext


class AgentLoggingCallback(BaseCallback):
    """Logs each Module call (grouped by call_id), serializing Predictions
       and capturing an example.task_id automatically if present."""

    def __init__(self, save_file_path: str):
        self._module_calls = {}   # in-flight start info
        self.history = []         # completed call records
        self.save_file_path = save_file_path

    def _serialize(self, obj):
        if isinstance(obj, Prediction):
            d = {}
            if hasattr(obj, "code"): d["code"] = obj.code
            if hasattr(obj, "codes"): d["codes"] = self._serialize(obj.codes)
            if hasattr(obj, "reasoning"): d["reasoning"] = obj.reasoning
            if hasattr(obj, "answer"):    d["answer"]    = obj.answer
            return d
        if isinstance(obj, dict):
            return {k: self._serialize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._serialize(v) for v in obj]
        try:
            json.dumps(obj)
            return obj
        except Exception:
            return repr(obj)

    def on_module_start(self, call_id, instance, inputs):
        tid = getattr(instance, "current_task_id", None)
        self._module_calls[call_id] = {
            "instance": instance.__class__.__name__,
            "task_id":  tid,
            "inputs":   self._serialize(inputs),
        }

    def on_module_end(self, call_id, outputs, exception):
        start = self._module_calls.pop(call_id, {})
        record = {
            "id":        call_id,
            "instance":  start.get("instance"),
            "task_id":   start.get("task_id"),
            "inputs":    start.get("inputs"),
            "outputs":   self._serialize(outputs),
            "status":    "FAILED" if exception else "OK",
            "exception": None if exception is None else repr(exception),
        }
        self.history.append(record)
        with open(self.save_file_path, "a") as fw:
            fw.write(json.dumps(record) + "\n")


############################################## HyperParameters ##########################################

TIMEOUT_CONSTANT = 40

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--difficulty", type=str, default="medium", help="difficulty of the problems")
parser.add_argument("--num_threads", type=int, default=1, help="Number of threads to use")
parser.add_argument('--temperature', type=float, default=0.7, help='Temperature for generation')
parser.add_argument('--n', type=int, default=16, help='Number of code generation samples.')
parser.add_argument('--context', type=str, default="all", help="'all' means use all history for self-debug. 'last' means only use latest code for self-debug.")
parser.add_argument('--selection', type=str, default="first", help="How to select the final solution.")
parser.add_argument('--num_round', type=int, default=3, help="How many rounds for generation for self-debug.")
parser.add_argument('--selfdebug_decision', type=str, default="exit", help="What to do when self debug has passed all public tests.")
parser.add_argument('--judge', type=str, default="openai/gpt-4o-mini", help="The model used to judge.")
parser.add_argument('--generator', type=str, default="openai/gpt-4o-mini", help="The model used to generate solution.")
parser.add_argument('--start_date', type=str, default=None, help="Start date for the contest (YYYY-MM-DD).")
parser.add_argument('--end_date', type=str, default=None, help="End date for the contest (YYYY-MM-DD).")
parser.add_argument('--result_json_path', type=str, required=True, help="Json file to store the current result.")
parser.add_argument('--ablation_judge_api_name', type=str, default=None, help="The model used to judge.")
parser.add_argument('--ablation_judge_api_base', type=str, default="openai/gpt-4o-mini", help="The model used to judge.")
parser.add_argument('--method', type=str, default="selfdebug", help="The method used to generate the code.")
parser.add_argument('--test_generator', type=str, default="openai/gpt-4o-mini", help="The model used to judge.")
parser.add_argument('--num_test_suites', type=int, default=1, help="The number of test suites to generate.")
parser.add_argument('--api_name', type=str, default=None, help="Whether to use local served model.")
parser.add_argument('--api_base', type=str, default=None, help="API Base for local served model.")
parser.add_argument('--no_refine', action="store_true", help="Whether to use reflection after one round of generation.")
parser.add_argument('--no_dspy_gen', action="store_true", help="Whether to use dspy for generating response.")
parser.add_argument('--lcb_version', type=str, default="release_v2", help="The version of the livecodebench dataset.")
parser.add_argument('--num_icl_examples', type=int, default=0, help="The number of ICL examples to use.")
parser.add_argument('--enable_llm_reflection_with_tool', action="store_true", help="Whether to use reflection.")
parser.add_argument('--enable_vanilla_reflection', action="store_true", help="Whether to use vanilla reflection.")
parser.add_argument('--ablation_qwq_vanilla_without_reasoning', action="store_true", help="Whether to include reasoning in vanilla self debug.")
parser.add_argument('--ablation_qwq_debug_with_4o_mini', action="store_true", help="Whether to use 4o-mini for debug.")
parser.add_argument('--load_cached_preds', action="store_true", help="Whether to load cached predictions for selection.")
parser.add_argument('--cached_preds_path', type=str, default=None, help="Path to the cached predictions for selection.")
parser.add_argument('--seed', type=int, default=42, help="Random seed for reproducibility.")
parser.add_argument('--resume', action="store_false", help="Whether to resume from cached predictions.")

args = parser.parse_args()
print(args)

if os.path.exists(args.result_json_path):
    with open(args.result_json_path, "r") as f:
        lines = f.readlines()
    if lines and "final_accuracy" in lines[-1]:
        print("This run has been finished previously. Skipped.")
        # sys.exit(0)


# Configure LMs
use_dspy_cache = True
def is_use_dspy_cache(model_name):
    return use_dspy_cache 


if args.api_name:
    lm = dspy.LM(args.api_name, api_base=args.api_base,  timeout=7200, cache=use_dspy_cache, cache_in_memory=False)
    args.generator = args.api_name
else:
    if "o1" in args.generator:
        lm = dspy.LM(args.generator, max_tokens=65536, temperature=1.0, cache=False, cache_in_memory=False)
    else:
        lm = dspy.LM(args.generator, cache=is_use_dspy_cache(args.generator) )
judge_lm = dspy.LM(args.judge, cache=is_use_dspy_cache(args.judge) )
if args.ablation_judge_api_name:
    ablation_judge_lm = dspy.LM(args.ablation_judge_api_name, api_base=args.ablation_judge_api_base,  cache=is_use_dspy_cache(args.ablation_judge_api_name))
else:
    ablation_judge_lm = dspy.LM('openai/gpt-4o-mini', cache=is_use_dspy_cache('openai/gpt-4o-mini') )
if "o1" in args.test_generator:
    test_generator_lm = dspy.LM(args.test_generator, max_tokens=65536, temperature=1.0, cache=True)
else:
    test_generator_lm = dspy.LM(args.test_generator, cache=True)

dspy.settings.configure(lm=lm)
dspy.configure(callbacks=[AgentLoggingCallback(args.result_json_path + ".detail")], trace=[])


lcb_codegen = load_dataset(
    "livecodebench/code_generation_lite",
    version_tag=args.lcb_version,
    split="test",
    trust_remote_code=True
)

def load_json_cached_preds(filename):
    results = {}
    with open(filename, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                def check_empty(variable):
                    return bool(variable and any(variable))
                if 'task_id' in obj and (
                   ('code' in obj and check_empty(obj["code"])) or
                   ('codes' in obj and check_empty(obj["codes"]))
                ):
                    if "passed" not in obj and "completion_and_pass" in obj:
                        obj["passed"] = obj["completion_and_pass"]
                    results[obj['task_id']] = obj
            except json.JSONDecodeError:
                print(f"Error decoding JSON line: {line[:100]}...")
    return results

if args.load_cached_preds:
    cached_preds_dict = load_json_cached_preds(args.cached_preds_path)
else:
    cached_preds_dict = None

def translate_private_test_cases(encoded_data):
    decoded = base64.b64decode(encoded_data)
    decompressed = zlib.decompress(decoded)
    original = pickle.loads(decompressed)
    return json.loads(original)

def update_dataset_in_place(dataset):
    for entry in dataset:
        try:
            entry["private_test_cases"] = translate_private_test_cases(entry["private_test_cases"])
        except Exception as e:
            print(e)

def map_to_dspy_example(row):
    return {
        "prompt": row["question_content"],
        "test": row["private_test_cases"],
        "entry_point": row["starter_code"],
        "canonical_solution": "",
        "task_id": row["question_id"],
        "is_stdin": has_test_type(row["public_test_cases"], "stdin"),
        "public_test_cases": row["public_test_cases"],
    }

def of_difficulty(entry, difficulty):
    tests = json.loads(entry["public_test_cases"])
    return bool(tests) and entry["difficulty"] == difficulty

random.seed(41)
print(f"Before: {len(lcb_codegen)}")
filtered_lcb = [e for e in lcb_codegen if of_difficulty(e, args.difficulty)]
print(f"After filtering difficulty: {len(filtered_lcb)}")

if args.start_date:
    sd = datetime.strptime(args.start_date, "%Y-%m-%d")
    filtered_lcb = [e for e in filtered_lcb if sd <= datetime.fromisoformat(e["contest_date"])]

if args.end_date:
    ed = datetime.strptime(args.end_date, "%Y-%m-%d")
    filtered_lcb = [e for e in filtered_lcb if datetime.fromisoformat(e["contest_date"]) <= ed]

print(f"After filtering date {args.start_date} - {args.end_date}: {len(filtered_lcb)}")

extracted_tests = {e["question_id"]: json.loads(e["public_test_cases"]) for e in filtered_lcb}
update_dataset_in_place(filtered_lcb)
extracted_private_tests = {e["question_id"]: e["private_test_cases"] for e in filtered_lcb}

live_code_bench_dataset = [
    dspy.Example(**map_to_dspy_example(row)).with_inputs(
        "prompt", "test", "entry_point", "canonical_solution", "task_id", "is_stdin", "public_test_cases"
    )
    for row in filtered_lcb
]

cached_preds_dict_resume = {}
if args.resume and os.path.isfile(args.result_json_path):
    cached_preds_dict_resume = load_json_cached_preds(args.result_json_path)

print(f"After resume: {len(filtered_lcb)}")
if not filtered_lcb:
    print("dataset is null")
    sys.exit(0)


def get_accuracy(dataset, num_process_evaluate, method="selfdebug", timeout=6):
    """Take in a dataset or subset of dataset, evaluate accuracy using multiprocessing"""
    total_passed = 0
    lock = None

    with tqdm(total=len(dataset), desc="Progress") as pbar:
        with ProcessPoolExecutor(max_workers=num_process_evaluate) as executor:
            futures = {
                executor.submit(
                    generate_and_evaluate,
                    (example, timeout, method, args.result_json_path, None)
                ): i for i, example in enumerate(dataset)
            }

            results = {}
            for future in as_completed(futures):
                idx = futures[future]
                result = future.result()
                results[idx] = result
                total_passed += int(result["passed"]) if type(result["passed"])!=list else int(all(result["passed"]))
                curr_acc = (total_passed / len(results)) * 100
                pbar.set_postfix({
                    'Accuracy': f'{curr_acc:.2f}%',
                    'Passed': f'{total_passed}/{len(results)}'
                })
                pbar.update(1)

    assert len(results) == len(dataset), f"results = {len(results)} inputs = {len(dataset)}"
    return total_passed / len(dataset)


def get_accuracy_all_rounds(dataset, num_process_evaluate, method="selfdebug", timeout=6):
    """Evaluate accuracy across multiple rounds using multiprocessing."""
    total_passed = [0] * args.num_round
    num_results = [0] * args.num_round

    with tqdm(total=len(dataset), desc="Progress") as pbar:
        with ProcessPoolExecutor(max_workers=num_process_evaluate) as executor:
            futures = {
                executor.submit(
                    generate_and_evaluate,
                    (example, timeout, method, args.result_json_path, None)
                ): i for i, example in enumerate(dataset)
            }

            results = {}
            for future in as_completed(futures):
                idx = futures[future]
                result = future.result()
                results[idx] = result
                for r in range(args.num_round):
                    total_passed[r] += int(result["passed"][r])
                    num_results[r] += 1
                last_acc = (total_passed[-1] / num_results[-1]) * 100 if num_results[-1] else 0
                pbar.set_postfix({
                    'Last Round Accuracy': f'{last_acc:.2f}%',
                    'Passed': f'{sum(total_passed)}/{len(results) * args.num_round}'
                })
                pbar.update(1)

    final_accs = [
        (total_passed[r] / num_results[r]) * 100 if num_results[r] else 0
        for r in range(args.num_round)
    ]
    return final_accs




# from tqdm import tqdm
#
# def get_accuracy(dataset, num_process_evaluate, method="selfdebug", timeout=6):
#     """
#     Take in a dataset or subset of dataset,
#     evaluate accuracy sequentially (no multiprocessing).
#     """
#     total_passed = 0
#     results_count = 0
#
#     with tqdm(total=len(dataset), desc="Progress") as pbar:
#         for example in dataset:
#             # Generate and evaluate for this example
#             result = generate_and_evaluate(
#                 (example,
#                 timeout,
#                 method,
#                 args.result_json_path,
#                 None)
#             )
#
#             # Accumulate results
#             passed = int(result["passed"])
#             total_passed += passed
#             results_count += 1
#
#             # Compute running accuracy
#             current_accuracy = (total_passed / results_count) * 100
#
#             # Update progress bar
#             pbar.set_postfix({
#                 'Accuracy': f'{current_accuracy:.2f}%',
#                 'Passed':   f'{total_passed}/{results_count}'
#             })
#             pbar.update(1)
#
#     # Sanity check
#     assert results_count == len(dataset), (
#         f"results = {results_count} inputs = {len(dataset)}"
#     )
#
#     # Final accuracy as a fraction
#     final_accuracy = total_passed / len(dataset)
#     return final_accuracy

# from tqdm import tqdm
#
# def get_accuracy_all_rounds(dataset, method="selfdebug", timeout=6):
#     """
#     Evaluate accuracy across multiple rounds by processing each example sequentially.
#     """
#     # Initialize counters for each round
#     total_passed = [0] * args.num_round
#     num_results_per_round = [0] * args.num_round
#
#     with tqdm(total=len(dataset), desc="Progress") as pbar:
#         for example in dataset:
#             # Generate and evaluate for this example
#             result = generate_and_evaluate(
#                 (example, timeout, method, args.result_json_path,None)
#                 )
#
#             # Accumulate results per round
#             for r in range(args.num_round):
#                 total_passed[r] += int(result["passed"][r])
#                 num_results_per_round[r] += 1
#
#             # Update progress bar with latest-round accuracy and overall passed count
#             last_acc = (total_passed[-1] / num_results_per_round[-1]) * 100 if num_results_per_round[-1] > 0 else 0
#             passed_sum = sum(total_passed)
#             total_checks = len(dataset) * args.num_round
#             pbar.set_postfix({
#                 'Last Round Acc': f'{last_acc:.2f}%',
#                 'Passed/Total': f'{passed_sum}/{total_checks}'
#             })
#             pbar.update(1)
#
#     # Compute final accuracy for each round
#     final_accuracy = [
#         (total_passed[r] / num_results_per_round[r]) * 100 if num_results_per_round[r] > 0 else 0
#         for r in range(args.num_round)
#     ]
#
#     return final_accuracy




def generate_and_evaluate(arguments):
    example, timeout, method, result_json_path, lock = arguments
    is_stdin = example.is_stdin
    task_id = example.task_id

    if task_id in cached_preds_dict_resume:
        return cached_preds_dict_resume[task_id]

    tests = None
    if "generated_tests" in args.selection or args.selfdebug_decision == "refine":
        retry = 1 if "o1" in args.test_generator else 3
        generation_fun = partial(generate_tests_repeat, temperature_base=1.0 if "o1" in args.test_generator else 0.7)
        with dspy.context(lm=test_generator_lm):
            tests = generate_tests_for_one_example(
                example, generation_fun=generation_fun,
                num_test_suites=args.num_test_suites, retry=retry,
                o1=("o1" in args.test_generator)
            )

    if method == "selfdebug":
        debug_lm = dspy.LM(
            'openai/gpt-4o-mini', api_key="sk-XXXXX_XXXXX",
            cache=True
        )
        test_program = CodeGeneratorWithSelfDebug(
            extracted_tests, num_round=args.num_round, n=args.n,
            temperature=args.temperature, lm=lm, selection=args.selection,
            context=args.context, judge_lm=judge_lm,
            pre_computed_tests=tests, selfdebug_decision=args.selfdebug_decision,
            ablation_judge_lm=ablation_judge_lm, debug_lm=debug_lm,
            num_icl_examples=args.num_icl_examples, args=args,
            enable_llm_reflection_with_tool=args.enable_llm_reflection_with_tool,
            enable_vanilla_reflection=args.enable_vanilla_reflection,
            ablation_qwq_vanilla_without_reasoning=args.ablation_qwq_vanilla_without_reasoning,
            ablation_qwq_debug_with_4o_mini=args.ablation_qwq_debug_with_4o_mini,
            cached_preds_dict=cached_preds_dict
        )
    elif "naive" in method:
        if method == "naive":
            test_program = NaiveCodeGenerator(cot=False)
        elif method == "naive_cot":
            test_program = NaiveCodeGenerator(cot=True)
        elif method == "naive_nodspy":
            test_program = NaiveCodeGeneratorNoDSPy(args)

    test_program.set_task_id(task_id)
    is_extracted = not is_stdin

    if method == "selfdebug":
        (pred, reflections), _ = test_program(example, None, task_id, None, None, is_stdin)
    elif "naive" in method:
        pred = test_program(example["prompt"], is_stdin)

    # Evaluate
    if args.selection == "oracle":
        res = check_correctness_oracle(example, pred, timeout,
                                       is_extracted=is_extracted,
                                       debug_mode=True, fast_check=True)
        result_json = {
            'task_id': task_id,
            'codes': res["codes"],
            'passed': res["completion_and_pass"],
            'raw_code': res["raw_codes"],
        }
    elif args.selection == "oracle_all_rounds":
        result_json = {
            'task_id': task_id,
            'codes': [[] for _ in range(args.num_round)],
            'passed': [0] * args.num_round,
            'raw_code': [[] for _ in range(args.num_round)],
        }
        for r in range(args.num_round):
            rd = check_correctness_oracle(
                example, pred[r], timeout,
                is_extracted=is_extracted,
                debug_mode=True, fast_check=True
            )
            result_json["codes"][r] = rd["codes"]
            result_json["passed"][r] = rd["passed"]
            result_json["raw_code"][r] = rd["raw_codes"]
    else:
        rd = check_correctness(
            example, post_process_code(pred.code), timeout,
            is_extracted=is_extracted, fast_check=True
        )
        result_json = {
            'task_id': task_id,
            'code': rd["code"],
            'passed': rd["passed"],
            'raw_code': pred.code,
        }

    # Append to JSON log
    try:
        with lock if lock is not None else nullcontext():
            with open(result_json_path, 'a') as f:
                f.write(json.dumps(result_json) + '\n')
    except FileNotFoundError:
        with open(result_json_path, 'a') as f:
            f.write(json.dumps(result_json) + '\n')

    return result_json


def namespace_to_serializable_dict(namespace):
    def default_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    return json.dumps(vars(namespace), default=default_serializer)


if __name__ == "__main__":
    open(args.result_json_path, 'a').close()
    with open(args.result_json_path, "a") as f:
        f.write(namespace_to_serializable_dict(args) + '\n')
    random.seed(args.seed)

    if args.selection != "oracle_all_rounds":
        accuracy = get_accuracy(live_code_bench_dataset, num_process_evaluate=args.num_threads, method=args.method, timeout=TIMEOUT_CONSTANT)
        print(f"Accuracy: {accuracy*100:.2f}%")
        with open(args.result_json_path, "a") as f:
            f.write(json.dumps({"final_accuracy": f"{accuracy*100:.2f}%"}) + '\n')
    else:
        accuracies = get_accuracy_all_rounds(live_code_bench_dataset, num_process_evaluate=args.num_threads, method=args.method, timeout=TIMEOUT_CONSTANT)
        print(f"Accuracy by round: {accuracies}")
        with open(args.result_json_path, "a") as f:
            f.write(json.dumps({"final_accuracy_list": accuracies}) + '\n')
