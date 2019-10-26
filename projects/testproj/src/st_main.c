static int a = 1;
static int p = 1;

static int poll()
{
	static int a = 2;
	a += p;
	return a;
}

int main()
{
	static int a = 2;
	a += p;
	return a;
}