import csv
import time
import datetime
from selenium import webdriver


class FootballDatabaseCrawler:
    """

    """
    def __init__(self, csv_filename, webdriver_path, start_year, end_year=int(datetime.datetime.now().year), branch_url='', read_csv_file=False, retry_period=30, retrial_limit=3):
        """

        :param csv_filename:
        :param webdriver_path:
        :param start_year:
        :param end_year:
        :param branch_url:
        :param read_csv_file:
        """
        self.csv_filename = csv_filename
        self.webdriver_path = webdriver_path
        self.start_year = start_year
        self.end_year = end_year
        self.base_url = 'http://www.footballdb.com/scores/index.html?lg=NFL'
        self.branch_url = branch_url
        self.read_csv_file = read_csv_file
        self.season_info = list([tuple(('reg', 17)), tuple(('post', 4))])
        if self.read_csv_file:
            self.csv_matrix = self.read_csv(self.csv_filename)
        else:
            self.csv_matrix = list([list(['Date', 'Away Team', 'Home Team', 'Score'])])
        self.retry_period = retry_period
        self.retrial_limit = retrial_limit

    def deploy(self):
        """

        :return:
        """
        driver = webdriver.Chrome(self.get_webdriver_path())
        for year in range(self.start_year, self.end_year + 1):
            for season_type, season_length in self.season_info:
                for week in range(1, season_length + 1):
                    self.set_branch_url(self.create_branch_url(year, season_type, week))
                    url = self.get_base_url() + self.get_branch_url()
                    print(url)
                    driver.get(url)
                    external_div = driver.find_element_by_xpath('//div[@id="leftcol"]')
                    sub_matrix = list(self.compile_sub_matrix(external_div))
                    self.append_sub_matrix(sub_matrix)
        driver.close()

    def create_branch_url(self, year, season_type, week):
        """

        :param year:
        :param season_type:
        :param week:
        :return:
        """
        return '&yr=' + str(year) + '&type=' + str(season_type) + '&wk=' + str(week)

    def compile_sub_matrix(self, external_div):
        """

        :param external_div:
        :return:
        """
        sub_matrix = list([])
        internal_divs = external_div.find_elements_by_xpath('//div')
        dates_divs = external_div.find_elements_by_xpath('//div[@class="divider"]')
        games_divs = external_div.find_elements_by_xpath('//div[@class="section_half"]')
        num_retrials = 0
        last_game_index = 0
        while num_retrials < self.get_retrial_limit():
            successful = False
            try:
                for date_div in dates_divs:
                    if dates_divs.index(date_div) != len(dates_divs) - 1:
                        next_date_div_index = internal_divs.index(dates_divs[dates_divs.index(date_div) + 1])
                    else:
                        next_date_div_index = len(internal_divs)
                    for game_div_index in range(last_game_index, len(games_divs)):
                        internal_game_div_index = internal_divs.index(games_divs[game_div_index])
                        if internal_game_div_index < next_date_div_index:
                            date = str(date_div.text)
                            game_div = games_divs[game_div_index]
                            away_team_div = game_div.find_element_by_xpath('.//tr[2]')
                            home_team_div = game_div.find_element_by_xpath('.//tr[3]')
                            away_team = str(away_team_div.find_element_by_xpath('.//span[@class="hidden-xs"]').text)
                            home_team = str(home_team_div.find_element_by_xpath('.//span[@class="hidden-xs"]').text)
                            away_score = str(away_team_div.find_element_by_xpath('.//td[6]').text)
                            home_score = str(home_team_div.find_element_by_xpath('.//td[6]').text)
                            score = away_score + ' @ ' + home_score
                            successful = True
                        else:
                            last_game_index = game_div_index
                            break
                        current_row = list([date, away_team, home_team, score])
                        sub_matrix.append(list(current_row))
            except Exception as e:
                print('Connection/Timeout/HTML Tree Traversal Error: Retrying in ' + str(self.get_retry_period()) + ' s ...')
                time.sleep(self.get_retry_period())

            if successful:
                break

            num_retrials += 1
        return sub_matrix

    def append_sub_matrix(self, sub_matrix):
        """

        :param sub_matrix:
        :return:
        """
        new_csv_matrix = self.get_csv_matrix()
        new_csv_matrix += sub_matrix
        self.set_csv_matrix(new_csv_matrix)

    def read_csv(self, csv_filename):
        """

        :param csv_filename:
        :return:
        """
        csv_matrix = []  # initialize the matrix
        with open(csv_filename, "r") as csv_file:  # open the file
            csv_reader = csv.reader(csv_file, delimiter=",")  # read the file
            for row in csv_reader:  # for every row, i.e. data field
                csv_matrix.append(list(row))  # append it to the matrix
        return csv_matrix  # return the data matrix

    def write_csv(self, csv_filename):
        """

        :param csv_filename:
        :return:
        """
        with open(csv_filename, "w") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=",")
            for row in self.get_csv_matrix():
                csv_writer.writerow(list(row))

    def set_csv_filename(self, new_csv_filename):
        """

        :param new_csv_filename:
        :return:
        """
        self.csv_filename = new_csv_filename

    def set_webdriver_path(self, new_webdriver_path):
        """

        :param new_webdriver_path:
        :return:
        """
        self.webdriver_path = new_webdriver_path

    def set_start_year(self, new_start_year):
        """

        :param new_start_year:
        :return:
        """
        self.start_year = new_start_year

    def set_end_year(self, new_end_year):
        """

        :param new_end_year:
        :return:
        """
        self.end_year = new_end_year

    def set_branch_url(self, new_branch_url):
        """

        :param new_branch_url:
        :return:
        """
        self.branch_url = new_branch_url

    def set_read_csv_file(self, new_read_csv_file):
        """

        :param new_read_csv_file:
        :return:
        """
        self.read_csv_file = new_read_csv_file

    def set_season_info(self, new_season_info):
        """

        :param new_season_info:
        :return:
        """
        self.season_info = new_season_info

    def set_csv_matrix(self, new_csv_matrix):
        """

        :param new_csv_matrix:
        :return:
        """
        self.csv_matrix = new_csv_matrix

    def set_retry_period(self, new_retry_period):
        """

        :param new_retry_period:
        :return:
        """
        self.retry_period = new_retry_period

    def set_retrial_limit(self, new_retrial_limit):
        """

        :param new_retrial_limit:
        :return:
        """
        self.retrial_limit = new_retrial_limit

    def get_csv_filename(self):
        """

        :return:
        """
        return self.csv_filename

    def get_webdriver_path(self):
        """

        :return:
        """
        return self.webdriver_path

    def get_start_year(self):
        """

        :return:
        """
        return self.start_year

    def get_end_year(self):
        """

        :return:
        """
        return self.end_year

    def get_base_url(self):
        """

        :return:
        """
        return self.base_url

    def get_branch_url(self):
        """

        :return:
        """
        return self.branch_url

    def get_read_csv_file(self):
        """

        :return:
        """
        return self.read_csv_file

    def get_season_info(self):
        """

        :return:
        """
        return self.season_info

    def get_csv_matrix(self):
        """

        :return:
        """
        return self.csv_matrix

    def get_retry_period(self):
        """

        :return:
        """
        return self.retry_period

    def get_retrial_limit(self):
        """

        :return:
        """
        return self.retrial_limit
