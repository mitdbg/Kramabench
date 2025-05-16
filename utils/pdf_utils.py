import fitz

def Pdf2Txt(filename):
    pdf = fitz.open(filename)
    text_content = ""
    for page in pdf:
        textpage = page.get_textpage()
        page_txt = textpage.extractText()
        text_content += page_txt
    return text_content