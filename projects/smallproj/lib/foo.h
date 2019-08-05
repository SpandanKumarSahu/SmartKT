#ifndef FOO_H_   /* Include guard */
#define FOO_H_

struct foo_str{
  int x;
  int y;
};

struct foo_str foo(struct foo_str x);  /* An example function declaration */

class LivingThing {
protected:
    bool isBreathing;
    void breathe() {
        this->isBreathing = true;
    }
public:
  LivingThing(){
    this->isBreathing = false;
  }
};

class Animal : virtual protected LivingThing {
protected:
    int breathCount;
    void breathe() {
        this->breathCount++;
    }
public:
  Animal(){
    this->breathCount = 0;
  }
};

class Reptile : virtual public LivingThing {
public:
  bool isCrawling;

  Reptile(){
    this->isCrawling = true;
  }
protected:
    void crawl() {
      this->isCrawling = true;
    }
};

class Snake : protected Animal, public Reptile {
public:
  void crawl();
};

#endif // FOO_H_
