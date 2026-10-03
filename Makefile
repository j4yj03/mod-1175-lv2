# Green Stripe 76 — native and MOD Plugin Builder friendly.
CXX ?= c++
PYTHON ?= python3
BUILD_DIR ?= build/native
PREFIX ?= /usr/local
LV2DIR ?= $(PREFIX)/lib/lv2
DESTDIR ?=
CPPFLAGS += -Isrc
CXXFLAGS += -O3
PROJECT_CXXFLAGS = -std=c++11 -Wall -Wextra -Wpedantic -fPIC -fvisibility=hidden -fno-fast-math -ffp-contract=off
LDFLAGS += -Wl,--no-undefined
LIBRARY = $(BUILD_DIR)/green-stripe-76.lv2/green-stripe-76.so
HEADERS = src/dsp/GreenStripe.hpp src/dsp/ModelConstants.hpp src/lv2_abi.h

.PHONY: all generate check-generated test benchmark measurement-probe install clean package
all: $(LIBRARY)

generate:
	$(PYTHON) tools/generate.py

check-generated:
	$(PYTHON) tools/generate.py --check

$(LIBRARY): src/lv2_plugin.cpp $(HEADERS) $(wildcard lv2/green-stripe-76.lv2/*.ttl) $(wildcard lv2/green-stripe-76.lv2/modgui/*)
	mkdir -p "$(BUILD_DIR)/green-stripe-76.lv2"
	cp -R lv2/green-stripe-76.lv2/. "$(BUILD_DIR)/green-stripe-76.lv2/"
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(PROJECT_CXXFLAGS) -fno-exceptions -fno-rtti -shared src/lv2_plugin.cpp $(LDFLAGS) -o "$@"

$(BUILD_DIR)/dsp_tests: tests/dsp_tests.cpp $(HEADERS)
	mkdir -p "$(BUILD_DIR)"
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(PROJECT_CXXFLAGS) tests/dsp_tests.cpp $(LDFLAGS) -o "$@"

$(BUILD_DIR)/transitions: tests/transitions.cpp $(HEADERS)
	mkdir -p "$(BUILD_DIR)"
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(PROJECT_CXXFLAGS) tests/transitions.cpp $(LDFLAGS) -o "$@"

test: all check-generated $(BUILD_DIR)/dsp_tests $(BUILD_DIR)/transitions
	"$(BUILD_DIR)/dsp_tests"
	"$(BUILD_DIR)/transitions"
	$(PYTHON) tests/test_lv2.py "$(LIBRARY)"
	$(PYTHON) tools/validate.py

$(BUILD_DIR)/benchmark: tests/benchmark.cpp $(HEADERS)
	mkdir -p "$(BUILD_DIR)"
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(PROJECT_CXXFLAGS) tests/benchmark.cpp $(LDFLAGS) -o "$@"

benchmark: $(BUILD_DIR)/benchmark
	"$(BUILD_DIR)/benchmark"

$(BUILD_DIR)/measurement_probe: tools/measurement_probe.cpp $(HEADERS)
	mkdir -p "$(BUILD_DIR)"
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(PROJECT_CXXFLAGS) tools/measurement_probe.cpp $(LDFLAGS) -o "$@"

measurement-probe: $(BUILD_DIR)/measurement_probe

install: all
	mkdir -p "$(DESTDIR)$(LV2DIR)/green-stripe-76.lv2"
	cp -R "$(BUILD_DIR)/green-stripe-76.lv2/." "$(DESTDIR)$(LV2DIR)/green-stripe-76.lv2/"

package: all
	$(PYTHON) tools/package.py --bundle "$(BUILD_DIR)/green-stripe-76.lv2"

clean:
	$(PYTHON) -c 'import pathlib,shutil; p=pathlib.Path("$(BUILD_DIR)"); assert p.parts[0]=="build"; shutil.rmtree(p,ignore_errors=True)'
