PLUGIN_PATH=/usr/lib/rhythmbox/plugins/remember-the-song
install:
	mkdir -p $(PLUGIN_PATH)
	cp remember-the-song.* $(PLUGIN_PATH) -Rf
	
uninstall:
	rm -Rf $(PLUGIN_PATH)
