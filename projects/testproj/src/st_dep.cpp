//dep.c
int unshared=20;
static int p = 1;

static int add_p()
{
	unshared += p;
	return unshared;
}

int selfincvar() 
{
  static int p = 2;
  static int unshared = 9;
  {
  	::unshared += p;
  	::unshared = add_p();
  	return unshared;
  }
}
