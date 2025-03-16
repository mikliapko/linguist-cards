# lingvist-cards

Sync project with RPi:
```bash
rsync -avx \
  --exclude="venv/" \
  --exclude="__pycache__/" \
  . pi@192.168.8.117:/home/pi/lingvist-cards
```

Build docker container:
```bash
docker build -t lingvist-cards .
```

Run docker container:
```bash
sudo docker run -d --env-file .env lingvist-cards english
```
