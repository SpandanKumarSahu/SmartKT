#include <stdio.h>
int x=50;

struct xe {
	int y;
};

int main()
{
	struct xe y;
	y.y = 9;
	printf("x= %d\n",y.y);
	static int x=100;
	{
		static int x = 90;
		printf("x= %d\n",x);
		{
			extern int x;
	    	printf("x= %d\n",x);
		}
	}
	printf("x= %d\n",x);
	return 0;
}