//lib.c
int shared=10;
int what=7;

static int rf = 7;
 
static void addonemore();
void addtwomore();
 
int libincvar() {
int y = rf;
 shared += y;
 addonemore();
 addtwomore();
 return shared;
}
 
static void addonemore() {
	int z = 1;
 shared += z;
}
 
void addtwomore() {
	int z = 2;
 shared += z;
}
