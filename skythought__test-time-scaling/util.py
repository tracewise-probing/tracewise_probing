import os, json
import re

def post_process_code(code):

    def extract_code(completion: str, language: str = "python") -> str:
        """
        Extracts the last fenced code block of the given language,
        optionally wrapped in <code>…</code> tags, from a completion string.
        """
        pattern = re.compile(
            rf"<code>\s*```{language}?\n(.*?)```.*?</code>|```{language}\n(.*?)```",
            re.DOTALL
        )
        matches = pattern.findall(completion)
        if not matches:
            fence = r"```[^\n]*\n"
            pattern = re.compile(
        rf"(?:<code>\s*)?{fence}(.*?)(?:(?:```|\s*</code>)|$)",

                            re.DOTALL
                        )
            matches = pattern.findall(completion)
            if not matches :
                return completion
        # each findall returns a tuple of the two capture groups; pick the non‐empty one
        last = matches[-1]
        code = last[0] or last[1]
        return code.strip()
    code = extract_code( code )
    return code


name_map = {
        "4o-mini": 'openai/gpt-4o-mini',
        "4o": 'openai/gpt-4o',
        "o1-mini": 'openai/o1-mini',
        "o1": 'openai/o1-preview',
        "o3-mini": 'openai/o3-mini',
        "o1-preview": 'openai/o1-preview',
        "qwen7b": 'Qwen/Qwen2.5-Coder-7B-Instruct',
        "qwen32b": 'Qwen/Qwen2.5-Coder-32B-Instruct',
        "hqwen1b5": 'hosted_vllm/Qwen/Qwen2.5-1.5B-Instruct',
        "qwen1b5": 'Qwen/Qwen2.5-1.5B-Instruct',
        "qwen1b5": 'Qwen/Qwen2.5-1.5B-Instruct',
        "deepseek-chat":"deepseek-chat",
}

if os.path.exists("v4_only_medium_correct_codes.json"):
    ICL_EXAMPLES = json.load(open("v4_only_medium_correct_codes.json", "r"))
else:
    print("No ICL examples available")
    ICL_EXAMPLES = {}