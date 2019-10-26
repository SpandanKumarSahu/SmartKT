// One function works for all data types.  This would work 
// even for user defined types if operator '>' is overloaded 
template <typename T> 
T myMax(T x, T y) 
{ 
   T r = (x > y)? x: y; 
   return r;
} 
  
int main() 
{ 
  int g = myMax<int>(3, 7);  // Call myMax for int 
  double h = myMax<double>(3.0, 7.5); // call myMax for double 
  char i = myMax<char>('g', 'e');   // call myMax for char
  return 0; 
}