# stardew_dashboard
This is a Python script that reads the data in a Stardew Valley save file and creates a dashboard of the things I monitor on my farm daily. 

The dashboard can be viewed in a web browser and refreshed after a save file has been updated on a new farm day.

To run the dashboard, replace <path> with the path to your save file in line 43.

Dashboard_Final_Product.png shows what the final product should look like.

The following key Python libraries are used:
- BeautifulSoup is used to parse the save file and extract metrics.
- Plotly is used to create indicator figures for each metric.
- Dash & Dash Bootstrap Components are used to build the dashboard.

If there are metrics you'd like to look for in the save file that I haven't shown in the code, have a look around in the soup. 
Working with the full file soup can be slow as the save file can be quite large. For ease, I filtered to specific blocks of code that contained the data I needed and stored them as separate variables: items, groups, buildings, trees, crops.
- Most items on the farm can be found in items.
- Groups are groups of items based on where they are stored: your backpack, chests, fridges, etc.
- Buildings I filtered to my Deluxe Barns and Deluxe Coops to be able to count the hay in the feeders.
- Trees I filtered to trees with fruit growing on them. 
- Crops I filtered to land with crops growing on it.

You can explore each of these using list comprehension:
  [x.find('name').text for x in items]
