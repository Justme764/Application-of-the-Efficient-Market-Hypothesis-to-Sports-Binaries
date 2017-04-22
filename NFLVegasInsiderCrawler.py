import csv
from selenium import webdriver


MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
          "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}

TEAM_ABBR = {"Arizona Cardinals": "ARI",
             "Atlanta Falcons": "ATL",
             "Baltimore Ravens": "BAL",
             "Buffalo Bills": "BUF",
             "Carolina Panthers": "CAR",
             "Chicago Bears": "CHI",
             "Cincinnati Bengals": "CIN",
             "Cleveland Browns": "CLE",
             "Dallas Cowboys": "DAL",
             "Denver Broncos": "DEN",
             "Detroit Lions": "DET",
             "Green Bay Packers": "GNB",
             "Houston Texans": "HOU",
             "Indianapolis Colts": "IND",
             "Jacksonville Jaguars": "JAC",
             "Kansas City Chiefs": "KAN",
             "Los Angeles Chargers": "LAC",
             "Los Angeles Raiders": "LAI",
             "Miami Dolphins": "MIA",
             "Minnesota Vikings": "MIN",
             "New England Patriots": "NWE",
             "New Orleans Saints": "NOR",
             "New York Giants": "NYG",
             "New York Jets": "NYJ",
             "Oakland Raiders": "OAK",
             "Philadelphia Eagles": "PHI",
             "Pittsburgh Steelers": "PIT",
             "San Diego Chargers": "SDG",
             "Seattle Seahawks": "SEA",
             "San Francisco 49ers": "SFO",
             "St. Louis Cardinals": "SLC",
             "Los Angeles Rams": "STL",
             "Tampa Bay Buccaneers": "TAM",
             "Tennessee Titans": "TEN",
             "Washington Redskins": "WAS"
             }


class NFLVegasInsiderCrawler:
    """

    """
    def __init__(self, csv_filename, webdriver_path, branch_url='', read_csv_file=False, waiting_time=2):
        """

        :param branch_url:
        """
        self.csv_filename = csv_filename
        self.webdriver_path = webdriver_path
        self.base_url = 'http://www.vegasinsider.com/'
        self.branch_url = branch_url
        self.read_csv_file = read_csv_file
        if self.read_csv_file:
            self.csv_matrix = self.read_csv(self.csv_filename)
        else:
            self.csv_matrix = list([list(['Date', 'Teams', 'Favorite/Underdog', 'Score',
                                          'Spread Min', 'Spread Max', 'Moneyline', 'Payout']),
                                    list([])])
        self.waiting_time = waiting_time

    def deploy(self, year):
        """

        :param year:
        :return:
        """
        moneylines_matrix = list([])
        spreads_matrix = list([])
        final_data_matrix = list([])
        num_weeks = 22
        casinos = list([])

        for week in range(num_weeks):
            if week != 20:
                url = self.get_base_url() + self.get_branch_url() + "/week/" + str(week + 1) + "/season/" + str(year)
                driver = webdriver.Chrome(self.get_webdriver_path())
                driver.get(url)

                game_tables = driver.find_elements_by_xpath('.//td[@class="sportPicksBorder"]')
                print(len(game_tables))

                for game_table_index in range(len(game_tables)):
                    away_moneylines, home_moneylines = list([]), list([])
                    away_spreads, home_spreads = list([]), list([])
                    final_data_upper_row, final_data_lower_row = list([]), list([])

                    game_driver = webdriver.Chrome(self.get_webdriver_path())
                    game_driver.get(url)

                    new_game_tables = game_driver.find_elements_by_xpath('.//td[@class="sportPicksBorder"]')
                    game_table = new_game_tables[game_table_index]

                    away_score_row, home_score_row = game_table.find_elements_by_xpath('.//tr[@class="tanBg"]')
                    away_score = [str(web_element.text) for web_element in away_score_row.
                        find_elements_by_xpath('.//td[@class="sportPicksBorderL2 zerocenter"]')][-1]
                    home_score = [str(web_element.text) for web_element in home_score_row.
                        find_elements_by_xpath('.//td[@class="sportPicksBorderL zerocenter"]')][-1]

                    line_movement_row = game_table.find_element_by_xpath('.//tr[@class="bbg2"]')
                    line_movement_link = line_movement_row.find_element_by_xpath('.//a[@class="white"]')
                    line_movement_link.click()

                    info_tables = game_driver.find_element_by_xpath('.//div[@class="SLTables1"]').\
                        find_elements_by_xpath('.//table[@cellspacing=0]')

                    game_title, game_datetime = info_tables[0], info_tables[1]

                    away_team, home_team = [str(team_name) for team_name in
                                            str(game_title.find_element_by_xpath('.//font').text).split(' @ ')]

                    print(away_team, away_score)
                    print(home_team, home_score)

                    """
                    if away_team != 'Chicago Bears':
                        game_driver.close()
                        continue
                    """

                    game_date, game_time = [str(game_info.text) for game_info in game_datetime.find_elements_by_xpath('.//td[@valign="top"]')]

                    game_date, game_time = " ".join(game_date.split()[2:]), " ".join(game_time.split()[2:])

                    print(game_date, game_time)
                    print('\n')

                    underdog = True

                    for info_table in info_tables[2:]:
                        casino_name = info_table.find_element_by_xpath('.//tr[@class="component_head"]').text
                        casino_name = casino_name[:len(casino_name) - 15]
                        print(casino_name)

                        if week == 0 and game_table_index == 0:
                            casinos.append(casino_name)

                        table_rows = [str(table_row.text) for table_row in info_table.
                            find_element_by_xpath('.//table[@class="rt_railbox_border2"]').
                            find_elements_by_xpath('.//tr')]

                        desired_table_rows = list([])
                        for table_row in table_rows[2:]:
                            if self.is_before_game(table_row, game_date, game_time) and self.has_money_line(table_row):
                                desired_table_rows.append(table_row)

                        if len(desired_table_rows) == 0:
                            away_moneylines.append(str(''))
                            home_moneylines.append(str(''))

                            away_spreads.append(str(''))
                            away_spreads.append(str(''))

                            continue

                        desired_table_row = self.determine_desired_table_row(desired_table_rows)

                        underdog = self.determine_underdog(desired_table_row, home_team)

                        desired_table_row = desired_table_row.split()

                        print(desired_table_row)

                        if underdog:
                            away_moneyline = self.handle_moneyline_pk(desired_table_row[2][3:])
                            home_moneyline = self.handle_moneyline_pk(desired_table_row[3][3:])

                            away_spread = self.handle_spread_pk(desired_table_row[4][3:])
                            home_spread = self.handle_spread_pk(desired_table_row[6][3:])
                        else:
                            away_moneyline = self.handle_moneyline_pk(desired_table_row[3][3:])
                            home_moneyline = self.handle_moneyline_pk(desired_table_row[2][3:])

                            away_spread = self.handle_spread_pk(desired_table_row[6][3:])
                            home_spread = self.handle_spread_pk(desired_table_row[4][3:])

                        away_moneylines.append(away_moneyline)
                        home_moneylines.append(home_moneyline)

                        away_spreads.append(away_spread)
                        home_spreads.append(home_spread)

                    if len(moneylines_matrix) == 0:
                        moneylines_matrix.append(list(['Date', 'Teams', 'Favorite/Underdog']) + casinos)
                        moneylines_matrix.append(list([]))

                    if len(spreads_matrix) == 0:
                        spreads_matrix.append(list(['Date', 'Teams', 'Favorite/Underdog']) + casinos)
                        spreads_matrix.append(list([]))

                    print('\n')
                    print('Away Moneylines:', away_moneylines)
                    print('Home Moneylines:', home_moneylines)
                    print('Away Spreads:', away_spreads)
                    print('Home Spreads:', home_spreads)
                    print('\n')

                    desired_away_moneyline = max([float(moneyline) for moneyline in away_moneylines if moneyline != ''])
                    desired_home_moneyline = max([float(moneyline) for moneyline in home_moneylines if moneyline != ''])

                    desired_away_payout = self.compute_payout(desired_away_moneyline)
                    desired_home_payout = self.compute_payout(desired_home_moneyline)

                    desired_min_away_spread = min([float(spread) for spread in away_spreads if spread != ''])
                    desired_max_away_spread = max([float(spread) for spread in away_spreads if spread != ''])
                    desired_min_home_spread = min([float(spread) for spread in home_spreads if spread != ''])
                    desired_max_home_spread = max([float(spread) for spread in home_spreads if spread != ''])

                    if underdog:
                        payouts_upper_row = list([self.rectify_date_format(game_date), away_team, '(Favorite)']) + \
                                            away_moneylines
                        payouts_lower_row = list(['', home_team, '(Underdog)']) + home_moneylines

                        spreads_upper_row = list([self.rectify_date_format(game_date), away_team, '(Favorite)']) + \
                                            away_spreads
                        spreads_lower_row = list(['', home_team, '(Underdog)']) + home_spreads

                        final_data_upper_row += list([self.rectify_date_format(game_date), away_team, '(Favorite)',
                                                      away_score, str(desired_min_away_spread),
                                                      str(desired_max_away_spread), str(desired_away_moneyline),
                                                      str(desired_away_payout)])
                        final_data_lower_row += list(['', home_team, '(Underdog)', home_score,
                                                      str(desired_min_home_spread), str(desired_max_home_spread),
                                                      str(desired_home_moneyline), str(desired_home_payout)])
                    else:
                        payouts_upper_row = list([self.rectify_date_format(game_date), home_team, '(Favorite)']) + \
                                            home_moneylines
                        payouts_lower_row = list(['', away_team, '(Underdog)']) + away_moneylines

                        spreads_upper_row = list([self.rectify_date_format(game_date), home_team, '(Favorite)']) + \
                                            home_spreads
                        spreads_lower_row = list(['', away_team, '(Underdog)']) + away_spreads

                        final_data_upper_row += list([self.rectify_date_format(game_date), home_team, '(Favorite)',
                                                      home_score, str(desired_min_home_spread),
                                                      str(desired_max_home_spread), str(desired_home_moneyline),
                                                      str(desired_home_payout)])
                        final_data_lower_row += list(['', away_team, '(Underdog)', away_score,
                                                      str(desired_min_away_spread),str(desired_max_away_spread),
                                                      str(desired_away_moneyline), str(desired_away_payout)])

                    moneylines_matrix.append(payouts_upper_row)
                    moneylines_matrix.append(payouts_lower_row)
                    moneylines_matrix.append(list([]))

                    spreads_matrix.append(spreads_upper_row)
                    spreads_matrix.append(spreads_lower_row)
                    spreads_matrix.append(list([]))

                    final_data_matrix.append(final_data_upper_row)
                    final_data_matrix.append(final_data_lower_row)
                    final_data_matrix.append(list([]))

                    game_driver.close()

                driver.close()

        self.append_to_csv_matrix(final_data_matrix)

        self.write_csv('NFL Vegas Moneyline (' + str(year) + ').csv', moneylines_matrix)
        self.write_csv('NFL Vegas Spreads (' + str(year) + ').csv', spreads_matrix)
        self.write_csv(self.get_csv_filename(), self.get_csv_matrix())

    def determine_desired_table_row(self, desired_table_rows):
        censor = 'XX'
        for row_index in range(len(desired_table_rows) - 1, -1, -1):
            row = desired_table_rows[row_index]
            print(row)
            modified_row = row.split()
            non_public = True
            for element in modified_row[:9]:
                non_public = non_public and (censor not in element)
            if non_public:
                return row

    @staticmethod
    def compute_payout(moneyline):
        """

        :param moneyline:
        :return:
        """
        if float(moneyline) < 0:
            return 100.00 / float(moneyline)
        else:
            return float(moneyline) / 100.00

    def is_before_game(self, table_row, game_date, game_time):
        """

        :param table_row:
        :param game_date:
        :param game_time:
        :return:
        """
        table_row = table_row.split()
        row_date, row_time = table_row[0], table_row[1]
        game_date = self.rectify_date_format(game_date)
        row_month, row_day = [int(num) for num in row_date.split('/')]
        if row_month == 12 and int(game_date[4:6]) == 1:
            row_year = str(int(game_date[:4]) - 1)
            row_month, row_day = row_date.split('/')
        else:
            row_year = game_date[:4]
            row_month, row_day = row_date.split('/')
        row_date = row_year + row_month + row_day
        return self.compare_dates(row_date, row_time, game_date, game_time)

    @staticmethod
    def has_money_line(table_row):
        """

        :param table_row:
        :return:
        """
        if len(table_row.split()) <= 2:
            return False
        table_row = str(table_row).split()
        first_entry, second_entry = table_row[2], table_row[3]
        return first_entry[:3].isalpha() and first_entry[4:].isnumeric() and \
               second_entry[:3].isalpha() and second_entry[4:].isnumeric()

    @staticmethod
    def determine_underdog(table_row, home_team):
        """

        :param table_row:
        :param home_team:
        :return:
        """
        table_row = table_row.split()
        fav_abbr = table_row[2][:3]
        if fav_abbr == TEAM_ABBR[home_team]:
            return False
        else:
            return True

    @staticmethod
    def handle_moneyline_pk(payout):
        """

        :param payout:
        :return:
        """
        if payout == 'PK':
            payout = str(100)
        return payout

    @staticmethod
    def handle_spread_pk(spread):
        """

        :param spread:
        :return:
        """
        if spread == 'PK':
            spread = str(0)
        return spread

    @staticmethod
    def compare_dates(row_date, row_time, game_date, game_time):
        """

        :param row_date:
        :param row_time:
        :param game_date:
        :param game_time:
        :return:
        """
        row_year, row_month, row_day = int(row_date[:4]), int(row_date[4:6]), int(row_date[6:])
        game_year, game_month, game_day = int(game_date[:4]), int(game_date[4:6]), int(game_date[6:])

        row_hhmin, row_meridiem = row_time[:len(row_time) - 2], row_time[len(row_time) - 2:]
        game_hhmin, game_meridiem = game_time.split()
        game_meridiem = game_meridiem.lower()

        row_hour, row_min = [int(num) for num in row_hhmin.split(':')]
        game_hour, game_min = [int(num) for num in game_hhmin.split(':')]

        if row_year < game_year:
            return True
        elif row_year > game_year:
            return False
        else:
            if row_month < game_month:
                return True
            elif row_month > game_month:
                return False
            else:
                if row_day < game_day:
                    return True
                elif row_day > game_day:
                    return False
                else:
                    if row_meridiem == 'am' and game_meridiem == 'pm':
                        return True
                    elif row_meridiem == 'pm' and game_meridiem == 'am':
                        return False
                    else:
                        if row_hour < game_hour:
                            return True
                        elif row_hour > game_hour:
                            return False
                        else:
                            if row_min <= game_min:
                                return True
                            else:
                                return False

    @staticmethod
    def rectify_date_format(footballdb_datestring):
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

    @staticmethod
    def read_csv(csv_filename):
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

    @staticmethod
    def write_csv(csv_filename, data_matrix):
        """

        :param csv_filename:
        :param data_matrix:
        :return:
        """
        with open(csv_filename, "w") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=",")
            for row in data_matrix:
                csv_writer.writerow(list(row))

    def append_to_csv_matrix(self, submatrix):
        """

        :param submatrix:
        :return:
        """
        new_csv_matrix = self.get_csv_matrix()
        new_csv_matrix += list(submatrix)
        self.set_csv_matrix(new_csv_matrix)

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


