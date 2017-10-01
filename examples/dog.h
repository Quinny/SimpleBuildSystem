#include "animal.h"

#ifndef DOG_H
#define DOG_H

class Dog : public Animal {
 public:
  virtual void Speak() override;
};

#endif /* DOG_H */
