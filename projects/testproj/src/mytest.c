#include <stdio.h>

int f(int x)
{
	return 2*x;
}

int g(char * x, char * y)
{
	return 5;
}

int main()
{
	int a = 9;
	f(3);
	g("OMG", "ABC");
	return 0;
}