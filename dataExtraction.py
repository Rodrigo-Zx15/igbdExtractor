from requests import post
import json
from time import sleep
from datetime import datetime
from datetime import timedelta
import pandas as pd
import os.path
def getCredentials():
    twitchCreds = pd.read_csv('./apiAccess.csv',sep=';')
    #clientSecret = twitchCreds['client_secret'][0].strip()
    clientID = twitchCreds['client_id'][0].strip()
    creds = []
    creds.append(clientID)
    data = ""
    if not os.path.exists('./apiToken.json'):
        refreshCredentials()
    with open('apiToken.json',encoding="utf-8") as file:   
        data = file.read()
    jsonResponse = json.loads(data)
    prevTimestamp = datetime.strptime(jsonResponse['timestamp'],"%Y-%m-%d %H:%M:%S")
    deltaT = datetime.now() - prevTimestamp
    if deltaT > timedelta(hours=1):
        refreshCredentials()
    accessToken = jsonResponse['access_token']
    creds.append(accessToken)
    return creds
    
def refreshCredentials():
    twitchCreds = pd.read_csv('./apiAccess.csv',sep=';')
    clientSecret = twitchCreds['client_secret'][0].strip()
    clientID = twitchCreds['client_id'][0].strip()
    response = post(f'https://id.twitch.tv/oauth2/token?client_id={clientID}&client_secret={clientSecret}&grant_type=client_credentials')
    rJson = response.json()
    #a timestamp serve para ajudar a gerar outro access token caso o anterior tenha expirado
    rJson['timestamp'] = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
    with open('./apiToken.json', 'w', encoding="utf-8") as file:
        json.dump(rJson,file,indent=4)

def getGames(accessToken,currentOffset,clientID):
    #o objetivo do "where" abaixo na request é para diminuir e garantir certa qualidade nos dados:
    # *apenas jogos completos são considerados (incluindo remakes e remasters), filtrados através da categoria - DLCs, mods, expansões e pacotes são ignorados;
    # *apenas os games lançados nos últimos 20 anos são considerados;
    # *plataformas mobile (celulares, tablets) e plataformas esotéricas (consoles antigos, arcades que ainda recebiam jogos pós anos 2000) são ignorados;
    # *o filtro de keywords serve para "desinflar" o tamanho dos dados de jogos para PC, excluindo fangames e homebrews
    response = post('https://api.igdb.com/v4/games', **{'headers': {'Client-ID': f'{clientID}', 'Authorization': f'{accessToken}'},\
                                                              'data': f'fields name, genres, game_modes, category, platforms, first_release_date, version_parent;\
                                                                where category = (0,8,9) & first_release_date>946692060 & version_parent=null & genres != null & platforms != (34,82,238,405,74,39,55) & keywords.name != ("fangame","nonofficial","homebrew");limit 500; offset {currentOffset};'})
    data = response.json()
    #print(data)
    return data

#o propósito dessa função é captar tabelas que auxiliem no enriquecimento dos dados de algum modo como, por exemplo, a tabela de consoles/plataformas
def getAuxiliaryTables(accessToken, clientID, tableName):
    response = post(f'https://api.igdb.com/v4/{tableName}', **{'headers': {'Client-ID': f'{clientID}', 'Authorization': f'{accessToken}'},\
                                                              'data': f'fields name, id;limit 500;'})
    data = response.json()
    return data

def main():
    creds = getCredentials()
    clientID = creds[0]
    accessToken = creds[1]
    accessToken = "Bearer " + accessToken
    accessToken = accessToken.strip()

    auxTables = ['platforms', 'genres', 'game_modes']

    for table in auxTables:
        rawTable = getAuxiliaryTables(accessToken, clientID, table)
        df = pd.DataFrame(rawTable)
        df.to_csv(f'./{table}.csv',index=False)

    resCount = post('https://api.igdb.com/v4/games/count', **{'headers': {'Client-ID': f'{clientID}', 'Authorization': f'{accessToken}'},\
                                                              'data': 'where category = (0,8,9) & first_release_date>946692060 & version_parent=null & genres != null & platforms != (34,82,238,405,74,39,55) & keywords.name != ("fangame","nonofficial","homebrew");'})
    
    gamesCount = resCount.json()['count']
    print(gamesCount)
    currentOffset = 0;
    
    while currentOffset <= gamesCount:
        array = []
        rawGames = getGames(accessToken,currentOffset,clientID)
        for rawGame in rawGames:
        #o objeto abaixo é criado de modo a uniformizar as linhas - houve casos de games sem game_mode ou poucos game_modes
        #acabarem com a ordem errada de colunas no pandas.
            game = {
                'id': 00000,
                'category': -1,
                'first_release_date':0000000,
                'game_modes': [-1],
                'genres':[-1],
                'name': "N/A",
                'platforms':[-1]

            }
            rawKeys = list(rawGame.keys())
            for key in rawKeys:
                game[key] = rawGame[key]
            array.append(game)
        #print(currentOffset)
        #o sleep serve apenas para espaçar as requests e não tomar IP ban da API.
        sleep(3)
        df = pd.DataFrame(array)
        if currentOffset == 0:
            df.to_csv('./rawGamesData.csv',mode='a',index=False,na_rep="empty")
        else:
            df.to_csv('./rawGamesData.csv',mode='a',index=False,header=False,na_rep="empty")
        #o offset serve para paginar as requests - há um limite de "tamanho" de request na API
        currentOffset = currentOffset+500
        print(currentOffset)
        print(df.head(3))
    #print(len(data))
if __name__ == "__main__":
    inputClient = input('Insira seu client id:\n')
    inputSecret = input('Insira seu client secret:\n')
    df = pd.DataFrame(data=[{
        'client_id': inputClient,
        'client_secret': inputSecret}])
    df.to_csv('./apiAccess.csv',sep=';',index=False)
    main()
    