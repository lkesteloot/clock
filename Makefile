
.PHONY: help cut json publish

USB=/Volumes/LAWRENCEUSB

help:
	@echo "See Makefile for targets."

cut:
	python cut.py clock.json >clock.svg

json:
	python clock.py >clock.json

publish:
	rsync -a --delete *.js *.html *.json lk@plunk.org:public_html/clock

thumb:
	@if [ ! -d $(USB) ]; then echo --------------------- Insert USB drive ---------------------; exit 1; fi
	cp clock.svg $(USB)
	diskutil eject $(USB)
