FROM apache/spark:4.0.1-scala2.13-java21-python3-r-ubuntu

USER root

# Create a real home for spark
RUN mkdir -p /home/spark && \
    chown -R spark:spark /home/spark

ENV HOME=/home/spark

# Install pip and Jupyter, match pyspark version with Spark version
RUN apt-get update && \
    apt-get install -y python3-pip wget libsnappy-dev zlib1g-dev \
    pip3 install --no-cache-dir notebook findspark pyspark==4.0.1 && \
    mkdir -p /opt/spark/jars && \
    # Download Iceberg runtime jar
    wget -P /opt/spark/jars https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-4.0_2.13/1.10.1/iceberg-spark-runtime-4.0_2.13-1.10.1.jar && \
    # Download Hadoop AWS jar
    wget -P /opt/spark/jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.4.1/hadoop-aws-3.4.1.jar && \
    # AWS SDK v2 bundle (must match Hadoop dependency)
    wget -P /opt/spark/jars \
    https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.24.6/bundle-2.24.6.jar

# Set SPARK_CLASSPATH to include jars
ENV SPARK_CLASSPATH=/opt/spark/jars/*
ENV LOG4J_CONFIGURATION_FILE=/opt/spark/conf/log4j2.properties

COPY log4j2.properties /opt/spark/conf/log4j2.properties

USER spark
WORKDIR /home/spark

# Expose Jupyter port
EXPOSE 8888

# Default command: start jupyter notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]