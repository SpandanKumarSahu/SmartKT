#include<stdio.h>
#include<stdlib.h>

extern int counter;

void * trythis(void * arg)
{
    unsigned long i = 0, r = 1;
    counter += r;
    printf("\n Job %d has started\n", counter);
    for (i = 0; i < 10; i++);
    	printf("\n Job %d has finished\n", counter);
    return NULL;
}