FROM apache/spark:4.0.1-scala2.13-java21-python3-r-ubuntu

USER root

# ---------------------------
# 1️⃣ Set up Spark home & Jupyter user
# ---------------------------
RUN mkdir -p /home/spark /home/iceberg/warehouse /home/iceberg/notebooks && \
    chown -R spark:spark /home/spark /home/iceberg/warehouse

ENV HOME=/home/spark
WORKDIR /home/spark

# ---------------------------
# 2️⃣ Install Python tools & Jupyter
# ---------------------------
RUN apt-get update && \
    apt-get install -y python3-pip wget libsnappy-dev zlib1g-dev && \
    pip3 install --no-cache-dir notebook findspark pyspark==4.0.1

# ---------------------------
# 3️⃣ Add required jars
# ---------------------------
RUN mkdir -p /opt/spark/jars && \
    # Iceberg runtime
    wget -P /opt/spark/jars https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-4.0_2.13/1.10.1/iceberg-spark-runtime-4.0_2.13-1.10.1.jar && \
    # Hadoop AWS
    wget -P /opt/spark/jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.4.1/hadoop-aws-3.4.1.jar && \
    # AWS SDK bundle
    wget -P /opt/spark/jars https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.24.6/bundle-2.24.6.jar

# ---------------------------
# 4️⃣ Remove conflicting SLF4J jars from base image
# ---------------------------
RUN rm -f /opt/spark/jars/slf4j-nop-*.jar /opt/spark/jars/slf4j-log4j12-*.jar

# ---------------------------
# 5️⃣ Configure logging & classpath
# ---------------------------
ENV SPARK_CLASSPATH=/opt/spark/jars/*
ENV LOG4J_CONFIGURATION_FILE=/opt/spark/conf/log4j2.properties
ENV PYSPARK_SUBMIT_ARGS="--driver-class-path /opt/spark/jars/* \
--conf spark.executor.extraClassPath=/opt/spark/jars/* pyspark-shell"

COPY conf/log4j2.properties /opt/spark/conf/log4j2.properties

# ---------------------------
# 6️⃣ Switch to spark user
# ---------------------------
USER spark

# Expose Jupyter port
EXPOSE 8888

# Default command: start jupyter notebook
CMD ["jupyter", "notebook", "--notebook-dir=/home/iceberg/notebooks", "--ip=0.0.0.0", "--port=8888", "--no-browser"]