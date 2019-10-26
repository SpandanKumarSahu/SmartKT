#include <stdio.h>

int f(int x)
{
	return x;
}

int g (char * p)
{
	return 4;
}

int main()
{
	int x = 3;
	char * y = "ABC";
	x = f(x);
	x = g(y);
	return 0;
}