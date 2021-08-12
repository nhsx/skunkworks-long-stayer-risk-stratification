# LTSS REST API

- [All Patient Records](#all-patient-records)
- [Single Patient Record](#single-patient-record)
- [Risk Forecast](#risk-forecast)

**All Patient Records**
----
  Returns the full set of available patient records.

* **URL**
  
  /api/records
  
* **Method:**
  
  `GET`
  
* **URL Params:**
  
  None
  
* **Data Params:**
  
  None
  
* **Success Response:**
  
  * **Code:** 200 <br />
    **Content:** <br />
      ```json
      {
        1: { "AGE_ON_ADMISSION": "25", "PATIENT_GENDER_CURRENT": "1", "DIVISION_NAME_AT_ADMISSION": "medical", ... },
        2: { "AGE_ON_ADMISSION": "41", "PATIENT_GENDER_CURRENT": "2", "DIVISION_NAME_AT_ADMISSION": "surgical", ... }, 
      }
      ```
    
* **Error Response:**
  
  * **Code:** 500 INTERNAL SERVER ERROR <br />
    **Content:** `"Error reading records from file"`
    
* **Example:**
  
  `GET /api/records`

**Single Patient Record**
----
  Returns a single patient record with a defined structure. 

* **URL**
  
  /api/record/:id
  
* **Method:**
  
  `GET`
  
* **URL Params:**
  
  **Required:**
  
    `id=[integer]` - ID of patient record (PoC application uses csv file row number as unique ID)
  
* **Data Params:**
  
  None

* **Success Response:**
  
  * **Code:** 200 <br />
    **Content:** Array of six key:value objects grouping fields in the record based on the class of data. 
    The six objects represent: Personal, Admission, Medical, Medical Codes, Administrative, and Demographic field groups.<br />
      ```json
      [
        {
          "AGE_ON_ADMISSION": "50",
          ...
        },
        {
          "AE_ARRIVAL_MODE": "ambulance",
          ...
        },
        {
          "DIABETES_TYPE": "none",
          ...
        },
        {
          "ALL_DIAGNOSIS_CODES": "101 102 103 104",
          ...
        },
        {
          "ARRIVAL_DAY_OF_THE_WEEK": "sun",
          ...
        },
        {
          "DISTRICT": "gloucester",
          ...
        }
      ]
      ```
    
* **Error Response:**
  
  * **Code:** 500 INTERNAL SERVER ERROR <br />
    **Content:** `"Error reading record at row index :id"`
    
  OR

  * **Code:** 404 NOT FOUND <br />
    **Content:** `"Unable to find record :id"`
    
* **Example:**
  
  `GET /api/record/12`

**Risk Forecast**
----
  Generate a set of predictions for a patient record

* **URL**
  
  /api/forecast
  
* **Method:**
  
  `POST`
  
* **URL Params:**
  
  None
  
* **Data Params:**
  
  **Required:**  
    `record` - Patient record data formatted as one of:  
      (a) Flat object of record field key:value pairs  
      (b) Array of record key:value object groups (matching the response format of the `/api/record/:id` endpoint)

* **Success Response:**
  
  * **Code:** 200 <br />
    **Content:** Patient risk prediction 
      ```json
      { "forecast": true,
        "results": {
          "MOT_DAYS": 2,
          "PERCENTAGE_RISK_CAT": 10,
          "PREDICTED_LOS": 1.054377638734,
          "RISK_BY_CATEGORY": {
            "AE_ARRIVAL_MODE": 1,
            "AE_ATTENDANCE_CATEGORY_CODE": 1,
            ...},
          "RISK_CAT_PROB_GENERAL_1": 0.5658058885022558,
          "RISK_CAT_PROB_GENERAL_2": 0.09146923120698841,
          "RISK_CAT_PROB_GENERAL_3": 0.04818847735792024,
          "RISK_CAT_PROB_GENERAL_4": 0.011120232152941771,
          "RISK_CAT_PROB_GENERAL_5": 0.0628401526005759,
          "RISK_STRATIFICATION": 2
        }
      }
      ```
  
  OR

  * **Code:** 200 <br />
    **Content:** No-forecast response for out of scope (non-major) cases
      ```json
        {
          "forecast": false,
          "msg": "Proof of concept system does not issue predictions for non-major cases"
        }
      ```
    
* **Error Response:**
  * **Code:** 400 BAD REQUEST <br />
    **Content:** `"Request body missing"`
    
  OR

  * **Code:** 500 INTERNAL SERVER ERROR <br />
    **Content:** `"Error processing record"`
    
  OR
  
  * **Code:** 500 INTERNAL SERVER ERROR <br />
    **Content:** `"Error formatting data for prediction"`
    
  OR

  * **Code:** 500 INTERNAL SERVER ERROR <br />
    **Content:** `"Error predicting against length of stay model"`
    
  OR

  * **Code:** 500 INTERNAL SERVER ERROR <br />
    **Content:** `"Error predicting against risk model"`
    
* **Example:**

  ```shell
  POST /api/forecast
  [
    {
      "AGE_ON_ADMISSION": "50",
      ...
    },
    {
      "AE_ARRIVAL_MODE": "ambulance",
      ...
    },
    {
      "DIABETES_TYPE": "none",
      ...
    },
    {
      "ALL_DIAGNOSIS_CODES": "101 102 103 104",
      ...
    },
    {
      "ARRIVAL_DAY_OF_THE_WEEK": "sun",
      ...
    },
    {
      "DISTRICT": "gloucester",
      ...
    }
  ]
  ```
  
  OR

  ```shell
  POST /api/forecast
  {
    "AGE_ON_ADMISSION": "50",
    "AE_ARRIVAL_MODE": "ambulance",
    "DIABETES_TYPE": "none",
    "ALL_DIAGNOSIS_CODES": "101 102 103 104",
    "ARRIVAL_DAY_OF_THE_WEEK": "sun",
    "DISTRICT": "gloucester",
    ...
  }
  ```
