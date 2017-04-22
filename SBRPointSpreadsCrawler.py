import csv
import random
from time import sleep
from selenium import webdriver


MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
          "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}


class SBRPointSpreadsCrawler:
    """

    """
    def __init__(self, csv_filename, webdriver_path, branch_url='', read_csv_file=False, waiting_time=2):
        """

        :param branch_url:
        """
        self.csv_filename = csv_filename
        self.webdriver_path = webdriver_path
        self.base_url = 'http://www.sportsbookreview.com/betting-odds/'
        self.branch_url = branch_url
        self.read_csv_file = read_csv_file
        if self.read_csv_file:
            self.csv_matrix = self.read_csv(self.csv_filename)
        else:
            self.csv_matrix = list([])
        self.waiting_time = waiting_time

    def deploy(self, date_strings):
        """

        :param date_strings:
        :return:
        """
        csv_matrix = list([])

        casinos_url = self.get_base_url() + self.get_branch_url() \
                      + '?date=' + self.rectify_date_format(date_strings[random.randrange(len(date_strings))])
        casinos = self.extract_casinos(casinos_url)

        heading = list(['Date', 'Teams']) + list(casinos)
        csv_matrix.append(heading)
        for date_string in date_strings:
            print(date_string)
            csv_submatrix = self.point_spreads_scraper(date_string)
            csv_matrix += csv_submatrix
        self.append_to_csv_matrix(csv_matrix)

    def point_spreads_scraper(self, date_string):
        """

        :param date_string:
        :return:
        """
        point_spreads_matrix = list([])
        underdog_bools = list([])

        date = self.rectify_date_format(date_string)

        url = self.get_base_url() + self.get_branch_url() + '?date=' + date
        driver = webdriver.Chrome(self.get_webdriver_path())
        driver.get(url)

        carousel_next_clicks = 3

        carousel_controller = driver.find_element_by_xpath('//div[@class="carousel-control"]')

        point_spreads_table = driver.find_element_by_xpath('//div[@class="section module OddsGridModuleClass "]')

        game_point_spreads = point_spreads_table.find_elements_by_xpath('//div[@class="event-holder holder-complete"]')

        while carousel_next_clicks > 0:
            point_spreads_submatrix = list([])
            for game in game_point_spreads:

                new_driver = webdriver.Chrome(self.get_webdriver_path())
                new_driver.get(url)
                dummy_table = driver.find_element_by_xpath('//div[@class="section module OddsGridModuleClass "]')
                dummy_point_spreads = dummy_table.find_elements_by_xpath('//div[@class="event-holder holder-complete"]')
                dummy_game = dummy_point_spreads[game_point_spreads.index(game)]

                underdog_point_spreads, favorite_point_spreads = list([date]), list([''])
                if carousel_next_clicks >= 3:
                    underdog = self.determine_underdog(url, game_point_spreads.index(game))
                    underdog_bools.append(underdog)
                else:
                    underdog = underdog_bools[game_point_spreads.index(game)]

                teams = dummy_game.find_elements_by_xpath('.//span[@class="team-name"]')
                if underdog:
                    away_team = str(teams[0].text) + ' (Favorite)'
                    home_team = str(teams[1].text) + ' (Underdog)'

                    underdog_point_spreads.append(home_team)
                    favorite_point_spreads.append(away_team)
                else:
                    away_team = str(teams[0].text) + ' (Underdog)'
                    home_team = str(teams[1].text) + ' (Favorite)'

                    underdog_point_spreads.append(away_team)
                    favorite_point_spreads.append(home_team)

                print(away_team, home_team)

                payouts = dummy_game.find_elements_by_xpath('.//div[@class="el-div eventLine-book"]')
                for payout in payouts:
                    away_team_point_spread, home_team_point_spread = \
                        [str(web_element.text) for web_element in payout.
                            find_elements_by_xpath('.//div[@class="eventLine-book-value "]')]

                    away_team_point_spread = self.handle_PK(away_team_point_spread)
                    home_team_point_spread = self.handle_PK(home_team_point_spread)

                    away_team_point_spread = self.extract_line(away_team_point_spread)
                    home_team_point_spread = self.extract_line(home_team_point_spread)

                    if len(away_team_point_spread) == 0 and len(home_team_point_spread) == 0:
                        away_team_point_spread, home_team_point_spread = str(0), str(0)
                    elif len(away_team_point_spread) == 0 and len(home_team_point_spread) != 0:
                        home_team_point_spread = home_team_point_spread.split()[0]
                        away_team_point_spread = str(-float(home_team_point_spread))
                    elif len(away_team_point_spread) != 0 and len(home_team_point_spread) == 0:
                        away_team_point_spread = away_team_point_spread.split()[0]
                        home_team_point_spread = str(-float(away_team_point_spread))
                    else:
                        away_team_point_spread = away_team_point_spread.split()[0]
                        home_team_point_spread = home_team_point_spread.split()[0]

                    if underdog:
                        underdog_point_spreads.append(home_team_point_spread)
                        favorite_point_spreads.append(away_team_point_spread)
                    else:
                        underdog_point_spreads.append(away_team_point_spread)
                        favorite_point_spreads.append(home_team_point_spread)

                if carousel_next_clicks >= 3:
                    point_spreads_submatrix.append(underdog_point_spreads)
                    point_spreads_submatrix.append(favorite_point_spreads)
                else:
                    point_spreads_submatrix.append(underdog_point_spreads[2:])
                    point_spreads_submatrix.append(favorite_point_spreads[2:])

                point_spreads_submatrix.append(list([]))

                new_driver.close()

            if carousel_next_clicks >= 3:
                point_spreads_matrix += point_spreads_submatrix
            else:
                for idx in range(len(point_spreads_submatrix)):
                    point_spreads_matrix[idx] = point_spreads_matrix[idx] + point_spreads_submatrix[idx]

            self.click_next(carousel_controller)
            carousel_next_clicks -= 1

        driver.close()

        return point_spreads_matrix

    def extract_casinos(self, url):
        """

        :param url:
        :return:
        """
        casinos = list([])
        carousel_next_clicks = 3
        driver = webdriver.Chrome(self.get_webdriver_path())
        driver.get(url)
        carousel_controller = driver.find_element_by_xpath('//div[@class="carousel-control"]')
        while carousel_next_clicks > 0:
            casinos_row = driver.find_element_by_xpath('//div[@class="carousel-bookslist"]')
            casino_elements = casinos_row.find_elements_by_tag_name('li')
            casino_names = [str(casino.text) for casino in casino_elements if str(casino.text) != '']
            casinos += casino_names
            self.click_next(carousel_controller)
            carousel_next_clicks -= 1
        driver.close()
        return casinos

    def determine_underdog(self, url, game_index):
        """

        :param url:
        :param game_index:
        :return:
        """
        driver = webdriver.Chrome(self.get_webdriver_path())
        driver.get(url)

        carousel_controller = driver.find_element_by_xpath('//div[@class="carousel-control"]')

        game_odds = driver.find_elements_by_xpath('//div[@class="event-holder holder-complete"]')

        game = game_odds[game_index]

        carousel_next_clicks = 3
        carousel_page = 0

        while carousel_next_clicks > 0:
            first_refreshed_page_game_odds = driver.find_elements_by_xpath \
                ('//div[@class="event-holder holder-complete"]')
            first_refreshed_game = first_refreshed_page_game_odds[game_odds.index(game)]

            casinos_info = first_refreshed_game.find_elements_by_xpath \
                ('.//div[@class="el-div eventLine-book"]')

            if carousel_next_clicks == 0:
                casinos_info = casinos_info[len(casinos_info) - 2:]

            for casino_info in casinos_info:
                upper_row, lower_row = casino_info.find_elements_by_xpath \
                    ('.//div[@class="eventLine-book-value "]')
                try:
                    line_value = self.extract_line(self.handle_PK(lower_row.text)).split()

                    if len(line_value) == 0:
                        continue

                    if float(line_value[0]) > 0:
                        driver.close()
                        return True
                    elif float(line_value[0]) < 0:
                        driver.close()
                        return False

                except Exception as exception:
                    print('Exception encountered! Moving to next casino to determine underdog...')
                    print('\n')
            self.click_next(carousel_controller)
            carousel_next_clicks -= 1
            carousel_page += 1
        driver.close()

    def handle_PK(self, string):
        """

        :param string:
        :return:
        """
        new_string = ''
        if string[0:2] == 'PK':
            new_string = '0 ' + string[2:]
        else:
            new_string += string
        return new_string

    def extract_line(self, string):
        """

        :param string:
        :return:
        """
        new_string = ""
        for character in string:
            if ord(character) != 189:
                new_string += character
            else:
                new_string += '.5'
        return new_string

    def click_next(self, carousel_controller):
        """

        :param carousel_controller:
        :return:
        """
        next_button = carousel_controller.find_element_by_link_text('Next Page')
        next_button.click()
        sleep(self.waiting_time)

    def click_previous(self, carousel_controller):
        """

        :param carousel_controller:
        :return:
        """
        previous_button = carousel_controller.find_element_by_link_text('Previous Page')
        previous_button.click()
        sleep(self.waiting_time)

    def rectify_date_format(self, footballdb_datestring):
        """

        :param footballdb_datestring:
        :return:
        """
        correct_datestring = ''
        date_pieces = footballdb_datestring.split(', ')
        year = date_pieces[len(date_pieces) - 1]
        month, day = date_pieces[1].split(' ')
        month = str(MONTHS[month])
        if len(month) == 1:
            month = '0' + str(month)
        if len(day) == 1:
            day = '0' + str(day)
        correct_datestring += year + month + day
        return correct_datestring

    def append_to_csv_matrix(self, submatrix):
        """

        :param submatrix:
        :return:
        """
        new_csv_matrix = self.get_csv_matrix()
        new_csv_matrix += list(submatrix)
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

    def set_csv_matrix(self, new_csv_matrix):
        """

        :param new_csv_matrix:
        :return:
        """
        self.csv_matrix = new_csv_matrix

    def set_waiting_time(self, new_waiting_time):
        """

        :param new_waiting_time:
        :return:
        """
        self.waiting_time = new_waiting_time

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

    def get_csv_matrix(self):
        """

        :return:
        """
        return self.csv_matrix

    def get_waiting_time(self):
        """

        :return:
        """
        return self.waiting_time


