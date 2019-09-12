//dep.c
int unshared=20;
 
int selfincvar() {
	static int p = 1;
 unshared += p;
 return unshared;
}