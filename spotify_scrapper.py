import re
from logger import get_logger

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from objects import SpotifyMusic


log = get_logger(__name__)


class SpotifyScrapper(Chrome):

    def __init__(self, username=None, password=None):

        options = ChromeOptions()
        options.add_argument('user-data-dir=data_dir') # TEMP

        log.info(f'Running Chrome')

        super().__init__(chrome_options=options)
        self.get('https://accounts.spotify.com/login')

        self.__is_logged = False
        if username or password:
            log.info('Found username and password, trying to login')
            self.login(username, password)
        else:
            log.warning('Not logged in any spotify account')

    def login(self, username, password):
        
        try:
            form_username = self.find_element_by_xpath('//input[@ng-model="form.username"]')
            form_username.send_keys(username)

            form_password = self.find_element_by_xpath('//input[@ng-model="form.password"]')
            form_password.send_keys(password)

            log.debug('Form completed, sending infos')

            form_password.send_keys(Keys.RETURN)

            # TODO: Check if login was valid

        except NoSuchElementException:
            self.__is_logged = True
            log.info('Already logged in, skipping') # TEMP

        try:
            WebDriverWait(self, 10).until(EC.presence_of_element_located(
                (By.XPATH, '//a[@ng-href="https://open.spotify.com"]')
            )).click()
            log.info(f'{"Login Succeded" if not self.__is_logged else "OK"}, loading WebPlayer')
        except:
            # TODO: Not logged? What Exception?
            log.error('Login Failed')
            self.quit()


        





