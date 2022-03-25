# Description

This repository helps filling out physical attributes of chemical compounds in the [dueperthal-connect app](https://app.dueperthal-connect.com) by loading the necessery data via the official [CAS API](https://commonchemistry.cas.org/api-overview?utm_source=eloqua&utm_campaign=Common%20chemistry%20follwup&utm_content=button&elqTrackId=44b6650cb0294583893c77bfe57d704a&elq=2d2b809e5a364bf9a0bd39ec9ea5aaaa&elqaid=2695&elqat=1&elqCampaignId=) and inserting them via [Selenium](https://www.selenium.dev/).

# Setup

1. install python 3 (should come with pip)
2. run `pip install -r requirements.txt` from inside the repository root directory to install dependencies
3. copy the `credentials.py.template` to `credentials.py` and fill in your loign credentials for the [dueperthal-connect app](https://app.dueperthal-connect.com)

# Execution

3. start scrypt via commandline with `python script.py` or **double click**
4. in the terminal type the **cas number** (regex: '[\d-]*') of the chemical compound you want to add
5. the script creates a new item and fills the data retrieved from the [CAS API](https://commonchemistry.cas.org/api-overview?utm_source=eloqua&utm_campaign=Common%20chemistry%20follwup&utm_content=button&elqTrackId=44b6650cb0294583893c77bfe57d704a&elq=2d2b809e5a364bf9a0bd39ec9ea5aaaa&elqaid=2695&elqat=1&elqCampaignId=)
6. manually insert whats missing
7. save