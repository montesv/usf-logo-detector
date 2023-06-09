# custom vision dependancies
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
import os, time, uuid, requests, glob
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# computer vision dependancies
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from msrest.authentication import ApiKeyCredentials
from array import array
import re

import yagmail
import json

# custom vision credentials
customvision_endpoint = "https://usflogodetector-prediction.cognitiveservices.azure.com/"
prediction_key = "139023d87b174213ab54f4c6db9ff98b"
ProjectID = "2c5d2353-119b-4244-9dd8-754a81b4bae3"
ModelName = "Iteration4"

# computer vision credentials
subscription_key = "f990511341b449048664f7a18991401c"
computervision_endpoint = "https://usf-textdetector.cognitiveservices.azure.com/"


def send_mail():
    # initiating connection with SMTP server
    FROM = "logo-detector@outlook.com"
    PASS = "Elephant5091"
    TO = "mohammedalhamzy@gmail.com"
    SUBJECT = "Logo Detector Summary"
    yag = yagmail.SMTP(FROM, PASS, host='smtp.outlook.com', port=587, smtp_starttls=True, smtp_ssl=False)

    # saving path of marked images, to be attached
    dirpath = './output-of-final-detector/'
    attachments_path = []
    if os.path.exists(dirpath):
        fnames = os.listdir("./output-of-final-detector/")
        for name in fnames:
            attachments_path.append(dirpath + name)

    # if any images were marked
    if len(attachments_path) != 0:
        TEXT = "Copyrighted material has been found in the link you entered. The images are attached below."

        # Adding Content and sending it
        yag.send(TO, SUBJECT, TEXT, attachments=attachments_path)
    else:
        TEXT = "No copyrighted material was found in the link you provided. Please try submitting it again or using a different one."
        # Adding Content and sending it
        yag.send(TO, SUBJECT, TEXT)

    print("Alert Sent!")


# start detection
if __name__ == '__main__':

    credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
    prediction_client = CustomVisionPredictionClient(endpoint=customvision_endpoint, credentials=credentials)
    input_file = 'urls.txt'
    copyrighted = 'copyrighted.txt'
    OPdirpath = './output-of-final-detector/'

    # remove old output files if they exist
    if os.path.isdir(OPdirpath):
        for file_name in os.listdir(OPdirpath):
            # construct full file path
            file = OPdirpath + file_name
            if os.path.isfile(file):
                os.remove(file)
        os.rmdir(OPdirpath)

    print('Detecting objects from ', input_file, ':')

    with open(input_file) as f:
        image_url_list = [line.rstrip('\n') for line in f]

    # Opening JSON file
    f = open('data.json')

    # returns JSON object as
    # a dictionary
    data = json.load(f)

    # Iterating through the json
    for i in data['url']:
        print(i)

    # Closing file
    f.close()

    image_count = 0
    for image_url in image_url_list:
        image_count = image_count + 1
        print("Analysing image ", image_count, "...")
        # preparing custom vision client
        results = prediction_client.detect_image_url(ProjectID, ModelName,
                                                     image_url)  # get prediction response for image url detection

        # preparing computer vision client
        computervision_client = ComputerVisionClient(computervision_endpoint,
                                                     CognitiveServicesCredentials(subscription_key))
        read_response = computervision_client.read(url=image_url,
                                                   raw=True)  # get response from "read" call, for text detection

        # Get the operation location (URL with an ID at the end) from the response
        read_operation_location = read_response.headers["Operation-Location"]
        # Grab the ID from the URL
        operation_id = read_operation_location.split("/")[-1]
        # Call the "GET" API and wait for it to retrieve the results
        while True:
            read_result = computervision_client.get_read_result(operation_id)
            if read_result.status not in ['notStarted', 'running']:
                break
            # time.sleep(1)

        # prepare output properties
        fig = plt.figure(figsize=(8, 8))
        plt.axis('off')
        color = 'magenta'

        for prediction in results.predictions:
            if (prediction.probability * 100) > 50:  # logo detected
                # start logo marking
                url_image = requests.get(image_url).content
                with open('output.jpg', 'wb') as handler:
                    handler.write(url_image)
                image_file = 'output.jpg'
                image_handler = Image.open(image_file)
                dimensions = np.array(image_handler).shape  # dimensions => (height,width,channel)
                h = dimensions[0]
                w = dimensions[1]
                if len(dimensions) == 3:
                    ch = dimensions[2]
                lineWidth = int(w / 200)
                draw = ImageDraw.Draw(image_handler)

                left = prediction.bounding_box.left * w
                top = prediction.bounding_box.top * h
                height = prediction.bounding_box.height * h
                width = prediction.bounding_box.width * w

                points = (
                (left, top), (left + width, top), (left + width, top + height), (left, top + height), (left, top),
                (left + width, top))

                draw.line(points, fill=color, width=lineWidth)
                plt.annotate(prediction.tag_name + ": {0:.2f}%".format(prediction.probability * 100), xy=(left, top))
                plt.imshow(image_handler)

                # check for existence of sensitive words next to logo
                if read_result.status == OperationStatusCodes.succeeded:
                    # check if any text was detected
                    text_result = read_result.analyze_result.read_results[0]
                    if len(text_result.lines) == 0:
                        print("No text on image.")
                        outputfile = 'marked_image' + str(image_count) + '.jpg'
                        if not os.path.isdir("output-of-logo-detector/"):
                            os.makedirs("output-of-logo-detector/")
                        fig.savefig('output-of-logo-detector/' + outputfile)
                        print('Results saved in ', 'output-of-logo-detector/' + outputfile)
                        continue

                    with open(copyrighted) as file:
                        copyrighted_phrases = [line.rstrip('\n') for line in file]
                    if copyrighted_phrases != None:
                        for text_result in read_result.analyze_result.read_results:  # for each line of text, print output and mark on image
                            for line in text_result.lines:
                                # check each detected line of text in image for copyrighted text
                                for phrase in copyrighted_phrases:
                                    if (phrase == ''):
                                        continue
                                    if re.search(phrase, line.text,
                                                 re.IGNORECASE) is not None:  # if sensitive word found
                                        points = (line.bounding_box[0], line.bounding_box[1], line.bounding_box[2],
                                                  line.bounding_box[3], line.bounding_box[4], line.bounding_box[5],
                                                  line.bounding_box[6], line.bounding_box[7], line.bounding_box[0],
                                                  line.bounding_box[1])
                                        draw.line(points, fill=color, width=lineWidth)
                                        plt.annotate(line.text, xy=(points[0], points[1]))
                                        plt.imshow(image_handler)

                # save marked image
                outputfile = 'marked_image' + str(image_count) + '.jpg'
                if not os.path.isdir("output-of-final-detector/"):
                    os.makedirs("output-of-final-detector/")
                fig.savefig('output-of-final-detector/' + outputfile)
                print('Results saved in ', 'output-of-detector/' + outputfile)

    # email results
    print("Emailing results...")
    send_mail()