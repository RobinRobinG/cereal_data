#Code by Adrian at PyImageSearch 
#from "OpenCV OCR and text recognition with Tesseract"
#Modified by Gilberto Lopez 24/10/2018

# import the necessary packages
from imutils.object_detection import non_max_suppression
import numpy as np
import pytesseract
import argparse
import cv2
import numpy
import base64
import io


def decode_predictions(scores, geometry):
	# grab the number of rows and columns from the scores volume, then
	# initialize our set of bounding box rectangles and corresponding
	# confidence scores
	(numRows, numCols) = scores.shape[2:4]
	rects = []
	confidences = []

	# loop over the number of rows
	for y in range(0, numRows):
		# extract the scores (probabilities), followed by the
		# geometrical data used to derive potential bounding box
		# coordinates that surround text
		scoresData = scores[0, 0, y]
		xData0 = geometry[0, 0, y]
		xData1 = geometry[0, 1, y]
		xData2 = geometry[0, 2, y]
		xData3 = geometry[0, 3, y]
		anglesData = geometry[0, 4, y]

		# loop over the number of columns
		for x in range(0, numCols):
			# if our score does not have sufficient probability,
			# ignore it
			if scoresData[x] < 0.5:
				continue

			# compute the offset factor as our resulting feature
			# maps will be 4x smaller than the input image
			(offsetX, offsetY) = (x * 4.0, y * 4.0)

			# extract the rotation angle for the prediction and
			# then compute the sin and cosine
			angle = anglesData[x]
			cos = np.cos(angle)
			sin = np.sin(angle)

			# use the geometry volume to derive the width and height
			# of the bounding box
			h = xData0[x] + xData2[x]
			w = xData1[x] + xData3[x]

			# compute both the starting and ending (x, y)-coordinates
			# for the text prediction bounding box
			endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
			endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
			startX = int(endX - w)
			startY = int(endY - h)

			# add the bounding box coordinates and probability score
			# to our respective lists
			rects.append((startX, startY, endX, endY))
			confidences.append(scoresData[x])

	# return a tuple of the bounding boxes and associated confidences
	return (rects, confidences)

def LetterFinding(database,imglocation,padding):
    # Receive the image in dashe's base64 string, we decode it into actual bytes.
    jpg_original = base64.b64decode(imglocation)
    # transform the decoded base64 into a np array of colors. 
    jpg_as_np = np.fromstring(jpg_original, dtype=np.uint8)
    # decode the array back into an image for opencv.
    image = cv2.imdecode(jpg_as_np, cv2.IMREAD_UNCHANGED)
    
    orig = image.copy()
    (origH, origW) = image.shape[:2]

    # set the new width and height and then determine the ratio in change
    # for both the width and height
    (newW, newH) = (320, 320)
    rW = origW / float(newW)
    rH = origH / float(newH)

    # resize the image and grab the new image dimensions
    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]

    # define the two output layer names for the EAST detector model that
    # we are interested -- the first is the output probabilities and the
    # second can be used to derive the bounding box coordinates of text
    layerNames = [
	    "feature_fusion/Conv_7/Sigmoid",
	    "feature_fusion/concat_3"]

    # load the pre-trained EAST text detector
    print("[INFO] loading EAST text detector...")
    net = cv2.dnn.readNet(database)

    # construct a blob from the image and then perform a forward pass of
    # the model to obtain the two output layer sets
    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
	    (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)

    # decode the predictions, then  apply non-maxima suppression to
    # suppress weak, overlapping bounding boxes
    (rects, confidences) = decode_predictions(scores, geometry)
    boxes = non_max_suppression(np.array(rects), probs=confidences)

    # initialize the list of results
    results = []

    # loop over the bounding boxes
    for (startX, startY, endX, endY) in boxes:
	    # scale the bounding box coordinates based on the respective
	    # ratios
	    startX = int(startX * rW)
	    startY = int(startY * rH)
	    endX = int(endX * rW)
	    endY = int(endY * rH)

	    # in order to obtain a better OCR of the text we can potentially
	    # apply a bit of padding surrounding the bounding box -- here we
	    # are computing the deltas in both the x and y directions
	    dX = int((endX - startX) * padding)
	    dY = int((endY - startY) * padding)

	    # apply padding to each side of the bounding box, respectively
	    startX = max(0, startX - dX)
	    startY = max(0, startY - dY)
	    endX = min(origW, endX + (dX * 2))
	    endY = min(origH, endY + (dY * 2))

	    # extract the actual padded ROI
	    roi = orig[startY:endY, startX:endX]

	    # in order to apply Tesseract v4 to OCR text we must supply
	    # (1) a language, (2) an OEM flag of 4, indicating that the we
	    # wish to use the LSTM neural net model for OCR, and finally
	    # (3) an OEM value, in this case, 7 which implies that we are
	    # treating the ROI as a single line of text
	    config = ("-l eng --oem 1 --psm 7")
	    text = pytesseract.image_to_string(roi, config=config)

	    # add the bounding box coordinates and OCR'd text to the list
	    results.append(((startX, startY, endX, endY), text))

    # sort the results bounding box coordinates from top to bottom
    results = sorted(results, key=lambda r:r[0][1])
    for result in results :
        print(result[1])
    return results
