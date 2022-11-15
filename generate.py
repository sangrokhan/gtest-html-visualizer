import sys
import os
import glob
import shutil
import xml.etree.ElementTree as elemTree
from datetime import datetime

htmlForm = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script
    src="https://code.jquery.com/jquery-3.6.1.slim.min.js"
    integrity="sha256-w8CvhFs7iHNVUtnSP0YKEg00p9Ih13rlL9zGqvLdePA="
    crossorigin="anonymous"></script>
    <link rel="stylesheet" type="text/css" href="report.css">
    <script src="report.js"></script>
    <title>GTest Reports</title>
</head>
<body>
    <table>
    {report}
    </table>
</body>
</html>'''

ReportHeader = \
    "<thead>\
        <tr>\
            <th>Status</th>\
            <th>Test Name</th>\
            <th>Total Unit Tests</th>\
            <th>Failed Unit Tests</th>\
            <th>Disabled Unit Tests</th>\
            <th>Timestamp</th>\
        </tr>\
    </thead>\n"

DetailReportHeader = \
    "<thead>\
        <tr>\
            <th>Name</th>\
            <th>Tests</th>\
            <th>Failed</th>\
            <th>Disabled</th>\
            <th>Time</th>\
        </tr>\
    </thead>"

outputFileName = "index.html"


def appendImage(data):
    if (data[2] != '0'):
        ret = '''<td><img src="fail.png" style="width:16px;height:16px"></td>'''
    elif (data[3] != '0'):
        ret = '''<td><img src="warning.png" style="width:16px;height:16px"></td>'''
    else:
        ret = '''<td><img src="pass.png" style="width:16px;height:16px"></td>'''
    return ret

def genTableRows(data, depth):
    ret = ""
    if (depth == 1):
        ret += "<tr class=\"view\">"
        ret += appendImage(data)
    else:
        ret += "<tr class=\"fold\">"
    ret += genTableItem(data)
    ret += "</tr>"
    return ret


def genTableItem(data):
    ret = ""
    for item in data:
        ret += f"<td>{item}</td>"
    return ret


def genHTMLDoc(inFiles, outDir):
    totTestNum = 0
    totFailNum = 0
    totDisabledNum = 0
    reports = ""

    for fName in inFiles:
        fNameOnly = os.path.basename(fName)
        fileXML = elemTree.parse(fName)
        root = fileXML.getroot()
        totTestNum += int(root.attrib['tests'])
        totFailNum += int(root.attrib['failures'])
        totDisabledNum += int(root.attrib['disabled'])
        reports += genTableRows([fNameOnly, root.attrib['tests'], root.attrib['failures'],
                                 root.attrib['disabled'], root.attrib['timestamp']], 1)
        suites = root.findall('./testsuite')
        for suite in suites:
            pass

    reports = genTableRows(["Total", str(totTestNum), str(totFailNum), str(
        totDisabledNum), datetime.now().strftime('%Y-%m-%dT%H:%M:%S')], 1) + reports
    reports = "<tbody>" + reports + "</tbody>"
    htmlDoc = htmlForm.format(report=ReportHeader + reports)
    # print(htmlDoc)
    with open(outDir + "/"+outputFileName, "wb") as writer:
        writer.write(htmlDoc.encode('utf-8'))

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
    shutil.copytree("resources", outputDir)

    # Input folder exist & check at lease one XML file
    if not os.path.isdir(inputDir):
        print(f"Directory \"{inputDir}\" is not exist. Terminate")
        sys.exit(0)

    inputFiles = glob.glob(inputDir + "/*.xml")
    if len(inputFiles) == 0:
        print(f"There is no xml file in \"{inputDir}\". Terminate")

    # Generate HTML Doc from XML files
    genHTMLDoc(inputFiles, outputDir)
