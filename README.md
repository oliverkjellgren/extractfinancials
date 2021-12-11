What Is This?:

This is a simple program that reads financial documents from the India government (https://mca.gov.in/) and extracts the meaningful financial line items. These documents (Annual eForms) come in the following names/types: 23AC/23ACA, 23AC-XBRL/23ACA-XBRL, AOC-4 and AOC4-XRBL.   

For more information on filing requirements with the India government please see
1. https://www.mca.gov.in/MinistryV2/annualefiling.html 
2. https://www.mca.gov.in/MinistryV2/annualefilingguidelines.html

Why Was This Built: 

Full income statements on a company's profile is a minimum standard that clients expect when researching private market data in countries that the figures are available (India, United Kingdom, France, ect.).

Currently PitchBook has about 20,000 private companies with a primairy HQ location based in India. Since a researcher can only extract and add financial statements for 30 companies a day it would take 667 FTE days to research financials for every private company in India.  

How This Program Works:
In India, financials are entered through forms and spit out the other end into an XFA version of PDF. These PDF's contain the direct data entered by the company in an XML format stored in the PDF document. This data can be accessed by either searching through the pypdf.resolvedObjects method for XFA items OR using pypdf's .getFormTextFields() method. The .getFormTextFields() method is the less effective way of extracting financials because some financial line items are not named and impossible to search for. 

If the data is available in a beautifulsoup format the .extractxfa() method can be used. This method iterates on a dictionary of possible searchable values for each financial line items and retrieves any that are non-null. 

If it is not possible to extract the XFA/XML data, use the pypdf .getFormTextFields() to retrieve a dictionary of values. This uses the same process as extractxfa().  

