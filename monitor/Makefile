BIN := icpc-monitor
SRC := go.mod $(wildcard *.go) index.html
LDFLAGS := -s -w

.PHONY: all clean

all: $(BIN)

$(BIN): $(SRC)
	CGO_ENABLED=0 go build -ldflags="$(LDFLAGS)"

clean:
	rm -f $(BIN)
