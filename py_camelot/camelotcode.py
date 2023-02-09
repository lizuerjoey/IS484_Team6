### PDF Tables Extraction###

#https://www.youtube.com/watch?v=702lkQbZx50#

#pip install camelot-py
#pip install opencv-python (if no cv2)
#pip install ghostscript
import camelot.io as camelot
import PyPDF2

# import matplotlib

# import ctypes
# from ctypes.util import find_library
# print(find_library("".join(("gsdll", str(ctypes.sizeof(ctypes.c_voidp) * 8), ".dll"))))

#flavour - stream/lattice

#table = camelot.read_pdf("../samples/public/nikon/q4fy2022-financial-data.pdf", pages = '1-end', flavor="stream", edge_tol=100, rol_tol=10)
#table = camelot.read_pdf("../samples/public/nikon/q1fy2023-financial-data.pdf", pages = '1-end', flavor="stream", edge_tol=100)
table = camelot.read_pdf("./upload_files/q1fy2023-financial-data.pdf", pages="1-end")

print("----Number of tables----")
print(len(table))

#export to csv
table.export('export_q1fy2023.csv', f='csv')

#loop through df <--DO THIS-->

# print("----Report----")
# print(table[0].parsing_report)

# print("----Data----")
# print(table[0].df)

#camelot.plot(table[0], process_background=True)

#write to csv -> .to_excel("name.xls")