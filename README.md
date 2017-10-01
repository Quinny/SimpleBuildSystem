# Simple Build System

A simple but relatively complete build system useful for getting small projects
started quickly without having to fight with make.

## Example

A very contrived (but telling) example usage can be found in examples/animal.
The spec.json file defined there is as follows:

```
{
  "builds": [
    {
      "name": "animal",
      "command": "g++ animal.cc -c -o lib/animal.o",
      "input_files": ["animal.cc", "animal.h"]
    },
    {
      "name": "dog",
      "command": "g++ dog.cc lib/animal.o -c -o lib/dog.o",
      "input_files": ["dog.cc", "dog.h"],
      "deps": ["animal"]
    },
    {
      "name": "main",
      "command": "g++ main.cc lib/dog.o -o bin/main.out",
      "deps": ["dog"],
      "input_files": ["main.cc"]
    }
  ]
}
```

When running the `sbs` command for the first time, all 3 rules will be built.

```
$> sbs
$> Running:
[\*] g++ animal.cc -c -o lib/animal.o
Running:
[\*] g++ dog.cc lib/animal.o -c -o lib/dog.o
Running:
[\*] g++ main.cc lib/dog.o -o bin/main.out
```

_Note that `sbs` will parallelize builds when possible._

Running `sbs` again yields no output.

```
$> sbs
$>
```

This is because no files have changed, therefore none of the rules need to be
rebuilt. After changing animal.h, all three rules will be rebuilt again:

```
$> sbs
$> Running:
[\*] g++ animal.cc -c -o lib/animal.o
Running:
[\*] g++ dog.cc lib/animal.o -c -o lib/dog.o
Running:
[\*] g++ main.cc lib/dog.o -o bin/main.out
```

`sbs` determined that `dog` needed to be built since it directly depends on
`animal`, and `main` needed to be rebuilt since it transitively depends on `animal`
through `dog`.

Changing `dog.h` will only trigger `dog` and `main` to be rebuilt, whereas
animal does not need to be updated.

```
$> sbs
$> Running:
[\*] g++ dog.cc lib/animal.o -c -o lib/dog.o
Running:
[\*] g++ main.cc lib/dog.o -o bin/main.out
```

And finally for completeness, chaging only `main.cc` will trigger a single build,
since no rules are dependant on it.

```
$> sbs
$> Running:
[\*] g++ main.cc lib/dog.o -o bin/main.out
```
