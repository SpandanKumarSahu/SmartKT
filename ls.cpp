template <int dim>
class Point<dim>
{
  ;
};

template <typename T>
class vector<T>
{
  public:
    vector<T> (int dim) {;}
};

template <typename T1, typename T2>
class pair<T1, T2>
{
  ;
};



template <int dim>
class Function<dim>
{
  public:
    int r, p;
    Function<dim> (int a) { r = dim; p = a;}
    virtual void
    vector_value(int & p, int &values) const {;}

    double get_time() {return 0;}
};


// homogeneous linear in time function
template <int dim>
class MyFunc : public Function<dim>
{
public:
  MyFunc(const double a, const double b)
    : Function<dim>(dim)
    , a(a)
    , b(b)
  {}

  virtual double
  value(const Point<dim> p, const unsigned int component = 0) const
  {
    return a * this->get_time() + b;
  }

  virtual void
  vector_value(const Point<dim> & p, Vector<double> &values) const override
  {
    for (unsigned int i = 0; i < dim; ++i)
      values[i] = a * this->get_time() + b;
  }

private:
  const double a;
  const double b;
};

template <int dim>
void
check()
{
  Vector<double> v1(dim);

  const Point<dim> point;

  MyFunc<dim> func(0.5, 10);

  func.vector_value(point, v1);
}


