#dependencies

https://pygccxml.readthedocs.io/en/master/install.html


sudo -H pip install pygccxml

sudo apt-get install castxml


sudo apt-get install gccxml


sudo apt-get install dwarfdump

sudo -H pip install flask


sudo -H pip install pillow


# CLANG SETUP

chnage the path for clang in parser/clang_parser

cl.Config.set_library_file("/usr/lib/x86_64-linux-gnu/libclang-6.0.so.1")

# RUN INSTRUCTIONS

* python initialize.py <path_to_file>
* python examine.py <name_of_project> <path_to_executable>

Example:

* python initialize.py ../smallproj
* python examine.py smallproj ../smallproj/build/prog

The server starts running at localhost:5000/
Currently supported queries:

* Static:
	* Class Map: (Sample query: "show classmap")
	* Design Patterns (Sample query: "what design patterns")
	* Type (Sample query: "what is the type of x")
	* Parent (Sample query: "What is the parent of x")
* Dynamic:
	* Thread activity (Sample query: "Display activity of thread 0")
	* Call graph (Sample query: "Show call graph")

