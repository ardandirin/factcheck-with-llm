import matplotlib.pyplot as plt

# Data for the plot
thresholds = [0.8, 0.9, 0.925, 0.95]
average_recall = [1.0, 0.822, 0.531, 0.2766]

# Creating the plot
plt.figure(figsize=(10, 6))
plt.plot(thresholds, average_recall, marker='o')

# Adding title and labels
plt.title('Average Recall at Different Thresholds')
plt.xlabel('Threshold')
plt.ylabel('Average Recall')

# Showing the plot
plt.grid(True)
plt.show()
