# %%
import os
import glob
import json
import requests
import configparser
import pandas as pd
from urllib.parse import urljoin
import storage.client as storage_client
from IPython.display import Image, display
from PIL import ImageDraw
from PIL import Image as PILImage
import argparse
import logging

import dotenv

dotenv.load_dotenv()

#%%
# set logging level
logging.basicConfig(level=logging.INFO)



logging.info(os.environ['api_storeoperations'])



#%%
# parse one argument for location
parser = argparse.ArgumentParser()
parser.add_argument("--folder", help="folder of the shelf images", required=True)  # , default='images/s2')
parser.add_argument('--aisle', help='aisle number', default=1)
parser.add_argument('--shelf', help='shelf number', default=1)
args = parser.parse_args()

# log the arguments
logging.info(f'folder: {args.folder}')
logging.info(f'aisle: {args.aisle}')
logging.info(f'shelf: {args.shelf}')

folder_root = os.path.normpath(os.path.join(os.getcwd(), f'{args.folder}/*'))
remote_path = args.folder
# %%
# list images in folder selected_item
blob_images = []

files_list = [os.path.normpath(f) for f in glob.glob(folder_root)]
for i, item in enumerate(files_list):
    logging.info(f'{i+1}. {item}')
    uploaded = storage_client.uploadLocalFile(filepath=item, remotepath=remote_path)
    blob_images.append(uploaded.replace('\\', '/'))
    logging.info(f'uploaded {uploaded}')

# %%
list_blob_images_sas = [{"url": blob_image + "?" + storage_client.sasForBlob(blob_image)} for blob_image in blob_images]
# blob_images_sas['images'].reverse()
logging.debug(json.dumps(list_blob_images_sas, indent=2))

payload_dict = {
    "ShelfInfos" :[
     {
        "ImageLocations" : list_blob_images_sas,
        "Shelf" : { "ShelfName" : f"Shelf {args.shelf}",
                 "Asile" : f"Asile {args.aisle}"
             }
     }
    ]
    }

logging.info(json.dumps(payload_dict, indent=2))


# %%
# call shelf analysis - SOA API
api_storeoperations = os.environ['api_storeoperations']
logging.info(f'api_storeoperations: {api_storeoperations}')

response = requests.post(
    api_storeoperations,
    json=payload_dict
)

# %%
logging.info(response)
logging.info(response.status_code)
# %%
shelfanlysis_result = response.json()['results'][0]

logging.info(shelfanlysis_result.keys())
# %%
# products and gaps
img_products = shelfanlysis_result['Result'].get('products', [])
img_gaps = shelfanlysis_result['Result'].get('gaps', [])
print(f'gaps: {len(img_gaps)}')
print(f'products: {len(img_products)}')

df = pd.DataFrame(img_products)
# classifications is a list of dict as follows [{'confidence': 0.9701688, 'label': 'product'}], extract the label and confidence into their own columns
df['label'] = df['classifications'].apply(lambda x: x[0]['label'])
df['confidence'] = df['classifications'].apply(lambda x: x[0]['confidence'])
display(df.head())
# summarise product counts
display(df['label'].value_counts())

# %%
shelfinfo = shelfanlysis_result['ShelfInfo']
for key, value in shelfinfo.items():
    print(f'{key}: {value}')
# %%
# %%
# annotated file
annotated_file = shelfanlysis_result['Filelocation']
logging.info(annotated_file)
print(f'annotated file: {annotated_file}')
print('displaying annotated file ...')
pilimg = PILImage.open(requests.get(annotated_file, stream=True).raw)
pilimg.show()
# %%
