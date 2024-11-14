from ratelimit import limits, sleep_and_retry
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time
import os



# List of fighter names (as they appear in the URL)
fighters = [
    'kyung-ho-kang',
    'max-holloway',
    'luke-rockhold',
    'brad-tavares',
    'tj-dillashaw',
    'derek-brunson',
    'louis-smolka',
    'vinc-pichel',
    'beneil-dariush',
    'donald-cerrone',
    'darren-elkins',
    'alex-caceres',
    'eddie-wineland',
    'nikita-krylov',
    'jose-aldo',
    'john-makdessi',
    'alan-patrick',
    'kevin-lee',
    'neil-magny',
    'erick-silva',
    'charles-oliveira',
    'francisco-trinaldo',
    'jesse-ronson',
    'zubaira-tukhugov',
    'douglas-silva-de-andrade',
    'sara-mcmann',
    'robert-whittaker',
    'stephen-thompson',
    'alexis-davis',
    'jessica-eye',
    'raphael-assuncao',
    'pedro-munhoz',
    'aljamain-sterling',
    'cody-gibson',
    'alexander-gustafsson',
    'michael-johnson',
    'gunnar-nelson',
    'ilir-latifi',
    'claudio-silva',
    'robbie-lawler',
    'ovince-saint-preux',
    'kelvin-gastelum',
    'raquel-pennington',
    'jessica-andrade',
    'sean-strickland',
    'daniel-pineda',
    'mauricio-rua',
    'leonardo-santos',
    'thiago-santos',
    'clay-guida',
    'rani-yahya',
    'dustin-poirier',
    'miesha-tate',
    'edson-barboza',
    'rafael-dos-anjos',
    'jorge-masvidal',
    'chas-skelly',
    'derrick-lewis',
    'glover-teixeira',
    'jon-jones',
    'jim-miller',
    'andre-fili',
    'tim-elliott',
    'matt-brown',
    'tim-means',
    'ed-herman',
    'zak-cummings',
    'michael-chiesa',
    'tony-ferguson',
    'aaron-phillips',
    'warlley-alves',
    'marcos-rogerio-de-lima',
    'drew-dober',
    'krzysztof-jotko',
    'andrei-arlovski',
    'cub-swanson',
    'diego-ferreira',
    'aleksei-oleinik',
    'jake-matthews',
    'dan-hooker',
    'chris-weidman',
    'uriah-hall',
    'rob-font',
    'frankie-edgar',
    'bobby-green',
    'brian-ortega',
    'gilbert-burns',
    'joanna-jedrzejczyk',
    'lauren-murphy',
    'sam-alvey',
    'colby-covington',
    'damon-jackson',
    'santiago-ponzinibbio',
    'amanda-nunes',
    'dominick-cruz',
    'jan-blachowicz',
    'charles-rosa',
    'christos-giagos',
    'leon-edwards',
    'yair-rodriguez',
    'alejandro-perez',
    'gabriel-benitez',
    'guido-cannetti',
    'marlon-vera',
    'dooho-choi',
    'ashlee-evans-smith',
    'carla-esparza',
    'rose-namajunas',
    'jessica-penne',
    'felice-herrig',
    'tecia-torres',
    'angela-hill',
    'nate-diaz',
    'bryan-barberena',
    'henry-cejudo',
    'renato-moicano',
    'jake-collier',
    'cody-garbrandt',
    'jared-cannonier',
    'makwan-amirkhani',
    'holly-holm',
    'germaine-de-randamie',
    'alex-oliveira',
    'julianna-pena',
    'shamil-abdurakhimov',
    'maryna-moroz',
    'taylor-lapilus',
    'islam-makhachev',
    'darren-till',
    'elizeu-zaleski-dos-santos',
    'nicolas-dalby',
    'arnold-allen',
    'kamaru-usman',
    'vicente-luque',
    'michelle-waterson',
    'cortney-casey',
    'scott-holtzman',
    'misha-cirkunov',
    'joaquim-silva',
    'matheus-nicolau',
    'danny-roberts',
    'ryan-hall',
    'julian-erosa',
    'chris-gruetzemacher',
    'court-mcgee',
    'karolina-kowalkiewicz',
    'valentina-shevchenko',
    'francis-ngannou',
    'alex-morono',
    'randy-brown',
    'mike-jackson',
    'mickey-gall',
    'anthony-smith',
    'davey-grant',
    'curtis-blaydes',
    'marcin-tybura',
    'damir-hadzovic',
    'alessio-di-chirico',
    'josh-emmett',
    'ion-cutelaba',
    'belal-muhammad',
    'khalil-rountree-jr.',
    'tatiana-suarez',
    'lando-vannata',
    'katlyn-chookagian',
    'devin-clark',
    'chase-sherman',
    'max-griffin',
    'marvin-vettori',
    'jack-hermansson',
    'rick-glenn',
    'lina-lansberg',
    'brandon-moreno',
    'ketlen-vieira',
    'marc-diakiese',
    'claudio-puelles',
    'alexa-grasso',
    'alexander-volkov',
    'abdul-razak-alhassan',
    'alexander-volkanovski',
    'tyson-pedro',
    'matt-schnell',
    'ashley-yoder',
    'gerald-meerschaert',
    'shane-burgos',
    'jj-aldrich',
    'paul-craig',
    'irene-aldana',
    'niko-price',
    'drakkar-klose',
    'alexandre-pantoja',
    'chan-sung-jung',
    'volkan-oezdemir',
    'ricardo-ramos',
    'gavin-tucker',
    'gina-mazany',
    'aiemann-zahabi',
    'cynthia-calvillo',
    'paulo-costa',
    'lucie-pudilova',
    'marlon-moraes',
    'brian-kelleher',
    'deiveson-figueiredo',
    'frank-camacho',
    'ji-yeon-kim',
    'dominick-reyes',
    'jared-gordon',
    'justin-gaethje',
    'cody-stamann',
    'trevin-giles',
    'amanda-lemos',
    'eryk-anders',
    'calvin-kattar',
    'aleksandar-rakic',
    'alex-reyes',
    'poliana-botelho',
    'nasrat-haqparast',
    'ramazan-emeev',
    'aspen-ladd',
    'karl-roberson',
    'jessica-rose-clark',
    'shane-young',
    'tai-tuivasa',
    'muslim-salikhov',
    'song-yadong',
    'roxanne-modafferi',
    'sean-omalley',
    'montana-de-la-rosa',
    'gillian-robertson',
    'benito-lopez',
    'alex-perez',
    'merab-dvalishvili',
    'julian-marquez',
    'michal-oleksiejczuk',
    'matt-frevola',
    'brandon-davis',
    'dan-ige',
    'julio-arce',
    'cory-sandhagen',
    'priscila-cachoeira',
    'polyana-viana',
    'israel-adesanya',
    'steven-peterson',
    'geoff-neal',
    'marcin-prachnio',
    'mackenzie-dern',
    'alexander-hernandez',
    'hakeem-dawodu',
    'magomed-ankalaev',
    'ricky-simon',
    'andrea-lee',
    'molly-mccann',
    'sijara-eubanks',
    'nathaniel-wood',
    'petr-yan',
    'michael-trizano',
    'brad-katona',
    'bryce-mitchell',
    'blagoy-ivanov',
    'said-nurmagomedov',
    'kurt-holobaugh',
    'raoni-barcelos',
    'jennifer-maia',
    'abu-azaitar',
    'khalid-taha',
    'kevin-holland',
    'montel-jackson',
    'matt-sayles',
    'andre-ewell',
    'marina-rodriguez',
    'ryan-spann',
    'augusto-sakai',
    'mayra-bueno-silva',
    'jalin-turner',
    'jonathan-martinez',
    'thiago-moises',
    'maycee-barber',
    'devonte-smith',
    'johnny-walker',
    'sergei-pavlovich',
    'vince-morales',
    'pannie-kianzad',
    'macy-chiasson',
    'edmen-shahbazyan',
    'antonina-shevchenko',
    'julija-stoliarenko',
    'roosevelt-roberts',
    'chris-gutierrez',
    'sodiq-yusuff',
    'jimmy-crute',
    'kai-kara-france',
    'damir-ismagulov',
    'kyle-nelson',
    'dwight-grant',
    'greg-hardy',
    'ariane-lipski',
    'alonzo-menifield',
    'mario-bautista',
    'anthony-hernandez',
    'taila-santos',
    'jairzinho-rozenstruik',
    'felipe-colares',
    'rogerio-bontorin',
    'raulian-paiva',
    'kron-gracie',
    'joel-alvarez',
    'grant-dawson',
    'nicolae-negumereanu',
    'mike-grundy',
    'kennedy-nzechukwu',
    'sabina-mazo',
    'randy-costa',
    'arman-tsarukyan',
    'alen-amedovski',
    'seungwoo-choi',
    'movsar-evloev',
    'alex-da-silva',
    'rafael-fiziev',
    'takashi-sato',
    'virna-jandiroba',
    'mike-davis',
    'serghei-spivac',
    'marc-andre-barriault',
    'luana-carolina',
    'viviane-araujo',
    'austin-hubbard',
    'charles-jourdain',
    'michel-pereira',
    'sergey-khandozhko',
    'deron-winn',
    'journey-newson',
    'dalcha-lungiambula',
    'amanda-ribas',
    'julia-avila',
    'wellington-turman',
    'miranda-granger',
    'hannah-goldy',
    'rodolfo-vieira',
    'ciryl-gane',
    'kazula-vargas',
    'jun-yong-park',
    'karol-rosa',
    'lerone-murphy',
    'ottman-azaitar',
    'fares-ziam',
    'tristan-connelly',
    'miles-johns',
    'askar-askarov',
    'ariane-carnelossi',
    'tyson-nam',
    'mark-madsen',
    'makhmud-muradov',
    'giga-chikadze',
    'jack-shore',
    'justin-tafa',
    'maki-pitolo',
    'brad-riddell',
    'jamie-mullarkey',
    'zarah-fairn',
    'bruno-silva',
    'miguel-baeza',
    'jonathan-pearce',
    'diana-belbita',
    'sean-woodson',
    'sean-brady',
    'brendan-allen',
    'tanner-boser',
    'loma-lookboonmee',
    'dontale-mayes',
    'roman-kopylov',
    'abubakar-nurmagomedov',
    'andre-muniz',
    'tracy-cortez',
    'billy-quarantillo',
    'joe-solecki',
    'mallory-martin',
    'chase-hooper',
    'punahele-soriano',
    'da-un-jung',
    'junyong-park',
    'omar-morales',
    'ode-osbourne',
    'aleksa-camur',
    'jamahal-hill',
    'tony-gravely',
    'herbert-burns',
    'nate-landwehr',
    'khaos-williams',
    'austin-lingo',
    'youssef-zalal',
    'shanna-young',
    'daniel-rodriguez',
    'josh-culibao',
    'norma-dumont',
    'darrick-minner',
    'kyler-phillips',
    'steve-garcia',
    'tj-brown',
    'jamall-emmers',
    'david-dvorak',
    'philipe-lins',
    'ike-villanueva',
    'rodrigo-nascimento',
    'gabe-green',
    'brandon-royval',
    'mariya-agapova',
    'zarrukh-adashev',
    'kyle-daukaus',
    'jason-witt',
    'kay-hansen',
    'jinh-yu-frey',
    'jiri-prochazka',
    'maxim-grishin',
    'zhalgas-zhumagulov',
    'mounir-lazzez',
    'khamzat-chimaev',
    'andreas-michailidis',
    'modestas-bukauskas',
    'roman-dolidze',
    'malcolm-gordon',
    'amir-albazi',
    'rhys-mckee',
    'jai-herbert',
    'tom-aspinall',
    'niklas-stolze',
    'john-castaneda',
    'johnny-munoz',
    'nate-maness',
    'cody-durden',
    'joaquin-buckley',
    'alexander-munoz',
    'danny-chavez',
    'chris-daukaus',
    'parker-porter',
    'tony-kelley',
    'jordan-wright',
    'matthew-semelsberger',
    'timur-valiev',
    'trevin-jones',
    'bill-algeo',
    'kevin-croom',
    'alexandr-romanov',
    'tj-laramie',
    'ludovit-klein',
    'william-knight',
    'danilo-marques',
    'cameron-else',
    'dusko-todorovic',
    'nassourdine-imavov',
    'dricus-du-plessis',
    'alan-baudot',
    'ilia-topuria'
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
df.to_csv(r'C:\Users\ashle\Documents\Projects\ufc\data\fighters.csv', index=False)

