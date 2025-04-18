
build: zip exe

zip: clean
	cd pyrepub && zip -r ../repub.zip . -x "*/__pycache__/*"

exe:
	echo '#!/usr/bin/env python3' | cat - repub.zip > repub && chmod +x repub
	rm repub.zip

deploy: build
	cp repub ~/.local/bin/

clean:
	rm -f repub.zip repub
	rm -rf repub/**/*.pyc
	rm -rf repub/**/__pycache__
