import sys, os, mimetypes, concurrent.futures

def resultsSearchFile(filepath, target):
    with open(filepath, "r", encoding="UTF-8") as thefile:
        result, foundOnce = "", False
        try:
            i = 1
            for line in thefile:
                if line.find(target) != -1:
                    if not foundOnce:
                        result += "\n" + os.path.relpath(filepath) + "\n" + "---------------------------------"
                        foundOnce = True
                    result += "\n" + "Line " + str(i) + ": " + "\n" + line + "\n" 
                i += 1
            return result
        except:
            return ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please choose a string to search for")
        raise SystemExit
    directories, filepaths, target = [os.path.abspath(os.getcwd()).replace("\\","/") + "/"], [], sys.argv[1]
    for directory in directories:
        elements = os.listdir(directory)
        for element in elements:
            element = os.path.abspath(directory + element).replace("\\", "/")
            if os.path.isfile(element) and element not in filepaths:
                filepaths.append(element)
            elif os.path.isdir(element) and ".svn" not in element:
                element += "/"
                if element not in directories:
                    directories.append(element)
    filepaths =  [filepath for filepath in filepaths if (filepath.endswith(".swp") is False and filepath.endswith("~") is False)]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        targets = [target for filepath in filepaths]
        for result in executor.map(resultsSearchFile, filepaths, targets):
            if result:
                print(result)
