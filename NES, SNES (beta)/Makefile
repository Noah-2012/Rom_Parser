.PHONY: read_rom

read_rom:
ifeq ($(word 2, $(MAKECMDGOALS)),)
	$(error Bitte gib eine Datei an: make read_rom <dateiname>)
endif
	python read_rom.py roms/$(word 2, $(MAKECMDGOALS))

# Standardregel, um Konflikte mit den Dateinamen zu vermeiden
%:
	@: