TUI = build_tui

all: $(TUI)

$(TUI):
	@# Check if the directory already exists so we don't try to clone twice
	@ #git clone https://github.com/neros29/tuilib/ ./include/tuilib/;
	@if [ ! -d "include/tuilib" ]; then \
		git clone https://github.com/neros29/tuilib/ ./include/tuilib/;\
	fi
	@# Create build directory if it doesn't exist
	rm -rf include/tuilib/build
	mkdir -p include/tuilib/build
	@# Use && to ensure cmake runs INSIDE the build directory
	cd include/tuilib/build && cmake .. && make

.PHONY: all $(TUI)
