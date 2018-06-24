archive: .venv
	.venv/bin/python gen.py

clean:
	rm -rf .cards
	rm -rf .venv
	rm finnish_traffic_signs.apkg

.venv:
	virtualenv --python=python3 .venv
	.venv/bin/pip install -r requirements.txt

.PHONY: clean archive
