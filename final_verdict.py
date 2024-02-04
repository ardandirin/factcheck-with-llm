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


def main(labels_path, gold_labels, predictions, classifcation):
    with open(labels_path, 'r') as data:
        unknown_count = 0
        for line in data:
            json_obj = json.loads(line.strip())
            # pred_labels = [item['predicted_label'] for item in json_obj['subquestion_data'] if item['confidence_level'] == 'high']]
            pred_labels = [item['predicted_label'] for item in json_obj['subquestion_data']]
            conf_levels = [item['confidence_level'] for item in json_obj['subquestion_data']]
            # print("Claim: ", json_obj['claim'])
            if classifcation == 'six-way':
                gold_lab = json_obj['gold_label']
                predicted_veracity = General.classify_veracity_new_6way(pred_labels)
                # predicted_veracity = General.classify_veracity_new_6way_with_conf(pred_labels, conf_levels)
            elif classifcation == 'three-way':
                gold_lab = General.map_six_to_three_categories(json_obj['gold_label'])
                predicted_veracity = General.classify_veracity_three_way(pred_labels)
                # predicted_veracity = General.classify_veracity_three_way_with_conf(pred_labels, conf_levels)
            elif classifcation == 'binary':
                gold_lab = classify_binary_truthfulness(json_obj['gold_label'])
                predicted_veracity = General.classify_binary_veracity(pred_labels)
                # predicted_veracity = General.classify_binary_veracity_with_conf(pred_labels, conf_levels)

                
            else:
                print("Please provide a predefined classification type.")
            
            if predicted_veracity == 'Unknown':
                    unknown_count += 1
            
            if predicted_veracity == 'Unknown':
                continue
            gold_labels.append(gold_lab)
            predictions.append(predicted_veracity)
            

            # pred_labels = [item['predicted_label'] for item in json_obj['subquestion_data'] if item['confidence_level'] == 'high']
            # print(pred_labels)

            # print("Predicted veracity: ", predicted_veracity)
            # print("Predicted veracity:", predictions)
            # print("Gold label: ", json_obj['gold_label'])
        print("Unknown count: ", unknown_count)

    if classifcation == 'six-way':
        labels_list = ['pants-fire', 'false', 'barely-true', 'half-true', 'mostly-true', 'true']
    elif classifcation == 'three-way':
        labels_list = ['false', 'half-true', 'true']
    elif classifcation == 'binary':
        labels_list = ['no', 'yes']

    
    # Generate classification report and confusion matrix
    # print("Gold labels: ", gold_labels)
    # print("Predictions: ", predictions) 
    report = classification_report(gold_labels, predictions, labels=labels_list, output_dict=True)
    matrix = confusion_matrix(gold_labels, predictions, labels=labels_list)

    pd.set_option('display.precision', 2)
    report_df = pd.DataFrame(report).transpose()
    print(report_df)

    heat_map_repr(matrix, labels_list)

            

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--labels_path', default='Results/labels_mixtral_icl_full_llm.jsonl', type=str)
    parser.add_argument('--classification', default='binary', type=str, choices=['six-way', 'three-way', 'binary'] ) # other options, three-way, binary
    args = parser.parse_args()
    gold_labels = [] 
    predictions = []  
    main(args.labels_path, gold_labels, predictions, args.classification)
