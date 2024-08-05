from lxml import etree

def fix_xml(file_path):
    try:
        parser = etree.XMLParser(recover=True)
        with open(file_path, 'rb') as file: 
            xml_content = file.read()
        tree = etree.fromstring(xml_content, parser=parser)
        fixed_xml_content = etree.tostring(tree, pretty_print=True, encoding='utf-8')

        with open(file_path, 'wb') as file:
            file.write(fixed_xml_content)
        print("XML file has been fixed.")
    except Exception as e:
        print(f"An error occurred: {e}")


fix_xml('extracted_files/word/document.xml')
