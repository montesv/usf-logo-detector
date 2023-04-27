import os
import CustomVision
import crochet
crochet.setup()

from flask import Flask , render_template, jsonify, request, redirect, url_for
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
import time
import yagmail

# Importing our Scraping Function from the amazon_scraping file

from tutorial.tutorial.spiders.usf_scraping import LinkSpider

app = Flask(__name__)

output_data = []
mailList = []
crawl_runner = CrawlerRunner()

def send_mail(email, notes):
    # initiating connection with SMTP server
    FROM = "logo-detector@outlook.com"
    PASS = "Elephant5091"

    # FROM= "USF.Logo.Detector@gmail.com"
    # PASS= "USFTeam$"

    TO = email
    SUBJECT = "Logo Detector Summary"
    yag = yagmail.SMTP(FROM, PASS, host='smtp.outlook.com', port=587, smtp_starttls=True, smtp_ssl=False)
    # yagmail.register("USF.Logo.Detector@gmail.com", "USFTeam$")
    # yag = yagmail.SMTP("USF.Logo.Detector@gmail.com")
    # saving path of marked images, to be attached
    # dirpath = './output-of-final-detector/'
    # attachments_path = []
    # if os.path.exists(dirpath):
    #     fnames = os.listdir("./output-of-final-detector/")
    #     for name in fnames:
    #         attachments_path.append(dirpath + name)


    # if any images were marked
    if len(mailList) != 0:
        TEXT = "Copyrighted material has been found in the link you entered. The images are linked below.\n" +"Notes: \n" +notes+ "\n"

        for text in mailList:
            TEXT = TEXT + text
        # Adding Content and sending it
        yag.send(TO, SUBJECT, TEXT)
    else:
        TEXT = "No copyrighted material was found in the link you provided. Please try submitting it again or using a different one.\n" +"Notes: \n" +notes+ "\n"
        # Adding Content and sending it
        yag.send(TO, SUBJECT, TEXT)

    print("Alert Sent To " +str(TO))


# By Deafult Flask will come into this when we run the file
@app.route('/')
def index():
    return render_template("index.html")  # Returns index.html file in templates folder.

@app.route('/about.html')
def about():
    return render_template("about.html")  # Returns index.html file in templates folder.

@app.route('/contact.html')
def contact():

    return render_template("contact.html")  # Returns index.html file in templates folder.

@app.route('/index.html')
def home():
    return render_template("index.html")  # Returns index.html file in templates folder.

# After clicking the Submit Button FLASK will come into this
@app.route('/', methods=['POST'])
def submit():
    if request.method == 'POST':
        s = request.form['url']  # Getting the Input Amazon Product URL
        e = request.form['email']
        n = request.form['notes']
        l = request.form['num_images']

        global notes
        notes = n

        global baseURL
        baseURL = s

        global email
        email = e

        global limit
        limit = l

        # This will remove any existing file with the same name so that the scrapy will not append the data to any previous file.
        if os.path.exists("<path_to_outputfile.json>"):
            os.remove("<path_to_outputfile.json>")

        return redirect(url_for('scrape'))  # Passing to the Scrape function


@app.route("/scrape")
def scrape():
    scrape_with_crochet(baseURL=baseURL)  # Passing that URL to our Scraping Function

    VisionAPI = CustomVision.Endpoint_class

    time.sleep(10)  # Pause the function while the scrapy spider is running
    count = 0
    print(len(output_data))
    OPdirpath = './output-of-final-detector/'

    # if os.path.isdir(OPdirpath):
    #     for file_name in os.listdir(OPdirpath):
    #         # construct full file path
    #         file = OPdirpath + file_name
    #         if os.path.isfile(file):
    #             os.remove(file)
    #     os.rmdir(OPdirpath)

    print(output_data)
    print("\n")
    print(str(limit))
    print("\n")
    for i in output_data:
        for v in i.values():
            print(v)
            findings = VisionAPI.Azure_endpoint(VisionAPI, v, count)
            if findings != "1":
                mailList.append(findings)
            print("count:",count)
            count = count + 1
            if count == int(limit):
                break

        if count == int(limit):
            break
    time.sleep(5)
    print("sending mail")

    # send_mail()

    return redirect(url_for('mail'))  # Returns the scraped data after being running for 20 seconds.


@app.route('/mail')
def mail():
    time.sleep(10)
    send_mail(email=email, notes=notes)
    return render_template("about.html")  # Returns index.html file in templates folder.

@crochet.run_in_reactor
def scrape_with_crochet(baseURL):
    # This will connect to the dispatcher that will kind of loop the code between these two functions.
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)

    # This will connect to the ReviewspiderSpider function in our scrapy file and after each yield will pass to the crawler_result function.
    eventual = crawl_runner.crawl(LinkSpider, category=baseURL)
    return eventual


# This will append the data to the output data list.
def _crawler_result(item, response, spider):
    output_data.append(dict(item))


if __name__ == "__main__":

    app.run(debug=True)


