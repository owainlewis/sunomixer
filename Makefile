.PHONY: generate upload list-genres list-moods clean help

# Default mood and genre (can be overridden)
MOOD ?= FOCUS
GENRE ?= dark_synthwave
TRACKS ?= 10
PRIVACY ?= private

help:
	@echo "Suno Mixer Commands"
	@echo ""
	@echo "  make generate              Generate a mix (uses defaults)"
	@echo "  make generate MOOD=AMBITION GENRE=lofi_chill TRACKS=8"
	@echo ""
	@echo "  make upload MIX=/path/to/mix"
	@echo "  make upload MIX=/path/to/mix PRIVACY=unlisted"
	@echo ""
	@echo "  make list-genres           Show available genres"
	@echo "  make list-moods            Show available mood words"
	@echo ""
	@echo "  make clean                 Remove all output mixes and temp files"
	@echo ""
	@echo "Defaults:"
	@echo "  MOOD=$(MOOD)  GENRE=$(GENRE)  TRACKS=$(TRACKS)  PRIVACY=$(PRIVACY)"

generate:
	uv run python -m suno_mixer generate --mood=$(MOOD) --genre=$(GENRE) --tracks=$(TRACKS)

upload:
ifndef MIX
	$(error MIX is required. Usage: make upload MIX=/path/to/mix)
endif
	uv run python -m suno_mixer publish "$(MIX)" --privacy=$(PRIVACY)

list-genres:
	uv run python -m suno_mixer list genres

list-moods:
	uv run python -m suno_mixer list moods

clean:
	@echo "Removing output mixes and temp files..."
	rm -rf ./output/*
	rm -rf ./temp/*
	@echo "Done."
