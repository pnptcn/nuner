FROM bitnami/minideb:latest

ENV CUDA=0

WORKDIR /app

RUN install_packages ca-certificates build-essential python3-full python3-pip git \
	&& useradd -m -s /bin/bash appuser \
	&& mv /usr/lib/python3.11/EXTERNALLY-MANAGED /usr/lib/python3.11/EXTERNALLY-MANAGED.old

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip \
	&& pip install --upgrade packaging \
	&& pip install --no-cache-dir -r requirements.txt \
	&& pip install flash-attn==2.6.3

COPY . .

RUN mkdir -p /home/appuser/.cache \
	&& chown -R appuser:appuser /home/appuser \
	&& chmod -R 777 /home/appuser/.cache

USER appuser

EXPOSE 5051

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5051"]
