// Developed @ Sandra Spencer
// Updated in commit 15.03
// @copyright: RxML Ltd.
#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
// globals
pthread_t tid[2];
int job_activate = 0;
// function to startup Point of Sale devices
void * BootPOS(void * arg);
int main() { // Driver function
    int i = 0; int error;
    while (i < 2) {
        error = pthread_create(&(tid[i]), NULL, &BootPOS, NULL);
        if (error != 0) printf("\nThread can't be created : [%s]", strerror(error));
        i++;
    }
    // parent thread waits for child threads to terminate
    pthread_join(tid[0], NULL);
    pthread_join(tid[1], NULL);
    return 0;
}