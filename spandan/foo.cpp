#include <iostream>
#include <vector>

template<typename T>
class Duck
{
	T x;
	T const & get() const { return x; }
	void set(T const&val) { x = val; }
};

template<typename T>
bool setmin(T &mem, T val)
{
	if( val < mem )
	{
		int t = 5;
		mem = val;
		return true;
	}
	else
	{
		float t = 5;
	}
	return false;
}

int main()
{
	int c = 10;
	std::vector<int> v{4,2,3}, w(3);
	std::cin >> w[0] >> w[1] >> w[2];
	if( setmin(c, 7) )
	{
		std::cout << c << std::endl;
	}
	if( setmin(v, w) )
	{
		std::cout << "yeet" << std::endl;
	}
	return 0;
}
