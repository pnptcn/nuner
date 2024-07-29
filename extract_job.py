import json
import logging

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

logger = logging.getLogger(__name__)

model = AutoModelForCausalLM.from_pretrained(
    "numind/NuExtract", trust_remote_code=True, torch_dtype=torch.bfloat16
)

tokenizer = AutoTokenizer.from_pretrained("numind/NuExtract", trust_remote_code=True)

model.eval()


class Job:
    def __init__(self, profile):
        self.profile = profile

    def predict_NuExtract(self, model, tokenizer, text, schema, example=["", "", ""]):
        schema = json.dumps(json.loads(schema), indent=4)
        input_llm = "<|input|>\n### Template:\n" + schema + "\n"
        for i in example:
            if i != "":
                input_llm += (
                    "### Example:\n" + json.dumps(json.loads(i), indent=4) + "\n"
                )

        input_llm += "### Text:\n" + text + "\n<|output|>\n"
        input_ids = tokenizer(
            input_llm, return_tensors="pt", truncation=True, max_length=4000
        ).to("cuda")

        output = tokenizer.decode(
            model.generate(**input_ids)[0], skip_special_tokens=True
        )
        return output.split("<|output|>")[1].split("<|end-output|>")[0]

    def do(self):
        schema = """{
            "nodes": [{
                "id": "",
                "name": "",
                "type": "",
                "status": "",
                "description": "",
                "history": [{
                    "timestamp": "",
                    "status": "",
                    "description": ""
                }],
                "tags": [],
                "urls": []
            }],
            "edges": [{
                "id": "",
                "source": "",
                "target": "",
                "label": "",
                "status": ""
            }]
        }"""

        page = self.profile.get("page")
        if not page:
            logger.error("Invalid profile data: missing page.")
            return

        content = page.get("content")
        if not content:
            logger.error("Invalid profile data: missing content.")
            return

        chunks = content.get("chunks")
        if not chunks:
            logger.error("Invalid profile data: missing chunks.")
            return

        for chunk in chunks:
            prediction = self.predict_NuExtract(
                model, tokenizer, chunk, schema, example=["", "", ""]
            )
            print(prediction)
