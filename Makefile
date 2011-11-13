PLUGIN_PATH=/usr/lib/rhythmbox/plugins/remember-the-rhythm
SCHEMA_PATH=/usr/share/glib-2.0/schemas/

build:

install:
	mkdir -p $(PLUGIN_PATH)
	cp src/* $(PLUGIN_PATH) -Rf
	cp schemas/org.gnome.rhythmbox.plugins.remember-the-rhythm.gschema.xml $(SCHEMA_PATH)
	glib-compile-schemas $(SCHEMA_PATH)
	
uninstall:
	rm -Rf $(PLUGIN_PATH)
	rm $(SCHEMA_PATH)org.gnome.rhythmbox.plugins.remember-the-rhythm.gschema.xml 
	glib-compile-schemas $(SCHEMA_PATH)
