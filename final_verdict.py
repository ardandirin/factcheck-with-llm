import argparse
import json
from helpers import general as General
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def classify_binary_truthfulness(value):
    false_values = ['pants-fire', 'false', 'barely-true']
    return 'no' if value in false_values else 'yes'

def classify_triway_truthfulness(value):
    false_values = ['pants-fire', 'false']
    in_between = ['barely-true', 'half-true']
    true_values = ['mostly-true', 'true']
    return 'no' if value in false_values else 'yes'

def heat_map_repr(matrix, labels):
    # Convert matrix to DataFrame for better labeling
    matrix_df = pd.DataFrame(matrix, index=labels, columns=labels)

    # Plotting the confusion matrix as a heatmap
    plt.figure(figsize=(10, 7))
    sns.heatmap(matrix_df, annot=True, fmt='g', cmap='Blues')
    plt.xlabel('Predicted Labels')
    plt.ylabel('True Labels')
    plt.title('Confusion Matrix for Veracity Classification')
    plt.show()


def main(labels_path, gold_labels, predictions):
    labels_list = ['pants-fire', 'false', 'barely-true', 'half-true', 'mostly-true', 'true']
    with open(labels_path, 'r') as data:
        for line in data:
            json_obj = json.loads(line.strip())
            print("Claim: ", json_obj['claim'])
            # binary_val = classify_binary_truthfulness(json_obj['gold_label'])
            gold_lab = General.map_six_to_three_categories(json_obj['gold_label'])
            gold_labels.append(gold_lab)
            # gold_labels.append(json_obj['gold_label'])
            pred_labels = [item['predicted_label'] for item in json_obj['subquestion_data']]
            print(pred_labels)
            # predicted_veracity = General.classify_veracity(pred_labels)
            # predicted_veracity = General.classify_binary_veracity(pred_labels)
            predicted_veracity = General.classify_veracity_three_way(pred_labels)
            print("Predicted veracity: ", predicted_veracity)
            predictions.append(predicted_veracity)
            print("Predicted veracity: ", predicted_veracity)
            print("Gold label: ", json_obj['gold_label'])

    # Label order
    # labels = ['pants-fire', 'false', 'barely-true', 'half-true', 'mostly-true', 'true']
    
    labels_binary = ['no', 'yes']
    labels_tri = ['false', 'half-true', 'true']

    
    # Generate classification report and confusion matrix
    print("Gold labels: ", gold_labels)
    print("Predictions: ", predictions) 
    report = classification_report(gold_labels, predictions, labels=labels_tri, output_dict=True)
    matrix = confusion_matrix(gold_labels, predictions, labels=labels_tri)

    pd.set_option('display.precision', 2)
    report_df = pd.DataFrame(report).transpose()
    print(report_df)

    heat_map_repr(matrix, labels_tri)

            

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--labels_path', default='DataProcessed/labels_web_llama.jsonl', type=str)
    args = parser.parse_args()
    gold_labels = [] 
    predictions = []  
    main(args.labels_path, gold_labels, predictions)
