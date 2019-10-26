//main.c
#include <iostream>
 
//Found in this executable file itself.
extern int unshared;
extern int selfincvar();

static int p = 2;

static int add_p()
{
	int x = 3;
	return x+p;
}

void selfcall() 
{
 int h = add_p();
 cout << "Unshared Variable=" << unshared << "\n";
 cout << "Incremented Unshared Variable=" << selfincvar() << "\n";
}
 
//Found in Shared Library.
// extern int shared;
// extern int libincvar();
 
// void libcall() 
// {
//  int r = 9;
//  printf("Shared Variable=%d\n",shared);
//  printf("Incremented Shared Variable=%d\n",libincvar());
// }
 
int main() 
{
 selfcall();
 //libcall();
}