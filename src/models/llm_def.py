"""
Surpported Models.
Supports:
- Open Source:LLaMA3, Qwen2.5, MiniCPM3, ChatGLM4
- Closed Source: ChatGPT, DeepSeek
"""

from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, AutoConfig, GenerationConfig
import torch
import openai
import os
from openai import OpenAI

# The inferencing code is taken from the official documentation

class BaseEngine:
    def __init__(self, model_name_or_path: str):
        self.name = None
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)
        self.temperature = 0.2
        self.top_p = 0.9
        self.max_tokens = 1024
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def get_chat_response(self, prompt):
        raise NotImplementedError

    def set_hyperparameter(self, temperature: float = 0.2, top_p: float = 0.9, max_tokens: int = 1024):
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens

class LLaMA(BaseEngine):
    def __init__(self, model_name_or_path: str):
        super().__init__(model_name_or_path)
        self.name = "LLaMA"
        self.model_id = model_name_or_path
        self.pipeline = pipeline(
            "text-generation",
            model=self.model_id,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto",
        )
        self.terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

    def get_chat_response(self, prompt):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
        outputs = self.pipeline(
            messages,
            max_new_tokens=self.max_tokens,
            eos_token_id=self.terminators,
            do_sample=True,
            temperature=self.temperature,
            top_p=self.top_p,
        )
        return outputs[0]["generated_text"][-1]['content'].strip()

class Qwen(BaseEngine):
    def __init__(self, model_name_or_path: str):
        super().__init__(model_name_or_path)
        self.name = "Qwen"
        self.model_id = model_name_or_path
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype="auto",
            device_map="auto"
        )

    def get_chat_response(self, prompt):
        messages = [
            {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
        generated_ids = self.model.generate(
            **model_inputs,
            temperature=self.temperature,
            top_p=self.top_p,
            max_new_tokens=self.max_tokens
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

        return response

class MiniCPM(BaseEngine):
    def __init__(self, model_name_or_path: str):
        super().__init__(model_name_or_path)
        self.name = "MiniCPM"
        self.model_id = model_name_or_path
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )

    def get_chat_response(self, prompt):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        model_inputs = self.tokenizer.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True).to(self.device)
        model_outputs = self.model.generate(
            model_inputs,
            temperature=self.temperature,
            top_p=self.top_p,
            max_new_tokens=self.max_tokens
        )
        output_token_ids = [
            model_outputs[i][len(model_inputs[i]):] for i in range(len(model_inputs))
        ]
        response = self.tokenizer.batch_decode(output_token_ids, skip_special_tokens=True)[0].strip()

        return response

class ChatGLM(BaseEngine):
    def __init__(self, model_name_or_path: str):
        super().__init__(model_name_or_path)
        self.name = "ChatGLM"
        self.model_id = model_name_or_path
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            low_cpu_mem_usage=True,
            trust_remote_code=True
        )

    def get_chat_response(self, prompt):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        model_inputs = self.tokenizer.apply_chat_template(messages, return_tensors="pt", return_dict=True, add_generation_prompt=True, tokenize=True).to(self.device)
        model_outputs = self.model.generate(
            **model_inputs,
            temperature=self.temperature,
            top_p=self.top_p,
            max_new_tokens=self.max_tokens
        )
        model_outputs = model_outputs[:, model_inputs['input_ids'].shape[1]:]
        response = self.tokenizer.batch_decode(model_outputs, skip_special_tokens=True)[0].strip()

        return response

class OneKE(BaseEngine):
    def __init__(self, model_name_or_path: str):
        super().__init__(model_name_or_path)
        self.name = "OneKE"
        self.model_id = model_name_or_path
        config = AutoConfig.from_pretrained(self.model_id, trust_remote_code=True)
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            llm_int8_threshold=6.0,
            llm_int8_has_fp16_weight=False,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            config=config,
            device_map="auto",
            quantization_config=quantization_config,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )

    def get_chat_response(self, prompt):
        system_prompt = '<<SYS>>\nYou are a helpful assistant. 你是一个乐于助人的助手。\n<</SYS>>\n\n'
        sintruct = '[INST] ' + system_prompt + prompt + '[/INST]'
        input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
        input_ids = self.tokenizer.encode(sintruct, return_tensors="pt").to(self.device)
        input_length = input_ids.size(1)
        generation_output = self.model.generate(input_ids=input_ids, generation_config=GenerationConfig(max_length=1024, max_new_tokens=512, return_dict_in_generate=True,pad_token_id=self.tokenizer.pad_token_id,eos_token_id=self.tokenizer.eos_token_id))
        generation_output = generation_output.sequences[0]
        generation_output = generation_output[input_length:]
        response = self.tokenizer.decode(generation_output, skip_special_tokens=True)

        return response

class ChatGPT(BaseEngine):
    def __init__(self, model_name_or_path: str, api_key: str, base_url=openai.base_url):
        self.name = "ChatGPT"
        self.model = model_name_or_path
        self.base_url = base_url
        self.temperature = 0.2
        self.top_p = 0.9
        self.max_tokens = 4096 # Close source model
        if api_key != "":
            self.api_key = api_key
        else:
            self.api_key = os.environ["OPENAI_API_KEY"]
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def get_chat_response(self, input):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": input},
            ],
            stream=False,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stop=None
        )
        return response.choices[0].message.content

class DeepSeek(BaseEngine):
    def __init__(self, model_name_or_path: str, api_key: str, base_url="https://api.deepseek.com"):
        self.name = "DeepSeek"
        self.model = model_name_or_path
        self.base_url = base_url
        self.temperature = 0.2
        self.top_p = 0.9
        self.max_tokens = 4096 # Close source model
        if api_key != "":
            self.api_key = api_key
        else:
            self.api_key = os.environ["DEEPSEEK_API_KEY"]
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def get_chat_response(self, input):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": input},
            ],
            stream=False,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stop=None
        )
        return response.choices[0].message.content

class LocalServer(BaseEngine):
    def __init__(self, model_name_or_path: str, base_url="http://localhost:8000/v1"):
        self.name = model_name_or_path.split('/')[-1]
        self.model = model_name_or_path
        self.base_url = base_url
        self.temperature = 0.2
        self.top_p = 0.9
        self.max_tokens = 1024
        self.api_key = "EMPTY_API_KEY"
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def get_chat_response(self, input):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": input},
                ],
                stream=False,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stop=None
            )
            return response.choices[0].message.content
        except ConnectionError:
            print("Error: Unable to connect to the server. Please check if the vllm service is running and the port is 8080.")
        except Exception as e:
            print(f"Error: {e}")
