# Инструкция по развёртыванию на сервере

## Что потребуется

- VPS/сервер с Ubuntu 22.04 или 24.04
- SSH-доступ с правами sudo
- Порт 8080 (или 80) открыт в firewall

---

## 1. Подготовка сервера

Подключись по SSH и установи зависимости:

```bash
sudo apt update && sudo apt upgrade -y

# Python 3.13
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install -y python3.13 python3.13-venv python3.13-dev

# Системные библиотеки для WeasyPrint (PDF)
sudo apt install -y libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0 \
  libcairo2 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env   # или перелогинься
```

---

## 2. Копирование файлов проекта

**На своём Mac** — скопируй проект на сервер:

```bash
# Исключаем .venv и кэш Python
rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' \
  /Users/mihailabakumov/Downloads/ohrana/ \
  mikhail@194.180.188.95:/home/mikhail/ohrana/
```

Или через git, если репозиторий уже на GitHub:

```bash
# На сервере:
git clone https://github.com/ВАШ_РЕПО/ohrana.git
cd ohrana
```

> **Важно**: если уже есть заполненная база `ohrana.db` — скопируй её отдельно:
> ```bash
> scp /Users/mihailabakumov/Downloads/ohrana.db mikhail@194.180.188.95:/home/mikhail/ohrana/
> ```

---

## 3. Установка зависимостей на сервере

```bash
cd /home/mikhail/ohrana
uv sync
```

---

## 4. Изменение хоста для сетевого доступа

Сейчас приложение слушает только `127.0.0.1` — с сервера оно будет недоступно снаружи.
Нужно поменять на `0.0.0.0`.

В файле `run.py`, строка 36:
```python
# Было:
config = uvicorn.Config(app, host="127.0.0.1", port=8080, log_config=None)

# Надо:
config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_config=None)
```

Либо запускай напрямую через uvicorn (без run.py):
```bash
uv run uvicorn src.presentation.app:app --host 0.0.0.0 --port 8080
```

---

## 5. Запуск как systemd-служба (чтобы работало в фоне)

Создай файл службы:

```bash
sudo nano /etc/systemd/system/ohrana.service
```

Содержимое:

```ini
[Unit]
Description=Охрана — управление объектами
After=network.target

[Service]
Type=simple
User=mikhail
WorkingDirectory=/home/mikhail/migration_ohrana
ExecStart=/home/mikhail/.local/bin/uv run uvicorn src.presentation.app:app --host 0.0.0.0 --port 8080
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```


Активируй и запусти:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ohrana
sudo systemctl start ohrana

# Проверить статус:
sudo systemctl status ohrana

# Посмотреть логи:
sudo journalctl -u ohrana -f
```

---

## 6. Открыть порт в firewall

```bash
sudo ufw allow 8080/tcp
sudo ufw status
```

---

## 7. Проверка

Открой в браузере: `http://194.180.188.95:8080`

---

## Остановить / удалить

```bash
# Остановить:
sudo systemctl stop ohrana

# Убрать из автозапуска:
sudo systemctl disable ohrana
```

---

## Замечания по безопасности

Приложение **без авторизации** — любой кто знает IP, может зайти. Для временного
использования внутри локальной сети или VPN это нормально. Если сервер публичный —
огради доступ по IP через firewall.

### Узнать внешний IP компьютера

На каждом компьютере, которому нужен доступ, открой браузер и зайди на:
- https://ifconfig.me
- https://2ip.ru

### Разрешить доступ только с конкретных IP

```bash
sudo ufw allow from IP_КОМПЬЮТЕРА_1 to any port 8080
sudo ufw allow from IP_КОМПЬЮТЕРА_2 to any port 8080
sudo ufw deny 8080
sudo ufw enable

# Проверить правила:
sudo ufw status
```
