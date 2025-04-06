
build: zip exe

zip: clean
	cd repub && zip -r ../repub-temp.zip . -x "*/__pycache__/*"

exe:
	echo '#!/usr/bin/env python3' | cat - repub-temp.zip > repub.zip && chmod +x repub.zip
	rm repub-temp.zip

deploy: build
	cp repub.zip ~/dev/bin/repub

clean:
	rm -f repub-temp.zip repub.zip
	rm -rf repub/**/*.pyc
	rm -rf repub/**/__pycache__
