import re
from logger import get_logger

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException
)

from objects import SpotifyMusic


log = get_logger(__name__)


class EC_wait_for_non_empty_text(object):

    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        try:
            element_text = EC._find_element(driver, self.locator).text.strip()
            return element_text != ''
        except StaleElementReferenceException:
            return False


class SpotifyScrapper(Chrome):

    def __init__(self, username=None, password=None):

        options = ChromeOptions()
        options.add_argument('user-data-dir=data_dir')  # TEMP

        log.info('Running Chrome')

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
            form_username = self.find_element_by_xpath(
                '//input[@ng-model="form.username"]'
            )
            form_username.send_keys(username)

            form_password = self.find_element_by_xpath(
                '//input[@ng-model="form.password"]'
            )
            form_password.send_keys(password)

            log.debug('Form completed, sending infos')

            form_password.send_keys(Keys.RETURN)

            # TODO: Check if login was valid

        except NoSuchElementException:
            self.__is_logged = True
            log.info('Already logged in, skipping')  # TEMP

        try:
            WebDriverWait(self, 10).until(EC.presence_of_element_located(
                (By.XPATH, '//a[@ng-href="https://open.spotify.com"]')
            )).click()
            status = 'Login Succeded' if not self.__is_logged else 'OK'
            log.info(f'{status}, loading WebPlayer')
        except Exception:
            # TODO: Not logged? What Exception?
            log.error('Login Failed')
            self.quit()

    def get_playlists(self):

        # TODO: Wait to load
        self.implicitly_wait(5)
        self.playlists = self.find_elements_by_xpath(
            '//a[contains(@href, "/playlist/")]'
        )
        self.playlists = {p.text: p for p in self.playlists}
        self.playlists.update({
            'collection': self.find_element_by_xpath(
                '//a[@href="/collection/tracks"]'
            )
        })

        return self.playlists

    def get_playlist(self, playlist_name):

        self.playlists[playlist_name].click()

        # TODO: Wait to load

        # Get nubmer of tracks
        # TODO: Is There a better way to do this? Probably
        WebDriverWait(self, 10).until(EC_wait_for_non_empty_text(
            (By.XPATH, '(//a[contains(@href, "/user/")])[2]')
        ))
        user = self.find_element_by_xpath(
            '(//a[contains(@href, "/user/")])[2]'
        )
        text = ' '.join(
            el.text for el in
            user.find_elements_by_xpath('./parent::*/span')
        )

        n_tracks_text = re.search(r'([\d\.]+) músicas', text).group(1)
        n_tracks_text = n_tracks_text.replace('.', '')
        n_tracks = int(n_tracks_text)

        log.info(f'There is {n_tracks} in "{playlist_name}" playlist')

        # This part can be optimized, the interchange between
        # js and python was done for learning purposes only :D
        with open('scroll_playlist.js', 'r') as js:
            js_code = js.read()

            # TODO: Check async js
            bottom_sentinel = WebDriverWait(self, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '//div[@data-testid="bottom-sentinel"]'
                ))
            )

            curr_track = 1
            all_tracks = []

            while True:
                WebDriverWait(self, 10).until(EC.presence_of_element_located((
                    By.XPATH,
                    f'//div[@role="row" and @aria-rowindex > {curr_track}]'
                )))

                tracks = self.find_elements_by_xpath(
                    f'//div[@role="row" and @aria-rowindex > {curr_track}]'
                )
                log.debug(f'curr={curr_track-1}, len={len(tracks)}')
                curr_track += len(tracks)
                all_tracks += [SpotifyMusic(t) for t in tracks]

                if curr_track-1 >= n_tracks:
                    break

                self.execute_script(js_code, bottom_sentinel)
                # self.execute_script(
                #     'arguments[0].scrollIntoView();',
                #     bottom_sentinel
                # )

            log.info('Proccess Finished')

            return all_tracks
