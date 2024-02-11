# Fix the subquestions format
from helpers import json_loader as JsonLoader
import json
import matplotlib.pyplot as plt


def main(subquestions_path):
    all_len_qs = []
    with open(subquestions_path, 'r', encoding='utf8') as subq_file:
        for line in subq_file:
            data = json.loads(line)
            id = data['example_id']
            questions = data['subquestions']
            # claim = data['claim']
            questions_list = JsonLoader.list_returner_q_mark(data)
            print(len(questions_list))
            all_len_qs.append(len(questions_list))
            # subqs =  questions.strip().split('\n')
            # data_to_write = {'example_id': id, 'claim': claim, 'subquestions': subqs}
            # json.dump(data_to_write, outfile)
            # outfile.write('\n')
    print(all_len_qs)
    # Plotting a histogram for the list of numbers
    plt.figure(figsize=(10, 6))
    plt.hist(all_len_qs, bins=10, color='skyblue', edgecolor='black')
    plt.title('Histogram of Numbers')
    plt.xlabel('Value')
    plt.ylabel('Frequency')

    plt.show()




if __name__ == "__main__":
    main('./ClaimDecomp/subquestions_finetuned.jsonl')