FROM apache/spark:4.0.1-scala2.13-java21-python3-r-ubuntu

# Install pip and Jupyter
RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install --no-cache-dir notebook findspark pyspark

# Expose Jupyter port
EXPOSE 8888

# Default command can be overridden by docker-compose
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]