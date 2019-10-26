int a = 1;
static int p = 2;

static int poll()
{
	static int a = 2;
	{
		extern int a;
		a += 1;
	}
	return a;
}