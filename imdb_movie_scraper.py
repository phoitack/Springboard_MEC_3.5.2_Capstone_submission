# Load Libraries
from bs4            import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen       as uReq  # Web client
from tqdm import tqdm

import pandas as pd
import numpy  as np

from tqdm import tqdm

# Webscraping function
def get_movie_details(movie_urls):
    
    # This determines the size of 'None' array to be later used 
    # in extending the empty list. If more information is needed, this 
    # number will change
    list_size_temp = 7
    
    # Add a sleep time (seconds) to not overload site
    sleep_time = 5
    
    count = 0    # Initialize Counter
    step  = 100  # Sleep every 100 items
    
    # Initialize arrays
    movie_title     = []
    imdb_score      = []
    meta_score      = []
    mpaa_rating     = []
    genres          = []
    
    budget          = []
    opening_weekend = []
    gross_usa       = []
    gross_world     = []
    rel_date        = []
    country         = []
    runtime         = []    
    
    # Now go through each movie's URL page and extract financial
    # and other information
    for i_url in tqdm(range(0,len(movie_urls))):
    #for i_url in tqdm(range(0,5)):
    
        count += 1
                
        url = movie_urls[i_url]
        
        # Opens the connection and downloads html page from url
        uClient = uReq(url)
        
        # Parses html into a soup data structure to traverse html
        # as if it were a json data type.
        page_soup = soup(uClient.read(), "html.parser")
        uClient.close()
        
        # Get Title
        try:
            m_title = page_soup.find('div', class_ = 'title_wrapper').h1.text.strip()
            movie_title.append(m_title)
        except Exception as e:
            movie_title.append(np.nan)
        
        
        # Get IMDB Score
        try:
            im_score = page_soup.find('div', class_ = 'ratingValue').text.split('/')[0].strip()
            #print('Score: ', im_score)
            imdb_score.append(im_score)
        except Exception as e:
            imdb_score.append(np.nan)
        
        
        # Get MPAA Rating
        try:
            rating = page_soup.find('div', class_ = 'subtext').text.split('|')[0].strip()
            mpaa_rating.append(rating)
            #print('Rated: ',rating)
        except Exception as e:
            mpaa_rating.append(np.nan)
        
        # Get Genre
        try:
            genre = []
            gen = page_soup.find('div', class_ = 'subtext').text.split('|')[2]
            
            for i_gen in gen.split(','):
                genre.append(i_gen.strip())
            
            genres.append(' '.join(genre))
                        
        except Exception as e:
            genres.append(np.nan)
        
        
        # Get Metacritic Score
        try:
            meta = page_soup.find('div', class_ = 'titleReviewBarItem').a.text.strip()
            meta_score.append(int(meta))
        except Exception as e:
            meta_score.append(np.nan)
            
        
        # Further information is stored in h4 tags
        h4s = page_soup.findAll('h4')
        
        # Initialize None array 
        detail = list_size_temp*[np.nan]
        
        for h4 in h4s:
            if 'Budget:' in h4:
                # Some movies are quoted in Euros, Francs, GBP, HKD, etc. Best is to just
                # parse the entire string and remove the commas. 
                # Deal with the conversion rate later
                #budg = int(''.join(h4.next_sibling.strip().replace('EUR','').replace('GBP','').replace('FRF','').replace('$','').split(',')))
                budg = ''.join(h4.next_sibling.strip().split(','))
                detail[0] = budg

            if 'Opening Weekend USA:' in h4:
                # To be safe, do not replace $, some may be in foreign currency
                # Removed replace('$','')
                op_wknd = ''.join(h4.next_sibling.strip().split(','))
                detail[1] = op_wknd

            if 'Gross USA:' in h4:
                # To be safe, do not replace $, some may be in foreign currency
                grs_usa = ''.join(h4.next_sibling.strip().split(','))
                detail[2] = grs_usa

            if 'Cumulative Worldwide Gross:' in h4:
                # To be safe, do not replace $, some may be in foreign currency
                grs_ww = ''.join(h4.next_sibling.strip().split(','))
                #print('WorldWide: ',int(''.join(h4.next_sibling.strip().replace('$','').split(','))))
                detail[3] = grs_ww

            # Get the release date
            if 'Release Date:' in h4:
                r_date = ' '.join(h4.next_sibling.strip().split()[:-1])
                detail[4] = r_date
                #print(temp5)

            # Get Country
            if 'Country:' in h4:
                cntry = h4.next_sibling.next_sibling.text
                detail[5] = cntry
                
            # Runtime
            if 'Runtime:' in h4:
                runt = h4.next_sibling.next_sibling.text.strip().split(' ')[0]
                detail[6] = runt
    
                
        budget.append(detail[0])
        opening_weekend.append(detail[1])
        gross_usa.append(detail[2])
        gross_world.append(detail[3])
        rel_date.append(detail[4])
        country.append(detail[5])
        runtime.append(detail[6])
        
        # Reprieve
        if (count%step == 0):
            time.sleep(sleep_time)
        
    movie_dict = {'Title'           : movie_title,
                  'url'             : movie_urls,
                  'IMDB Score'      : imdb_score,
                  'Metacritic'      : meta_score,
                  'Runtime (mins)'  : runtime,
                  'Budget'          : budget,
                  'Opening Weekend' : opening_weekend,
                  'Gross USA'       : gross_usa,
                  'Gross World'     : gross_world,
                  'Release Date'    : rel_date,
                  'Rating'          : mpaa_rating,
                  'Genres'          : genres,
                  'Country'         : country}
    
    dfm = pd.DataFrame(movie_dict)
    
    return(dfm)

# Let's set parameters
input_file  = './data/movies_sequels_extra_manual_input_for_testing.csv'
output_file = './data/movies_with_sequels_imdb_details_for_testing.csv'

# Load data files
df = pd.read_csv(input_file)

# Now scrap information
m_urls = df['url']

df_movie_details = get_movie_details(m_urls)

print(df_movie_details.head(6))

df_movie_details.to_csv(output_file,index=False)

