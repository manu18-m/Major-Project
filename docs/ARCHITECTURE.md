# System Architecture

User / HSE Analyst
        |
        v
Web Interface
        |
        v
Django Application
        |
        +--> NLP preprocessing
        |
        +--> TF-IDF + Logistic Regression
        |       |
        |       +--> SIF probability
        |
        +--> Precursor keyword/entity extraction
        |
        +--> Life-Saving Rule category mapping
        |
        v
Safety Analytics / Dashboard

For production:
- authorised OIL data source
- expert-labelled SIF dataset
- model validation and monitoring
- authenticated access
- audit logs
- approved IOGP rule mapping
