import time
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import chromedriver_autoinstaller
import edgedriver_autoinstaller

from multiprocessing import Pool, cpu_count


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('로스트아크 길드원 목록 갱신 v1.3.2 by CP개구링')
        grid = QGridLayout()
        self.setLayout(grid)

        grid.addWidget(QLabel('길드명:'), 0, 0)

        self.gname_text = QLineEdit()
        self.gname_text.returnPressed.connect(self.button_event)
        grid.addWidget(self.gname_text, 0, 1)

        search_btn = QPushButton('검색', self)
        search_btn.clicked.connect(self.button_event)
        grid.addWidget(search_btn, 1, 1)

        self.setGeometry(200, 200, 300, 100)
        self.show()

    def button_event(self):
        guild = self.gname_text.text()
        start_time = time.time()

        pool = Pool(processes=cpu_count() * 2)
        pool.map(member_update, getlist(guild))
        pool.close()
        pool.join()
        QMessageBox.information(self, '완료 알림', f'길드원 목록 갱신이 완료되었습니다.\n소요시간: {time.time() - start_time:.2f}초')

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Enter:
            self.button_event()

        elif e.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, e):
        QMessageBox.information(self, '종료 알림', '프로그램이 종료됩니다.')


def getlist(guild_name):
    driver_ver, browser = get_driver_ver()
    driver = getdriver(driver_ver, browser)

    guild_url = 'https://loawa.com/guild/'
    driver.get(guild_url + guild_name)
    guild_soup = BeautifulSoup(driver.page_source, 'html.parser')
    member_list = guild_soup.find_all('table', {'cellpadding': '1', 'style': 'width: 100%; font-size: 13px;'})

    driver.quit()

    return member_list


def get_driver_ver():
    try:
        driver_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
        browser = 0  # chrome의 브라우저 코드 = 0
    except:  # Edge 브라우저가 없는 환경인 경우 --> 크롬으로 대체
        driver_ver = edgedriver_autoinstaller.get_edge_version().split('.')[0]  # Edge 브라우저 드라이버 버전 확인
        browser = 1  # edge의 브라우저 코드 = 1
    # 나중에 할진 모르겠지만.. safari = 2, firefox = 3, opera = 4
    return driver_ver, browser


def member_update(member_list):
    driver_ver, browser = get_driver_ver()
    driver = getdriver(driver_ver, browser, False)
    url = 'https://loawa.com/char/'
    for itr in member_list:
        cname = itr.find('span', {'style': 'font-size: 13px; color: var(--theme-0); letter-spacing: -1px;'}).text.strip()
        driver.get(url + cname)

    driver.quit()


def getdriver(ver, browser_type, needwait=True):
    if browser_type == 0:
        options = webdriver.ChromeOptions()  # 옵션 생성
        options.add_argument('--headless')  # 창 숨기는 옵션 추가
        dc = DesiredCapabilities.CHROME.copy()
        dc['loggingPrefs'] = {'driver': 'OFF', 'server': 'OFF', 'browser': 'OFF'}
        if not needwait:
            dc['pageLoadStrategy'] = 'none'
        try:
            driver = webdriver.Chrome(f'./{ver}/chromedriver', options=options, desired_capabilities=dc)
        except:
            chromedriver_autoinstaller.install(True)
            driver = webdriver.Chrome(f'./{ver}/chromedriver', options=options, desired_capabilities=dc)

    elif browser_type == 1:
        options = webdriver.EdgeOptions()  # 옵션 생성
        options.add_argument('--headless')  # 창 숨기는 옵션 추가
        dc = DesiredCapabilities.EDGE.copy()
        dc['loggingPrefs'] = {'driver': 'OFF', 'server': 'OFF', 'browser': 'OFF'}
        if not needwait:
            dc['pageLoadStrategy'] = 'none'
        try:
            driver = webdriver.Edge(f'./{ver}/msedgedriver', options=options, capabilities=dc)
        except:
            edgedriver_autoinstaller.install(True)
            driver = webdriver.Edge(f'./{ver}/msedgedriver', options=options, capabilities=dc)

    return driver


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.setrecursionlimit(10 ** 6)
    ex = MyApp()
    sys.exit(app.exec_())
