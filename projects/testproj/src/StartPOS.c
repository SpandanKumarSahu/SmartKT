#include<stdio.h>
#include<stdlib.h>
// defined in DriverPOS.c
extern int job_activate;
void * BootPOS (void * arg) { //Start method for threads
    unsigned long i = 0, r = 1;
    job_activate += r;
    printf("\n Job %d has started\n", job_activate);
    for (i = 0; i < 10; i++);
	printf("\n Job %d has finished\n", job_activate);
    return NULL;
}