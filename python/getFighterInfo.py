from ratelimit import limits, sleep_and_retry
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time
import os


# List of fighter names (as they appear in the URL)
fighters = [
    'ericka-almeida',
    'ricardo-almeida',
    'marcus-davis',
    'phil-davis',
    'rick-davis',
    'junior-hernandez',
    'noe-hernandez',
    'justin-jones',
    'marcus-jones',
    'paul-jones',
    'dan-miller',
    'jason-miller',
    'phillip-miller',
    'albert-morales',
    'dante-rivera',
    'francisco-rivera',
    'jorge-rivera',
    'eddie-sanchez',
    'joby-sanchez',
    'julian-sanchez',
    'roberto-sanchez',
    'anderson-dos-santos',
    'antonio-dos-santos',
    'rayanne-dos-santos',
    'justin-edwards',
    'te-edwards',
    'yves-edwards',
    'renzo-gracie',
    'roger-gracie',
    'rolles-gracie',
    'royce-gracie',
    'gerald-harris',
    'phil-harris',
    'jorge-lopez',
    'steve-lopez',
    'diego-nunes',
    'kevin-souza',
    'bruno-souza',
    'amilcar-alves',
    'andy-anderson',
    'lowell-anderson',
    'jessica-rose-clark',
    'laverne-clark',
    'logan-clark',
    'alexandre-ferreira',
    'lewis-gonzalez',
    'king-green',
    'forrest-griffin',
    'tyson-griffin',
    'mark-hughes',
    'matt-hughes',
    'jeff-hughes',
    'jason-macdonald',
    'rob-macdonald',
    'ruslan-magomedov',
    'danny-mitchell',
    'david-mitchell',
    'shane-nelson',
    'luis-ramos',
    'vernon-ramos',
    'milton-vieira',
    'donny-walker',
    'gilbert-aldana',
    'hector-aldana',
    'sean-alvarez',
    'alex-andrade',
    'viscardi-andrade',
    'kevin-burns',
    'marcio-cruz',
    'josh-ferguson',
    'kevin-ferguson',
    'cj-fernandes',
    'colin-fletcher',
    'eddie-gordon',
    'tj-grant',
    'mark-hall',
    'dan-hardy',
    'cory-hendricks',
    'josh-hendricks',
    'geane-herrera',
    'paul-herrera',
    'corey-hill',
    'trent-jenkins',
    'phil-johns',
    'joe-jordan',
    'kevin-jordan',
    'steve-kennedy',
    'tim-kennedy',
    'john-lewis',
    'bernardo-magalhaes',
    'vinny-magalhaes',
    'antonio-mendes',
    'mario-miranda',
    'joe-moreira',
    'mark-munoz',
    'tom-murphy',
    'kazuhiro-nakamura',
    'chris-price',
    'dorian-price',
    'hector-ramirez',
    'thomas-ramirez',
    'polo-reyes',
    'alessandro-ricci',
    'mike-ricci',
    'alvin-robinson',
    'colin-robinson',
    'mark-robinson',
    'aaron-rosa',
    'jesse-sanders',
    'chris-saunders',
    'townsend-saunders',
    'alex-soto',
    'greg-soto',
    'jesse-taylor',
    'paul-taylor',
    'nick-thompson',
    'oli-thompson',
    'brandon-vera',
    'kyle-watson',
    'tom-watson',
    'walel-watson',
    'vernon-white',
    'aaron-wilkinson',
    'mike-wilkinson',
    'chris-wilson',
    'jason-young',
    'scott-adams',
    'ildemar-alcantara',
    'houston-alexander',
    'sultan-aliev',
    'matt-arroyo',
    'junior-assuncao',
    'chris-avila',
    'josh-barnett',
    'pat-barry',
    'dean-barry',
    'joey-beltran',
    'arjan-bhullar',
    'kb-bhullar',
    'kyle-bradley',
    'paul-bradley',
    'fernando-bruno',
    'steve-bruno',
    'bubba-bush',
    'todd-butler',
    'cheyanne-buys',
    'chris-camozzi',
    'kevin-casey',
    'gil-castillo',
    'ernest-chavez',
    'chris-cope',
    'kit-cope',
    'randy-couture',
    'ryan-couture',
    'andrew-craig',
    'jeff-curran',
    'kailin-curran',
    'jason-day',
    'edilberto-de-oliveira',
    'jorge-de-oliveira',
    'nick-diaz',
    'doug-evans',
    'jason-fairn',
    'maiquel-falcao',
    'glaico-franca',
    'hermes-franca',
    'zane-frazier',
    'justin-frazier',
    'sam-fulton',
    'travis-fulton',
    'lance-gibson',
    'ulysses-gomez',
    'kendall-grove',
    'neil-grove',
    'fabio-gurgel',
    'jorge-gurgel',
    'horacio-gutierrez',
    'dan-henderson',
    'dave-herman',
    'harold-howard',
    'enson-inoue',
    'brock-jardine',
    'keith-jardine',
    'daniel-kelly',
    'paul-kelly',
    'yuki-kondo',
    'dan-lauzon',
    'justin-lawrence',
    'cung-le',
    'dileno-lopes',
    'nate-loughran',
    'jon-madsen',
    'eliot-marshall',
    'terry-martin',
    'gan-mcgee',
    'antonio-mckee',
    'cody-mckenzie',
    'tim-mckenzie',
    'anistavio-medeiros',
    'brandon-melendez',
    'ashkan-mokhtarian',
    'suman-mokhtarian',
    'peggy-morgan',
    'sammy-morgan',
    'brad-morris',
    'scott-morris',
    'carlos-newton',
    'jeff-newton',
    'minotauro-nogueira',
    'rogerio-nogueira',
    'jake-obrien',
    'tj-obrien',
    'tito-ortiz',
    'damacio-page',
    'rousimar-palhares',
    'tulio-palhares',
    'claude-patrick',
    'hernani-perpetuo',
    'thiago-perpetuo',
    'wagner-prado',
    'jimmy-quinlan',
    'gideon-ray',
    'johnny-rhodes',
    'kenny-robertson',
    'ricardo-romero',
    'jake-rosholt',
    'jared-rosholt',
    'marco-ruas',
    'rodrigo-ruas',
    'eddie-ruiz',
    'sean-salmon',
    'boston-salmon',
    'joseph-sandoval',
    'jorge-santiago',
    'yuki-sasaki',
    'matt-serra',
    'nick-serra',
    'adrian-serrano',
    'fredy-serrano',
    'frank-shamrock',
    'ken-shamrock',
    'tony-sims',
    'wes-sims',
    'joe-son',
    'sean-spencer',
    'joe-stevenson',
    'kyle-stewart',
    'curtis-stout',
    'sam-stout',
    'john-teixeira',
    'din-thomas',
    'ryan-thomas',
    'matt-van-buren',
    'cain-velasquez',
    'david-velasquez',
    'danillo-villefort',
    'yuri-villefort',
    'crafton-wallace',
    'rodney-wallace',
    'patrick-walsh',
    'richard-walsh',
    'andy-wang',
    'sai-wang',
    'kenichi-yamamoto',
    'norifumi-yamamoto',
    'jianping-yang',
    'antonio-silva',
    'assuerio-silva',
    'jay-silva',
    'thiago-silva',
    'wanderlei-silva',
    'manuel-rodriguez',
    'paul-rodriguez',
    'ricco-rodriguez',
    'ronaldo-rodriguez',
    'colton-smith',
    'gilbert-smith',
    'maurice-smith',
    'patrick-smith',
    'scott-smith',
    'trevor-smith',
    'cole-smith',
    'damarques-johnson',
    'jordan-johnson',
    'lavar-johnson',
    'tim-johnson',
    'adriano-santos',
    'bruno-santos',
    'iliarde-santos',
    'mairon-santos',
    'andre-roberts',
    'buddy-roberts',
    'daniel-roberts',
    'david-roberts',
    'joey-roberts',
    'ryan-roberts',
    'tyrone-roberts',
    'ednaldo-oliveira',
    'rafaello-oliveira',
    'david-lee',
    'james-lee',
    'vaughan-lee',
    'patrick-williams',
    'pete-williams',
    'tedd-williams',
    'cole-williams',
    'danny-martinez',
    'henry-martinez',
    'rainy-martinez',
    'eugene-jackson',
    'jeremy-jackson',
    'kevin-jackson',
    'rampage-jackson',
    'alex-torres',
    'anthony-torres',
    'miguel-torres',
    'ronys-torres',
    'mike-brown',
    'todd-brown',
    'edgar-garcia',
    'leonard-garcia',
    'danny-abbadi',
    'david-abbott',
    'daichi-abe',
    'papy-abedi',
    'sam-adkins',
    'nick-agallar',
    'marcelo-aguiar',
    'yoshihiro-akiyama',
    'rostem-akman',
    'john-albert',
    'wes-albritton',
    'alfonso-alcarez',
    'jim-alers',
    'john-alessio',
    'royce-alger',
    'benny-alloway',
    'mostapha-al-turk',
    'adlan-amagov',
    'matt-andersen',
    'jermaine-andre',
    'dylan-andrews',
    'reese-andy',
    'collin-anglin',
    'yoji-anjo',
    'zu-anyanwu',
    'romie-aram',
    'cesar-arzamendia',
    'ben-askren',
    'rich-attonito',
    'olivier-aubin-mercier',
    'pat-audinwood',
    'marcus-aurelio',
    'jessin-ayari',
    'niklas-backstrom',
    'izabela-badurek',
    'ali-bagautinov',
    'siyar-bahadurzada',
    'shamar-bailey',
    'scott-baker',
    'marcin-bandel',
    'antonio-banuelos',
    'david-baron',
    'phil-baroni',
    'dan-barrera',
    'carlos-barreto',
    'alexandre-barros',
    'stephen-bass',
    'shayna-baszler',
    'michel-batista',
    'chris-beal',
    'ariel-beck',
    'alan-belcher',
    'dave-beneteau',
    'deanna-bennett',
    'lance-benoist',
    'steve-berger',
    'keith-berish',
    'dieusel-berto',
    'allen-berube',
    'scott-bessac',
    'matt-bessette',
    'magomed-bibulatov'
]

# Base URL
base_url = 'https://www.ufc.com/athlete/'


def fetch_fighter_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response
    else:
        print(f"Failed to retrieve data for URL: {url}")
        return None

# Initialize a list to store the data
data = []

for fighter in fighters:
    url = f"{base_url}{fighter}"
    response = fetch_fighter_data(url)

    if response:
        print(f"Processing {fighter}")
        soup = BeautifulSoup(response.content, 'html.parser')
        bio_section = soup.find('div', id='tab-panel-1')
        
        if bio_section:
            fighter_data = {'Name': fighter.replace('-', ' ').title()}
            labels = bio_section.find_all('div', class_='c-bio__label')
            values = bio_section.find_all('div', class_='c-bio__text')
            
            for label, value in zip(labels, values):
                fighter_data[label.get_text(strip=True)] = value.get_text(strip=True)
            
            data.append(fighter_data)
        else:
            print(f"Bio section not found for {fighter}")

# Save to CSV
df = pd.DataFrame(data)
df.to_csv(r'C:\Users\ashle\Documents\Projects\ufc\data\fighterInfo.csv', index=False)

