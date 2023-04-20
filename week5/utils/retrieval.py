import os
import matplotlib.pyplot as plt
import numpy as np


def extract_retrieval_examples_img2text(neighbors_index, neighbors_id, databaseDataset, queryDataset, output_path):
    
    query_list = [0, 1, 2, 3, 4, 5]
    
    for query in query_list:
        path = os.path.join(output_path, f'query_{query}')
        # Create directory if it does not exist
        os.makedirs(path, exist_ok=True)

        print(query)
        print("Query image:")
        # Get image
        img, _ = queryDataset[query]
        img = np.array(img).transpose(1,2,0)
        plt.imshow(img)
        plt.savefig(os.path.join(path, 'query.png'))
        
        # Get Captions
        captionIds = queryDataset.getCaptionsId_fromImageIdx(query)
        captionStr = [databaseDataset[databaseDataset.getCaptionIdx_fromId(capt)] for capt in captionIds]
        print("Caption: ", captionStr)
        
        # Write text file with objects
        with open(os.path.join(path, 'query.txt'), 'w') as f:
            f.write("Query Captions: ")
            for capt in captionStr:
                f.write(capt[0])
                f.write(" \n")
        
        # Get 5 most close strings
        for i in range(5):
            print(i, ". closest caption:")
            
            neighbor_id = neighbors_id[query, i]
            neighbor_idx = neighbors_index[query, i]
            
            # Get caption and it's correspondent image
            caption, caption_id = databaseDataset[neighbor_idx]
            assert caption_id == neighbor_id
            
            print("Caption: ", caption)
            
            imageDB_id = databaseDataset.getImageId_fromCaptionIdx(neighbor_idx)[0]
            imageDB_idx = queryDataset.getImageIdx_fromId(imageDB_id)
            imageDB, imageDB_id = queryDataset[imageDB_idx]
            img = np.array(imageDB).transpose(1,2,0)
            plt.imshow(img)
            plt.savefig(os.path.join(path, f'neighbor_{i}.png'))
            
            with open(os.path.join(path, 'query.txt'), 'a') as f:
                f.write(f'neighbor_{i} Caption: {caption}\n')
               


# def extract_retrieval_examples(db_dataset_val, neighbors, query_list, output_path):
    
#     classes =  ["", 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
#            'fire hydrant', '', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep',
#            'cow', 'elephant', 'bear', 'zebra', 'giraffe', '', 'backpack', 'umbrella', '', '', 'handbag', 'tie',
#            'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
#            'skateboard', 'surfboard', 'tennis racket', 'bottle', '', 'wine glass', 'cup', 'fork', 'knife', 'spoon',
#            'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut',
#            'cake', 'chair', 'couch', 'potted plant', 'bed', '', 'dining table', '', '', 'toilet', '', 'tv',
#            'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
#            'refrigerator', '', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
#            'toothbrush']
    
#     for query in query_list:
#         path = os.path.join(output_path, f'query_{query}')
#         # Create directory if it does not exist
#         os.makedirs(path, exist_ok=True)

#         print(query)
#         print("Query image:")
#         # Get image
#         img, _ = db_dataset_val[query]
#         img = np.array(img).transpose(1,2,0)
#         plt.imshow(img)
#         plt.savefig(os.path.join(path, 'query.png'))
        
#         # Get values
#         objIds = db_dataset_val.getObjs(query)
#         objStr = [classes[int(i)] for i in objIds]
#         print("Objects: ", objStr)
        
#         # Write text file with objects
#         with open(os.path.join(path, 'query.txt'), 'w') as f:
#             f.write("Query Objects: ")
#             for obj in objStr:
#                 f.write(obj)
#                 f.write(" ")
        
#         # Get 5 most close images
#         for i in range(5):
#             print(i, ". closest image:")
            
#             neighbor = neighbors[query, i]
            
#             # Get image
#             img,_ = db_dataset_train[neighbor]
#             img = np.array(img).transpose(1,2,0)
#             plt.imshow(img)
#             plt.savefig(os.path.join(path, f'neighbor_{i}.png'))
#             # Get values
#             objIds = db_dataset_train.getObjs(neighbor)
#             objStr = [classes[int(i)] for i in objIds]
#             print("Objects: ", objStr)
#             # Write objects in the previous txt file
#             with open(os.path.join(path, 'query.txt'), 'a') as f:
#                 f.write(f'neighbor_{i} Objects: ')
#                 for obj in objStr:
#                     f.write(obj)
#                     f.write(" ")