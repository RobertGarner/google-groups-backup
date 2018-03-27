from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pickle
import json
import pathlib
import os

def move_to_download_folder(downloadPath, folder_path, filename, file_extension, foldername, i):  
    if filename == '':
        oldfilename = 'missing_filename'
        newfilename = foldername + '_' + str(i)
    else:
        oldfilename = filename
        newfilename = filename    
    # New File
    oldfile = download_path + '\\' + oldfilename + file_extension
    # print('oldfile', type(oldfile), oldfile)

    # Old File
    # newfile = folder_path / pathlib.Path(newFileName + file_extension)
    newfile = folder_path + '\\' + newfilename + file_extension
    # print('newfile', type(newfile), newfile)
    
    print("\t\tMoving {} to {}".format(oldfile, newfile))
    # Move File
    for _ in range(20):
        try: 
            os.rename(oldfile, newfile)
            break
        except Exception as e:
            print(e)
            print("File has not finished downloading")
            time.sleep(1)    


def setup_chrome_driver(download_path, username=None, password=None):
    ChromeOptions = webdriver.ChromeOptions()
    ChromeOptions.add_argument('--disable-browser-side-navigation')
    prefs = {'download.default_directory' : download_path}
    ChromeOptions.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome('chromedriver.exe', chrome_options=ChromeOptions)

    if os.path.exists('cookies.pkl'):
        driver.get('http://google.com/')
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        time.sleep(1)        
        return driver
    else:
        driver.get('https://accounts.google.com/signin/v2/identifier?hl=EN&flowName=GlifWebSignIn&flowEntry=ServiceLogin')        
        if username != None or password != None:
            driver.find_element_by_id("identifierId").send_keys(username)
            driver.find_element_by_id("identifierNext").click()
            time.sleep(2)
            driver.find_element_by_name("password").send_keys(password)
            element = driver.find_element_by_id('passwordNext')
            driver.execute_script("arguments[0].click();", element)
            time.sleep(1)
            pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))    
        else:
            print("Username/Password incorrect")   
        return driver


def find_conversation_urls(driver, google_group_url, url_file=None):
    driver.get(google_group_url)
    time.sleep(2)
    driver.refresh()
    time.sleep(2)

    # Scroll to bottom of list
    elm = driver.find_element_by_tag_name('html')
    for x in range(10):
        elm.send_keys(Keys.END)
        time.sleep(2)
    p = driver.find_elements_by_xpath("//*[contains(@id,'l_topic_title_')]")
    
    links = []
    if url_file != None:
        f = open(url_file, 'w')
        for x in p:
            links += x.get_attribute("href")
            f.write("%s\n" % x.get_attribute("href"))
        f.close()
    else:
        for x in p:
            links += x.get_attribute("href")
    return links


def import_conversation_urls(driver, url_file):
    with open(url_file) as f:
        content = f.readlines()
    return [x.strip('\n') for x in content] 


def open_all_posts(driver, link):
    print("\tOpening all posts")
    print("\t\tGetting Page")    
    driver.get(link)
    time.sleep(7)
    
    print("\t\tFinding Table Element")
    table_element = driver.find_element_by_class_name('F0XO1GC-mb-N')

    # Open all posts
    print("\t\tFind all posts")
    posts = table_element.find_elements_by_class_name('F0XO1GC-nb-W')

    print("\t\tOpening all closed posts")
    for x in table_element.find_elements_by_class_name('F0XO1GC-nb-v'):
        x.click()
    return table_element


def download_archive(driver, linklist, message_archive, download_files=False):
    if os.path.exists(message_archive) == False:
        data = {}
        with open(message_archive, 'w') as f:
            json.dump(data, f)        
    
    j = 1
    for link in linklist:
        print("Archiving conversation at {}".format(link))
        table_element = open_all_posts(driver, link)
        download_conversations(driver, link, table_element, j, message_archive)
        if download_files == True:
            download_attachments(driver, link, table_element)
        print("\tDone.")
        j = j + 1


def download_conversations(driver, link, table_element, j, message_archive):
    posts = table_element.find_elements_by_class_name('F0XO1GC-nb-F')
    newdata = {}
    content = []
    messagesDict = {}
    i = 1

    print("\tMining data from posts...")
    for x in posts:
        messageDict = {}
        try:
            messageDict['poster'] = x.find_element_by_class_name('_username').text
        except: 
            print('Error finding poster')
            messageDict['poster'] = 'none'    
        try:
            messageDict['date'] = x.find_element_by_class_name('F0XO1GC-b-Cb').text
        except:
            print('Error finding date')
            messageDict['date'] = 'none'
        try:
            messageDict['other-recipients'] = x.find_element_by_class_name('F0XO1GC-nb-q').text
        except:
            print('Error finding other-recipients')
            messageDict['other-recipients'] = 'none'
        try:
            messageDict['content'] = x.find_element_by_class_name('F0XO1GC-nb-P').text
        except:
            try:
                messageDict['content'] = x.find_element_by_class_name('F0XO1GC-nb-C').text 
                print('Deleted message found')  
            except:
                print('Error finding message contents')         
        messagesDict.update({'message' + str(i): messageDict})
        i = i + 1        
    
    print("\t\tWriting Data to dictionary...")
    threadDict = {"url": link, "subject": driver.find_element_by_id('t-t').text, "messages": messagesDict}
    # print(threadDict)
    newdata['thread' + str(j)] = threadDict

    
    # print(newdata)
    with open(message_archive) as f:
        data = json.load(f)

    data.update(newdata)

    print("\t\tSaving json...")
    with open(message_archive, 'w') as f:
        json.dump(data, f)    
    time.sleep(2)
    # print("Done...", link, j)


def download_attachments(driver, link, table_element):
        
        posts = table_element.find_elements_by_class_name('F0XO1GC-uc-c')
        if posts:
            print("\tAttachments Found. Downloading...")
            # path = pathlib.Path(r'C:\Users\Robert Garner\Documents\repos\Google_groups_scrape\Downloads\\' + link[-11:])
            folder_path = download_path  + '\\' +  link[-11:]
            pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True) 
            # print('folder_path:', type(folder_path), folder_path)
            # print(posts)
            # y = []
            i = 0
            for x in posts:
                # print(x)
                # print(x.find_elements_by_class_name('F0XO1GC-uc-d'))
                time.sleep(1)
                filename, file_extension = os.path.splitext(x.find_element_by_class_name('F0XO1GC-uc-d').text)
                print('\t\tAttachment filename: {} '.format(filename))
                print('\t\tAttachment file extension: {}'.format(file_extension))
                click_element = x.find_element_by_partial_link_text('Download')
                driver.execute_script("arguments[0].click();", click_element)
                time.sleep(3)
                
                move_to_download_folder(download_path, folder_path, filename, file_extension, link[-11:], i)

                i = i + 1


if __name__ == '__main__':
    # Setup Selenium Driver, and configure download directory if required
    # print(os.getcwd())
    download_path = os.getcwd() + r'\Downloads'
    print('download_path', download_path)
    driver = setup_chrome_driver(download_path)
    
    linklist = find_conversation_urls(driver,'https://groups.google.com/forum/#!forum/cantera-users','conversation_urls.txt')
    #linklist = import_conversation_urls(driver,'conversation_urls.txt')

    download_archive(driver, linklist, 'backup.json', True)
    driver.quit()