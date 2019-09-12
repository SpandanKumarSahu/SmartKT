#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>

// globals
pthread_t tid[2];
int counter = 0;

// external declarations
void * trythis(void * arg);

int main()
{
    int i = 0;
    int error;

    while (i < 2)
    {
        error = pthread_create(&(tid[i]), NULL, &trythis, NULL);
        if (error != 0)
            printf("\nThread can't be created : [%s]", strerror(error));
        i++;
    }

    pthread_join(tid[0], NULL);
    pthread_join(tid[1], NULL);

    return 0;
}
