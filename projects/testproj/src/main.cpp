//main.c
#include <stdio.h>
 
//Found in this executable file itself.
extern int unshared;
extern int selfincvar();
 
void selfcall() {
 printf("Unshared Variable=%d\n",unshared);
 printf("Incremented Unshared Variable=%d\n",selfincvar());
}
 
//Found in Shared Library.
extern int shared;
extern int libincvar();
 
void libcall() {
	int r = 9;
 printf("Shared Variable=%d\n",shared);
 printf("Incremented Shared Variable=%d\n",libincvar());
}
 
int main() {
 selfcall();
 libcall();
}