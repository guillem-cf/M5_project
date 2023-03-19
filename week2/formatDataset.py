import os
import random

import cv2
import numpy as np
import pycocotools.mask as mask_utils
from detectron2.data import DatasetCatalog, MetadataCatalog
from detectron2.structures.boxes import BoxMode
from detectron2.utils.visualizer import Visualizer
from tqdm import tqdm


def line_to_object(line, pretrained):
    line = line.replace("\n", "").split(" ")

    # Each line of an annotation txt file is structured like this (where rle means run-length encoding from COCO): time_frame id class_id img_height img_width rle

    time_frame, obj_id, class_id, img_height, img_width, rle_aux = (
        int(line[0]),
        int(line[1]),
        int(line[2]),
        int(line[3]),
        int(line[4]),
        line[5],
    )

    if pretrained:
        kitti_to_coco = {1: 2, 2: 0}
        if class_id not in kitti_to_coco:
            return None
        class_id = kitti_to_coco[class_id]

    else:
        if class_id > 2:
            return None
        class_id = class_id - 1
        

    # obj_instance_id = obj_id % 1000

    rle = {'size': [img_height, img_width], 'counts': rle_aux}
    mask = mask_utils.decode(rle)

    if mask.sum() == 0:
        return None
    y, x = np.where(mask == 1)
    bbox = [int(np.min(x)), int(np.min(y)), int(np.max(x) - np.min(x)), int(np.max(y) - np.min(y))]

    # rle_new = mask_utils.encode(np.asfortranarray(mask))
    # rle_new['counts'] = rle_new['counts'].decode('UTF-8')

    # https://towardsdatascience.com/train-maskrcnn-on-custom-dataset-with-detectron2-in-4-steps-5887a6aa135d
    #  segmentation is a polygon with n points, (x_i, y_i)
    #  'segmentation': [[x_0, y_0, x_1, y_1, ..., x_n, y_n]],
    #  bbox is a list of 4 numbers: [x, y, width, height]
    poly = [(x.tolist(), y.tolist()) for x, y in zip(x, y)]
    poly = [p for x in poly for p in x]

    return {
        "bbox": bbox,
        "bbox_mode": BoxMode.XYWH_ABS,
        "segmentation": [poly],
        # "segmentation": mask_utils.encode(np.asarray(mask.astype(np.uint8), order="F")),
        "category_id": class_id,
    }


def get_kitti_dicts(subset, pretrained = False):
    anotations_dir = "../../datasets/KITTI-MOTS/instances_txt/"
    images = "../../datasets/KITTI-MOTS/training/image_02/"

    if subset == "train":
        sequences_id = ["0000", "0001", "0003", "0004", "0005", "0009", "0011", "0012", "0015", "0017", "0019", "0020"]
        # sequences_id = ["0000", "0001", "0003"]

    elif subset == "val":
        sequences_id = ["0002", "0006", "0007", "0008", "0010", "0013", "0014", "0016", "0018"]
        # sequences_id = ["0002"]

    elif subset == "val_subset":
        sequences_id = ["0002", "0007", "0010", "0014", "0018"]
        # sequences_id = ["0002"]
        # sequences_id = ["0000", "0001", "0003"]

    dataset_dicts = []
    idx = 1

    for seq_id in tqdm(sequences_id):
        sequence_txt = os.path.join(anotations_dir, seq_id + ".txt")

        with open(sequence_txt) as f:
            lines = f.readlines()

        # for each line in the txt file we have an integer on first position that represents the frame
        # construct a list of list named frames that contains the number of line that corresponds at each frame, for example:
        #  frame = [[0,1],[2,3,4]]
        #  frame[0] = [0,1] -> lines 0 and 1 correspond to frame 0
        frames = []
        for i in range(len(lines)):
            if i == 0:
                frames.append([i])
            else:
                if int(lines[i].split(" ")[0]) == int(lines[i - 1].split(" ")[0]):
                    frames[-1].append(i)
                else:
                    frames.append([i])

        for i, frame in enumerate(frames):
            record = {}
            time_frame = str(i).zfill(6)
            #  time_frame = str(line.split(" ")[0]).zfill(6)

            filename = os.path.join(images, seq_id, time_frame + ".png")

            height, width = cv2.imread(filename).shape[:2]

            record["file_name"] = filename
            record["image_id"] = idx
            record["height"] = height
            record["width"] = width

            if subset != "test":
                objs = []
                for line in frame:
                    obj = line_to_object(lines[line], pretrained)
                    if obj is not None:
                        objs.append(obj)

                record["annotations"] = objs

            dataset_dicts.append(record)

            idx += 1

    return dataset_dicts


def register_kitti_dataset(type="train"):  # type = "train" or "val"
    # classes = ['person', 'bicycle', 'car', 'motorcycle', 'bus', 'truck']
    classes = ['car', 'bicycle', 'person', 'motorcycle', 'bus', 'truck']
    for subset in ["train", "val", "val_subset"]:
        DatasetCatalog.register(f"kitti_{subset}", lambda subset=subset: get_kitti_dicts(subset))
        print(f"Successfully registered 'kitti_{subset}'!")
        MetadataCatalog.get(f"kitti_{subset}").set(thing_classes=classes)

    if type == "train":
        kitty_metadata = MetadataCatalog.get("kitti_train")
    elif type == "val":
        kitty_metadata = MetadataCatalog.get("kitti_val")
    elif type == "val_subset":
        kitty_metadata = MetadataCatalog.get("kitti_val_subset")

    return kitty_metadata


if __name__ == "__main__":
    kitty_metadata = register_kitti_dataset()
    dataset_dicts = get_kitti_dicts("train")

    # for i, d in enumerate(dataset_dicts):
    #     img = cv2.imread(d["file_name"])
    #     visualizer = Visualizer(img[:, :, ::-1], metadata=kitty_metadata, scale=0.5)
    #     out = visualizer.draw_dataset_dict(d)
    #     name = d["file_name"].split("/")[-1].split(".")[0]
    #     cv2.imwrite(
    #         f"/ghome/group03/M5-Project/week2/Results/preprocessing/train_{name}.png", out.get_image()[:, :, ::-1]
    #     )
    #     if i == 4:
    #         break

    for d in dataset_dicts:
        img = cv2.imread(d["file_name"])
        visualizer = Visualizer(img[:, :, ::-1], metadata=kitty_metadata, scale=0.5)
        out = visualizer.draw_dataset_dict(d)
        name = d["file_name"].split("/")[-1].split(".")[0]
        cv2.imwrite(
            f"/ghome/group03/M5-Project/week2/Results/preprocessing/train_{name}.png", out.get_image()[:, :, ::-1]
        )
