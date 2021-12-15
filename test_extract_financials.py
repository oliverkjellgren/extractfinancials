import unittest
from datetime import datetime, date
import extract_financials as ef
#import extract_financials as ef 
import PyPDF2 as pypdf
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup


class Testing(unittest.TestCase):
    
    def test_year(self):
        self.assertEqual(ef.DataType.year('2015-03-31T00:00:00+05:30'),
                                         datetime.strptime('2015-03-31','%Y-%m-%d'))
        self.assertEqual(ef.DataType.year('01/03/2016'),#this is wrong M and D are switched
                                          datetime.strptime('01/03/2016','%m/%d/%Y'))
        self.assertEqual(ef.DataType.year('2015-03-31'),
                                          datetime.strptime('2015-03-31','%Y-%m-%d'))
        self.assertEqual(ef.DataType.year('05/05/2016'),
                                          datetime.strptime('05/05/2016','%m/%d/%Y'))

    def test_pdf_type(self):
        form = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 1/161456-32/Annual Returns and Balance Sheet eForms/Form 23AC-121007%12-10-2007.pdf'
        xml = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 5/60912-37/Annual Returns and Balance Sheet eForms/Form AOC-4-051115%05-11-2015.pdf'
        with open(form,'rb') as open_form:
            pdf = pypdf.PdfFileReader(open_form)
            xfa = ef.findInDict('/XFA',pdf.resolvedObjects)
            answer = ef.PdfSetup.pdf_type(xfa)
            self.assertEqual(answer,'form')
        with open(xml,'rb') as open_xml:
            pdf = pypdf.PdfFileReader(open_xml)
            xfa = ef.findInDict('/XFA',pdf.resolvedObjects)
            answer = ef.PdfSetup.pdf_type(xfa)
            self.assertEqual(answer,'xml')

    def test_data_type_update(self):
        pre_update_data = {'YEAR': '2015-03-31', 'REVENUE': '89247314.00000000',
                           'MATERIAL_COST': '0.00000000', 'AMORTIZATION_AND_DEPRECIATION': '3149055.00000000',
                           'FINANCE_EXPENSE': '0.00000000', 'TOTAL_EXPENSES': '71639057.00000000',
                           'PROFIT_BEFORE_TAX': '17608257.00000000', 'CURRENT_TAX': '647199.00000000',
                           'DEFERRED_TAX': '0.00000000', 'PROFIT_LOSS': '16961058.00000000',
                           'RETAINED_EARNINGS': '79911363.00000000', 'SHARE_CAPITAL': '315583.00000000',
                           'LONG_TERM_BORROWINGS': '0.00000000', 'DEFERRED_TAX_LIABILITIES_NET': '0.00000000',
                           'OTHER_LONG_TERM_LIABILITIES': '0.00000000', 'LONG_TERM_PROVISIONS': '2782273.00000000',
                           'SHORT_TERM_DEBT': '0.00000000', 'ACCOUNTS_PAYABLE': '13264842.00000000',
                           'OTHER_CURRENT_LIABILITIES': '5508940.00000000', 'SHORT_TERM_PROVISIONS': '1533416.00000000',
                           'TANGIBLE_ASSETS': '2102353.00000000', 'INTANGIBLE_ASSETS': '751387.00000000',
                           'CAPITAL_WORK_IN_PROGRESS': '0.00000000', 'INTANGIBLE_ASSETS_UNDER_DEVELOPMENT': '32085192.00000000',
                           'NON_CURRENT_INVESTMENTS': '0.00000000', 'DEFERRED_TAX_ASSETS_NET': '0.00000000',
                           'LONG_TERM_LOANS_ADVANCES': '7212497.00000000', 'OTHER_NON_CURRENT_ASSETS': '0.00000000',
                           'CURRENT_INVESTMENTS': '23726679.00000000', 'INVENTORIES': '0.00000000',
                           'ACCOUNTS_RECEIVABLES': '22529421.00000000', 'CASH': '5173988.00000000',
                           'LOANS_AND_ADVANCES': '2544171.00000000', 'OTHER_CURRENT_ASSETS': '7190729.00000000',
                           'TOTAL_ASSETS': '103316417.00000000'}
        year = datetime.strptime('31/03/2015','%d/%m/%Y')
        post_update_data = {'YEAR':year,'REVENUE': 89247314,
                            'MATERIAL_COST': 0, 'AMORTIZATION_AND_DEPRECIATION': 3149055,
                            'FINANCE_EXPENSE': 0, 'TOTAL_EXPENSES': 71639057,
                            'PROFIT_BEFORE_TAX': 17608257, 'CURRENT_TAX': 647199,
                            'DEFERRED_TAX': 0, 'PROFIT_LOSS': 16961058,
                            'RETAINED_EARNINGS': 79911363, 'SHARE_CAPITAL': 315583,
                            'LONG_TERM_BORROWINGS': 0, 'DEFERRED_TAX_LIABILITIES_NET': 0,
                            'OTHER_LONG_TERM_LIABILITIES': 0, 'LONG_TERM_PROVISIONS': 2782273,
                            'SHORT_TERM_DEBT': 0, 'ACCOUNTS_PAYABLE': 13264842,
                            'OTHER_CURRENT_LIABILITIES': 5508940, 'SHORT_TERM_PROVISIONS': 1533416,
                            'TANGIBLE_ASSETS': 2102353, 'INTANGIBLE_ASSETS': 751387,
                            'CAPITAL_WORK_IN_PROGRESS': 0, 'INTANGIBLE_ASSETS_UNDER_DEVELOPMENT': 32085192,
                            'NON_CURRENT_INVESTMENTS': 0, 'DEFERRED_TAX_ASSETS_NET': 0,
                            'LONG_TERM_LOANS_ADVANCES': 7212497, 'OTHER_NON_CURRENT_ASSETS': 0,
                            'CURRENT_INVESTMENTS': 23726679, 'INVENTORIES': 0,
                            'ACCOUNTS_RECEIVABLES': 22529421, 'CASH': 5173988,
                            'LOANS_AND_ADVANCES': 2544171, 'OTHER_CURRENT_ASSETS': 7190729,
                            'TOTAL_ASSETS': 103316417} 
        financials_data = ef.DataTypeUpdate.update_data(pre_update_data)
        self.assertEqual(post_update_data,financials_data)
        
    def test_aoc4(self):
        aoc4 = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 5/60912-37/Annual Returns and Balance Sheet eForms/Form AOC-4-051115%05-11-2015.pdf'
        aoc_base = datetime.strptime('31/03/2015','%d/%m/%Y')
        aoc_data= {'YEAR': aoc_base,
                'REVENUE': 89247314, 'MATERIAL_COST': 0, 
                'AMORTIZATION_AND_DEPRECIATION': 3149055, 
                'FINANCE_EXPENSE': 0, 'TOTAL_EXPENSES': 71639057,
                'PROFIT_BEFORE_TAX': 17608257, 'CURRENT_TAX': 647199,
                'DEFERRED_TAX': 0, 'PROFIT_LOSS': 16961058,
                'RETAINED_EARNINGS': 79911363,'SHARE_CAPITAL': 315583,
                'LONG_TERM_BORROWINGS': 0,'DEFERRED_TAX_LIABILITIES_NET': 0,
                'OTHER_LONG_TERM_LIABILITIES': 0, 'LONG_TERM_PROVISIONS': 2782273,
                'SHORT_TERM_DEBT': 0, 'ACCOUNTS_PAYABLE': 13264842,
                'OTHER_CURRENT_LIABILITIES': 5508940, 'SHORT_TERM_PROVISIONS': 1533416,
                'TANGIBLE_ASSETS': 2102353, 'INTANGIBLE_ASSETS': 751387,
                'CAPITAL_WORK_IN_PROGRESS': 0, 'INTANGIBLE_ASSETS_UNDER_DEVELOPMENT': 32085192,
                'NON_CURRENT_INVESTMENTS': 0, 'DEFERRED_TAX_ASSETS_NET': 0,
                'LONG_TERM_LOANS_ADVANCES': 7212497, 'OTHER_NON_CURRENT_ASSETS': 0,
                'CURRENT_INVESTMENTS': 23726679, 'INVENTORIES': 0,
                'ACCOUNTS_RECEIVABLES': 22529421, 'CASH': 5173988,
                'LOANS_AND_ADVANCES': 2544171, 'OTHER_CURRENT_ASSETS': 7190729,
                'TOTAL_ASSETS': 103316417}
        new_year = ef.DataExtration.from_filepath(aoc4)
        pdfobject2=open(new_year.get_filepath(),'rb')
        pdf2=pypdf.PdfFileReader(pdfobject2,strict=False) 

        pdf_object = ef.PdfSetup(pdf2)

        try:
            xfa = ef.findInDict('/XFA',pdf2.resolvedObjects)
            xml = pdf_object.xfa_extractor(xfa)
            base_soup = BeautifulSoup(xml,'lxml')
            financials_year = new_year.extractxfa(base_soup)
            form_data = pdf2.getFormTextFields()
            financials_year2 = new_year.extractform(form_data)
        except:
            form_data = pdf2.getFormTextFields()
            financials_year = {}
            financials_year2 = new_year.extractform(form_data)

        #Pulling back the final financials for 
        if len(financials_year) > len(financials_year2):
            d1 = ef.DataTypeUpdate.update_data(financials_year)
        else:
            d1 = ef.DataTypeUpdate.update_data(financials_year2)
        self.assertEqual(d1,aoc_data)

    def test_aoc4_2(self):
        aoc4 = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 2/469654-03/Annual Returns and Balance Sheet eForms/Form AOC-4-02122016_signed%02-12-2016.pdf'
        aoc_base = datetime.strptime('31/03/2016','%d/%m/%Y')
        aoc_data= {'YEAR': aoc_base,'REVENUE': 156602,
                   'MATERIAL_COST': 0, 'AMORTIZATION_AND_DEPRECIATION': 0,
                   'FINANCE_EXPENSE': 0, 'OTHER_EXPENSES': 5694822,
                   'TOTAL_EXPENSES': 9812936, 'PROFIT_BEFORE_TAX': -9656334,
                   'CURRENT_TAX': 0, 'DEFERRED_TAX': 0,
                   'PROFIT_LOSS': -9656334, 'RETAINED_EARNINGS': -9656334,
                   'SHARE_CAPITAL': 100000, 'LONG_TERM_BORROWINGS': 36000000,
                   'DEFERRED_TAX_LIABILITIES_NET': 0, 'OTHER_LONG_TERM_LIABILITIES': 0,
                   'LONG_TERM_PROVISIONS': 0, 'SHORT_TERM_DEBT': 0,
                   'ACCOUNTS_PAYABLE': 96653, 'OTHER_CURRENT_LIABILITIES': 444364,
                   'SHORT_TERM_PROVISIONS': 292794, 'TANGIBLE_ASSETS': 0,
                   'INTANGIBLE_ASSETS': 0, 'CAPITAL_WORK_IN_PROGRESS': 0,
                   'INTANGIBLE_ASSETS_UNDER_DEVELOPMENT': 0, 'NON_CURRENT_INVESTMENTS': 0,
                   'DEFERRED_TAX_ASSETS_NET': 0, 'LONG_TERM_LOANS_ADVANCES': 0,
                   'OTHER_NON_CURRENT_ASSETS': 0, 'CURRENT_INVESTMENTS': 1506602,
                   'INVENTORIES': 0, 'ACCOUNTS_RECEIVABLES': 0,
                   'CASH': 1316466, 'LOANS_AND_ADVANCES': 0,
                   'OTHER_CURRENT_ASSETS': 24454409, 'TOTAL_ASSETS': 27277477}
        new_year = ef.DataExtration.from_filepath(aoc4)
        pdfobject2=open(new_year.get_filepath(),'rb')
        pdf2=pypdf.PdfFileReader(pdfobject2,strict=False) 

        pdf_object = ef.PdfSetup(pdf2)

        try:
            xfa = ef.findInDict('/XFA',pdf2.resolvedObjects)
            xml = pdf_object.xfa_extractor(xfa)
            base_soup = BeautifulSoup(xml,'lxml')
            financials_year = new_year.extractxfa(base_soup)
            form_data = pdf2.getFormTextFields()
            financials_year2 = new_year.extractform(form_data)
        except:
            form_data = pdf2.getFormTextFields()
            financials_year = {}
            financials_year2 = new_year.extractform(form_data)

        #Pulling back the final financials for 
        if len(financials_year) > len(financials_year2):
            d1 = ef.DataTypeUpdate.update_data(financials_year)
        else:
            d1 = ef.DataTypeUpdate.update_data(financials_year2)
        self.assertEqual(d1,aoc_data)   

    def test_aca(self):
        aca = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 7/124248-52/Annual Returns and Balance Sheet eForms/Form 23ACA-261006%26-10-2006.pdf'
        aca_date = datetime.strptime('31/03/2006','%d/%m/%Y')
        aca_data = {'REVENUE': 2391935, 'YEAR': aca_date,
                    'PROFIT_BEFORE_TAX': 450856, 'FINANCE_EXPENSE': 1305,
                    'AMORTIZATION_AND_DEPRECIATION': 162397, 'TOTAL_EXPENSES': 1941078,
                    'CURRENT_TAX': 173296} 
        new_year = ef.DataExtration.from_filepath(aca)
        pdfobject2=open(new_year.get_filepath(),'rb')
        pdf2=pypdf.PdfFileReader(pdfobject2,strict=False) 

        pdf_object = ef.PdfSetup(pdf2)
        try:
            xfa = ef.findInDict('/XFA',pdf2.resolvedObjects)
            xml = pdf_object.xfa_extractor(xfa)
            base_soup = BeautifulSoup(xml,'lxml')
            financials_year = new_year.extractxfa(base_soup)
            form_data = pdf2.getFormTextFields()
            financials_year2 = new_year.extractform(form_data)
        except:
            form_data = pdf2.getFormTextFields()
            financials_year = {}
            financials_year2 = new_year.extractform(form_data)

            #Pulling back the final financials for 
        if len(financials_year) > len(financials_year2):
            d1 = ef.DataTypeUpdate.update_data(financials_year)
        else:
            d1 = ef.DataTypeUpdate.update_data(financials_year2)
        self.assertEqual(d1,aca_data)

    def test_ac(self):
        ac = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 6/233565-58/Annual Returns and Balance Sheet eForms/Form23AC-211113 for the FY ending on-310313%21-11-2013.pdf'
        ac_date = datetime.strptime('31/03/2013','%d/%m/%Y')
        ac_data = {'YEAR': ac_date, 'RETAINED_EARNINGS': 30946816,
                   'SHARE_CAPITAL': 5600000, 'LONG_TERM_BORROWINGS': 14005070,
                   'DEFERRED_TAX_LIABILITIES_NET': 0, 'OTHER_LONG_TERM_LIABILITIES': 4504200,
                   'LONG_TERM_PROVISIONS': 0, 'SHORT_TERM_DEBT': 0,
                   'ACCOUNTS_PAYABLE': 2249204, 'OTHER_CURRENT_LIABILITIES': 0,
                   'SHORT_TERM_PROVISIONS': 2598502, 'TANGIBLE_ASSETS': 0,
                   'INTANGIBLE_ASSETS': 49398339, 'CAPITAL_WORK_IN_PROGRESS': 0,
                   'INTANGIBLE_ASSETS_UNDER_DEVELOPMENT': 0, 'NON_CURRENT_INVESTMENTS': 688554,
                   'DEFERRED_TAX_ASSETS_NET': 2422697, 'LONG_TERM_LOANS_ADVANCES': 0,
                   'OTHER_NON_CURRENT_ASSETS': 0, 'CURRENT_INVESTMENTS': 0,
                   'INVENTORIES': 377876, 'ACCOUNTS_RECEIVABLES': 2363202,
                   'CASH': 116216, 'LOANS_AND_ADVANCES': 4536908,
                   'OTHER_CURRENT_ASSETS': 0, 'TOTAL_ASSETS': 59903792}
        new_year = ef.DataExtration.from_filepath(ac)
        pdfobject2=open(new_year.get_filepath(),'rb')
        pdf2=pypdf.PdfFileReader(pdfobject2,strict=False) 

        pdf_object = ef.PdfSetup(pdf2)
        try:
            xfa = ef.findInDict('/XFA',pdf2.resolvedObjects)
            xml = pdf_object.xfa_extractor(xfa)
            base_soup = BeautifulSoup(xml,'lxml')
            financials_year = new_year.extractxfa(base_soup)
            form_data = pdf2.getFormTextFields()
            financials_year2 = new_year.extractform(form_data)
        except:
            form_data = pdf2.getFormTextFields()
            financials_year = {}
            financials_year2 = new_year.extractform(form_data)

            #Pulling back the final financials for 
        if len(financials_year) > len(financials_year2):
            d1 = ef.DataTypeUpdate.update_data(financials_year)
        else:
            d1 = ef.DataTypeUpdate.update_data(financials_year2)
        self.assertEqual(d1,ac_data)

    def test_get_forms(self):
        get_forms = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 1/161457-31/Annual Returns and Balance Sheet eForms/Form 23AC-191108%18-11-2008.pdf'
        base_year = datetime.strptime('31/03/2006','%d/%m/%Y')
        data = {'YEAR': base_year, 'CAPITAL_WORK_IN_PROGRESS': 0,
                'NON_CURRENT_INVESTMENTS': 600000, 'DEFERRED_TAX_ASSETS_NET': 0,
                'CASH': 149703, 'LONG_TERM_LOANS_ADVANCES': 2014400,
                'INVENTORIES': 0, 'AMORTIZATION_AND_DEPRECIATION': 0,
                'RETAINED_EARNINGS': 0, 'SHARE_CAPITAL': 6057375,
                'TOTAL_ASSETS': 6057375}
        new_year = ef.DataExtration.from_filepath(get_forms)
        pdfobject2=open(new_year.get_filepath(),'rb')
        pdf2=pypdf.PdfFileReader(pdfobject2,strict=False) 

        pdf_object = ef.PdfSetup(pdf2)

        try:
            xfa = ef.findInDict('/XFA',pdf2.resolvedObjects)
            xml = pdf_object.xfa_extractor(xfa)
            base_soup = BeautifulSoup(xml,'lxml')
            financials_year = new_year.extractxfa(base_soup)
            form_data = pdf2.getFormTextFields()
            financials_year2 = new_year.extractform(form_data)
        except:
            form_data = pdf2.getFormTextFields()
            financials_year = {}
            financials_year2 = new_year.extractform(form_data)

        #Pulling back the final financials for 
        if len(financials_year) > len(financials_year2):
            d1 = ef.DataTypeUpdate.update_data(financials_year)
        else:
            d1 = ef.DataTypeUpdate.update_data(financials_year2)
        self.assertEqual(d1,data)

if __name__ == '__main__':
    unittest.main()