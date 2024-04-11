import argparse
import json
from helpers import general as General
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
# from transformers import T5Tokenizer, T5ForConditionalGeneration

def classify_binary_truthfulness(value):
    false_values = ['pants-fire', 'false', 'barely-true']
    return 'false' if value in false_values else 'true'

def heat_map_repr(matrix, labels):
    matrix_df = pd.DataFrame(matrix, index=labels, columns=labels)
    plt.figure(figsize=(10, 7))
    sns.heatmap(matrix_df, annot=True, fmt='g', cmap='Blues')
    plt.xlabel('Predicted Labels')
    plt.ylabel('Gold Labels')
    plt.title('Confusion Matrix')
    # plt.show()

def main(labels_path, classification):

    results = {
        "sixway": {"gold_labels": [], "predictions": []},
        "threeway": {"gold_labels": [], "predictions": []},
        "binary": {"gold_labels": [], "predictions": []},
    }

    with open(labels_path, 'r') as data:
        unknown_count = 0
        for line in data:
            json_obj = json.loads(line.strip())
            pred_labels = [item['predicted_label'] for item in json_obj['subquestion_data']]

            if classification == 'all':
                binary_gold = classify_binary_truthfulness(json_obj['gold_label'])
                threeway_gold = General.map_six_to_three_categories(json_obj['gold_label'])
                sixway_gold = json_obj['gold_label']

                binary_pred = General.classify_binary_veracity(pred_labels)
                threeway_pred = General.classify_veracity_three_way(pred_labels)
                sixway_pred = General.classify_veracity_new_6way(pred_labels)


                results["binary"]["gold_labels"].append(binary_gold)
                results["binary"]["predictions"].append(binary_pred)
                results["threeway"]["gold_labels"].append(threeway_gold)
                results["threeway"]["predictions"].append(threeway_pred)
                results["sixway"]["gold_labels"].append(sixway_gold)
                results["sixway"]["predictions"].append(sixway_pred)
            else:
                pass

    print("Unknown count:", unknown_count)

    all_reports = []
    if classification == 'all':
        for key in results:
            labels_list = ['pants-fire', 'false', 'barely-true', 'half-true', 'mostly-true', 'true'] if key == 'sixway' else ['false', 'half-true', 'true'] if key == 'threeway' else ['false', 'true']
            report = classification_report(results[key]["gold_labels"], results[key]["predictions"], labels=labels_list, output_dict=True)
            matrix = confusion_matrix(results[key]["gold_labels"], results[key]["predictions"], labels=labels_list)
            pd.set_option('display.precision', 3)
            report_df = pd.DataFrame(report).transpose()
            report_df['Classification_Type'] = key
            all_reports.append(report_df)

            print(f"{key.capitalize()} Classification Report:")
            print(report_df)

            heat_map_repr(matrix, labels_list)
            plt.savefig(f"mixtral_llmweb_{key}_conf.pdf")
     # Concatenate all reports and save to a single CSV
    all_reports_df = pd.concat(all_reports)
    all_reports_df = all_reports_df.round(3)
    all_reports_df.to_csv("Reports/mixtral_llmweb_classification_reports.csv", index=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--labels_path', default='Data/6_Results/Mistral/labels_mixtral_icl_llmweb.jsonl', type=str)
    parser.add_argument('--classification', default='all', type=str, choices=['six-way', 'three-way', 'binary', 'all'])
    args = parser.parse_args()
    main(args.labels_path, args.classification)