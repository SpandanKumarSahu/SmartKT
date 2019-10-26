#include <stdio.h>
#define ll long long
#define mycall(x) f(x)

typedef short int ps;

ll f (ps x)
{
	return (ll)x;
}

int main()
{
	ps oll = 3;
	ll ops = mycall (3);
	printf("%d %lld\n", oll, ops);
	return 0;
}
