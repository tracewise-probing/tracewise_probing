import json
import os
from abc import ABC, abstractmethod
from typing import List
from warnings import warn

import openai

import signal
import time
import random

import openai
from openai.types.chat import ChatCompletion


def make_request(
    client: openai.Client,
    message: str,
    model: str,
    max_tokens: int = 512,
    temperature: float = 1,
    n: int = 1,
    **kwargs
) -> ChatCompletion:
    if type(message) == str :
        system_msg = "You are a helpful assistant good at coding."
        if (
            kwargs.get("response_format", None)
            and kwargs["response_format"]["type"] == "json_object"
        ):
            system_msg = "You are a helpful assistant designed to output JSON."
        messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": message},
            ]
    else:
        messages = message

    return client.chat.completions.create(
        model=model,
        messages = messages , 
        max_tokens=max_tokens,
        temperature=temperature,
        n=n,
        **kwargs
    )


def handler(signum, frame):
    # swallow signum and frame
    raise Exception("end of time")


TIMEOUT=600 

def make_auto_request(*args, **kwargs) -> ChatCompletion:
    ret = None
    while ret is None:
        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm( TIMEOUT )
            ret = make_request(*args, **kwargs)
            signal.alarm(0)
        except openai.RateLimitError:
            print("Rate limit exceeded. Waiting...")
            signal.alarm(0)
            time.sleep(5)
        except openai.APIConnectionError:
            print("API connection error. Waiting...")
            signal.alarm(0)
            time.sleep(5)
        except openai.APIError as e:
            print(e)
            signal.alarm(0)
        except Exception as e:
            print("Unknown error. Waiting...")
            print(e)
            signal.alarm(0)
            time.sleep(1)
    return ret

EOS = [
    "<|endoftext|>",
    "<|endofmask|>",
    "</s>",
    "\nif __name__",
    "\ndef main(",
    "\nprint(",
]


def extra_eos_for_direct_completion(dataset) -> List[str]:
    if dataset.lower() == "humaneval":
        return ["\ndef ", "\nclass ", "\nimport ", "\nfrom ", "\nassert "]
    elif dataset.lower() == "mbpp":
        return ['\n"""', "\nassert"]
    raise ValueError(f"Unknown dataset: {dataset}")


# some random words which serves as the splitter
_MAGIC_SPLITTER_ = "-[[]]-this-is-really-our-highest-priority-[[]]-"


def make_chat_prompt(
    task_prompt: str,
    instruction_prefix: str,
    response_prefix: str,
    tokenizer: None,# AutoTokenizer,
) -> str:
    # directly return prompt if it does not have a tokenizer.chat_template
    if tokenizer.chat_template is None:
        return task_prompt

    assert instruction_prefix is not None, "Instruction prefix is required!"
    assert response_prefix is not None, "Response prefix is required!"

    task_prompt = f"""\
{instruction_prefix}
```
{task_prompt.strip()}
```
"""
    response = f"""\
{response_prefix}
```python
{_MAGIC_SPLITTER_}
```
"""
    task_prompt = tokenizer.apply_chat_template(
        [
            {"role": "user", "content": task_prompt},
            {"role": "assistant", "content": response},
        ],
        tokenize=False,
    ).split(_MAGIC_SPLITTER_)[0]
    return task_prompt


class DecoderBase(ABC):
    def __init__(
        self,
        name: str,
        batch_size: int = 1,
        temperature: float = 0.8,
        max_new_tokens: int = 2048*2,
        dtype: str = "bfloat16",  # default
        trust_remote_code: bool = False,
        instruction_prefix: str = None,
        response_prefix: str = None,
    ) -> None:
        print("Initializing a decoder model: {} ...".format(name))
        self.name = name
        self.batch_size = batch_size
        self.temperature = temperature
        self.eos = EOS
        self.skip_special_tokens = False
        self.max_new_tokens = max_new_tokens
        self.dtype = dtype
        self.trust_remote_code = trust_remote_code
        self.instruction_prefix = instruction_prefix
        self.response_prefix = response_prefix

    @abstractmethod
    def codegen(
        self, prompt: str, do_sample: bool = True, num_samples: int = 200
    ) -> List[str]:
        pass

    @abstractmethod
    def is_direct_completion(self) -> bool:
        pass

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name






class OpenAIChatDecoder(DecoderBase):
    def __init__(self, name: str, base_url=None, **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.client = openai.OpenAI(base_url=base_url,timeout= TIMEOUT )
        self.base_url = base_url 

    def codegen(
        self, prompt: str, do_sample: bool = True, num_samples: int = 200
    ) -> List[str]:
        if do_sample:
            assert self.temperature > 0, "Temperature must be positive for sampling"
        batch_size = min(self.batch_size, num_samples)

        if type( prompt) ==str :
            message = self.instruction_prefix
            message += f"\n\n{prompt.strip()}\n"
        else:
            message = prompt 
            assert type( prompt) == list , (prompt )
        

        fmt = "json_object" if self.name == "gpt-4-1106-preview" else "text"
        if fmt == "json_object":
            message += (
                r'Note: the output code should follow a JSON schema of {"code": ""}'
            )
        add_kwargs={}#{"stop":"[/ANSWER]","seed":random.randint(0,1000)}
        #print ("batch_size", batch_size )
        #if "llama" in self.name.lower() :
        #    add_kwargs={"request_timeout":60} 
        name_x = self.name 
        if "bitdeer.ai" in self.base_url and name_x=="llama3.1" :
            #name_x = "llama3.1:8b-instruct-q4_0"
            name_x = "meta/llama-3.1-8b-instruct"#llama3.1:8b-instruct-q4_0"
        if "nvidia.com" in self.base_url and name_x=="meta-llama-3.1-70b-instruct" :
            name_x = "meta/llama-3.1-70b-instruct"
        elif "nvidia.com" in self.base_url and name_x=="meta-llama-3.3-70b-instruct" :
            name_x = "meta/llama-3.3-70b-instruct"


        ret = make_auto_request(
            self.client,
            message=message,
            model=name_x,
            max_tokens=self.max_new_tokens,
            temperature=self.temperature,
            n=batch_size,
            response_format={"type": fmt} if "gpt-"  in name_x else None ,
            **add_kwargs,
        )

        outputs = []
        assert type(ret) != str , (message,  "prompt<---", ret ,type(ret)  )
        for item in ret.choices:
            content = item.message.content
            # if json serializable
            if fmt == "json_object":
                try:
                    json_data = json.loads(content)
                    if json_data.get("code", None) is not None:
                        outputs.append(prompt + "\n" + json_data["code"])
                        continue

                    print(f"'code' field not found in: {json_data}")
                except Exception as e:
                    print(e,message)
            outputs.append(content)

        return outputs

    def is_direct_completion(self) -> bool:
        return False



def make_model(
    model: str,
    backend: str,
    dataset: str,
    batch_size: int = 1,
    temperature: float = 0.0,
    tp=1,
    base_url=None,
    instruction_prefix=None,
    response_prefix=None,
):
    if backend == "vllm":
        return GeneralVllmDecoder(
            name=model,
            batch_size=batch_size,
            temperature=temperature,
            dataset=dataset,
            tp=tp,
            instruction_prefix=instruction_prefix,
            response_prefix=response_prefix,
        )
    elif backend == "hf":
        return GenenralHfTorchDecoder(
            name=model,
            batch_size=batch_size,
            temperature=temperature,
            dataset=dataset,
            instruction_prefix=instruction_prefix,
            response_prefix=response_prefix,
        )
    elif backend == "openai":
        return OpenAIChatDecoder(
            name=model,
            batch_size=batch_size,
            temperature=temperature,
            base_url=base_url,
            instruction_prefix=instruction_prefix,
            response_prefix=response_prefix,
        )
    elif backend == "mistral":
        return MistralChatDecoder(
            name=model,
            batch_size=batch_size,
            temperature=temperature,
            instruction_prefix=instruction_prefix,
            response_prefix=response_prefix,
        )
    elif backend == "anthropic":
        return AnthropicMessageDecoder(
            name=model,
            batch_size=batch_size,
            temperature=temperature,
            instruction_prefix=instruction_prefix,
            response_prefix=response_prefix,
        )
