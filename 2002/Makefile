RUNXML2RFC=/home/aaronsw/sources/xml2rfc-1.22/run.tcl

all: rdf-mediatype.txt rdf-mediatype.html rdf-mediatype.ms draft-swartz-pgp-urn-00.html

rdf-mediatype.txt: draft-swartz-rdfcore-rdfxml-mediatype-05.xml
	$(RUNXML2RFC) xml2txt draft-swartz-rdfcore-rdfxml-mediatype-05

rdf-mediatype.html: draft-swartz-rdfcore-rdfxml-mediatype-05.xml
	$(RUNXML2RFC) xml2html draft-swartz-rdfcore-rdfxml-mediatype-05

rdf-mediatype.ms: draft-swartz-rdfcore-rdfxml-mediatype-05.xml
	$(RUNXML2RFC) xml2nroff draft-swartz-rdfcore-rdfxml-mediatype-05

draft-swartz-pgp-urn-00.html: draft-swartz-pgp-urn-00.xml
	$(RUNXML2RFC) xml2html draft-swartz-pgp-urn-00
	$(RUNXML2RFC) xml2nroff draft-swartz-pgp-urn-00
	$(RUNXML2RFC) xml2txt draft-swartz-pgp-urn-00