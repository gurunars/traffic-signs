publish: archive
	rm -rf /tmp/traffic-signs
	cp -arv .cards /tmp/traffic-signs
	cd /tmp/traffic-signs
	git init
	git checkout -b gh-pages
	echo .cache > .gitignore
	git add .
	git ci -am init
	git push origin gh-pages

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
