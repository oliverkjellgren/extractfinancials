import extract_financials as ef 
import PyPDF2 as pypdf
from bs4 import BeautifulSoup

data = {}


n_3 = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 1/184622-23/Annual Returns and Balance Sheet eForms/Form AOC-4(XBRL)-05102018_signed%05-10-2018.pdf'
pi = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 1/161456-32/Annual Returns and Balance Sheet eForms/Form 23AC-121007%12-10-2007.pdf'
n_4 = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 5/129225-97/Annual Returns and Balance Sheet eForms/Form23AC-310114 for the FY ending on-310312%31-01-2014.pdf'

new_year = ef.DataExtration.from_filepath(n_3)
with open(new_year.get_filepath(),'rb') as open_pdf:
    pdf_file_reader_object=pypdf.PdfFileReader(open_pdf,strict=False)
    pdf_object = ef.PdfSetup(pdf_file_reader_object)
    try:
        xfa = ef.findInDict('/XFA',pdf_file_reader_object.resolvedObjects)
        xml = pdf_object.xfa_extractor(xfa)
        base_soup = BeautifulSoup(xml,'lxml')
        financials_year_xml = new_year.extractxfa(base_soup)
        form_data = pdf_file_reader_object.getFormTextFields()
        financials_year_form = new_year.extractform(form_data)
    except:
        form_data = pdf_file_reader_object.getFormTextFields()
        financials_year_xml = {}
        financials_year_form = new_year.extractform(form_data)
    

    if len(financials_year_xml) > len(financials_year_form):
        financials_data = ef.DataTypeUpdate.update_data(financials_year_xml)
    else:
        financials_data = ef.DataTypeUpdate.update_data(financials_year_form)

    if len(financials_data) < 2:
        print("No Good Data")
    print(len(financials_data))


