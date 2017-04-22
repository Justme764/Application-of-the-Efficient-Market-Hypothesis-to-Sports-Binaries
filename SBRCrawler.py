import csv
import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
          "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}


class SBRCrawler:
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
            self.csv_matrix = list\
                ([list(['Date', 'Away', 'Home', 'MinLine', 'MaxLine',
                        'Optimal Underdog Payout', 'Optimal Underdog Casino',
                        'Optimal Favorite Payout', 'Optimal Favorite Casino'])])
        self.waiting_time = waiting_time

    def deploy(self, date_strings):
        """

        :param date_strings:
        :return:
        """
        submatrix = list([])
        casinos_url = self.get_base_url() + self.get_branch_url() \
                      + '?date=' + self.rectify_date_format(date_strings[random.randrange(len(date_strings))])
        casinos = self.extract_casinos(casinos_url)
        for date_string in date_strings:
            url = self.get_base_url() + self.get_branch_url() + '?date=' + self.rectify_date_format(date_string)
            self.money_line_scraper(date_string)

    def money_line_scraper(self, date_string):
        payouts_submatrix = list([])

        url = self.get_base_url() + self.get_branch_url() + \
              'money-line/' + '?date=' + self.rectify_date_format(date_string)
        driver = webdriver.Chrome(self.get_webdriver_path())
        driver.get(url)

        carousel_next_clicks = 3

        carousel_controller = driver.find_element_by_xpath('//div[@class="carousel-control"]')

        payouts_table = driver.find_element_by_xpath('//div[@class="section module OddsGridModuleClass "]')

        game_payouts = payouts_table.find_elements_by_xpath('//div[@class="event-holder holder-complete"]')

        while carousel_next_clicks > 0:
            for game in game_payouts:
                underdog_payouts, favorite_payouts = list([]), list([])
                underdog = self.determine_underdog(url, game_payouts.index(game))

                teams = game.find_elements_by_xpath('.//span[@class="team-name"]')

                if underdog:
                    away_team = str(teams[0].text) + ' (Favorite)'
                    home_team = str(teams[1].text) + ' (Underdog)'

                    underdog_payouts.append(home_team)
                    favorite_payouts.append(away_team)
                else:
                    away_team = str(teams[0].text) + ' (Underdog)'
                    home_team = str(teams[1].text) + ' (Favorite)'

                    underdog_payouts.append(away_team)
                    favorite_payouts.append(home_team)

                payouts = game.find_elements_by_xpath('.//div[@class="el-div eventLine-book"]')
                for payout in payouts:
                    away_payout, home_payout = \
                        [str(num.text) for num in payout.find_elements_by_xpath('.//div[@class="eventLine-book-value "]')]
                    if underdog:
                        underdog_payouts.append(home_payout)
                        favorite_payouts.append(away_payout)
                    else:
                        underdog_payouts.append(away_payout)
                        favorite_payouts.append(home_payout)
                if carousel_next_clicks >= 3:
                    payouts_submatrix.append(underdog_payouts)
                    payouts_submatrix.append(favorite_payouts)
                else:
                    game_index = game_payouts.index(game)
                    first_payout_index = 2 * game_index
                    second_payout_index = 2 * game_index + 1

                    payouts_submatrix[first_payout_index] = \
                        payouts_submatrix[first_payout_index] + underdog_payouts[1:]
                    payouts_submatrix[second_payout_index] = \
                        payouts_submatrix[second_payout_index] + underdog_payouts[1:]

            self.click_next(carousel_controller)
            carousel_next_clicks -= 1

        driver.close()

        return payouts_submatrix

    def point_spread_scraper(self):
        pass

    def line_movement_scraper(self):
        pass

    def game_scraper(self, url, date_string, game_index, casinos):

        max_iter = 10
        iter = 0

        driver = webdriver.Chrome(self.get_webdriver_path())
        driver.get(url)

        date = self.rectify_date_format(date_string)

        carousel_controller = driver.find_element_by_xpath('//div[@class="carousel-control"]')

        game_odds = driver.find_elements_by_xpath('//div[@class="event-holder holder-complete"]')

        game = game_odds[game_index]

        lines, underdog_payouts, favorite_payouts = list([]), list([]), list([])
        underdog = self.determine_underdog(url, game_odds.index(game))
        carousel_next_clicks = 3
        carousel_previous_clicks = 3
        carousel_page = 0
        game_time = str(game.find_element_by_xpath('.//div[@class="el-div eventLine-time"]').text) + 'm'
        first_refreshed_page_game_odds = driver.find_elements_by_xpath \
            ('//div[@class="event-holder holder-complete"]')
        first_refreshed_game = first_refreshed_page_game_odds[game_odds.index(game)]
        teams = first_refreshed_game.find_elements_by_xpath('.//span[@class="team-name"]')
        if underdog:
            away_team = str(teams[0].text) + ' (Favorite)'
            home_team = str(teams[1].text) + ' (Underdog)'
        else:
            away_team = str(teams[0].text) + ' (Underdog)'
            home_team = str(teams[1].text) + ' (Favorite)'
        while carousel_next_clicks >= 0:
            second_refreshed_page_game_odds = driver.find_elements_by_xpath \
                ('//div[@class="event-holder holder-complete"]')
            second_refreshed_game = second_refreshed_page_game_odds[game_odds.index(game)]

            casinos_info = second_refreshed_game.find_elements_by_xpath \
                ('.//div[@class="el-div eventLine-book"]')

            if carousel_next_clicks == 0:
                casinos_info = casinos_info[len(casinos_info) - 2:]

            if carousel_next_clicks > 2:
                pre_actions = ActionChains(driver)
                second_casino = casinos_info[1]
                pre_actions.move_to_element(second_casino)
                pre_actions.click()
                pre_actions.perform()
                sleep(self.get_waiting_time())

            """
            try:
                closer = ActionChains(driver)

                ml_box = driver.find_element_by_xpath \
                    ('//div[@class="ui-dialog ui-widget ui-widget-content ui-corner-all ui-front ui-draggable"]')
                ml_box_title = ml_box.find_element_by_xpath \
                    ('.//div[@class="ui-dialog-titlebar ui-widget-header ui-corner-all ui-helper-clearfix"]')
                ml_box_close_button = ml_box_title.find_element_by_xpath \
                    ('.//button[@class="ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only ui-dialog-titlebar-close"]')

                closer.move_to_element(ml_box_close_button)
                closer.click()
                closer.perform()

            except Exception as exception:
                print(exception)
                pass

            """

            casino_idx = 0

            while casino_idx != len(casinos_info):
                print(casinos[casinos_info.index(casinos_info[casino_idx]) + (abs(carousel_next_clicks - 3)) * 10])

                if iter >= max_iter:
                    closed = False
                    while not closed:
                        try:
                            intra_actions = ActionChains(driver)
                            intra_actions.move_to_element(casinos_info[casino_idx])
                            intra_actions.click()
                            intra_actions.perform()
                            sleep(self.get_waiting_time())
                            closer = ActionChains(driver)

                            ml_box = driver.find_element_by_xpath \
                                ('//div[@class="ui-dialog ui-widget ui-widget-content ui-corner-all ui-front ui-draggable"]')
                            ml_box_title = ml_box.find_element_by_xpath \
                                ('.//div[@class="ui-dialog-titlebar ui-widget-header ui-corner-all ui-helper-clearfix"]')
                            ml_box_close_button = ml_box_title.find_element_by_xpath \
                                ('.//button[@class="ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only ui-dialog-titlebar-close"]')

                            closer.move_to_element(ml_box_close_button)
                            closer.click()
                            closer.perform()

                            intra_actions = ActionChains(driver)
                            intra_actions.move_to_element(casinos_info[casino_idx])
                            intra_actions.click()
                            intra_actions.perform()
                            if casinos[casinos_info.index(casinos_info[casino_idx]) + (abs(carousel_next_clicks - 3)) * 10] == 'matchbook':
                                sleep(5 * self.get_waiting_time())
                            else:
                                sleep(self.get_waiting_time())
                            closed = True
                            print('DONE!!!')

                        except Exception as exception:
                            print('trying')
                            intra_actions = ActionChains(driver)
                            intra_actions.move_to_element(casinos_info[casino_idx])
                            intra_actions.click()
                            intra_actions.perform()
                            if casinos[casinos_info.index(casinos_info[casino_idx]) + (abs(carousel_next_clicks - 3)) * 10] == 'matchbook':
                                sleep(5 * self.get_waiting_time())
                            else:
                                sleep(self.get_waiting_time())
                            pass

                opened = False
                iter2 = 0
                while not opened:
                    try:
                        ml_box = driver.find_element_by_xpath \
                            ('//div[@class="ui-dialog ui-widget ui-widget-content ui-corner-all ui-front ui-draggable"]')
                        spreads_boxes_widget = ml_box.find_elements_by_xpath('.//div[@class="ui-dialog-content ui-widget-content"]')
                        spreads_boxes = spreads_boxes_widget[0].find_elements_by_xpath('.//div[@class="info-box"]')
                        point_spreads = spreads_boxes[0]
                        money_lines = spreads_boxes[1]

                        point_spread_rows = point_spreads.find_elements_by_xpath('.//tr[@class="info_line_alternate1"]')
                        for point_spread_row in point_spread_rows:
                            point_spread_time = point_spread_row.find_element_by_xpath('.//td[@class="left"]').text
                            if self.compare_dates(self.rectify_date_format(date_string), game_time, point_spread_time):
                                away_team_point_spread, home_team_point_spread = \
                                    [str(web_element.text) for web_element in
                                     point_spread_row.find_elements_by_xpath('.//td[@width="86"]')]

                                away_team_point_spread = self.handle_PK(away_team_point_spread)
                                home_team_point_spread = self.handle_PK(home_team_point_spread)

                                away_team_point_spread = self.extract_line(away_team_point_spread)
                                home_team_point_spread = self.extract_line(home_team_point_spread)

                                away_team_point_spread = float(away_team_point_spread.split()[0])
                                home_team_point_spread = float(home_team_point_spread.split()[0])

                                lines.append(away_team_point_spread)
                                lines.append(home_team_point_spread)

                                break

                        money_line_rows = money_lines.find_elements_by_xpath('.//tr[@class="info_line_alternate1"]')
                        for money_line_row in money_line_rows:
                            money_line_time = money_line_row.find_element_by_xpath('.//td[@class="left"]').text
                            if self.compare_dates(self.rectify_date_format(date_string), game_time, money_line_time):
                                away_team_money_line, home_team_money_line = \
                                    [str(web_element.text) for web_element in
                                     money_line_row.find_elements_by_xpath('.//td[@width="86"]')]

                                away_team_money_line = int(away_team_money_line)
                                home_team_money_line = int(home_team_money_line)

                                print(away_team_money_line, home_team_money_line)

                                if underdog:
                                    underdog_payouts.append(home_team_money_line)
                                    favorite_payouts.append(away_team_money_line)
                                else:
                                    underdog_payouts.append(away_team_money_line)
                                    favorite_payouts.append(home_team_money_line)

                                break

                        if len(money_line_rows) == 0:
                            underdog_payouts.append(-float('inf'))
                            favorite_payouts.append(-float('inf'))
                            print(casinos[casinos_info.index(casinos_info[casino_idx]) + (abs(carousel_next_clicks - 3)) * 10] +
                                  ' is currently not allowing bets on ' + away_team + ' @ ' + home_team +
                                  ' scheduled for ' + date_string)

                        opened = True

                    except Exception as exception:
                        iter2 += 1
                        if iter2 >= max_iter:
                            underdog_payouts.append(-float('inf'))
                            favorite_payouts.append(-float('inf'))
                            break
                        pass

                close_successful = False
                iter = 0
                while not close_successful:
                    try:
                        if iter > max_iter:
                            closer = ActionChains(driver)
                            closer.send_keys(Keys.ESCAPE)
                            break
                        else:
                            closer = ActionChains(driver)

                            ml_box = driver.find_element_by_xpath \
                                (
                                    '//div[@class="ui-dialog ui-widget ui-widget-content ui-corner-all ui-front ui-draggable"]')
                            ml_box_title = ml_box.find_element_by_xpath \
                                ('.//div[@class="ui-dialog-titlebar ui-widget-header ui-corner-all ui-helper-clearfix"]')
                            ml_box_close_button = ml_box_title.find_element_by_xpath \
                                (
                                    './/button[@class="ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only ui-dialog-titlebar-close"]')

                            closer.move_to_element(ml_box_close_button)
                            closer.click()
                            closer.perform()

                            close_successful = True

                    except Exception as exception:
                        iter += 1
                        pass

                sleep(self.get_waiting_time())

                casino_idx += 1

            self.click_next(carousel_controller)
            carousel_next_clicks -= 1
            carousel_page += 1

        while carousel_previous_clicks >= 0:
            self.click_previous(carousel_controller)
            carousel_previous_clicks -= 1

        minline = str(min(lines))
        maxline = str(max(lines))

        optimal_underdog_payout = str(max(underdog_payouts))
        optimal_favorite_payout = str(max(favorite_payouts))

        optimal_underdog_casino = casinos[underdog_payouts.index(float(optimal_underdog_payout))]
        optimal_favorite_casino = casinos[favorite_payouts.index(float(optimal_favorite_payout))]

        matrix_row = list([date, away_team, home_team, minline, maxline,
                           optimal_underdog_payout, optimal_underdog_casino,
                           optimal_favorite_payout, optimal_favorite_casino])
        print(matrix_row)

        driver.close()

        return matrix_row

    def extract_casinos(self, url):
        """

        :param url:
        :return:
        """
        casinos = list([])
        while len(casinos) != 32:
            carousel_next_clicks = 3
            driver = webdriver.Chrome(self.get_webdriver_path())
            driver.get(url)
            carousel_controller = driver.find_element_by_xpath('//div[@class="carousel-control"]')
            while carousel_next_clicks >= 0:
                casinos_row = driver.find_element_by_xpath('//div[@class="carousel-bookslist"]')
                casino_elements = casinos_row.find_elements_by_tag_name('li')
                if carousel_next_clicks == 0:
                    casino_elements = casino_elements[len(casino_elements) - 2:]
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

        while carousel_next_clicks >= 0:
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
                    handled_lower_row_text = self.handle_PK(str(lower_row.text))
                    line_value = float(self.extract_line(handled_lower_row_text.split()[0]))

                    if line_value > 0:
                        driver.close()
                        return True
                    elif line_value < 0:
                        driver.close()
                        return False

                except Exception as exception:
                    print('Exception encountered! Moving to next casino to determine underdog...')
                    print('\n')
            self.click_next(carousel_controller)
            carousel_next_clicks -= 1
            carousel_page += 1
        driver.close()

    def compare_dates(self, date_string, game_time, spread_date):
        date_string_month = int(date_string[4:6])
        date_string_day = int(date_string[6:])

        game_time_hhmin, game_time_meridiem = game_time[:len(game_time)-2], game_time[len(game_time)-2:]
        game_time_hour, game_time_min = [int(string) for string in game_time_hhmin.split(':')]

        spread_date_mmdd, spread_date_time, spread_date_meridiem = spread_date.split()
        spread_date_meridiem = spread_date_meridiem.lower()
        spread_date_month, spread_date_day = [int(string) for string in spread_date_mmdd.split('/')]
        spread_date_hour, spread_date_min = [int(string) for string in spread_date_time.split(':')]

        if spread_date_month == 12 and date_string_month == 1:
            return True

        if spread_date_month < date_string_month:
            return True
        elif spread_date_month > date_string_month:
            return False
        else:
            if spread_date_day < date_string_day:
                return True
            elif spread_date_day > date_string_day:
                return False
            else:
                if spread_date_meridiem == 'am' and game_time_meridiem == 'pm':
                    return True
                elif spread_date_meridiem == 'pm' and game_time_meridiem == 'am':
                    return False
                else:
                    if spread_date_hour < game_time_hour:
                        return True
                    elif spread_date_hour > game_time_hour:
                        return False
                    else:
                        if spread_date_min < game_time_min:
                            return True
                        elif spread_date_min > game_time_min:
                            return False
                        else:
                            return False

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


