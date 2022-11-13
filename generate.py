import sys
import os
import glob
import shutil
import xml.etree.ElementTree as elemTree

htmlForm = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" type="text/css" href="report.css">
    <title>GTest Reports</title>
</head>
<body>
    <table>
    {report}
    </table>
</body>
</html>'''

ReportHeader = \
    "<tr>\
        <th>Test Name</th>\
        <th>Total Unit Tests</th>\
        <th>Failed Unit Tests</th>\
        <th>Disabled Unit Tests</th>\
        <th>Timestamp</th>\
    </tr>\n"

outputFileName = "index.html"


def genTableRows(data):
    ret = "<tr>"
    ret += genTableItem(data)
    ret += "</tr>"
    print(ret)
    return ret


def genTableItem(data):
    ret = ""
    for item in data:
        ret += f"<td>{item}</td>"
    return ret


def genHTMLDoc(inFiles, outDir):
    totTCNum = 0
    reports = ""

    for fName in inFiles:
        print(fName)
        fNameOnly = os.path.basename(fName)
        print(f"fileName {fNameOnly}")
        fileXML = elemTree.parse(fName)
        root = fileXML.getroot()
        print(root.tag)
        print(root.attrib)
        reports += genTableRows([fNameOnly, root.attrib['tests'], root.attrib['failures'],
                                 root.attrib['disabled'], root.attrib['timestamp']])

    htmlDoc = htmlForm.format(report=ReportHeader + reports)
    # print(htmlDoc)
    print(outDir + "/" + outputFileName)
    with open(outDir + "/"+outputFileName, "wb") as writer:
        writer.write(htmlDoc.encode('utf-8'))

#        suites = root.findall('./testsuite')
#        print(len(suites))
#        print(suites)
#        for suite in suites:
#            print(suite.attrib)
#            for test in suite:
#                print(test.attrib)

    pass


if __name__ == '__main__':
    print("Generate html report from gtest output xmls")
    if (len(sys.argv) < 3):
        print("Need input dir & output dir name is required")
        print("example) $ python generate.py in_dir out_dir")
        sys.exit(0)

    inputDir = sys.argv[1]
    outputDir = sys.argv[2]

    # Setup output folder (check existence & clean up)
    if os.path.isdir(outputDir):
        print(f"Remove files in the \"{outputDir}\"")
        shutil.rmtree(outputDir, ignore_errors=True)
    os.makedirs(outputDir)

    # TODO: input folder exist & check at lease one file
    if not os.path.isdir(inputDir):
        print(f"Directory \"{inputDir}\" is not exist. Terminate")
        sys.exit(0)

    inputFiles = glob.glob(inputDir + "/*.xml")
    if len(inputFiles) == 0:
        print(f"There is no xml file in \"{inputDir}\". Terminate")
    print(inputFiles)

    # TODO: processing
    genHTMLDoc(inputFiles, outputDir)

    shutil.copy("report.css", outputDir)
