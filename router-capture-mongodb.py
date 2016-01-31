#!/usr/bin/env python

# Extract Draytek router ADSL Status and store in MongoDB

# http://www.draytek.co.uk/support/guides/kb-dsl-status-more
    
import telnetlib
import time
import pymongo
import datetime
import re

print "Starting..."

host = "192.168.1.1"
user = ""
password = ""

def fetchStatus():

    tn = telnetlib.Telnet(host)

    tn.read_until("Account:")

    print 'Found Account'

    tn.write(user + "\n")
    if password:
        tn.read_until("Password: ")
        print 'Found Password'
        tn.write(password + "\n")

    tn.read_until("> ")
    print 'Found >'

    tn.write("adsl status\n")
    status = tn.read_until("> ")

    tn.write("exit\n")

    tn.close()

    print 'Done'
    
    return status 

def addDocument(collection, status):

    print status

    # extract interesting stats from status text
    m = re.search("State\s+:\s+([A-Z]+)\s+", status)
    state = m.group(1)
    
    m = re.search("Cur SNR Margin\s+:\s+(\d+)\s+dB", status)
    currentSNRMargin = int(m.group(1))
    
    m = re.search("DS Actual Rate\s+:\s+(\d+)\s+bps", status)
    DSActualRate = int(m.group(1))

    m = re.search("US Actual Rate\s+:\s+(\d+)\s+bps", status)
    USActualRate = int(m.group(1))

    m = re.search("NE Current Attenuation\s+:\s+(\d+)\s+dB", status)
    NECurrentAttenuation = int(m.group(1))

    m = re.search("NE CRC Count\s+:\s+(\d+)", status)
    NECRCCount = int(m.group(1))

    m = re.search("NE ES Count\s+:\s+(\d+)", status)
    NEESCount = int(m.group(1))

    m = re.search("FE CRC Count\s+:\s+(\d+)", status)
    FECRCCount = int(m.group(1))

    m = re.search("FE\s+ES Count\s+:\s+(\d+)", status)
    FEESCount = int(m.group(1))
  
    post = {
        "State": state,
        "SNR Margin": currentSNRMargin,
        "DS Actual Rate": DSActualRate,
        "US Actual Rate": USActualRate,
        "NE Current Attenuation": NECurrentAttenuation,
        "NE CRC Count": NECRCCount,
        "NE ES Count": NEESCount,
        "FE CRC Count": FECRCCount,
        "FE ES Count": FEESCount,
        "date": datetime.datetime.utcnow()}

    insert = collection.insert_one(post)
    print insert.inserted_id

    print collection.count()
    
from pymongo import MongoClient
client = MongoClient()

client = MongoClient('mongodb://localhost:27017/')
db = client['Draytek2860']

collection = db['adsl-status']

while True:

    starttime = time.time()

    status = fetchStatus()
    addDocument(collection, status)

    t = ((time.time() - starttime))
    time.sleep(60 - t);
    
