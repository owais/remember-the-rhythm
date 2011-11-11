PLUGIN_PATH=/usr/lib/rhythmbox/plugins/remember-the-rhythm
install:
	mkdir -p $(PLUGIN_PATH)
	cp src/* $(PLUGIN_PATH) -Rf
	
uninstall:
	rm -Rf $(PLUGIN_PATH)
