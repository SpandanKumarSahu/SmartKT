//dep.c
int unshared=20;

int selfincvar() 
{
  static int p = 1;
  static int unshared = 9;
  {
  	extern int unshared;
  	unshared += p;
  }
  return unshared;
}
