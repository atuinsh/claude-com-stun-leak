.PHONY: run-remote deploy build

SERVER = 152.236.5.33
REMOTE = rocky@$(SERVER)
WHEEL = dist/claude_com_stun_leak-0.1.0-py3-none-any.whl
REMOTE_WHEEL = ~/$(notdir $(WHEEL))
REMOTE_VENV = ~/.csl-venv

run-remote: deploy
	ssh -t $(REMOTE) 'python3 -m venv $(REMOTE_VENV) && $(REMOTE_VENV)/bin/pip install --force-reinstall --no-deps $(REMOTE_WHEEL) && exec $(REMOTE_VENV)/bin/stun-server --host 0.0.0.0 --port 3478'

deploy: build
	scp $(WHEEL) $(REMOTE):$(REMOTE_WHEEL)

build:
	uv build
