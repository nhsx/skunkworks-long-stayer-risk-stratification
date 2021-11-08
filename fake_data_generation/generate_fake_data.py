"""
This file generates fake data randomly.
The purpose of this data is to test the running of the models and setup of the repo.
Field values are generated randomly independently of each other.
Instructions on how to run this file can be found in the README.md in this directory.
"""

import argparse
import json
import numpy as np
import pandas as pd
import random

# Get arguments from command line
# (If args are not specified default values will be used.)
parser = argparse.ArgumentParser(
    description="""The purpose of `generate_fake_data.py` is to create a `.csv` file with fake data with the following intended applications: 
    An example of how data needs to be formatted to be passed into the model and to test the setup and running of the repo."""
)

# Args to generate
parser.add_argument(
    "--number_of_records",
    "-nr",
    type=int,
    default=100,
    help="[int] Number of records to generate. Default is 100.",
)
parser.add_argument(
    "--filename",
    "-fn",
    type=str,
    default="fake_data",
    help="""[str] The name of the csv file saved at the end (do not add.csv).
    The default name is set to "fake_data". This will generate a file called "fake_data.csv" . """,
)

parser.add_argument(
    "--only_major_cases",
    "-mc",
    default=False,
    action="store_true",
    help=""" [False - no need to specify, True - specify by just including: --only_major_cases]
    If True all records generated will have major cases listed as 'Y' if False cases will be a mix of 'N' and 'Y'.""",
)

parser.add_argument(
    "--seed",
    "-s",
    default=None,
    type=int,
    help="[int] If specified will ensure result is reproducible. Default is set to None so will generate a different result each time.",
)

# Read arguments from the command line
args = parser.parse_args()

# Set seed if specified:
if args.seed is not None:
    np.random.seed(seed=args.seed)

# Load data_description.json to get columns required for training data
with open("../config/data_description.json", "r") as file:
    data_columns = json.load(file)

# Create dataframe with original data fields
columns = [x.upper() for x in data_columns["Original_Data_Fields"]]
df = pd.DataFrame(columns=columns)

# Load data_categories.json to get the data categories required for each field in the fake data
with open("../config/fake_data_categories.json", "r") as file:
    data_cat = json.load(file)

# Assign data categories to fields in dataframe
for column in columns:
    if column in data_cat.keys():
        df[column] = np.random.choice(data_cat[column], size=args.number_of_records)

# Remaining fields to fill in so they are not null
# fields requiring int:
df["LENGTH_OF_STAY"] = np.random.randint(1, 40, size=(args.number_of_records))
df["LENGTH_OF_STAY_IN_MINUTES"] = df["LENGTH_OF_STAY"] * 24 * 60
df["AGE_ON_ADMISSION"] = np.random.randint(18, 80, size=(args.number_of_records))
df["LOCAL_PATIENT_IDENTIFIER"] = np.random.randint(
    1000, 2000, size=(args.number_of_records)
)
df["CDS_UNIQUE_IDENTIFIER"] = np.random.randint(
    1000, 2000, size=(args.number_of_records)
)
df["PREVIOUS_30_DAY_HOSPITAL_PROVIDER_SPELL_NUMBER"] = np.random.randint(
    1000, 2000, size=(args.number_of_records)
)
df["ED_ATTENDANCE_EPISODE_NUMBER"] = np.random.randint(
    1000, 2000, size=(args.number_of_records)
)
df["UNIQUE_INTERNAL_ED_ADMISSION_NUMBER"] = np.random.randint(
    1000, 2000, size=(args.number_of_records)
)
df["UNIQUE_INTERNAL_IP_ADMISSION_NUMBER"] = np.random.randint(
    1000, 2000, size=(args.number_of_records)
)
df["AE_ATTENDANCE_CATEGORY"] = np.random.randint(1, 3, size=(args.number_of_records))
df["HEALTHCARE_RESOURCE_GROUP_CODE"] = np.random.randint(
    1000, 2000, size=(args.number_of_records)
)
df["PRESENTING_COMPLAINT_CODE"] = np.random.randint(
    1000, 2000, size=(args.number_of_records)
)
df["WAIT"] = np.random.randint(1, 3, size=(args.number_of_records))
df["ALL_INVESTIGATION_CODES"] = np.random.randint(
    1000, 2000, size=(args.number_of_records)
)
df["ALL_DIAGNOSIS_CODES"] = np.random.randint(1000, 2000, size=(args.number_of_records))
df["ALL_TREATMENT_CODES"] = np.random.randint(1000, 2000, size=(args.number_of_records))
df["ALL_BREACH_REASON_CODES"] = np.random.randint(
    1000, 2000, size=(args.number_of_records)
)
df["ALL_LOCATION_CODES"] = np.random.randint(1000, 2000, size=(args.number_of_records))
df["ALL_LOCAL_INVESTIGATION_CODES"] = np.random.randint(
    1000, 2000, size=(args.number_of_records)
)

df["ALL_LOCAL_TREATMENT_CODES"] = np.random.randint(
    1000, 2000, size=(args.number_of_records)
)

df["INITIAL_WAIT"] = np.random.randint(0, 5, size=(args.number_of_records))
df["INITIAL_WAIT_MINUTES"] = np.random.randint(0, 600, size=(args.number_of_records))
df["AE_PATIENT_GROUP_CODE"] = np.random.randint(
    1000, 2000, size=(args.number_of_records)
)
df["AE_INITIAL_ASSESSMENT_TRIAGE_CATEGORY"] = np.random.randint(
    1, 3, size=(args.number_of_records)
)
df["EMCOUNTLAST12M"] = np.random.choice([10, 20, 30], size=args.number_of_records)
df["EL COUNTLAST12M"] = np.random.choice([10, 20, 30], size=args.number_of_records)
df["ED COUNTLAST12M"] = np.random.choice([10, 20, 30], size=args.number_of_records)
df["OP FIRST COUNTLAST12M"] = np.random.choice(
    [10, 20, 30], size=args.number_of_records
)
df["OP FU COUNTLAST12M"] = np.random.choice([10, 20, 30], size=args.number_of_records)
# fields requiring str:
df["DISCHARGE_DATE_HOSPITAL_PROVIDER_SPELL"] = "2122-05-01"
df["DISCHARGE_READY_DATE"] = "2122-05-01"
df["EXPECTED_DISCHARGE_DATE"] = "2122-05-01"
df["EXPECTED_DISCHARGE_DATE_TIME"] = "2122-05-01"
df["FIRST_REGULAR_DAY_OR_NIGHT_ADMISSION_DESCRIPTION"] = "2122-05-01"
df["FIRST_START_DATE_TIME_WARD_STAY"] = "2122-05-01"
df["START_DATE_HOSPITAL_PROVIDER_SPELL"] = "2122-05-01"
df["START_DATE_TIME_HOSPITAL_PROVIDER_SPELL"] = "2122-05-01"
df["TREATMENT_FUNCTION_CODE_AT_ADMISSION_DESCRIPTION"] = "test"
df["PATIENT_GENDER_CURRENT_DESCRIPTION"] = "test"
df["ALL_DIAGNOSES"] = "test"
df["REASON_FOR_ADMISSION"] = "test"
df["ALL_INVESTIGATIONS"] = "test"
df["ALL_DIAGNOSIS"] = "test"
df["ALL_TREATMENTS"] = "test"
df["ALL_LOCAL_INVESTIGATIONS"] = "test"
df["ALL_LOCAL_TREATMENTS"] = "test"
df["PRESENTING_COMPLAINT"] = "test"
df["AE_PATIENT_GROUP"] = "test"
df["OAC GROUP NAME"] = "test"
df["OAC SUBGROUP NAME"] = "test"
df["OAC SUPERGROUP NAME"] = "test"
df["DISTRICT"] = "test"
df["FIRST_WARD_STAY_IDENTIFIER"] = "test"
df["MAIN_SPECIALTY_CODE_AT_ADMISSION_DESCRIPTION"] = "test"
df["PATIENT_CLASSIFICATION_DESCRIPTION"] = "test"
df["SOURCE_OF_ADMISSION_HOSPITAL_PROVIDER_SPELL_DESCRIPTION"] = "test"
df["POST_CODE_AT_ADMISSION_DATE_DISTRICT"] = "PostCode"
# fields requiring float:
df["IMD COUNTY DECILE"] = np.random.choice([0.1, 0.2, 0.3], size=args.number_of_records)

# Ensure all records only show "Y" for is "IS_MAJOR" if args.only_major_cases is True
if args.only_major_cases:
    df["IS_MAJOR"] = "Y"

# Write dataframe to csv
df.to_csv(f"{args.filename}.csv", index=False)

# Message to show script has run
print(
    f"fake data Generated! File saved: {args.filename}.csv with {args.number_of_records} records created. Seed was set to {args.seed}."
)
