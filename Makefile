RPMSOURCEDIR := $(HOME)/rpmbuild/SOURCES

.PHONY: all prepare rpm

all: rpm

prepare:
	mkdir -p $(RPMSOURCEDIR)
	cp redis-* redis.init redis.logrotate $(RPMSOURCEDIR)

rpm: prepare
	rpmbuild -ba redis.spec
