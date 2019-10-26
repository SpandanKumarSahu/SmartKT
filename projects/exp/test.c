#include <stdio.h>

int p = 20;

extern int addtwomore();

int main()
{
	static int p = 10;
	printf ("Local p here: %d\n", p);
	int r = addtwomore();
	printf ("Local p there inc to: %d\n", r);
	return 0;
}