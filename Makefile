OUTDIR=/tmp
.PHONY: readme
readme:
	python3 -c 'import mistune' && cat README.md | python3 -c 'from mistune import Markdown;from sys import stdin;print(Markdown()(stdin.read()))' > $(OUTDIR)/readme.html && cp celerykube.png $(OUTDIR)
