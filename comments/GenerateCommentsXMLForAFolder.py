import sys, os
from os.path import join as PJOIN
import pickle

def runForFolder(folder_name):
    for file in os.listdir(PJOIN(BASE_DIR, PROJECT_NAME, folder_name)):
        if os.path.isdir(PJOIN(BASE_DIR, PROJECT_NAME, folder_name, file)):
            if not os.path.exists(PJOIN(OUTPUT_FOLDER, folder_name, file)):
                os.mkdir(PJOIN(OUTPUT_FOLDER, folder_name, file))
            runForFolder(PJOIN(folder_name, file))
            continue
        split_filename = os.path.splitext(file)
        if split_filename[1] not in [".cpp",".c"]:
            continue
        xml_file = split_filename[0] + "_clang.xml"
        if not os.path.exists(PJOIN(XML_BASE_DIR, folder_name, xml_file)):
            try:
                s = "python parsers/clang_parser.py " + PJOIN(BASE_DIR, PROJECT_NAME, folder_name, file)
                for d in dep[PJOIN(BASE_DIR, PROJECT_NAME, folder_name, file)]:
                    s += " " + d
                os.system(s)
                os.system("mv "+ PJOIN(BASE_DIR, folder_name, xml_file) + " " + PJOIN(XML_BASE_DIR, folder_name, xml_file)) 
                pass
            except:
                continue
        if os.path.exists(PJOIN(OUTPUT_FOLDER, folder_name, split_filename[0]+"_comments.xml")):
            print("Skipping: Already Exists: ", PJOIN(OUTPUT_FOLDER, folder_name, split_filename[0]+"_comments.xml"))
            continue
	os.chdir("comments/")
        os.system("python2 GenerateCommentsXMLForAFile.py " + PJOIN(BASE_DIR, PROJECT_NAME, folder_name, file) + " " + VOCAB_FILE + " " +
        PROBLEM_DOMAIN_FILE + " " + PJOIN(XML_BASE_DIR, folder_name, xml_file) + " " + PJOIN(PROJECT_NAME, folder_name, file) + " " +
        PJOIN(OUTPUT_FOLDER, folder_name, split_filename[0]+"_comments.xml"))
	os.chdir("../")

if len(sys.argv) != 7:
    print("Give 6 arguments: Base Dir, Project Name, XML Base Dir, vocab file, probelm domain file, output xml folder - in this order")
    exit(-1)

dep, src, obj = pickle.load(open("dependencies.p", "rb"))
BASE_DIR = sys.argv[1]
PROJECT_NAME = sys.argv[2]
XML_BASE_DIR = sys.argv[3]
VOCAB_FILE = sys.argv[4]
PROBLEM_DOMAIN_FILE = sys.argv[5]
OUTPUT_FOLDER = sys.argv[6]

if PROJECT_NAME[-1] == '/':
    PROJECT_NAME = PROJECT_NAME[:-1]

if not os.path.exists(OUTPUT_FOLDER):
    os.mkdir(OUTPUT_FOLDER)

runForFolder("")
