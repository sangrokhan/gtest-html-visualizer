import sys
import os
import glob
import shutil
import xml.etree.ElementTree as elemTree
from datetime import datetime
import csv

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


def getStatus(data):
    status = "pass"
    if (data[2] != '0'):
        status = "failed"
    elif (data[3] != '0'):
        status = "warning"
    return status


def appendImage(status):
    if (status == "failed"):
        ret = '''<td><img src="fail.png" style="width:16px;height:16px"></td>'''
    elif (status == "warning"):
        ret = '''<td><img src="warning.png" style="width:16px;height:16px"></td>'''
    else:
        ret = '''<td><img src="pass.png" style="width:16px;height:16px"></td>'''
    return ret


def genTableRows(data, status, classes):
    ret = "<tr"
    if (len(classes)):
        ret += " class=\""
        for item in classes:
            ret += item + " "
        ret += "\""
    ret += ">"

#    ret += "<tr class=\"view\">"
    ret += appendImage(status)
#    else:
#        ret += "<tr class=\"fold\">"
    ret += genTableItem(data)
    ret += "</tr>"
    return ret


def genTableItem(data):
    ret = ""
    for item in data:
        ret += "<td>" + item + "</td>"
    return ret


def genHTMLDoc(inFiles, outDir, csvInfo):
    totTestNum = 0
    totFailNum = 0
    totDisabledNum = 0
    reports = ""

    if csvInfo != None:
        fNameOnlyList = []
        for fName in inFiles:
            fNameOnlyList.append(os.path.basename(fName))

        for testName in csvInfo:
            tmpName = testName + ".xml"
            if tmpName not in fNameOnlyList:
                reports += genTableRows([tmpName, "", "", "", "Unknown Error"], "warning", ["error"])

    for fName in inFiles:
        fNameOnly = os.path.basename(fName)
        fileXML = elemTree.parse(fName)
        root = fileXML.getroot()
        totTestNum += int(root.attrib['tests'])
        totFailNum += int(root.attrib['failures'])
        totDisabledNum += int(root.attrib['disabled'])
        data = [fNameOnly, root.attrib['tests'], root.attrib['failures'],
                root.attrib['disabled'], root.attrib['timestamp']]
        status = getStatus(data)
        classes = ["view", status]
        reports += genTableRows(data, status, classes)
        suites = root.findall('./testsuite')
        for suite in suites:
            pass

    data = ["Total", str(totTestNum), str(totFailNum), str(
        totDisabledNum), datetime.now().strftime('%Y-%m-%dT%H:%M:%S')]
    status = getStatus(data)
    classes = [status]
    reports = genTableRows(data, status, classes) + reports
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
    csvInfo = None

    # Setup output folder (check existence & clean up)
    if os.path.isdir(outputDir):
        print("Remove files in the \"" + outputDir + "\"")
        shutil.rmtree(outputDir, ignore_errors=True)
    shutil.copytree("resources", outputDir)

    # Input folder exist & check at lease one XML file
    if not os.path.isdir(inputDir):
        print("Directory \"" + inputDir + "\" is not exist. Terminate")
        sys.exit(0)

    inputFiles = glob.glob(inputDir + "/*.xml")
    if len(inputFiles) == 0:
        print("There is no xml file in \"" + inputDir + "\". Terminate")

    if (len(sys.argv) == 4):
        csvInfo = []
        with open(sys.argv[3]) as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                csvInfo.extend(row)

    # Generate HTML Doc from XML files
    genHTMLDoc(inputFiles, outputDir, csvInfo)
