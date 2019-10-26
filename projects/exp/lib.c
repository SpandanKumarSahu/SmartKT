#include <stdio.h>
extern int p;
  
static void addonemore()
{
	p += 1;
	printf ("Global p inc to: %d\n", p);
}
  
int addtwomore() 
{
	static int p = 7;
	addonemore();
	return p + 1;
}