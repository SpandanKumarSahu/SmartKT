CFLAGS := -gdwarf-4
CC := /usr/bin/cc

main: test.o lib.o
	$(CC) $(CFLAGS) $^ -o $@
clean:
	- rm *.o
	- rm main