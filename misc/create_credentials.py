import os
import random
import string

if __name__ == '__main__':
    path =os.path.join(os.path.expanduser("~"), '.dmd','config',)
    if not os.path.exists(path):
        os.makedirs(path)
    page = open(str(path) + os.sep + 'credentials.txt', "w")
    randomString = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
    strs = [randomString]
    page.writelines(strs)
    page.close()
