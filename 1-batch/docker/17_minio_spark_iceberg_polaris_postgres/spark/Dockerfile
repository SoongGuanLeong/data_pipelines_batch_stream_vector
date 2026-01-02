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
    pip3 install --no-cache-dir notebook findspark pyspark==4.0.1 boto3

# ---------------------------
# 3️⃣ Add required jars
# ---------------------------
RUN wget -P /opt/spark/jars https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-4.0_2.13/1.10.1/iceberg-spark-runtime-4.0_2.13-1.10.1.jar && \
    # Hadoop AWS
    wget -P /opt/spark/jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.4.1/hadoop-aws-3.4.1.jar && \
    # AWS SDK bundle
    wget -P /opt/spark/jars https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.24.6/bundle-2.24.6.jar && \
    wget -P /opt/spark/jars https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-slf4j-impl/2.20.0/log4j-slf4j-impl-2.20.0.jar

# ---------------------------
# 6️⃣ Switch to spark user
# ---------------------------
USER spark

# Expose Jupyter port
EXPOSE 8888

# Default command: start jupyter notebook
CMD ["jupyter", "notebook", "--notebook-dir=/home/iceberg/notebooks", "--ip=0.0.0.0", "--port=8888", "--no-browser"]