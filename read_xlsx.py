import sys
import os

folder = '/Users/dm_chamber/Desktop/경험BRIEF'
files = [f for f in os.listdir(folder) if f.endswith('.xlsx') and '3C4P' in f]
if not files:
    print("File not found")
    sys.exit(1)

target = os.path.join(folder, files[0])

try:
    import pandas as pd
    xls = pd.ExcelFile(target)
    for s in xls.sheet_names:
        print(f'\n--- Sheet: {s} ---')
        df = pd.read_excel(xls, s).fillna('')
        print(df.to_markdown())
except ImportError:
    print("pandas not found, using zipfile")
    import zipfile
    import xml.etree.ElementTree as ET
    
    with zipfile.ZipFile(target, 'r') as z:
        shared_strings = []
        try:
            strings_xml = z.read('xl/sharedStrings.xml')
            root = ET.fromstring(strings_xml)
            for si in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'):
                shared_strings.append(si.text or '')
        except KeyError:
            pass
            
        # Read sheets
        for i in range(1, 10):
            try:
                sheet_xml = z.read(f'xl/worksheets/sheet{i}.xml')
                print(f'\n--- Sheet {i} ---')
                root = ET.fromstring(sheet_xml)
                for row in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                    row_data = []
                    for c in row.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        if v is not None:
                            val = v.text
                            if c.get('t') == 's':
                                val = shared_strings[int(val)]
                            row_data.append(val)
                        else:
                            row_data.append('')
                    if any(row_data):
                        print(' | '.join(str(x).replace('\n', ' ') for x in row_data))
            except KeyError:
                break
