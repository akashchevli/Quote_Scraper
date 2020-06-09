import base64
import io
import os
import urllib

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

# My path name, where CSV file store
CSV_FOLDER = os.path.join('static','CSV')
app = Flask(__name__)
app.config['CSV_FOLDER'] = CSV_FOLDER
dummy_search = ''


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route('/quote', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            # replace spaces.
            searchString = request.form['content'].replace(" ","")
            # below link is a target link, on that particular link i extract the data.[i.e happy]
            quote_url = 'https://www.thegood.co/?s=' + searchString
            # Request to that particular url or page.
            uClient = uReq(quote_url)
            # Read the whole page. But it will give me raw data.
            quoteread = uClient.read()
            uClient.close()
            # Beautiful soup allow to arrange the data in a proper indent.
            quote_html = bs(quoteread, "html.parser")
            # Next step is depends upon your task what actually you want, so here i want to read quotes and all quotes is available in below class.
            # so i just find out that class.
            columns = quote_html.findAll("div", {"class": "col-xs-6 col-sm-6 col-md-3"})
            #container = leftcontainer[2]
            # Only english types of data i want.
            columns.encoding = 'utf-8'
            # Whatever user search it will be save in system by the name of filename.
            filename = searchString + ".csv"
            fw = open(filename, "w")
            # header of the file.
            headers = "Quote, Author \n"
            fw.write(headers)
            # Empty list, which hold all data of each iteration.
            index.quotes = []
            # Now, it's time to iterate data which i store in columns variable.
            for column in columns:
                try:
                    quote = column.div.span.p.text
                except:
                    quote = "No Quote"
                try:
                    author = column.div.find_all('p', {'class': 'name'})[0].text
                    if author == '':
                        author = "No Author"
                except:
                    author = "No Author"

                # Create a dictionary which will hold the data of each iteration.
                header_dict = {"Quote": quote, "Author": author}
                # And append the data into a list.
                index.quotes.append(header_dict)

            # dummy se
            dummy_search = searchString
            # After iteration i create a dataframe. Main purpose to create dataframe that user can download the data.
            df = pd.DataFrame(index.quotes)
            # Give the path name. Where all my CSV file store.
            csv_path = os.path.join(app.config['CSV_FOLDER'], searchString)
            file_extension = '.csv'
            final_path = f"{csv_path}{file_extension}"
            df.to_csv(final_path, index=None)
            print("File saved successfully..")
            return render_template('results.html', quotes=index.quotes[0:len(index.quotes)], download_csv=final_path)

        except Exception as e:
            print(e)
            return render_template('404.html')

    else:
        return render_template('index.html')


@app.route('/word_sentiment', methods=['POST','GET'])
@cross_origin()
# This function do the sentiment of the the data.
def word_sentimate():
    try:
        txt = ''
        cnt = 0
        lst = []
        for i in index.quotes:
            txt = txt + (index.quotes[cnt]['Quote'])
            cnt += 1

        lst.append(txt)
        wordcloud_positive = WordCloud(background_color='black', width=512, height=384, stopwords=STOPWORDS).generate(str(lst))
        plt.figure(figsize=(10, 7), facecolor='k', edgecolor='k')
        plt.imshow(wordcloud_positive)
        plt.axis('off')
        image = io.BytesIO()
        plt.savefig(image, format='png')
        image.seek(0)
        string = base64.b64encode(image.read())
        image_64 = 'data:image/png;base64,' + urllib.parse.quote(string)

        return render_template("word_sentiment.html", text=image_64)
    except Exception as e:
        print(e)
        return render_template('404.html')



port = int(os.getenv("PORT"))
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)
    #app.run(host='127.0.0.1', port=8001, debug=True)
