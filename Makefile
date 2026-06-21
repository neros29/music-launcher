TUI = build_tui

all: $(TUI)

$(TUI):
	@# Check if the directory already exists so we don't try to clone twice
	@if [ ! -d "include/tui" ]; then \
		git clone https://github.com/neros29/tuilib/ ./include/tui/; \
	fi
	@# Create build directory if it doesn't exist
	mkdir -p include/tui/build
	@# Use && to ensure cmake runs INSIDE the build directory
	cd include/tui/build && cmake .. && make

.PHONY: all $(TUI)
