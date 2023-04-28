import matplotlib
import requests as requests
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes

from msrest.authentication import CognitiveServicesCredentials
from msrest.authentication import ApiKeyCredentials


import os, time, uuid
from matplotlib import pyplot as plt
matplotlib.use('Agg')

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import requests

import re
import yagmail
import json




class Endpoint_class:

    ENDPOINT = "https://usflogodetector-prediction.cognitiveservices.azure.com/"
    prediction_key = "139023d87b174213ab54f4c6db9ff98b"
    # prediction_resource_id = "/subscriptions/f294215e-1528-4d11-a41c-2c5eb70966a0/resourceGroups/USFCapstoneSpring2023/providers/Microsoft.CognitiveServices/accounts/usflogodetector"
    ProjectID = "2c5d2353-119b-4244-9dd8-754a81b4bae3"
    ModelName = "Iteration5"

    # computer vision credentials
    subscription_key = "f990511341b449048664f7a18991401c"
    computervision_endpoint = "https://usf-textdetector.cognitiveservices.azure.com/"

    def Azure_endpoint(self, imageurl,count):
        credentials = ApiKeyCredentials(in_headers={"Prediction-key": self.prediction_key})
        prediction_client = CustomVisionPredictionClient(endpoint=self.ENDPOINT, credentials=credentials)

        # image_file = 'testing/silvertest.JPG'
        print('Detecting objects in image')
        # image = Image.open(image_file)


        #########new declarations

        copyrighted = 'copyrighted.txt'
        # OPdirpath = './output-of-final-detector/'

        # if os.path.isdir(OPdirpath):
        #     for file_name in os.listdir(OPdirpath):
        #         # construct full file path
        #         file = OPdirpath + file_name
        #         if os.path.isfile(file):
        #             os.remove(file)
        #     os.rmdir(OPdirpath)

        image_url = imageurl
        # with open(image_file, mode="rb") as image_data:
        # results = prediction_client.detect_image(ProjectID,ModelName,image_data)

        results = prediction_client.detect_image_url(self.ProjectID, self.ModelName, image_url)


        ######new stuff
        computervision_client = ComputerVisionClient(self.computervision_endpoint,
                                                     CognitiveServicesCredentials(self.subscription_key))
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

        #######new stuff

        # fig = plt.figure(figsize=(8, 8))
        # plt.axis('off')
        #
        # color = 'magenta'

        # "\\output-of-final-detector\\" +
        # pathtest = os.path.abspath('.')
        # imgout = "output"
        # imgcount = count

        ret_str = "1"
        for prediction in results.predictions:
            # fileout = pathtest+"/"+imgout + str(imgcount) + ".jpg"

            if (prediction.probability * 100) > 30 and prediction.tag_name != "fsu-logo":
                pred_prob = str(prediction.probability)
                ret_str = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.4; color: #333333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f0f0f0; border-radius: 4px;">
                            <h2 style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">Violation Detected</h2>
                            <p style="margin-top: 0; margin-bottom: 10px;">
                                Violation found at the following image:
                            </p>
                            <p style="margin-top: 0; margin-bottom: 10px;">
                                <img src="{image_url}" alt="Violation Image" style="max-width: 100%;" />
                            <br/>
                            <a href="{image_url}" style="display: inline-block; margin-top: 5px; color: #0066cc; text-decoration: none;">
                            {image_url}
                            </a>
                            </p>
                            <p style="margin-top: 0; margin-bottom: 10px;">
                                <strong>Confidence Level:</strong> {pred_prob}
                            </p>
                        </div>
                    </body>
                </html>
                """

                # url_image = requests.get(image_url).content
                # with open(fileout, 'wb') as handler:
                #     handler.write(url_image)
                # image_file = fileout
                # image = Image.open(image_file)
                # h, w, ch = np.array(image).shape
                # lineWidth = int(w / 100)
                # draw = ImageDraw.Draw(image)

                # left = prediction.bounding_box.left * w
                # top = prediction.bounding_box.top * h
                # height = prediction.bounding_box.height * h
                # width = prediction.bounding_box.width * w
                #
                # points = ((left, top), (left + width, top), (left + width, top + height), (left, top + height), (left, top))
                # draw.line(points, fill=color, width=lineWidth)
                # plt.annotate(prediction.tag_name + ": {0:.2f}%".format(prediction.probability * 100), xy=(left, top))


                # plt.imshow(image)

                # my_path = os.path.abspath()
                # result_path = os.path.join(my_path,"output-of-final-detector/")
                # print(result_path+fileout)
                # fig.savefig(result_path+fileout)

                # outputfile = fileout
                # fig.savefig(outputfile)
                # print('Results saved in ', fileout)
                # imgcount = imgcount+1

                if read_result.status == OperationStatusCodes.succeeded:
                    # check if any text was detected
                    text_result = read_result.analyze_result.read_results[0]
                    if len(text_result.lines) == 0:
                        print("No text on image.")
                        # outputfile = 'marked_image' + str(imgcount) + '.jpg'
                        # if not os.path.isdir(pathtest+"/output-of-logo-detector/"):
                        #     os.makedirs(pathtest+"/output-of-logo-detector/")
                        # plt.imshow(image)
                        # fig.savefig(pathtest+"/output-of-logo-detector/" + outputfile)
                        # plt.close(fig)
                        # print('Results saved in ',pathtest + '/output-of-logo-detector/' + outputfile)
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
                                        # points = (line.bounding_box[0], line.bounding_box[1], line.bounding_box[2],
                                        #           line.bounding_box[3], line.bounding_box[4], line.bounding_box[5],
                                        #           line.bounding_box[6], line.bounding_box[7], line.bounding_box[0],
                                        #           line.bounding_box[1])
                                        # draw.line(points, fill=color, width=lineWidth)
                                        # plt.annotate(line.text, xy=(points[0], points[1]))
                                        # plt.imshow(image)
                                        sensitive_word = str(line.text)
                                        ret_str = ret_str + f"""
                                        <html>
                                            <body style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.4; color: #333333;">
                                                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f0f0f0; border-radius: 4px;">
                                                <h2 style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">Sensitive Word Detected</h2>
                                                <p style="margin-top: 0; margin-bottom: 10px;">
                                                    Sensitive word found in the following text:
                                                </p>
                                                <p style="margin-top: 0; margin-bottom: 10px;">
                                                    <strong>Line:</strong> {line.text}
                                                </p>
                                                </div>
                                            </body>
                                        </html>
                                        """

                                        # save marked image
                                        # outputfile = 'marked_image' + str(imgcount) + '.jpg'
                                        # if not os.path.isdir(pathtest +"/output-of-final-detector/"):
                                        #     os.makedirs(pathtest+"/output-of-final-detector/")
                                        # fig.savefig(pathtest+'/output-of-final-detector/' + outputfile)
                                        # plt.close(fig)
                                        # print('Results saved in ',pathtest+ '/output-of-detector/' + outputfile)

                                    # email results

        return ret_str