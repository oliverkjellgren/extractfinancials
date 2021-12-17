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
for key, value in HUMAN_EXTRACTION_XFA.items(): #items iterates though dict and unpack key value pairs as tuples
    for v in value:
        #print(line_item_title,values)  
        XFA_[v] = key

#Putting the human readable dictionary into GET_FORM_TEXT_FIELDS_DICTIONARY
for key, value in HUMAN_GET_FORM_TEXT_FIELDS_DICTIONARY.items():
    for v in value:
        #print(line_item_title,values)  
        GET_FORM_TEXT_FIELDS_DICTIONARY[v] = key

# Creates an object from inputting thefilepath 
class FinancialYear:
    def __init__(self,pbid,year,file_path):
        self.__pbid = pbid
        self.__year = year
        self.__filepath = file_path
    
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
    def from_filepath(cls ,file_path: str):  #use type hinting when you can, make code more readable and will throw error if a worng data type comes through
        #if you are finding all and getting the first one, just use find
        pbid = re.find(r'\d{3}+\-\d{2}',file_path)  #r before the string designates it as regular expression
        year = re.findall(r'[0-9][0-9]\-[0-9][0-9]\-[0-9][0-9][0-9][0-9]',file_path)[0]
        year = datetime.strptime(year, '%d-%m-%Y')
        return cls(pbid,year,file_path)

# Used to define the PDF and ensure the same format   
class PdfSetup:
    def __init__(self,pdf_reader):
        self.__pdf = pdf_reader 

    # Some filings the xml data is not available. If the data is not avialable then we only want to use form method  
    # Using the xml/beautifulsoup method is much more accurate and comprehensive   
    #ADD TO THIS - IF pdf.getFormTextFields() = {} then form
    def pdf_type(xfa_data):
        #below is how documentation should look, you can get an extention to generate these automatically
        """[Summary]

        Args:
            xfa_data ([type]): [description]

        Returns:
            [type]: [description]
        """
        if xfa_data:  #no need for == None here, if valiable is an if exists check
            document_type = 'form'
        else:
            document_type = 'both'
        return document_type  
    
    # Function returns the proper version of XML data. Data is only contained in 7 or 11, comparing amount of data in each response to return the best result
    def xfa_extractor(self,xfa_base):
        seven = xfa_base[7].getObject().getData()
        eleven =  xfa_base[11].getObject().getData()
        # personally dont like assigning useless varibles, except for better readability
        if len(seven) > len(eleven):
            return seven
        else:
            return eleven

# Class is used to extract financials either in xfa or .getFormTextFields style 
# The format of data (xfa vs. .getFormTextFields) depends on how old the document is  
class DataExtration(FinancialYear):
    # A large portion of the documets contain data in xml format where it is needed to grab data using beautifulsoup 
    # Taking the beautifulsoup data and iterating through possible bs4 search names & adding non-null values into a dictionary   
    def extractxfa(self,soup):
        financial_year = {}
        for key, value in XFA_.items(): # again here items returns an iterator of (key), (value)
            #searchable_value = financial_line_items[0]  # this is redundant varible assignment, just use the variable from the for loop
            # soup_values = soup.findAll(key)  #even this isnt nessecary as you dont use the list oter than the for loop below
            for value in soup.findAll(key):
                if value.text != '':
                    #column = financial_line_items[1] #updated
                    #financial_item =  value.text
                    financial_year[value] = value.text
        return financial_year 

    # Some entities data is only able to be extracted through pypdf's .getFormTextFields 
    # the key is an item we are looking for/matches EX_GETTEXT dictionary and the value we receive is not == None
    def extractform(self,form_dictionary):
        financial_year = {}
        for key, value in form_dictionary.items():
            if key and key in GET_FORM_TEXT_FIELDS_DICTIONARY.keys(): #run exist checks first, if it fails, the second condition will not be checked, saving you the time checking if key in keys
                #line_item = GET_FORM_TEXT_FIELDS_DICTIONARY[value[0]]
                financial_year[GET_FORM_TEXT_FIELDS_DICTIONARY[key]] = value
        return financial_year

# Updates a variable data type   
class DataType: 
    #Turn all financial figures into int data type 
    def non_year(non_year):
        #some values come with commas 
        int_ = str(non_year)
        int_ = int(int_.replace(',','')) #could just make it an int unless theres an error coming up I dont know about
        value = int(int_)
        return value
    
    #Turn date into datetime
    def year(dictionary_year):
        if '-' in dictionary_year: #re.search('-',dictionary_year):
            #searching for the financial format YYYY-MM-DD since some pdf's include seconds 
            year = re.find(r'\d*\-\d{2}\-\d{2}',dictionary_year)
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
class DataTypeUpdate:
    
    def update_data(financial_dictionary):
        if financial_dictionary:
            updated_financial_dictionary = {}
            return updated_financial_dictionary
        updated_financial_dictionary = {}   
        for key, value in financial_dictionary.items():
            if key == 'YEAR':
                updated_financial_dictionary[key] = DataType.year(value)
            else:
                updated_financial_dictionary[key] = DataType.non_year(value)
        return updated_financial_dictionary
    
    def results_update(financials_year_xml,financials_year_form):
        if len(financials_year_xml) > len(financials_year_form):
            return financials_year_xml
        #elif len(financials_year_form) > len(financials_year_xml): no need for elif if there is no else case
        else:
            return financials_year_form


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




