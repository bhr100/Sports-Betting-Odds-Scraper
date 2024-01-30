from playwright.sync_api import sync_playwright
import os
import time
import csv

class BettingScraper:
    def __init__(self, url):
        self.url = url
        self.df = []

    def change_dir(self):
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        current_path_file = os.getcwd()
        return current_path_file
    
    def write_append_data(self, data):
        with open(self.change_dir()+'\\18bet.csv',mode='w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(['Leagues', 'Date', 'Time', 'HomeTeam', 'AwayTeam', 'MatchResult','OverUnderGoals','AltOverGoals','AltUnderGoals','BothTeamstoScore',
                             'ToWinEitherHalf','TotalGoalsOddEven','CleanSheet','NoCleanSheet','HomeTeamtoScoreinBothHalves','AwayTeamtoScoreinBothHalves','FirstHalfOverUnder',
                             'YesBothtoScoreTotalGoalsOverUnder25','NoBothtoScoreTotalGoalsOverUnder25','YesBothtoScoreTotalGoalsOverUnder35','NoBothtoScoreTotalGoalsOverUnder35',
                             'YesBothtoScoreTotalGoalsOverUnder45','NoBothtoScoreTotalGoalsOverUnder45'])
            writer.writerows(data)
    
    def scrape_data(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto(self.url)
            page.set_viewport_size({'width': 1920, 'height': 1080})
            page.wait_for_selector('body')
            leagues = page.locator('div[class="featured-league-item"]').all()

            def return_selector(text):
                try:
                    all_text = page.locator('div[class*="market-title-label"]').all_inner_texts()
                    idx = all_text.index(text)
                    selector = all_markets[idx]
                except ValueError:
                    selector = 'not specified'
                return selector
            
            for league in leagues:
                league_name = league.locator('div[class="featured-league-label"]').inner_text()
                league.click()
                time.sleep(2)
                if page.locator('div[class="nav-item all"]').count():
                    page.locator('div[class="nav-item all"]').click()
                else:
                    # there's no events:
                    break
     
                dates = page.locator('div[class="date-item"]').all()
                 
                for date_item in dates:
                    time.sleep(2)
                    if page.locator('div[class="no-events-message text-center"]').count():
                        page.reload()
                        page.wait_for_selector('span[class*="date-title"]',timeout=5000)
                        Date = date_item.locator('span[class*="date-title"]').inner_text()
                        matches = date_item.locator('div[class*="event-container"]').all()
                    else:
                        try:
                            Date = date_item.locator('span[class*="date-title"]').inner_text()
                            matches = date_item.locator('div[class*="event-container"]').all()
                        except:
                            page.reload()
                            page.wait_for_selector('span[class*="date-title"]',timeout=5000)
                            Date = date_item.locator('span[class*="date-title"]').inner_text()
                            matches = date_item.locator('div[class*="event-container"]').all()
                        
                    for match in matches:
                        time.sleep(2)
                        if page.locator('div[class="no-events-message text-center"]').count():
                            page.reload()
                            page.wait_for_selector('div[class*="event-participants"]',timeout=5000)
                            Time = match.locator('div[class="date-time-container"]').inner_text()
                            home_team = match.locator('div[class*="event-team-home"]').inner_text()
                            away_team = match.locator('div[class*="event-team-away"]').inner_text()
                            match.locator('div[class*="event-participants"]').click()
                        else:
                            try:
                                page.wait_for_selector('div[class*="event-participants"]')
                                Time = match.locator('div[class="date-time-container"]').inner_text()
                                home_team = match.locator('div[class*="event-team-home"]').inner_text()
                                away_team = match.locator('div[class*="event-team-away"]').inner_text()
                                match.locator('div[class*="event-participants"]').click()
                            except:
                                page.reload()
                                page.wait_for_selector('div[class*="event-participants"]',timeout=5000)
                                Time = match.locator('div[class="date-time-container"]').inner_text()
                                home_team = match.locator('div[class*="event-team-home"]').inner_text()
                                away_team = match.locator('div[class*="event-team-away"]').inner_text()
                                match.locator('div[class*="event-participants"]').click()
                        try:
                            page.wait_for_selector('div[class*="market-list"]')
                        except:
                            page.reload()
                            time.sleep(5)
                        page.keyboard.press('End')
                        time.sleep(2)

                        all_markets = page.locator('div[class="event-market es-market-container"]').all()
                        

                        market = return_selector(text='Match Result')
                        if market != 'not specified':
                            odds = market.locator('div[class*="odd-container"]').all()
                            match_result = " | ".join(
                                        [odd.locator('div[class*="odd-holder-label"]').inner_text() + "   " +
                                        odd.locator('div[class*="market-odd_odd"]').inner_text() for odd in odds])
                        else:
                            match_result = 'not specified'

                        market = return_selector(text='Over/Under Goals')
                        if market != 'not specified':
                            odds = market.locator('div[class*="odd-container"]').all_inner_texts()
                            OverUnderGoals = ' | '.join(['  '.join(odd.split('\n')) for odd in odds])
                        else:
                            OverUnderGoals = 'not specified'

                        market = return_selector(text='Alt. Over/Under Goals')
                        if market != 'not specified':
                            odds = market.locator('div[class*="odd-container"]').all_inner_texts()
                            AltOverGoals=[]
                            AltUnderGoals = []
                            for i in range(len(odds)+1):
                                try:
                                    if i %2 == 0:
                                        AltOverGoals.append(odds[i])
                                    else:
                                        AltUnderGoals.append(odds[i])
                                except IndexError:
                                    pass
                            AltOverGoals = ' | '.join(['   '.join(over.split('\n')) for over in AltOverGoals])
                            AltUnderGoals = ' | '.join(['   '.join(under.split('\n'))  for under in AltUnderGoals])
                        else:
                            AltOverGoals = 'not specified'
                            AltUnderGoals = 'not specified'

                        market = return_selector(text='Both Teams to Score')
                        if market != 'not specified':
                            odds = market.locator('div[class*="odd-container"]').all_inner_texts()
                            BothTeamstoScore = ' | '.join(['  '.join(odd.split('\n')) for odd in odds])
                        else:
                            BothTeamstoScore = 'not specified'

                        market = return_selector(text='To Win Either Half')
                        if market != 'not specified':
                            odds = market.locator('div[class*="odd-container"]').all_inner_texts()
                            ToWinEitherHalf = ' | '.join(['  '.join(odd.split('\n')) for odd in odds])
                        else:
                            ToWinEitherHalf = 'not specified'

                        market = return_selector(text='Both Teams to Score')
                        if market != 'not specified':
                            odds = market.locator('div[class*="odd-container"]').all_inner_texts()
                            TotalGoalsOddEven = ' | '.join(['  '.join(odd.split('\n')) for odd in odds])
                        else:
                            TotalGoalsOddEven = 'not specified'                           
                        
                        market = return_selector(text='Clean Sheet')
                        if market != 'not specified':
                            odds = market.locator('div[class*="odd-container"]').all_inner_texts()
                            CleanSheet = home_team+'   '+ odds[0]+' | '+away_team+'   '+odds[2]
                            NoCleanSheet = home_team+'   '+ odds[1]+' | '+away_team+'   '+odds[-1]
                        else:
                            CleanSheet = 'not specified'       
                            NoCleanSheet = 'not specified'      

                        market = return_selector(text='Home Team to Score in Both Halves')
                        if market != 'not specified':
                            odds = market.locator('div[class*="odd-container"]').all_inner_texts()
                            HomeTeamtoScoreinBothHalves = ' | '.join(['  '.join(odd.split('\n')) for odd in odds])
                        else:
                            HomeTeamtoScoreinBothHalves = 'not specified' 

                        market = return_selector(text='Away Team to Score in Both Halves')
                        if market != 'not specified':
                            odds = market.locator('div[class*="odd-container"]').all_inner_texts()
                            AwayTeamtoScoreinBothHalves = ' | '.join(['  '.join(odd.split('\n')) for odd in odds])
                        else:
                            AwayTeamtoScoreinBothHalves = 'not specified' 

                        market = return_selector(text='1st Half - Over/Under Goals')
                        if market != 'not specified':
                            odds = market.locator('div[class*="odd-container"]').all_inner_texts()
                            FirstHalfOverUnder = ' | '.join(['  '.join(odd.split('\n')) for odd in odds])
                        else:
                            FirstHalfOverUnder = 'not specified' 

                        market = return_selector(text='Both to Score & Total Goals 2.5')
                        if market != 'not specified':
                            odds = market.locator('div[class*="odd-container"]').all_inner_texts()
                            YesBothtoScoreTotalGoalsOverUnder25 = 'Yes'+'   '+ '  '.join(odds[0].split('\n'))+' | '+'  '.join(odds[1].split('\n'))
                            NoBothtoScoreTotalGoalsOverUnder25 = 'No'+'   '+ '  '.join(odds[2].split('\n'))+' | '+'  '.join(odds[3].split('\n'))
                        else:
                            YesBothtoScoreTotalGoalsOverUnder25 = 'not specified' 
                            NoBothtoScoreTotalGoalsOverUnder25 = 'not specified' 

                        market = return_selector(text='Both to Score & Total Goals 3.5')
                        if market != 'not specified':
                            odds = market.locator('div[class*="odd-container"]').all_inner_texts()
                            YesBothtoScoreTotalGoalsOverUnder35 = 'Yes'+'   '+ '  '.join(odds[0].split('\n'))+' | '+'  '.join(odds[1].split('\n'))
                            NoBothtoScoreTotalGoalsOverUnder35 = 'No'+'   '+ '  '.join(odds[2].split('\n'))+' | '+'  '.join(odds[3].split('\n'))
                        else:
                            YesBothtoScoreTotalGoalsOverUnder35 = 'not specified' 
                            NoBothtoScoreTotalGoalsOverUnder35 = 'not specified' 

                        market = return_selector(text='Both to Score & Total Goals 4.5')
                        if market != 'not specified':
                            odds = market.locator('div[class*="odd-container"]').all_inner_texts()
                            YesBothtoScoreTotalGoalsOverUnder45 = 'Yes'+'   '+ '  '.join(odds[0].split('\n'))+' | '+'  '.join(odds[1].split('\n'))
                            NoBothtoScoreTotalGoalsOverUnder45 = 'No'+'   '+ '  '.join(odds[2].split('\n'))+' | '+'  '.join(odds[3].split('\n'))
                        else:
                            YesBothtoScoreTotalGoalsOverUnder45 = 'not specified' 
                            NoBothtoScoreTotalGoalsOverUnder45 = 'not specified'

                        self.df.append([league_name, Date, Time, home_team, away_team, match_result,OverUnderGoals,AltOverGoals,AltUnderGoals,BothTeamstoScore,ToWinEitherHalf,TotalGoalsOddEven,
                                        CleanSheet,NoCleanSheet,HomeTeamtoScoreinBothHalves,AwayTeamtoScoreinBothHalves,FirstHalfOverUnder,YesBothtoScoreTotalGoalsOverUnder25,NoBothtoScoreTotalGoalsOverUnder25,
                                        YesBothtoScoreTotalGoalsOverUnder35,NoBothtoScoreTotalGoalsOverUnder35,YesBothtoScoreTotalGoalsOverUnder45,NoBothtoScoreTotalGoalsOverUnder45])
                        print([league_name, Date, Time, home_team, away_team, match_result,OverUnderGoals,AltOverGoals,AltUnderGoals,BothTeamstoScore,ToWinEitherHalf,TotalGoalsOddEven,
                               CleanSheet,NoCleanSheet,HomeTeamtoScoreinBothHalves,AwayTeamtoScoreinBothHalves,FirstHalfOverUnder,YesBothtoScoreTotalGoalsOverUnder25,NoBothtoScoreTotalGoalsOverUnder25,
                               YesBothtoScoreTotalGoalsOverUnder35,NoBothtoScoreTotalGoalsOverUnder35,YesBothtoScoreTotalGoalsOverUnder45,NoBothtoScoreTotalGoalsOverUnder45])
                        print('=='*50)
                        page.go_back()
                        time.sleep(1)
                        
                        


                # break

            self.write_append_data(self.df)

if __name__ == "__main__":
    start_time = time.time()

    scraper = BettingScraper(url='https://18bet.com/sports/soccer?tab=featured')
    scraper.scrape_data()

    end_time = time.time()
    print('Time Running (min):', (end_time - start_time) / 60)
