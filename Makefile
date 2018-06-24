publish: archive
	rm -rf /tmp/traffix-signs
	cp -arv .cards /tmp/traffix-signs
	cd /tmp/traffix-signs
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
