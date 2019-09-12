import sys
import re
import glob
import os
import shutil

if __name__ == "__main__":
	if len(sys.argv) != 7:
		print("Give 6 arguments: filename, vocab dictionary location, problem domain location, xml file location, absolute source code location, comments xml file output location - in this order")
		exit(-1)

	filename = sys.argv[1]
	vocab_loc = sys.argv[2]
	prob_loc = sys.argv[3]
	xmlfilename = sys.argv[4]
	cfilename = sys.argv[5]
	output_xml_file = sys.argv[6]

	if os.path.isfile(filename) == False:
		print("Error", filename, " is not a valid filename")
		exit(-1)

	fName1 = str(filename.replace("/" , "_"))
	fName = ""
	print(fName1)
	if fName1.endswith(".c") :
		fName = fName1.replace(".c" , ".p")
	elif fName1.endswith(".cpp") :
		fName = fName1.replace(".cpp" , ".p")
	else :
		fName = fName1 + ".p"
	print(fName)
	# if os.path.exists("CSV/" + filename.replace("/", "_") + "_train.csv"):
	# 	print("Skipping: ",fName)
	# 	exit(0)
	try :
		x = os.system("python2 XML_CommentExtractor.py " + filename)
		print("CommentExtractor " + str(x))
		#key = input("Hit a key")
		if x != 0 :
			exit(-1)
		print "++++ CommentExtractor succesfully done!\n\n\n"

		x = os.system("python2 XML_ScopeModule.py " + filename)
		if x != 0 :
			exit(-1)
		print "++++ ScopeModule succesfully done!\n\n\n"

		os.chdir("Identifier/")
		print xmlfilename, cfilename
		x = os.system("python2 xmlparser_with_id.py " + xmlfilename + " " + cfilename + " ../" + vocab_loc + " ../" + prob_loc)
		if x != 0:
			exit(-1)
		print "++++ Identifier succesfully done!\n\n\n"
		os.chdir("../")

		x = os.system("python2 XML_FinalExcelGeneration_with_id.py " + filename + " " + vocab_loc + " " + prob_loc)
		if x != 0:
			exit(-1)
		print "++++ Knowledge base generation done!\n\n\n"

		project_name = cfilename[:cfilename.find("/")]
		project_path = filename[:filename.find(project_name) + len(project_name)]
		x = os.system("python2 GetFinalXMLForComments.py " + project_name + " " + project_path + " " + cfilename + " " + filename + " knowledge_base_commentsXML.csv " + output_xml_file)
		if x!=0:
			exit(-1)
		print "++++ XML Generation Done!\n\n\n"

	except Exception as e :
		print("Error in running the command " + str(e))
		exit(-1)
	exit(0)
