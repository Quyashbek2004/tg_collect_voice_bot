SERVICE = $(shell cat config.yaml | grep "service_name:" | cut -d ":" -f2 | tr -d " " | tr -d '"')
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
SERVICE_FILE = ~/.config/systemd/user/$(SERVICE).service

.PHONY: init start stop restart logs check-config

init:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	mkdir -p ~/.config/systemd/user
	echo "[Unit]" > $(SERVICE_FILE)
	echo "Description=Voice Bot Service" >> $(SERVICE_FILE)
	echo "After=network.target" >> $(SERVICE_FILE)
	echo "" >> $(SERVICE_FILE)
	echo "[Service]" >> $(SERVICE_FILE)
	echo "Type=simple" >> $(SERVICE_FILE)
	echo "WorkingDirectory=$(PWD)" >> $(SERVICE_FILE)
	echo "ExecStart=$(PWD)/$(VENV)/bin/python $(PWD)/main.py" >> $(SERVICE_FILE)
	echo "Restart=always" >> $(SERVICE_FILE)
	echo "" >> $(SERVICE_FILE)
	echo "[Install]" >> $(SERVICE_FILE)
	echo "WantedBy=default.target" >> $(SERVICE_FILE)
	systemctl --user daemon-reload
	systemctl --user enable $(SERVICE)

start:
	systemctl --user start $(SERVICE)

stop:
	systemctl --user stop $(SERVICE)

restart:
	systemctl --user restart $(SERVICE)

logs:
	journalctl --user-unit $(SERVICE) -f
