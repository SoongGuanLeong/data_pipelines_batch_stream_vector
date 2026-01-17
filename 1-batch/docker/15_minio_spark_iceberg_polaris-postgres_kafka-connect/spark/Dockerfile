FROM apache/spark:4.0.1-scala2.13-java21-python3-r-ubuntu

USER root

# ---------------------------
# 1️⃣ Set up Spark home & Jupyter user
# ---------------------------
RUN mkdir -p /home/spark /home/iceberg/warehouse /home/iceberg/notebooks /opt/spark/conf && \
    chown -R spark:spark /home/spark /home/iceberg/warehouse /home/iceberg/notebooks /opt/spark/conf

ENV HOME=/home/spark
ENV SPARK_HOME=/opt/spark
ENV SPARK_CONF_DIR=/opt/spark/conf
ENV JUPYTER_RUNTIME_DIR=/home/spark/.local/share/jupyter/runtime
ENV JUPYTER_CONFIG_DIR=/home/spark/.jupyter
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3
ENV PATH=$PATH:$SPARK_HOME/bin

WORKDIR /home/spark

# ---------------------------
# 2️⃣ Install Python tools & Jupyter
# ---------------------------
RUN apt-get update && \
    apt-get install -y python3-pip wget libsnappy-dev zlib1g-dev && \
    pip3 install --no-cache-dir notebook findspark pyspark==4.0.1

COPY target/jars/* /opt/spark/jars/

# ---------------------------
# 6️⃣ Switch to spark user
# ---------------------------
USER spark

# Expose Jupyter port
EXPOSE 8888

# Default command: start Jupyter Notebook
CMD ["jupyter", "notebook", "--notebook-dir=/home/iceberg/notebooks", "--ip=0.0.0.0", "--port=8888", "--no-browser"]