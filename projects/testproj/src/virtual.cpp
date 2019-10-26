class Base
{
    public:
    // virtual function
    virtual int show_val()
    {
        int f = 9;
        return f;
    }
};
class Derived:public Base
{
    public:
    // virtual overriden
    int show_val()
    {
        int g = 8;
        return g; 
    } 
}; 

int main() 
{ 
    Base* b; //Base class pointer 
    Derived d; //Derived class object 
    b = &d; 
    int x = b->show_val();   //late binding 
}