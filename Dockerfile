# Use an official Anaconda runtime as a parent image
FROM continuumio/miniconda3

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Run any commands you need to set up your environment
# RUN conda update conda -y

RUN apt-get update && apt-get install -y gcc python3-dev 
RUN conda env create -f environment.yaml
SHELL ["conda", "run", "-n", "apple_info_env", "/bin/bash", "-c"]

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME RAG_API

CMD ["conda", "run", "--no-capture-output", "-n", "apple_info_env", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
