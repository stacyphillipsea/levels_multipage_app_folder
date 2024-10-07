# Welcome to my Read Me doc!

## This is my attempt at making a multi page FETA app

# 16/07/2024
* Initialised the repository. Using existing files, not sure what state they are in and waht problems there are currently
* Tried to use this tutorial but the code doesn't navigate between the pages properly: https://medium.com/@mcmanus_data_works/how-to-create-a-multipage-dash-app-261a8699ac3f
* Installed GitLens extension to help roll back changes
* Current version allows me to navigate between pages and gifs show

* Have successfully copied over the analysis to the common.py and the intro text to the home page. Haven't updated links or changed the header or styling.
* Will now try loading the layout for the charts on the other pages
* Analysis and intro text added successfully
* Imported the same navbar as my levels app
* Images are being correctly pulled from the assets/logos folder into the navbar (and would be pulled into pages too)

* Page 1 loads each component 
* Updated the csv files so that they have the same data as the Levels app so all sites are correctly in there



# 07/10/2024
* Changed the code to get the most recent September 2024 data and run analysis
* Some minor changes to the code but all fine
* Looks to be correctly identifying peaks over 3 possibl periods
* df is saved directly to an Excel file
* App is not deploying properly - I think I'm using the right delpoyment code because it appears in Posit, but is just blank or times out. Could copy the Levels App and try it in there instead