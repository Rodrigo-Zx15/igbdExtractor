import pandas as pd
from datetime import UTC
from datetime import datetime
def main():
    df = pd.read_csv('rawGamesData.csv')
    dataDict = df.to_dict(orient='records')
    keys = ['genres','platforms','game_modes']
    gameList = []
    errorList = []
    for game in dataDict:
        try:
            game['release_date'] = datetime.fromtimestamp(game['first_release_date'], UTC).strftime("%Y-%m-%d")
        except:
            errorList.append(game)
            continue
        else:
            for key in keys:
                if type(game[key]) == type('string') and game[key][0] == '[':
                    
                    game[key] = game[key].replace('[','')
                    game[key] = game[key].replace(']','')
                    tagArray = game[key].split(',')
                    n = 1;
                    for tag in tagArray:
                        if key == 'platforms' and n > 5:
                            break
                        if n > 3 and key != 'platforms':
                            break
                        game[f'{key}{n}'] = tag.strip()
                        n = n+1
                    del game[key]
            gameList.append(game)
    df = pd.DataFrame(gameList)
    df.to_csv('gamesTreated.csv',index=False,na_rep="-1")
    errorDf = pd.DataFrame(errorList)
    errorDf.to_csv('errors.csv',index=False)
if __name__ == "__main__":
    main()