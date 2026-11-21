"""Rebuild models/ai-image-detector-int8.onnx from the Hugging Face checkpoint.

Only needed if you want to regenerate the weights. Requires the heavy deps:
    pip install torch transformers onnx onnxscript onnxruntime
Then split it into 20 MB parts and upload them to a GitHub release, e.g.
    split -b 20000000 -d -a 2 models/ai-image-detector-int8.onnx ai-image-detector-int8.onnx.part
    gh release upload detector-v1 ai-image-detector-int8.onnx.part*
and update MODEL_PARTS / MODEL_SHA256 in api/index.py.
"""
import os

import torch
from onnxruntime.quantization import QuantType, quantize_dynamic
from transformers import AutoModelForImageClassification

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
os.makedirs(OUT, exist_ok=True)
fp32 = os.path.join(OUT, "ai-image-detector-fp32.onnx")

model = AutoModelForImageClassification.from_pretrained("haywoodsloan/ai-image-detector-deploy").eval()


class Logits(torch.nn.Module):
    def __init__(self, m):
        super().__init__()
        self.m = m

    def forward(self, x):
        return self.m(pixel_values=x).logits


torch.onnx.export(Logits(model), (torch.randn(1, 3, 256, 256),), fp32,
                  input_names=["pixel_values"], output_names=["logits"],
                  opset_version=17, dynamo=False)
quantize_dynamic(fp32, os.path.join(OUT, "ai-image-detector-int8.onnx"), weight_type=QuantType.QInt8)
os.remove(fp32)
print("wrote", os.path.join(OUT, "ai-image-detector-int8.onnx"))
