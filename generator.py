import os.path as pt
import pdfkit
import markdown2

def generateFile(text, novelId ):
    filePath = pt.abspath(f'generations/{str(novelId)}.pdf')
    
    #with open(filePath,'wb') as file:
     #   pass
    
    content = markdown2.markdown(text)
    pdfkit.from_string(content, filePath)
        
    return filePath