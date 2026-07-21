ARG BASE_IMAGE=nvcr.io/nvidia/pytorch:26.03-py3
FROM ${BASE_IMAGE}

RUN apt-get update && apt-get install -y git wget && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
RUN git clone https://github.com/comfyanonymous/ComfyUI.git

#RUN apt-get install -y \
#    libx11-dev \
#    libgl1-mesa-dev \
#    libglu1-mesa-dev \
#    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/ComfyUI

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# FlashAttention + xFormers (Blackwell‑friendly)
RUN pip install flash-attn --no-build-isolation || true
RUN pip install xformers || true

#Additional Customisation for Add-ons

COPY custom_nodes /workspace/ComfyUI/custom_nodes

#https://github.com/chibiace/ComfyUI-Chibi-Nodes

#https://github.com/Comfy-Org/ComfyUI-Manager
WORKDIR /workspace/ComfyUI/custom_nodes/comfyui-manager
RUN pip install -r requirements.txt

#https://github.com/yolain/ComfyUI-Easy-Use
WORKDIR /workspace/ComfyUI/custom_nodes/ComfyUI-Easy-Use
RUN chmod +x install.sh && ./install.sh || true

#https://github.com/city96/ComfyUI-GGUF
WORKDIR /workspace/ComfyUI/custom_nodes/ComfyUI-GGUF
RUN pip install -r requirements.txt

#https://github.com/r-vage/ComfyUI_Eclipse
WORKDIR /workspace/ComfyUI/custom_nodes/ComfyUI_Eclipse
RUN pip install -r requirements.txt

#https://github.com/chflame163/ComfyUI_LayerStyle
WORKDIR /workspace/ComfyUI/custom_nodes/comfyui_layerstyle
RUN chmod +x install.sh && ./install.sh || true

#https://github.com/MushroomFleet/ComfyUI-FLUX2-JSON
WORKDIR /workspace/ComfyUI/custom_nodes/comfyui-flux2
RUN pip install -r requirements.txt

#https://github.com/rgthree/rgthree-comfy
WORKDIR /workspace/ComfyUI/custom_nodes/rgthree-comfy
RUN pip install -r requirements.txt

#https://github.com/ltdrdata/ComfyUI-Impact-Pack
WORKDIR /workspace/ComfyUI/custom_nodes/comfyui-impact-pack
RUN pip install -r requirements.txt

#https://github.com/aistudynow/ComfyUI-QwenVL
WORKDIR /workspace/ComfyUI/custom_nodes/ComfyUI-QwenVL
RUN pip install -r requirements.txt

#WORKDIR /workspace/ComfyUI/custom_nodes/DJZ-Nodes
#RUN pip install -r requirements.txt

WORKDIR /workspace/ComfyUI

#Set the security level to allow node installs
RUN apk add --no-cache jq || apt-get update && apt-get install -y jq
RUN mkdir -p /workspace/ComfyUI/user/default && \
    echo '{"security_level": "strict"}' > /workspace/ComfyUI/user/default/security.json

RUN jq '.security_level = "weak"' \
    /workspace/ComfyUI/user/default/security.json \
    > /workspace/ComfyUI/user/default/security.json.tmp && \
    mv /workspace/ComfyUI/user/default/security.json.tmp \
       /workspace/ComfyUI/user/default/security.json


# Prefer BF16 on Blackwell
ENV TORCH_DTYPE=bf16
# ComfyUI Security Level Weak allows third-party nodes installation
ENV COMFYUI_SECURITY_LEVEL=weak

EXPOSE 8188

CMD ["python3", "main.py", "--listen", "0.0.0.0", "--port", "8188"]
