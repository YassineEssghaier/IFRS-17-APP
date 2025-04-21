import pandas as pd
import numpy as np

# Read the CSV files
assumptions = pd.read_csv("sample-Annual_v1_NDP.csv")
parameters = pd.read_csv("Parameters.csv")

# Validation class to handle the checks
class validation:
    def __init__(self, file, parameters):
        
        # Initialize variables and parameters
        self.Parameters = parameters
        self.File1 = file.copy()
        self.File2 = file.copy()
        self.File3 = file.copy()
        date_check = []
        
        # Placeholder for validation checks
        self.checks = []
        self.status = []

        # Cohort date check (e.g., for annual data)
        date = pd.to_datetime(file['Cohort'], format='%d/%m/%Y').dt.month
        if self.Parameters.loc[2, "Selection"] == "Annually":
            if any(date != 12):
                check = "Cohort Dates In-Correctly Specified"
                status = "Failed"
            else:
                check = "Cohort Dates Correctly Specified"
                status = "Passed"
            self.checks.append(check)
            self.status.append(status)
        
        # Handling missing values (NA's)
        self.File1.drop(self.File1.columns[[3,4]], axis=1, inplace=True)
        count_missing = self.File1.isnull().sum().sum()
        if count_missing == 0:
            check = "No Missing Value"
            status = "Passed"
        else:
            check = str(count_missing) + " Missing Values"
            status = "Failed"
        
        self.checks.append(check)
        self.status.append(status)
        
        # Signage checks
        for i in self.File2.loc[self.File2['Key'] == 'MAP003', "Gross_BE"]:
            if i > 1:
                check = "Correct Sign for Expected Premiums (MAP003-Gross)"
                status = "Passed"
            else:
                check = "Incorrect Sign for Expected Premiums (MAP003-Gross)"
                status = "Failed"
            self.checks.append(check)
            self.status.append(status)
        
        for i in self.File2.loc[self.File2['Key'] == 'MAP002', "Gross_Actual_BE"]:
            if i > 1:
                check = "Correct Sign for Actual Premiums (MAP002-Gross)"
                status = "Passed"
            else:
                check = "Incorrect Sign for Actual Premiums (MAP002-Gross)"
                status = "Failed"
            self.checks.append(check)
            self.status.append(status)

        for i in self.File2.loc[self.File2['Key'] == 'MAP012', "Gross_Actual_BE"]:
            if i < 1:
                check = "Correct Sign for Actual BE Cash Outflows (MAP012-Gross)"
                status = "Passed"
            else:
                check = "Incorrect Sign for Actual BE Cash Outflows (MAP012-Gross)"
                status = "Failed"
            self.checks.append(check)
            self.status.append(status)
        
        for i in self.File2.loc[self.File2['Key'] == 'MAP013', "Gross_BE"]:
            if i < 1:
                check = "Correct Sign for Expected BE Cash Outflows (MAP013-Gross)"
                status = "Passed"
            else:
                check = "Incorrect Sign for Expected BE Cash Outflows (MAP013-Gross)"
                status = "Failed"
            self.checks.append(check)
            self.status.append(status)
        
        # Continue checking for other data points, handling 'MAP012', 'MAP013', etc., similarly...

        ## Reinsurance Checks
        for i in self.File2.loc[self.File2['Key'] == 'MAP003', "Reins_BE"]:
            if i > 1:
                check = "Correct Sign for Expected Premiums (MAP003-Reinsurance)"
                status = "Passed"
            else:
                check = "Incorrect Sign for Expected Premiums (MAP003-Reinsurance)"
                status = "Failed"
            self.checks.append(check)
            self.status.append(status)
        
        # Continue checks for reinsurance similarly to the gross checks above...

        # Filter out non-zero values to check signage (Gross and Reinsurance)
        filtered_gross = self.File2.loc[self.File2['Gross_BE'] * self.File2['Gross_RA'] != 0]
        filtered_Reins = self.File2.loc[self.File2['Reins_BE'] * self.File2['Reins_RA'] != 0]
        
        # Check for opposite signs in Gross and Reinsurance data
        opposite_signs_gross = (np.sign(filtered_gross['Gross_BE']) != np.sign(filtered_gross['Gross_RA'])).sum()
        opposite_signs_Reins = (np.sign(filtered_Reins['Reins_BE']) != np.sign(filtered_Reins['Reins_RA'])).sum()
        
        if opposite_signs_gross == 0:
            check = "Correct BEL and RA signage (Gross)"
            status = "Passed"
        else:
            check = f"The dataset has {opposite_signs_gross} set of rows where the Gross BE values have opposite signs as compared to Gross RA (Gross)"
            status = "Failed"
        self.checks.append(check)
        self.status.append(status)
        
        if opposite_signs_Reins == 0:
            check = "Correct BEL and RA signage (Reinsurance)"
            status = "Passed"
        else:
            check = f"The dataset has {opposite_signs_Reins} set of rows where the Gross BE values have opposite signs as compared to Gross RA (Reinsurance)-- Re-check Inputs"
            status = "Failed"
        self.checks.append(check)
        self.status.append(status)
        
        # Grouping data by product and sub-product
        data_dict = {
            'assumption_' + str(i): grp
            for i, grp in self.File3.groupby(['Product', 'Sub-Product'])
        }
        
        # Loop through the groups and check sums for business CSM
        for group in data_dict:
            cohort = data_dict[group]
            sum_gross = cohort.loc[cohort['Key'] == 'MAP002', "Gross_Actual_BE"] + \
                        cohort.loc[cohort['Key'] == 'MAP015', "Gross_Actual_BE"] + \
                        cohort.loc[cohort['Key'] == 'MAP004', "Gross_BE"] + \
                        cohort.loc[cohort['Key'] == 'MAP004', "Gross_RA"] + \
                        cohort.loc[cohort['Key'] == 'MAP004', "Gross_LossC_BE"] + \
                        cohort.loc[cohort['Key'] == 'MAP004', "Gross_LossC_RA"] + \
                        cohort.loc[cohort['Key'] == 'MAP004', "Gross_CSM"]
            sum_Reins = cohort.loc[cohort['Key'] == 'MAP002', "Reins_Actual_BE"] + \
                        cohort.loc[cohort['Key'] == 'MAP015', "Reins_Actual_BE"] + \
                        cohort.loc[cohort['Key'] == 'MAP004', "Reins_BE"] + \
                        cohort.loc[cohort['Key'] == 'MAP004', "Reins_RA"] + \
                        cohort.loc[cohort['Key'] == 'MAP004', "Reins_LossC_BE"] + \
                        cohort.loc[cohort['Key'] == 'MAP004', "Reins_LossC_RA"] + \
                        cohort.loc[cohort['Key'] == 'MAP004', "Reins_CSM"]
            
            if sum_gross.sum() == 0:
                check = "New business CSM (Gross) is correct"
                status = "Passed"
            else:
                check = "New business CSM (Gross) is incorrect"
                status = "Failed"
            self.checks.append(check)
            self.status.append(status)

            if sum_Reins.sum() == 0:
                check = "New business CSM (Reinsurance) is correct"
                status = "Passed"
            else:
                check = "New business CSM (Reinsurance) is incorrect"
                status = "Failed"
            self.checks.append(check)
            self.status.append(status)

        # Combine checks and status into a DataFrame for reporting
        self.checks = pd.DataFrame(self.checks, columns=["Validation Checks"])
        self.status = pd.DataFrame(self.status, columns=["Status"])
        self.validation_table = pd.concat([self.checks, self.status], axis=1)
        
        # Print the results
        passed_count = self.validation_table.loc[self.validation_table['Status'] == "Passed", "Status"].count()
        failed_count = self.validation_table.loc[self.validation_table['Status'] == "Failed", "Status"].count()

        self.print_count_status = f"{passed_count} Validation Checks Passed\n{failed_count} Validation Checks Failed"
        print(self.print_count_status)
        print("\nValidation Checks and Status:")
        print(self.validation_table)

# Run the validation
validation(assumptions, parameters)
