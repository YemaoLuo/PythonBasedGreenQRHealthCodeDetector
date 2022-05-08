import numpy as np
import cv2
import onnxruntime
import argparse
import time
import easyocr
import re


def letterbox(img, new_shape=(416, 416), color=(114, 114, 114), auto=False, scaleFill=False, scaleup=True):
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:
        r = min(r, 1.0)

    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, 64), np.mod(dh, 64)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2
    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return img, ratio, (dw, dh)


def clip_coords(boxes, img_shape):
    # Clip bounding xyxy bounding boxes to image shape (height, width)
    boxes[:, 0].clip(0, img_shape[1])  # x1
    boxes[:, 1].clip(0, img_shape[0])  # y1
    boxes[:, 2].clip(0, img_shape[1])  # x2
    boxes[:, 3].clip(0, img_shape[0])  # y2


def scale_coords(img1_shape, coords, img0_shape, ratio_pad=None):
    # Rescale coords (xyxy) from img1_shape to img0_shape
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    coords[:, [0, 2]] -= pad[0]  # x padding
    coords[:, [1, 3]] -= pad[1]  # y padding
    coords[:, :4] /= gain
    clip_coords(coords, img0_shape)
    return coords


class Detector():

    def __init__(self, opt):
        super(Detector, self).__init__()
        self.img_size = opt.img_size
        self.threshold = opt.conf_thres
        self.iou_thres = opt.iou_thres
        self.stride = 1
        self.weights = opt.weights
        self.init_model()

    def init_model(self):
        sess = onnxruntime.InferenceSession(self.weights)
        self.input_name = sess.get_inputs()[0].name
        input_shape = sess.get_inputs()[0].shape
        self.m = sess

    def preprocess(self, img):

        img0 = img.copy()
        img = letterbox(img, new_shape=self.img_size)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)
        img = np.ascontiguousarray(img).astype(np.float32)
        img /= 255.0  # 图像归一化
        img = np.expand_dims(img, axis=0)
        assert len(img.shape) == 4

        return img0, img

    def detect(self, im):

        im0, img = self.preprocess(im)
        W, H = img.shape[2:]

        pred = self.m.run(None, {self.input_name: img})[0]
        pred = pred.astype(np.float32)
        pred = np.squeeze(pred, axis=0)

        boxes = []
        classIds = []
        confidences = []
        for detection in pred:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID] * detection[4]

            if confidence > self.threshold:
                box = detection[0:4]
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                classIds.append(classID)
                confidences.append(float(confidence))

        idxs = cv2.dnn.NMSBoxes(
            boxes, confidences, self.threshold, self.iou_thres)

        pred_boxes = []
        pred_confes = []
        pred_classes = []
        if len(idxs) > 0:
            for i in idxs.flatten():
                confidence = confidences[i]
                if confidence >= self.threshold:
                    pred_boxes.append(boxes[i])
                    pred_confes.append(confidence)
                    pred_classes.append(classIds[i])

        return im, pred_boxes, pred_confes, pred_classes


def main(opt):
    time1 = time.time()
    det = Detector(opt)
    image = cv2.imread(opt.source)
    shape = (det.img_size, det.img_size)
    im0, pred_boxes, pred_confes, pred_classes = det.detect(image)
    box = pred_boxes[0]
    left, top, width, height = box[0], box[1], box[2], box[3]
    box = (left, top, left + width, top + height)
    box = np.squeeze(
        scale_coords(shape, np.expand_dims(box, axis=0).astype("float"), im0.shape[:2]).round(),
        axis=0).astype("int")

    result_det = {
        'Conf': str(pred_confes[0]),
        'S_Point': str([box[0], box[1]]),
        'E_Point': str([box[2], box[3]]),
        'D_Time': '{0}s'.format(str(time.time() - time1)),
    }

    cut_img = image[box[1]:box[3], box[0]:box[2]]
    result_ocr = readtext(cut_img)

    result = {
        "flag": True,
        'result_det': result_det,
        'result_ocr': result_ocr
    }
    return result


def readtext(img4ocr):
    time1 = time.time()
    reader = easyocr.Reader(['ch_sim', 'en'])
    result = reader.readtext(img4ocr)
    result_all = []
    for i in result:
        result_all.append(i[1])
    result_all = str(result_all).replace(' ', '')
    expDate = re.findall(r'\d{4}\/\d{2}\/\d{2}', result_all)[0]
    nameSex = re.findall(r'[\u0391-\uFFE5]{2,13}\,[\u0391-\uFFE5]', result_all)[0]
    name = str(nameSex).split(',')[0]
    sex = str(nameSex).split(',')[1]
    flag = False
    if re.search(r'可以通行', str(result)):
        flag = True
    flag2 = False
    if re.search(r'全程接种', str(result)):
        flag2 = True

    result_set = {
        'Name': name,
        'Sex': sex,
        'Exp': expDate,
        'Flag': flag,
        'Vaccine': flag2,
        'O_Time': '{0}s'.format(str(time.time() - time1)),
    }
    return result_set


def run(path, conf):
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='templates/OCRWeight.onnx', help='onnx path(s)')
    parser.add_argument('--source', type=str, default=path, help='source')
    parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=conf, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='IOU threshold for NMS')
    opt = parser.parse_args(args=[])
    result = main(opt)
    return result
