# STATIC INSTRUMENTATION

## Project Dependency Parser
The first part of the project is to extract dependency of one file over other
header files and libraries. For this, we use cmake. To get started, first clone
the repo and then execute the following commands:
1. `mkdir build; cd build`
2. `cmake ..; make VERBOSE=1 > make_log.txt`
3. `cd ..`
4. `python parsers/cmake_extractor/project_parser.py build/make_log.txt`

The output has two segments. The second segment can be safely ignored for the
time being (detailed documentation has been mentioned in the `project_parser` file).
The first segment has 3 columns, out of which only the following are significant:
* first part, which is of the type `/usr/bin/cc` (or `/usr/bin/c++`). This specifies
the location of the compiler being used
* The second segment is of the type `-I/home/...`, this represents the dependencies
* The third and most important is the one ending with `.c` or `.cpp`, which tells
  the files being compiled, for which dependencies are being noted.

PS: Note that, the `make_log.txt` must contain all the compile/build/linking instructions
Hence, if there is any changes to the code, and the project is being build again,
first run `make clean`, and then repeat step 2, before proceeding further


## Sytax Parser

As a general rule, for each compilation line in the output generated above,
you have to copy the dependency and the filename (for the time, will be automated later),
each time a parser is being used. A sample for each parser has been provided.

1. To run the latest, most logical XML-parser:
  `python parsers/syntax_parser.py <c_filename> -I<dependencies`
  For example, for me it would be something like this:
  `python parsers/syntax_parser.py src/prog.c -Ilib`

  The result would be stored in the same place as the source C/C++ file, with
  XML extension. The XML may be viewed in a browser or a normal text editor. This
  parser has been made from the SyntaxTree.cpp file from Clang/Examples

2. Run parsed_parser.py (Important features, plus conversion to xml):
  `python parsers/parsed_parser.py <filename> -I/<dependencies>`

  example: `python parsers/parsed_parser.py src/prog.c -Ilib`
  This is basically the same as above, but the features are either at-times,
  over-explaining, or some attributes are missing in some very particular nodes.
  This can be used for future development and to test new features to be included

3. To run parser2.py or parser1.py:
  `python parsers/parser2.py src/prog.c -I/<path to lib>`
  (In parser1, there is no option for taking care of dependencies)

  This is basically the same as above, but these are sample codes. Kept, in case
  things go wrong and we need to revert

4. Use pycparser (For c based programs only):
  * First, get a precompiled program using `gcc -E <filename> <dependencies> > <preprocessed_filename>` (or `g++`)
  * Then use python python to run parser.py:
    `python parsers/parser.py <path_to_preprocessed_file>`
    (For me, the series of commands would be:
      `gcc -E src/prog.c -Ilib > temp.i` followed by `python parsers/parser.py temp.i`)

5. Use native clang expressions:
  `clang -Xclang -ast-dump -fsyntax-only <filename> <dependencies>` and
  `clang-check -ast-dump --extra-arg="<dependencies>" <filename>`

  This is the inbuilt Clang AST dump function. Hasn't been explored in great depth
  (Except that, you don't need to install anything else for it to work. Can work
  with bare clang installations)


### [TODO]:
- [X] Add .gitignore
- [ ] Include all features
- [ ] Provide flag for excluding standard libraries
- [X] Provide a cmake for building this file
