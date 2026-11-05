.PHONY: run-remote deploy build

SERVER = 152.236.5.33

run-remote: deploy
	ssh -t rocky@$(SERVER) '<CMD>'

deploy:
	scp dist/claude_com_stun_leak-0.1.0-py3-none-any.whl rocky@$(SERVER):~/csl-py3-none-any.whl

build:
	uv build
