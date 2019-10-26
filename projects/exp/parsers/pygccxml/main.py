import os
import sys

# Run pygccxml and get the document
filename = sys.argv[1].split('.')[0]+"_pygccxml.txt"
s = "python get_features_crude.py "
for x in sys.argv[1:]:
    s += x + " "
os.system( s + " > "+ filename)

# Convert to XML file
os.system("python convert_to_xml.py "+ filename+" > " + filename.split(".")[0]+".xml")
os.system("rm " + filename)

# Get curate XML file
os.system("python curate_xml.py " + filename.split(".")[0]+".xml")

# Analyze the design pattern
# os.system("python analyze.py " + str(sys.argv[1]))

# Cleanup
# os.system("rm output.txt output.xml output_rectified.xml")
