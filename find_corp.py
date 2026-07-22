import xml.etree.ElementTree as ET

tree = ET.parse("CORPCODE.xml")
root = tree.getroot()

target_name = "야놀자"

for company in root.findall("list"):
    name = company.find("corp_name").text
    code = company.find("corp_code").text
    if name == target_name:
        print("찾음! 기업명:", name, "/고유번호:", code)
        break
