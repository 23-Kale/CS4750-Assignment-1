#Import argparse for easy CLI
import argparse
import json
import sqlite3

#Function to check if the filetypes are correct
def checkFiles(args):
    if not args.names[0].endswith(".json"):
        raise Exception("JSON file not given")
    if not args.names[1].endswith(".sqlite"):
        raise Exception("sqlite Database not given")

#Function to open JSON in read to get information
#Assumption that JSON is in the same folder
def openJSON(args):

    #First check if filetypes are right
    checkFiles(args)
    
    #Open up the json (read by default)
    fileName = args.names[0]
    file = open(fileName, 'r')
    jsonFile = json.load(file)
    
    #Testing if it works like I want it to
    #print(fileJSON["books"])
    
    #Return the json object
    return jsonFile

#Change each json line to a string
#Returned as an array of arrays
def jsonToArray(jsonFile, medium):
    #Resultant array, should be filled with an array for each review, start out as null and fill them in
    result = []
    
    #loop through each review
    for review in jsonFile[medium]:
        #Each review has 6 possible entries
        entry = [None] * 6
        for category in review:
            match category:
                case "title":
                    entry[0] = review[category]  # String, using title as primary key now so title should be first
                case "order":
                    entry[1] = review[category] #int
                case "sandersonCoWrote":
                    entry[2] = review[category] #Boolean (Integer in sqlite3)
                case "goodreadsAverage":
                    entry[3] = review[category] #real number (double)
                case "mcburneyScore":
                    entry[4] = review[category] #Int
                case "mcburneyReview":
                    entry[5] = review[category] #String
                case _:
                    raise Exception("Unknown rating category encountered: " + category)

        result.append(entry)
    return result
    
def chuck_into_database(parsed, medium):
    connection = sqlite3.connect(medium)
    cursor = connection.cursor()

    cursor.execute('CREATE TABLE books(title TEXT PRIMARY KEY,'
                   'orderNumber INT,'
                   'sandersonCoWrote INT,'
                   'goodreadsAverage REAL,'
                   'mcburneyScore INT,'
                   'mcburneyReview TEXT)')
    cursor.executemany("INSERT INTO books VALUES(?, ?, ?, ?, ?, ?)", parsed)

    connection.commit()
    connection.close()

def main():
    ###Throw all underneath into main prolly
    #Parser object
    parser = argparse.ArgumentParser(description = "Insert JSON to database")
    
    #Argument checking the commands
    #Set nargs to 1 to ensure 2 arguments are passed in
    parser.add_argument("names", nargs = 2, metavar = "text", type = str, 
                        help = "Please input json filename and .sqlite database file to write the contents of file to")
    
    #Parse arguments
    args = parser.parse_args()
    
    #Open the JSON 
    jsonFile = openJSON(args)
    
    #Get the array of reviews
    parsed_input = jsonToArray(jsonFile, "books")

    #print parsed_input to check for errors/weird input
    #for i in parsed_input: print(i)
    chuck_into_database(parsed_input, args.names[1])
    print("Data from "+args.names[1]+" written to "+args.names[0]+".sqlite successfully.")

if __name__ == "__main__":
    #Call the main function
    main()
