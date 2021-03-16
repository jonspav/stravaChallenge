import xml.etree.ElementTree as ET
import os
import re
from json import dumps
from pathlib import Path
import urllib.request, json 
import time
import requests
from datetime import datetime
from datetime import date

# Gets the file path
def getFilePath():
    cwd_path = os.path.dirname(os.path.abspath(__file__))
    filePath = cwd_path
    return cwd_path

# Loads data from the config file
def loadSet():
    cvConfigFiletree = ET.parse('cvConfig.xml')
    cvConfigFileroot = cvConfigFiletree.getroot()
    url = [cvConfigFileroot[0][0].text.strip()]
    clubID = [cvConfigFileroot[0][1].text.strip()]
    dataHeader = [cvConfigFileroot[0][2].text.strip()]
    distanceRun = [cvConfigFileroot[0][3].text.strip()]
    distanceWalk = [cvConfigFileroot[0][4].text.strip()]
    distanceBike = [cvConfigFileroot[0][5].text.strip()]
    pageLines = [cvConfigFileroot[0][7].text.strip()]
    client_id = [cvConfigFileroot[0][8].text.strip()]
    client_secret = [cvConfigFileroot[0][9].text.strip()]
    search_term = [cvConfigFileroot[0][10].text.strip()]
    return url, clubID, dataHeader, distanceRun, distanceWalk, distanceBike, pageLines, client_id, client_secret, search_term

def returnTheDate():
    now = date.today()
    full = "-" + str(now.day) + "-" + str(now.month) +"-" + str(now.year)
    return full

def writeDataToFile(dWalk,dRun,dRide):

    #Create the fileName
    date = returnTheDate()
    file_name = 'myfile' + date + '.txt'
    print(file_name)

    # if file dosn't exist create - it will be created
    # if file name exists - over wright 
    file=open(file_name,"w")

    #Write race data to file
    dataToFile = "Walk:"+ str(dWalk)+" Run:"+str(dRun)+" Ride:"+str(dRide)
    file.write(dataToFile)
    
    #Close the file
    file.close()

def outputTotals(dWalk,dRun,dRide):
            print("Totals --- Walk Distance: ",dWalk, " Run Distance: ",dRun," Total Run/Walk=",dWalk+dRun, "Ride Distance: ",dRide, " Total KM:", dWalk+dRun+dRide)
            print("Totals --- Walk Distance: ",(dWalk)/1000*0.621371, " Run Distance: ",dRun/1000*0.621371)
            print("Total Run/Walk=",dWalk+dRun/1000*0.621371, "Ride Distance: ",dRide/1000*0.621371, " Total Miles:", (dWalk+dRun+dRide)/1000*0.621371)


def refreshTokens(strava_tokens, access_token,client_secret,client_id):
    # Make Strava auth API call with current refresh token
    response = requests.post(
    url = 'https://www.strava.com/oauth/token',
        data = {
               'client_id': client_id,
               'client_secret': client_secret,
               'grant_type': 'refresh_token',
               'refresh_token': strava_tokens['refresh_token']
                }
              )

    # Save response as json in new variable
    new_strava_tokens = response.json()
    # Save new tokens to file
    with open('strava_tokens.json', 'w') as outfile:
        json.dump(new_strava_tokens, outfile)
        # Use new Strava tokens from now
        strava_tokens = new_strava_tokens
        access_token=strava_tokens['access_token']
    return access_token


# Main program. 
def main():

    try:
        #load data from config file 
        url, clubID, dataHeader, distanceRun, distanceWalk, distanceBike, pageLines, client_id, client_secret, search_term = loadSet()
        print (dataHeader)
        dRun = float(distanceRun[0])
        dWalk = float(distanceWalk[0])
        dRide = float(distanceBike[0])
        pLines = str(pageLines[0])
        client_id = str(client_id[0])
        client_secret = str(client_secret[0])
        search_term = str(search_term[0])

        with open('strava_tokens.json') as json_file:
            strava_tokens = json.load(json_file)

        file_path = getFilePath()
        access_token=strava_tokens['access_token']
         
        # If access_token has expired then use the refresh_token to get the new access_token
        if strava_tokens['expires_at'] < time.time():
            print("TOKEN - expired")

            try:
                #Refresh tokens
                access_token = refreshTokens(strava_tokens, access_token,client_secret,client_id)
 
            except:
                print("Program was unable to refresh token.")


        # build the URL             
        urlApi = url[0].strip()+clubID[0].strip()+"/activities?access_token="+access_token+"&per_page="+pLines

        # Grab the data using the URL
        with urllib.request.urlopen(urlApi) as url:
            data = json.loads(url.read().decode())
            
            #######################################
            # Write Data to File if/when needed
            #######################################

            #file=open("testDataFile.txt","w")

            ##Write race data to file
            #dataToFile = json.dumps(data)
            #file.write(dataToFile)
    
            ##Close the file
            #file.close()

            # Get/check number of lines fetched
            length = len(data)
            
            # Loop through the lines and add up distances for Walk, Run and Ride
            for x in range(0,length):
            #for name in data['name']:
            #    printx['name']

            #for x in data:
                if re.search(search_term,data[x]["name"]) or re.search(search_term.lower(),data[x]["name"]):

                    #Check if Walk/Run/Ride and total up
                    if re.search('Walk',data[x]["type"]):
                        print(" --- ", data[x]["athlete"]["firstname"], ", ",data[x]["name"], ", -Walk- " ,", Distance:",",", data[x]["distance"])
                        dWalk = dWalk + data[x]["distance"]

                    if re.search('Run',data[x]["type"]):
                        print(" --- ", data[x]["athlete"]["firstname"], ", ",data[x]["name"], ", -Run- " ,", Distance:",",",  data[x]["distance"])
                        dRun = dRun + data[x]["distance"]

                    if re.search('Ride',data[x]["type"]):
                        print(" --- ", data[x]["athlete"]["firstname"], ", ",data[x]["name"], ", -Ride- " ,", Distance:",",",  data[x]["distance"])
                        dRide = dRide + data[x]["distance"]
                
                # if the activity hasn't got required ID in the title it will be printed with ELSE  
                #else:
                #    print(" -ELSE- ", "Name: ", data[x]["athlete"]["firstname"], " ", data[x]["name"], " ", data[x]["distance"])
                        
            #Output totals
            outputTotals(dWalk,dRun,dRide)
            
            #Output to file
            writeDataToFile(dWalk,dRun,dRide)

    except:
            print("Program was unable to run.")

if __name__ == "__main__":
    main()
