import csv
from time import time
from SBRPayoutsCrawler import SBRPayoutsCrawler
from KillerSportsCrawler import KillerSportsCrawler
from SBRPointSpreadsCrawler import SBRPointSpreadsCrawler
from NFLVegasInsiderCrawler import NFLVegasInsiderCrawler


year = 2016

WEBDRIVER_PATH = '/Users/ragibmostofa/Downloads/chromedriver'

NFL_CSV_FILENAME = 'NFL Vegas Data (' + str(year) + ').csv'

NFL_KS_FILENAME = 'NFL Vegas KS (' + str(year) + ').csv'

NFL_EV_FILENAME = 'NFL Vegas EV (' + str(year) + ').csv'

#NFL_FINAL_CSV = 'NFL Final.csv'

t_0 = time()


csv_matrix = []  # initialize the matrix
with open(NFL_EV_FILENAME, "r") as csv_file:  # open the file
    csv_reader = csv.reader(csv_file, delimiter=",")  # read the file
    for row in csv_reader:  # for every row, i.e. data field
        csv_matrix.append(list(row))  # append it to the matrix


# nfl_vegas_ks_spider = KillerSportsCrawler(NFL_KS_FILENAME, WEBDRIVER_PATH, branch_url='nfl/query')
#
# nfl_vegas_ks_spider.deploy(csv_matrix)

# new_csv_matrix = list([list(['Date', 'Teams', 'Favorite/Underdog', 'Score', 'Spread Min', 'Spread Max',
#                                           'Moneyline', 'Payout', 'Win Percentage', 'Number of Wins',
#                                           'Number of Losses', 'Sample Size', 'EV']), csv_matrix[1]])
#
# for row_idx in range(2, len(csv_matrix), 3):
#     fav_row = csv_matrix[row_idx]
#     dog_row = csv_matrix[row_idx + 1]
#     spacer_row = csv_matrix[row_idx + 2]
#
#     fav_payout = float(fav_row[7])
#     dog_payout = float(dog_row[7])
#
#     fav_row[8] = str(float(fav_row[8]) / 100)
#     dog_row[8] = str(float(dog_row[8]) / 100)
#
#     fav_win_pct = float(fav_row[8])
#     dog_win_pct = float(dog_row[8])
#
#     fav_ev = fav_payout * fav_win_pct - (1 - fav_win_pct)
#     dog_ev = dog_payout * dog_win_pct - (1 - dog_win_pct)
#
#     fav_row.append(fav_ev)
#     dog_row.append(dog_ev)
#
#     new_csv_matrix.append(fav_row)
#     new_csv_matrix.append(dog_row)
#     new_csv_matrix.append(spacer_row)
#
# with open(NFL_EV_FILENAME, "w") as csv_file:
#     csv_writer = csv.writer(csv_file, delimiter=",")
#     for row in new_csv_matrix:
#         csv_writer.writerow(list(row))

threshold = 0.005

eps = 0.20

profits = list([])

edge = 0

total = 0
total_bet_on = 0
correct = 0
wrong = 0

double_pos = 0

winning_returns = 0.00
losing_returns = 0.00

theoretical_ev = 0.00

for row_idx in range(2, len(csv_matrix), 3):
    total += 1

    fav_row = csv_matrix[row_idx]
    dog_row = csv_matrix[row_idx + 1]
    spacer_row = csv_matrix[row_idx + 2]

    fav_ev = float(fav_row[12])
    dog_ev = float(dog_row[12])

    fav_score = float(fav_row[3])
    dog_score = float(dog_row[3])

    fav_payout = float(fav_row[7])
    dog_payout = float(dog_row[7])

    fav_win_pct = float(fav_row[8])
    dog_win_pct = float(dog_row[8])

    if fav_win_pct < (0.5 - eps) or fav_win_pct > (0.5 + eps):
        edge += 1
        total_bet_on += 1
        if fav_win_pct > dog_win_pct:
            theoretical_ev += fav_ev
            if fav_score > dog_score:
                correct += 1
                winning_returns += fav_payout
            elif fav_score < dog_score:
                wrong += 1
                losing_returns -= 1
        elif fav_win_pct < dog_win_pct:
            theoretical_ev += dog_ev
            if dog_score > fav_score:
                correct += 1
                winning_returns += dog_payout
            elif dog_score < fav_score:
                wrong += 1
                losing_returns -= 1
    else:
        if (fav_ev > 0 and dog_ev < 0) or (fav_ev < 0 and dog_ev > 0):  # (fav_ev > 0 and dog_ev > 0):
            if fav_ev > dog_ev:
                if fav_ev > 0.035:
                    total_bet_on += 1
                    theoretical_ev += fav_ev
                    if fav_score > dog_score:
                        correct += 1
                        winning_returns += fav_payout
                    elif fav_score < dog_score:
                        wrong += 1
                        losing_returns -= 1
            elif fav_ev < dog_ev:
                if dog_ev > 0.035:
                    total_bet_on += 1
                    theoretical_ev += dog_ev
                    if dog_score > fav_score:
                        correct += 1
                        winning_returns += dog_payout
                    elif dog_score < fav_score:
                        wrong += 1
                        losing_returns -= 1
        # elif fav_ev > 0 and dog_ev > 0:
        #     double_pos += 1
        #     if fav_score > dog_score:
        #         if fav_ev > threshold:
        #             theoretical_ev += fav_ev + dog_ev
        #             total_bet_on += 2
        #             #correct += 1
        #             winning_returns += fav_payout
        #             losing_returns -= 1
        #     elif fav_score < dog_score:
        #         if dog_ev > threshold:
        #             theoretical_ev += fav_ev + dog_ev
        #             total_bet_on += 2
        #             #wrong += 1
        #             winning_returns += dog_payout
        #             losing_returns -= 1
    # profits.append((winning_returns + losing_returns) / total_bet_on * 100)
    profits.append((winning_returns + losing_returns))

# print('Threshold:', t/1000)

print('Total Number of Games:', total)
print('\n')
print('Total Number of Games Bet On:', total_bet_on)
print('\n')
print('Total Number of Correct Bets:', correct)
print('\n')
print('Total Number of Wrong Bets:', wrong)
print('\n')
print('Total Number of Tied Bets:', total_bet_on - (correct + wrong))
print('\n')
print('Total Winning Returns:', winning_returns)
print('\n')
print('Total Losing Returns:', losing_returns)
print('\n')
print('Aggregate Returns:', winning_returns + losing_returns)
print('\n')
print('Aggregate Returns (%):', (winning_returns + losing_returns) / total_bet_on * 100)
print('\n')
print('Theoretical Returns:', theoretical_ev)
print('\n')
print('Theoretical Returns (%):', theoretical_ev / total_bet_on * 100)
print('\n')
print('Double Positive Games:', double_pos)
print('\n')

print(edge)

print(profits)

t_1 = time()

print('\n')
print('Time Taken: ' + str(t_1 - t_0))
print('\n')


