FROM nvcr.io/nvidia/pytorch:25.11-py3

# Set CUDA environment variables
ENV CUDA_HOME=/usr/local/cuda-13.0
ENV CUDA_PATH=$CUDA_HOME
ENV PATH=$CUDA_HOME/bin:$PATH
ENV LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
ENV C_INCLUDE_PATH=/usr/local/include
ENV CPLUS_INCLUDE_PATH=/usr/local/include
ENV C_INCLUDE_PATH=$CUDA_HOME/include:$C_INCLUDE_PATH
ENV CPLUS_INCLUDE_PATH=$CUDA_HOME/include:$CPLUS_INCLUDE_PATH

# Install triton from source for latest blackwell support
RUN git clone https://github.com/triton-lang/triton.git && \
    cd triton && \
    git checkout c5d671f91d90f40900027382f98b17a3e04045f6 && \
    pip install -r python/requirements.txt && \
    pip install . && \
    cd ..

# Install xformers from source for blackwell support
RUN git clone -b v0.0.33 --depth=1 https://github.com/facebookresearch/xformers --recursive && \
    cd xformers && \
    export TORCH_CUDA_ARCH_LIST="12.1" && \
    python setup.py install && \
    cd ..

# Install unsloth and other dependencies
RUN pip install --no-deps bitsandbytes==0.48.0 transformers==4.56.2 trl==0.22.2
#RUN pip install unsloth unsloth_zoo

# Clone the actual Unsloth repository
RUN git clone https://github.com/unslothai/unsloth /opt/unsloth

# This is the step that actually "sets up" the studio
WORKDIR /opt/unsloth
RUN ./install.sh --local

# Ensure that 'unsloth studio' is accessible
ENV PATH="/opt/unsloth:${PATH}"

# Set your working directory back to /workspace
WORKDIR /workspace
#Put Unsloth into the ENV PATH
ENV PATH="/root/.unsloth/studio/unsloth_studio/bin:${PATH}"

# Start the container
CMD ["/bin/bash", "-c", "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root & unsloth studio --host 0.0.0.0 --port 8000"]
