FROM openjdk:slim
COPY --from=python:3.9 / /
RUN apt-get update && apt-get clean

COPY . /app
WORKDIR /app

# Install Java (OpenJDK 17)
RUN apt-get update && apt-get install -y openjdk-22-jre

# Set JAVA_HOME environment variable
#ENV JAVA_HOME /usr/lib/jvm/java-22-openjdk-amd64
#ENV PATH "$JAVA_HOME/bin:$PATH"

COPY requirements.txt /
RUN pip3 install -r requirements.txt

EXPOSE 8501

CMD streamlit run --server.port $PORT interface.py