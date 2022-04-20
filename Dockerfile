FROM gorialis/discord.py AS builder
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt

FROM builder as runner
COPY . .
CMD [ "python", "annoyer.py"]