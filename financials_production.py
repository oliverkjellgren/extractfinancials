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
# def main(filepath):
#     new_year = ef.DataExtration.from_filepath(filepath)
#     with open(new_year.get_filepath(),'rb') as open_pdf:
#         pdf_file_reader_object=pypdf.PdfFileReader(open_pdf,strict=False)
#         pdf_object = ef.PdfSetup(pdf_file_reader_object)
#         xfa = ef.findInDict('/XFA',pdf_file_reader_object.resolvedObjects)
#         pdf_extraction_type = ef.PdfSetup.pdf_type(xfa)
#         if pdf_extraction_type == 'form':
#             form_data = pdf_file_reader_object.getFormTextFields()
#             financials_year_form = new_year.extractform(form_data)
#             financials_year_xml = {}
#         elif pdf_extraction_type == 'xml':
#             form_data = pdf_file_reader_object.getFormTextFields()
#             financials_year_form = new_year.extractform(form_data)
#             xml = pdf_object.xfa_extractor(xfa)
#             base_soup = BeautifulSoup(xml,'lxml')
#             financials_year_xml = new_year.extractxfa(base_soup)
#         if len(financials_year_xml) > len(financials_year_form):
#             financials_data = ef.DataTypeUpdate.update_data(financials_year_xml)
#         else:
#             financials_data = ef.DataTypeUpdate.update_data(financials_year_form)

#         return financials_data

def main(filepath):
    new_year = ef.DataExtration.from_filepath(filepath)
    with open(new_year.get_filepath(),'rb') as open_pdf:
        pdf_file_reader_object=pypdf.PdfFileReader(open_pdf,strict=False)
        pdf_object = ef.PdfSetup(pdf_file_reader_object)
        xfa = ef.findInDict('/XFA',pdf_file_reader_object.resolvedObjects)
        pdf_extraction_type = ef.PdfSetup.pdf_type(xfa)
        if pdf_extraction_type == 'form':
            form_data = pdf_file_reader_object.getFormTextFields()
            financials_year_form = new_year.extractform(form_data)
            financials_data = ef.DataTypeUpdate.update_data(financials_year_form)
        elif pdf_extraction_type == 'both':
            form_data = pdf_file_reader_object.getFormTextFields()
            financials_year_form = new_year.extractform(form_data)

            xml = pdf_object.xfa_extractor(xfa)
            base_soup = BeautifulSoup(xml,'lxml')
            financials_year_xml = new_year.extractxfa(base_soup)

            financials_data = ef.DataTypeUpdate.results_update(financials_year_xml,financials_year_form)
            financials_data = ef.DataTypeUpdate.update_data(financials_data)

        return financials_data


# HOW I would do it
if __name__== "__main__":
    df = pd.read_excel('12_10_files.xlsx')  # never have running code that isnt config or global variables outside of main or a method
    main_df = df.iloc[2500:3000]
    updated_df = df.iloc[2500:3000]['FILEPATH']
    for filepath in updated_df:
        try:
            financials_data = main(filepath)
            if len(financials_data) > 2:
                """
                updating dataframes in this way is inefficient, if you think about it, every time you process
                a pdf program has to find the file path in the dataframe, also daframes are not built for iteration
                even though its possible
                
                main_df.loc[main_df['FILEPATH'] == filepath,'FINANCIALS_EXTRACTED'] = True 
                main_df.loc[main_df['FILEPATH'] == filepath,'PROCESSED_DATE'] = date.today()""" #no need to call date.today() every iteration
                for datavalues in financials_data.items():
                    # if you really want to iterate through a df, look into at and use indexing to update values
                    main_df.loc[main_df['FILEPATH'] == filepath, datavalues[0]] = datavalues[1]
        except Exception as e: #log your error
            logging.debug(f"ERROR: {e}; filepath: {filepath}",exc_info=True)
    main_df.to_excel('t_Batch.xlsx')


# how I would do it
if __name__== "__main__":
    df = pd.read_excel('12_10_files.xlsx')
    list_of_rows = df.iloc[2500:3000].to_dict('records') #lists is usually going to be the fastest thing for iteration, makes list of dicts from df
    results = []  # its bad practice to modify data structures that you are iterating over so just add modified rows to result list
    today = date.today()
    for row in list_of_rows:
        try:
            financials_data = main(row['FILEPATH'])
            if len(financials_data) > 2:
                row['FINANCIALS_EXTRACTED'] = True
                row['PROCESSED_DATE'] = today
                for key, val in financials_data.items():
                    row[key] = val
            results.append(row)
        except Exception as e: #log your error
            logging.debug(f"ERROR: {e}; filepath: {filepath}",exc_info=True)
            row['error'] = e  # could put error messages in result or not, personal preference
            results.append(row)
            pass #might as well just keep going and deal with errors after the run
    pd.DataFrame(results).to_excel('t_Batch.xlsx', index=False)