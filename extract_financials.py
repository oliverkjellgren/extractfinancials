import re
from datetime import datetime
import logging

# Dictionary containing the searchable values if using the xml/beautifulsoup form of extraction
HUMAN_EXTRACTION_XFA = {
    'YEAR':['to_date_cr','frm:curreportingdate','frcurreportingdatem:','frm:currfiyrtill','frm:currfiyrdateto','fy_end_date'],
    'REVENUE':['total_revenue_cr','frm:curtotalrev'],
    'MATERIAL_COST':['cost_material_cr','frm:curmaterialcost'],
    'AMORTIZATION_AND_DEPRECIATION':['deprectn_amort_c','deprectn_amort_c','frm:curdepamortexpense','frm:curdeprecatn'],
    'FINANCE_EXPENSE':['finance_cost_cr','frm:curfinancecost'],
    'OTHER_EXPENSES':['other_expenses_c'],
    'TOTAL_EXPENSES':['total_expenses_c','frm:curtotalexpenses'],
    'PROFIT_BEFORE_TAX':['profit_bef_tax_c','frm:curprofitbfrtax'],
    'CURRENT_TAX':['current_tax_cr','frm:curcurrenttax'],
    'DEFERRED_TAX':['deferred_tax_cr','frm:curdeferredtax'],
    'PROFIT_LOSS':['prof_loss_oper_c','frm:curprofitorlossfrmco','frm:curprofit_loss','prof_los_12_15_c'],
    'RETAINED_EARNINGS':['reserve_surplus1','frm:currsrvandsurplus','frm:curreservsurplus'],
    'SHARE_CAPITAL':['share_capital_cr','frm:cursharecptl','frm:curpaidupcaptl','frm:curshrarecptl'],
    'LONG_TERM_BORROWINGS':['long_term_borr_c','frm:curlngtermborrow'],
    'DEFERRED_TAX_LIABILITIES_NET':['deferred_tl_cr','frm:curdefrdtaxliabilities','frm:curdeftaxliab'],
    'OTHER_LONG_TERM_LIABILITIES':['other_lng_trm_cr','frm:curothrlngtrmborrow'],
    'LONG_TERM_PROVISIONS':['long_term_prov_c','frm:curlngtermprovisions'],
    'SHORT_TERM_DEBT':['short_term_bor_c','frm:curshorttermborrow'],#'total_st_borr_cr',
    'ACCOUNTS_PAYABLE':['trade_payables_c','frm:curtradepayables'],
    'OTHER_CURRENT_LIABILITIES':['other_curr_lia_c','frm:curothrcrntliabilities'],
    'SHORT_TERM_PROVISIONS':['short_term_pro_c','frm:curshorttermprovisions'],
    'TANGIBLE_ASSETS':['tangible_asset_c','frm:curtangibleassets'],
    'INTANGIBLE_ASSETS':['intangible_ast_c','frm:curintangibleassets'],
    'CAPITAL_WORK_IN_PROGRESS':['capital_wip_cr','frm:curcapitalwip'],
    'INTANGIBLE_ASSETS_UNDER_DEVELOPMENT':['intangible_aud_c','frm:curintangibleasstsindev'],
    'NON_CURRENT_INVESTMENTS':['non_curr_inv_cr','frm:curnoncrntinvstmnt'],
    'DEFERRED_TAX_ASSETS_NET':['deferred_ta_cr','frm:curdeftaxassetsnet'],
    'LONG_TERM_LOANS_ADVANCES':['lt_loans_adv_cr','frm:curlongtermloans'],
    'OTHER_NON_CURRENT_ASSETS':['other_non_ca_cr','frm:curothrnoncrntassets'],
    'CURRENT_INVESTMENTS':['current_inv_cr','frm:curinvestment'],
    'INVENTORIES':['inventories_cr','frm:curinventories','frm:curinventries'],
    'ACCOUNTS_RECEIVABLES':['trade_receiv_cr','frm:curtradereceivables','frm:cursundrydebtrs'],
    'CASH':['cash_and_equ_cr','frm:curcastandeqvlnts','frm:curcshbnkbalnce'],
    'LOANS_AND_ADVANCES':['short_trm_loa_cr','frm:curshrttermloans'],
    'OTHER_CURRENT_ASSETS':['other_curr_ca_cr','frm:curothrcrntassets','frm:curothrassts'],
    'TOTAL_ASSETS':['total_curr_rep','frm:curassetstotal']
              }

# Dictionary containing the searchable values if using the method .getFormTextFields()
HUMAN_GET_FORM_TEXT_FIELDS_DICTIONARY = {
    'YEAR':['EndCurrDate_D[0]','DateOfFinancialYrTo_D[0]','BalanceShtFromDate[0]','ToDate[0]','HiddenBalsheetDate_D[0]','HiddenBalDate_D[0]'],
    'REVENUE':['CurTotalRev[0]','TotalCurrIncom_N[0]'],
    'MATERIAL_COST':['CurMaterialCost[0]'],
    'AMORTIZATION_AND_DEPRECIATION':['DepreAmorCurr_N[0]','DeprAmorCurr_N[0]','CurDepAmortExpense[0]'],
    'FINANCE_EXPENSE':['InterestCurr_N[0]','CurFinanceCost[0]'],
    'OTHER_EXPENSES':['CurOthrExpenses[0]','CurTotalExpenses[0]'],
    'TOTAL_EXPENSES':['TotalExpCurr_N[0]'],
    'PROFIT_BEFORE_TAX':['TotalCurrIncome_N[0]','CurProfitBfrTax[0]'],
    'CURRENT_TAX':['IncomeTDefTCurr_N[0]'],
    'DEFERRED_TAX':[],
    'PROFIT_LOSS':['CurProfit_Loss[0]'],
    'RETAINED_EARNINGS':['ReservesSurpCur_N[0]','CurRsrvAndSurplus[0]','ResSur[0]'],
    'SHARE_CAPITAL':['ShareCap[0]','TotPaidCap[0]','Total1Curr_N[0]'],
    'LONG_TERM_BORROWINGS':['LongTerm[0]','CurLngTermBorrow[0]'],
    'DEFERRED_TAX_LIABILITIES_NET':['DefLiabl[0]','CurDefrdTaxLiabilities[0]'],
    'OTHER_LONG_TERM_LIABILITIES':['LongLiabl[0]','CurOthrLngTrmBorrow[0]'],
    'LONG_TERM_PROVISIONS':['CurLngTermProvisions[0]','LongProv[0]'],
    'SHORT_TERM_DEBT':['ShortBorrow[0]','CurShortTermBorrow[0]'],
    'ACCOUNTS_PAYABLE':['CurTradePayables[0]','Trade[0]'],
    'OTHER_CURRENT_LIABILITIES':['CurrentLiabl[0]','CurOthrCrntLiabilities[0]'], #could be wrong
    'SHORT_TERM_PROVISIONS':['ShortProv[0]','CurShortTermProvisions[0]'],
    'TANGIBLE_ASSETS':['TangAsset[0]','CurTangibleAssets[0]'],
    'INTANGIBLE_ASSETS':['IntangAsset[0]','CurIntangibleAssets[0]'],
    'CAPITAL_WORK_IN_PROGRESS':['CapWIPCurr_N[0]','CapWork[0]','CurCapitalWIP[0]'],
    'INTANGIBLE_ASSETS_UNDER_DEVELOPMENT':[],
    'NON_CURRENT_INVESTMENTS':['NonCurrent[0]','CurNonCrntInvstmnt[0]','InvestmentCurr_N[0]'],
    'DEFERRED_TAX_ASSETS_NET':['DeffTaxAsstCurr_N[0]','DefTax[0]','CurDefTaxAssetsNet[0]'],
    'LONG_TERM_LOANS_ADVANCES':['LoansAdvCurr_N[0]','LongLoan[0]','CurLongTermLoans[0]'],
    'OTHER_NON_CURRENT_ASSETS':['CurOthrNonCrntAssets[0]','OtherAsset[0]','OthersCurr_N[0]'],
    'CURRENT_INVESTMENTS':[],
    'INVENTORIES':['CurInventories[0]','Inventory[0]','InventoriesCurr_N[0]'],
    'ACCOUNTS_RECEIVABLES':['ShortLoan[0]','CurTradeReceivables[0]'],
    'CASH':['CashBankBalCurr_N[0]','CurCastAndEqvlnts[0]','Cash[0]'],
    'LOANS_AND_ADVANCES':['ShortLoan[0]','CurShrtTermLoans[0]'],
    'OTHER_CURRENT_ASSETS':['OtherAsset[0]','CurOthrCrntAssets[0]'],
    'TOTAL_ASSETS':['CurAssetsTotal[0]','TotalCurr_N[0]']}

#Blank dictionaries one for XFA and one for Forms
XFA_ = {}
GET_FORM_TEXT_FIELDS_DICTIONARY = {}

#Putting the human readable dictionary into XFA_
for i in HUMAN_EXTRACTION_XFA.items():
    line_item_title = i[0]
    line_item_values = i[1]
    for values in line_item_values:
        #print(line_item_title,values)  
        XFA_[values] = line_item_title

#Putting the human readable dictionary into GET_FORM_TEXT_FIELDS_DICTIONARY
for i in HUMAN_GET_FORM_TEXT_FIELDS_DICTIONARY.items():
    line_item_title = i[0]
    line_item_values = i[1]
    for values in line_item_values:
        #print(line_item_title,values)  
        GET_FORM_TEXT_FIELDS_DICTIONARY[values] = line_item_title

# Creates an object from inputting thefilepath 
class FinancialYear:
    def __init__(self,pbid,year,file_path):
        self.__pbid = pbid
        self.__year = year
        self.__filepath =  file_path
    
    def set_pbid(self, pbid):
        self.__pbid = pbid

    def set_year(self,year):
        self.__year = year

    def get_year(self):
        return self.__year

    def get_pbid(self):
        return self.__pbid
    
    def get_filepath(self):
        return self.__filepath
  
    @classmethod
    def from_filepath(cls,file_path):
        pbid = re.findall('[0-9][0-9][0-9]+\-[0-9][0-9]',file_path)[0]
        year = re.findall('[0-9][0-9]\-[0-9][0-9]\-[0-9][0-9][0-9][0-9]',file_path)[0]
        year = datetime.strptime(year, '%d-%m-%Y')
        return cls(pbid,year,file_path)

# Used to define the PDF and ensure the same format   
class PdfSetup:
    def __init__(self,pdf_reader):
        self.__pdf = pdf_reader 

    # Function determines if we need to extract the data through the xml function or the form function 
    # DEPRICATED function no Longer in use because sometimes the .getFormTextFields returns a dictionary but fields are not labeled. 
        # Using the xml/beautifulsoup method is much more accurate and comprehensive   
    def pdf_type(xfa_data):
        if xfa_data == None:
            document_type = 'form'
        else:
            document_type = 'xml'
        return document_type  
    
    # Function returns the proper version of XML data. Data is only contained in 7 or 11, comparing amount of data in each response to return the best result
    def xfa_extractor(self,xfa_base):
        seven = xfa_base[7].getObject().getData()
        eleven =  xfa_base[11].getObject().getData()
        if len(seven) > len(eleven):
            xml = seven
        else:
            xml = eleven
        return xml

# Class is used to extract financials either in xfa or .getFormTextFields style 
# The format of data (xfa vs. .getFormTextFields) depends on how old the document is  
class DataExtration(FinancialYear):
    # A large portion of the documets contain data in xml format where it is needed to grab data using beautifulsoup 
    # Taking the beautifulsoup data and iterating through possible bs4 search names & adding non-null values into a dictionary   
    def extractxfa(self,soup):
        financial_year = {}
        for financial_line_items in XFA_.items():
            searchable_value = financial_line_items[0]
            soup_values = soup.findAll(searchable_value)
            for value in soup_values:
                if value.text != '':
                    column = financial_line_items[1] #updated
                    financial_item =  value.text
                    financial_year[column] = financial_item
        return financial_year 

    # Some entities data is only able to be extracted through pypdf's .getFormTextFields 
    # the key is an item we are looking for/matches EX_GETTEXT dictionary and the value we receive is not == None
    def extractform(self,form_dictionary):
        financial_year = {}
        for value in form_dictionary.items():
            if value[0] in GET_FORM_TEXT_FIELDS_DICTIONARY.keys() and not re.search('None',str(value[1])):
                line_item = GET_FORM_TEXT_FIELDS_DICTIONARY[value[0]]
                financial_year[line_item] = value[1]
        return financial_year

# Updates a variable data type   
class DataType: 
    #Turn all financial figures into int data type 
    def non_year(non_year):
        #some values come with commas 
        int_ = str(non_year)
        int_ = int(float(int_.replace(',','')))
        value = int(float(int_))
        return value
    
    #Turn date into datetime
    def year(dictionary_year):
        if re.search('-',dictionary_year):
            #searching for the financial format YYYY-MM-DD since some pdf's include seconds 
            year = re.findall('[0-9]*\-[0-9][0-9]\-[0-9][0-9]',dictionary_year)[0]
            value = datetime.strptime(year, '%Y-%m-%d')
        elif re.search('/',dictionary_year):
            sp = dictionary_year.split('/')
            if sp[0] > sp[1]:
                value = datetime.strptime(dictionary_year, '%d/%m/%Y')
            elif sp[0] < sp[1]:
                value = datetime.strptime(dictionary_year, '%m/%d/%Y')
            elif sp[0] == sp[1]:
                value = datetime.strptime(dictionary_year, '%m/%d/%Y')
            else:
                logging.debug("Year Exception occurred",exc_info=True)
        else:
            logging.debug("Exception occurred",exc_info=True)
        return value

# Updates an entire dictionary values into the correct data type using methods from the DataType class
class DataTypeUpdate():
    
    def update_data(financial_dictionary):
        updated_financial_dictionary = {}   
        for item in financial_dictionary.items():
            if item[0] == 'YEAR':
                dict_value = DataType.year(item[1])
            else:
                dict_value = DataType.non_year(item[1])
            updated_financial_dictionary[item[0]] = dict_value
        return updated_financial_dictionary

# Search through underlying data for /XFA items
def findInDict(needle, haystack):
    for key in haystack.keys():
        try:
            value=haystack[key]
        except:
            continue
        if key==needle:
            return value
        if isinstance(value,dict):            
            x=findInDict(needle,value)            
            if x is not None:
                return x


if __name__=="__main__":
    pass




