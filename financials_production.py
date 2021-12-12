import extract_financials as ef 
import PyPDF2 as pypdf
from bs4 import BeautifulSoup
import pandas as pd 
from datetime import date
import logging

FORMAT = '%(asctime)s:%(levelname)s:%(lineno)d:%(message)s'
logging.basicConfig(level=logging.DEBUG, filename='extract_financials.log',format=FORMAT)

# Extracting the financials into dictionary
# Some files through the XML method do not open in pypdf
# If files do not open in pypdf then we can use the form method  
def main(filepath):
    new_year = ef.DataExtration.from_filepath(filepath)
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
        
        
        return financials_data


df = pd.read_excel('12_10_files.xlsx')
main_df = df.iloc[2500:3000]
updated_df = df.iloc[2500:3000]['FILEPATH']

if __name__== "__main__":
    for filepath in updated_df:
        try:
            financials_data = main(filepath)
            # Sometimes the financials_data dictionary only includes year or is empty  
            # This happens if the underlying document doesn't contain any information
            # We do not need to track that 
            if len(financials_data) > 2:
                main_df.loc[main_df['FILEPATH'] == filepath,'FINANCIALS_EXTRACTED'] = True
                main_df.loc[main_df['FILEPATH'] == filepath,'PROCESSED_DATE'] = date.today()
                for datavalues in financials_data.items():
                    main_df.loc[main_df['FILEPATH'] == filepath, datavalues[0]] = datavalues[1]
        except:
            logging.debug(f"Exception occurred at {filepath}",exc_info=True)
    main_df.to_excel('t_Batch.xlsx')