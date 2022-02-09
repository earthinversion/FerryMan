df = pd.read_csv("Solenopsis invicta.csv",
                 skiprows = 1,
                encoding="iso-8859-1")
plt.figure(figsize=(10,10))
m = Basemap(projection='cyl', resolution = 'l',
    llcrnrlat=-90, urcrnrlat=90,llcrnrlon=-180,urcrnrlon=180)
lon = df["Longitude"]
lat = df["Latitude"]
lon_ = [];lat_ = []
for x, y in zip(lon,lat):
    try:
        xx, yy = m(float(x),float(y))
        lon_.append(xx);lat_.append(yy)
    except:
        pass
m.scatter(lon_, lat_, marker = "o" ,s=15, c="r" , edgecolors = "k", alpha = 1)
m.drawcoastlines()
plt.title('Fire ant occurence')
plt.show()
