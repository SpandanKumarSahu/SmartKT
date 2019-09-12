# DEPENDENCIES

Install dependencies using:
	`sudo ./install_dependencies.sh`

# CLANG SETUP

chnage the path for clang in parser/clang_parser
cl.Config.set_library_file("/usr/lib/x86_64-linux-gnu/libclang-6.0.so.1")

# RUN INSTRUCTIONS

* python initialize.py <path_to_file>
* python examine.py <name_of_project> <path_to_executable>

Example:

* python initialize.py projects/smallproj
* python examine.py smallproj projects/smallproj/build/prog

The server starts running at localhost:5000/
Currently supported queries:

* Static:
	* Class Map: (Sample query: "show classmap")
	* Design Patterns (Sample query: "what design patterns")
	* Type (Sample query: "what is the type of x")
	* Parent (Sample query: "What is the parent of x")
	* Return type
	* Function details
	* List all global variables
	* Dependencies
* Dynamic:
	* Thread activity (Sample query: "Display activity of thread 0")
	* Call graph (Sample query: "Show call graph")
* VCS:
	* Github Issues
	* Github commits (minimal)
# DOCKER

## RUNNING ON DOCKER
In order to run SmartKT:
* Get the latest image (you can specify any other label that `latest`)
	`sudo docker pull spandankumarsahu/smartkt:latest`
* Run the container:
	`sudo docker run --name <anyName> --security-opt="apparmor=unconfined" --cap-add=SYS_PTRACE -p 5000:5000 smartkt`
* Get the IP of the docker:
	`sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <containerName>`
* On the browser, point to `http://<IP>:5000/`
* Stopping the docker:
	`sudo docker stop <containerName>`
	`sudo docker rm <containerName>`

## BUILDING ON DOCKER

Please note that this repository is internally connected to Dockerhub. So, any changes you push to this Github
repository, results in the latest docker image on Dockerhub. Even then, if you need to manually push some changes
to Dockerhub, follow these instructions. (** It is however, highly discouraged that you push to Dockerhub directly.
You should make appropriate changes in the Dockerfiles and let the integrated system build the new image.**)

* To build a dockerized image:
	`sudo docker build -t spandankumarsahu/smartkt:latest .`
* You can view the images created by running:
	`sudo docker images`
* In order to run an image, you just need to run:
	`sudo docker run --name <anyName> --security-opt="apparmor=unconfined" --cap-add=SYS_PTRACE smartkt`
* Once started, you can view the current images running:
	`sudo docker ps`
* In order to get inside one of these containers, just run:	
	`sudo docker exec -it <containerID> bash`
* Once inside the docker, you can make as many edits to the container as you like. Once done, exit the container and run:
	`sudo docker commit <containerID> spandankumarsahu/smartkt:latest`
* After building, you must login to Dockerhub:
	`sudo docker login`
* After login, you can now push the new docker image as:
	`sudo docker push smartkt spandankumarsahu/smartkt:latest`
