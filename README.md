# RVA Dashboard Backend
This repository contains the backend code for RVA Dashboard, a free informational resource for the people of Richmond. You can find the code for the frontend [here](https://github.com/rvacivtech/rva_dashboard).  

The backend consists of an open web API built in Python(Flask) and persisting data in Postgresql.  The application is currently deployed to Google Cloud, though we may search around for a new home (once our free credit on Google Cloud runs out).  The URL is https://35.236.207.129/.

## API Endpoints



#### `/api/parcel_summary?address=<required street address>&zip_code=<optional zip code>`
This endpoint only provides information on addresses within the city of Richmond.  The provided street address has a limited ability to handle name variation (e.g. "123 N. Fake St" and "123 North Fake Street" should both work). The zip_code is optional.  The data comes from: https://data.richmondgov.com/Unique-and-Inclusive-Neighborhoods/Parcel-Geographic-Summary/b52i-7ygb.  

This endpoint provide general information about a particular property, including:
  * Census Tract
  * Neighborhood
  * Trash Pickup Day
  * Congressional District
  * City Council District
  * VA State House District
  * Police District
  * School Zones
  * Voter Precinct
  
The information is returned in JSON.  If the provided address is not found is will return a JSON indicating the error.
  
#### `/api/property_assessment?address=<required street address>&zip_code=<optional zip code>`
This endpoint only provides information on addresses within the city of Richmond.  The provided street address has a limited ability to handle name variation (e.g. "123 N. Fake St" and "123 North Fake Street" should both work). The zip_code is optional.  The data comes from: https://data.richmondgov.com/Well-Managed-Government/Property-Assessments-Current/vm9j-9f88

This endpoint provide information related to preperty assessment for taxes, including:
  * Latitude and Longitude
  * Property Owner
  * Square Feet
  * Assessed Value
  
The information is returned in JSON.  If the provided address is not found is will return a JSON indicating the error.
  
#### `/api/slack_invite?email=<required email>`
This endpoint takes an email address (e.g. "user@example.com") and will generate a slack invite for the RVACivTech slack to be sent to the provided email address.  It will return a json indicating if the slack request was successfully sent.

#### `/api/crime-summary?start_date=<optional start date>&end_date=<optional end date>&neighborhood=<optional neighborhood>`
This enpoint will provide the count of reported crimes in all neighborhoods in a given time period (including an entry for the count of all neighborhoods).  This information is updated daily.  The start_date and end_date should be provided in the yyyy-mm-dd format (e.g. `/api/crime-summary?start_date=2018-01-01&end_date=2018-12-31`.  The start_date and end_date are inclusive.  If no dates are provided the endpoint will provide data on the last 365 days.

This endpoint can also take neighborhood arguments, which will limit the response to specific neighborhoods.  If multiple neighborhoods are desired you should enter the `neighborhood` argument more than once (e.g. `/api/crime-summary?neighborhood=westover%20hills&neighborhood=church%20hill`).


## [Resources](https://github.com/rvacivtech/rva_dash/tree/master/resources)  
Examples of local data in use, literature on the topic, etc. I find stuff like this to be really helpful, but understand if its not wanted in a repository.  

## [Dashboard Notes](https://github.com/rvacivtech/rva_dash/blob/master/notes.md)  
These notes should most likely be merged into this file.  

## [Meeting Notes](https://github.com/rvacivtech/rva_dash/blob/master/meeting-notes-2018-12.md)  
From 2018-12, these need to @ least be turned into issues, if not merged here.  

## Dashboard Ideas
* Crime Map and Visualizations
* Trash Pickup Tool
* Voting Location Tool
* Government Contact Page
* Elected Officials Biographies
* Property Values Map and Visualizations
* City Budget Visualizations
* Demographics Map and Visualizations
* Hiking and Biking Trail Map
* City Park Map
* School Districts Tool
* Traffic Accidents Map
