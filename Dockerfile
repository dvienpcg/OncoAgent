FROM python:3.11.11-slim
WORKDIR /workspace
COPY . .
RUN pip install --no-cache-dir .
ENTRYPOINT ["oncoagent"]

