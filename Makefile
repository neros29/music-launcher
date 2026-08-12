# --- XDG-Compliant configuration ---
APP_NAME = music-launcher

# Fall back to standard XDG paths if environment variables are not explicitly set
XDG_STATE_HOME ?= $(HOME)/.local/state
XDG_BIN_HOME ?= $(HOME)/.local/bin

INSTALL_DIR = $(XDG_STATE_HOME)/$(APP_NAME)
BIN_DIR = $(XDG_BIN_HOME)
VENV_DIR = $(INSTALL_DIR)/venv
PYTHON = python3

TUI = build_tui

all: $(TUI)
	@echo "Building application dependencies..."

$(TUI):
	@# 1. Ensure the XDG state installation directory exists
	mkdir -p $(INSTALL_DIR)
	
	@# 2. Create a virtual environment inside the XDG state directory if missing
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating Python virtual environment in XDG state path..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

	@# 3. Install required Python packages into the venv
	@echo "Installing package dependencies..."
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r requirements.txt

	@# 4. Clone tuilib if not present
	@if [ ! -d "include/tuilib" ]; then \
		git clone https://github.com/neros30/tuilib/ ./include/tuilib/; \
	fi
	
	@# 5. Compile C++ Pybind11 extension using the venv's python interpreter
	rm -rf include/tuilib/build
	mkdir -p include/tuilib/build
	cd include/tuilib/build && cmake -DPython3_EXECUTABLE=$(VENV_DIR)/bin/python .. && make

install: all
	@echo "Installing $(APP_NAME) utilizing XDG standards..."
	mkdir -p $(BIN_DIR)
	mkdir -p $(INSTALL_DIR)/logs
	
	# Copy source code and include files over to XDG state location
	rm -rf $(INSTALL_DIR)/src $(INSTALL_DIR)/include
	cp -r src $(INSTALL_DIR)/
	cp -r include $(INSTALL_DIR)/
	
	@echo "Writing dynamic execution wrapper to $(BIN_DIR)/$(APP_NAME)..."
	
	# Generate wrapper script pointing straight to the venv python and app source
	@echo '#!/bin/bash' > $(BIN_DIR)/$(APP_NAME)
	@echo 'cd $(INSTALL_DIR)' > $(BIN_DIR)/$(APP_NAME)
	@echo 'exec $(VENV_DIR)/bin/python $(INSTALL_DIR)/src/main.py "$$@"' >> $(BIN_DIR)/$(APP_NAME)
	
	chmod +x $(BIN_DIR)/$(APP_NAME)
	@echo "Installation successful!"
	@echo "Command '$(APP_NAME)' is now available globally (ensure $(BIN_DIR) is in your PATH)."

uninstall:
	@echo "Removing $(APP_NAME) from XDG paths..."
	rm -rf $(INSTALL_DIR)
	rm -f $(BIN_DIR)/$(APP_NAME)
	@echo "Uninstallation complete."

debug:
	@# Check if the directory already exists so we don't try to clone twice
	@if [ ! -d "include/tuilib" ]; then \
		git clone https://github.com/neros29/tuilib/ ./include/tuilib/; \
	fi
	@# Create build directory if it doesn't exist
	rm -rf include/tuilib/build
	mkdir -p include/tuilib/build
	@# Use && to ensure cmake runs INSIDE the build directory
	cd include/tuilib/build && cmake .. && make

.PHONY: all install uninstall debug $(TUI)
