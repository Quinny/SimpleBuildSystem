#include "dog.h"

#include <memory>

int main() {
  std::unique_ptr<Animal> animal = std::make_unique<Dog>();
  animal->Speak();
}
