# custom vision dependencies
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
import os, time, uuid, requests, glob, shutil
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# computer vision dependencies
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

# storage (blob) account credentials and dependencies
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ServiceRequestError,
    ResourceNotFoundError,
    AzureError
)

storage_account_key = "KdsX4U+yxixrh3wEREZI/lpV//iw1uFg9OagYzuC/FPDHyCWHfMpAazNgkRCkxLGyJTvgRgYyR8f+AStzHBlIQ=="
storage_account_name = "usfcapstone"
connection_string = "DefaultEndpointsProtocol=https;AccountName=usfcapstone;AccountKey=n0SZVgFCXOOFGwhJXVBAWSLL6gijP0Ohmn2dLADxtd+2nT0s+y05ZiGfvf65OcwYKxjBaRQCK28o+ASt/Y1V1g==;EndpointSuffix=core.windows.net"



def blob_upload(output_path):
    from datetime import datetime

    today = datetime.now()
    cur_time = today.strftime('%m/%d/%Y-%H_%M_%S')

    
    try:
        print("Azure Blob Storage Python quickstart sample")

        # Quickstart code goes here
        # account_url = "https://usfcapstone.blob.core.windows.net"
        # default_credential = DefaultAzureCredential()

        # Create the BlobServiceClient object
        # blob_service_client = BlobServiceClient(account_url, credential=default_credential)
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        

        # Create a unique name for the container
        # container_name = 'USF'#-Logo-Detector-Results-on-'
        container_name = str(uuid.uuid4())

        print("new cont name:",container_name)

        # Create the container
        container_client = blob_service_client.create_container(container_name)
        
        print("client container connected")
        # Create a local directory to hold blob data
        container_data_path = "./container_data_" + cur_time
        if os.path.exists(container_data_path):
            shutil.rmtree(container_data_path)
            
        os.makedirs(container_data_path)
        print("dir crted")

        # # Create a file in the local data directory to upload and download
        # # local_file_name = str(uuid.uuid4()) + ".txt"
        # local_file_name = 
        # upload_file_path = os.path.join(local_path, local_file_name)

        # # Write text to the file
        # file = open(file=upload_file_path, mode='w')
        # file.write("Hello, World!")
        # file.close()

        # Create a blob client using the local file name as the name for the blob
        # blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)
        
        root_path = os.getcwd()
        # root_path = '<your root path>'
        dir_name = output_path
                
        path = f"{output_path}"

        # path = f"{root_path}/{dir_name}"
        file_names = os.listdir(path)
        try:
            blob_client = blob_service_client.get_blob_client(container=container_name, blob="my_blob")
            block_blob_service = BlockBlobService(
                account_name=storage_account_name,
                account_key=storage_account_key
            )

            for file_name in file_names:
                blob_name = f"{dir_name}/{file_name}"
                file_path = f"{path}/{file_name}"
                block_blob_service.create_blob_from_path(container_name, blob_name, file_path)
                
                
        except ResourceNotFoundError:
            print("No blob found.")

        print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

        # Upload the created file
        # with open(file=upload_file_path, mode="rb") as data:
            
        #     print("opened and about to upload data:",data)
        #     upload_status = blob_client.upload_blob(data)
        #     print("uplaod status:",upload_status)
        
        
        with open(file=upload_file_path, mode="rb") as data:
                print("opened and about to upload data:",data)
                upload_status = blob_client.upload_blob(data)
                print("uplaod status:",upload_status)
        
        print("Listing blobs in container")
        # List the blobs in the container
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            print("\t" + blob.name)
            
            
        # Download the blob to a local file
        # Add 'DOWNLOAD' before the .txt extension so you can see both files in the data directory
        
        download_file_path = os.path.join(local_path, str.replace(local_file_name ,'.txt', 'DOWNLOAD.txt'))
        container_client = blob_service_client.get_container_client(container= container_name) 
        print("\nDownloading blob to \n\t" + download_file_path)

        with open(file=download_file_path, mode="wb") as download_file:
            download_file.write(container_client.download_blob(blob.name).readall())
        
        # Clean up
        print("\nPress the Enter key to begin clean up")
        input()

        print("Deleting blob container...")
        container_client.delete_container()

        print("Deleting the local source and downloaded files...")
        os.remove(upload_file_path)
        os.remove(download_file_path)
        os.rmdir(local_path)

        print("Done")


    except Exception as ex:
        print('Exception:')
        print(ex)
    

def send_mail(output_path):
    # initiating connection with SMTP server
    FROM = "logo-detector@outlook.com"
    PASS = "Elephant5091"
    TO = "mohammedalhamzy@gmail.com"
    SUBJECT = "Logo Detector Summary"
    yag = yagmail.SMTP(FROM, PASS, host='smtp.outlook.com', port=587, smtp_starttls=True, smtp_ssl=False)

    # populate images to attach
    attachments_path = []
    if os.path.exists(output_path):
        fnames = os.listdir(output_path)
        for name in fnames:
            attachments_path.append(output_path +"\\"+ name)
    # if os.path.exists.


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
    print("conn string: ",connection_string)

    cwd = os.getcwd()
    credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
    prediction_client = CustomVisionPredictionClient(endpoint=customvision_endpoint, credentials=credentials)
    copyrighted = 'copyrighted.txt'
    json_path = 'detector test\\data.json'

    

    print('Detecting objects from ', json_path, ':')



    # Open the JSON file
    url_path = os.path.join(cwd,json_path)
    with open(url_path) as f:
        # Initialize an empty set to store the unique URLs
        unique_urls = set()

        # Initialize an empty list to store the JSON objects with unique URLs
        unique_json_objects = []

        # Iterate over each line in the file
        for line in f:
            # Load the JSON object from the line
            data = json.loads(line)

            # Check if the URL is already in the set of unique URLs
            if data['url'] not in unique_urls:
                # If the URL is unique, append the JSON object to the list
                unique_json_objects.append(data)

                # Add the URL to the set of unique URLs
                unique_urls.add(data['url'])

    # Rewrite the JSON file with only the unique JSON objects
    with open(url_path, 'w') as f:
        for data in unique_json_objects:
            f.write(json.dumps(data) + '\n')

    # Open the JSON file
    with open(json_path) as f:
        # Initialize an empty list to store the URLs
        url_list = []
        
        # Iterate over each line in the file
        for line in f:
            # Load the JSON object from the line
            data = json.loads(line)
            
            # Append the URL to the list
            url_list.append(data['url'])
    # Print the list of URLs
    print(url_list)

    # get cwd for output folders' path, create paths for each folder
    
    logo_output_path = os.path.join(cwd,'output-of-logo-detector')
    final_output_path = os.path.join(cwd,'final-output-of-detector')
    
    # create a new directory for final output
    if os.path.exists(final_output_path):
        shutil.rmtree(final_output_path)
    os.makedirs(final_output_path)
    
    
    image_count = 0
    for image_url in url_list:
        image_count = image_count + 1
        cwd = os.getcwd()

        print("cwd:",cwd)
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

        # access each prediction from model's results
        for prediction in results.predictions:
            if (prediction.probability * 100) > 50:  # logo detected
                # start marking current image
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
                print("finished marking image: ",image_count)
                # check for sensitive text
                if read_result.status == OperationStatusCodes.succeeded:
                    # check if any text was detected
                    text_result = read_result.analyze_result.read_results[0]
                    
                    if len(text_result.lines) == 0: # not text detected
                        print("No text on image.")
                        
                        # outputfile = 'marked_image' + str(image_count) + '.jpg'
                        
                        # if not os.path.exists(logo_output_path):
                        #     os.makedirs(logo_output_path)
                        # else:
                        #     shutil.rmtree(logo_output_path)
                        #     os.makedirs(logo_output_path)
                            
                        # output_path = logo_output_path+ '\\' + outputfile
                        # fig.savefig(output_path) # save in directory
                        # print('Results saved in '+ logo_output_path + outputfile)
                        
                    else: # mark text detected on image 
                        print("Text detected in image:",image_count)
                        with open(copyrighted) as file:
                            copyrighted_phrases = [line.rstrip('\n') for line in file]
                        if copyrighted_phrases is not None:
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
                
                 
                output_path = final_output_path + '\\' + outputfile
                fig.savefig(output_path) # save in directory
                print('Results saved in '+ final_output_path + '\\' + outputfile)

    # email results
    print("Emailing results...")
  #  send_mail(final_output_path)
    blob_upload(final_output_path) 
