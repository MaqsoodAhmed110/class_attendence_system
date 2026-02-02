from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from PIL import Image
import csv
from datetime import datetime
from ultralytics import YOLO

# Flask app initialization
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['RESULT_FOLDER'] = './results'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

# Load models
detection_model = YOLO("./models/best_de.pt")  # Detection model
classification_model = YOLO("./models/best_class.pt")  # Classification model

# here is 28 Class labels for classification model
classification_labels = [
    '2022002', '2022074', '2022081', '2022120', '2022201', '2022246',
    '2022248', '2022267', '2022274', '2022275', '2022277', '2022295',
    '2022313', '2022378', '2022383', '2022387', '2022405', '2022414',
    '2022488', '2022531', '2022559', '2022560', '2022624', '2022655',
    '2022656', '2022664', '2022672', '2022909'
]

# Detect and classify function
def detect_and_classify(image_path):
    # Load the input image
    image = Image.open(image_path)

    # Run detection
    detection_results = detection_model(image_path)
    bounding_boxes = detection_results[0].boxes.xyxy.cpu().numpy()  # Extract bounding boxes

    predictions = []

    for box in bounding_boxes:
        # Convert bounding box to integers
        x1, y1, x2, y2 = map(int, box)

        # Crop the region from the image
        cropped_region = image.crop((x1, y1, x2, y2))

        # Convert cropped region to the format expected by YOLO classification model
        cropped_region.save('./temp_crop.jpg')  # Save temporarily
        classification_results = classification_model('./temp_crop.jpg')

        # Extract class and confidence
        top1_class_idx = int(classification_results[0].probs.top1)  # Convert Tensor to int
        confidence = float(classification_results[0].probs.top1conf)  # Convert Tensor to float

        # Append the result for each detected person
        predictions.append({
            'bounding_box': (x1, y1, x2, y2),
            'class': classification_labels[top1_class_idx],
            'confidence': round(confidence, 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    return predictions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Run detection and classification
        predictions = detect_and_classify(file_path)

        # Save results to CSV
        csv_path = os.path.join(app.config['RESULT_FOLDER'], 'predictions.csv')
        with open(csv_path, mode='a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Bounding Box', 'Class', 'Confidence', 'Timestamp'])
            for pred in predictions:
                writer.writerow([
                    pred['bounding_box'], pred['class'], pred['confidence'], pred['timestamp']
                ])

        return render_template('index.html', predictions=predictions)

if __name__ == '__main__':
    app.run(debug=True)
