import csv
import matplotlib.pyplot as plt


if __name__ == "__main__":
    timestamps = {}
    age_in_seconds = {}
    with open("output_cmc.csv") as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            timestamp = int(row[0])
            currency_pair = row[2]
            age = int(row[-1])
            if currency_pair not in timestamps:
                timestamps[currency_pair] = []
                age_in_seconds[currency_pair] = []
            timestamps[currency_pair].append(timestamp)
            age_in_seconds[currency_pair].append(age)

    plt.figure(figsize=(10, 6))
    for currency_pair, ages in age_in_seconds.items():
        plt.plot(timestamps[currency_pair], ages, label=currency_pair)

    plt.xlabel("Timestamp")
    plt.ylabel("Age in Seconds")
    plt.title("Gecko last updated at")
    plt.legend()

    # Display the chart
    plt.grid(True)  # Add grid for better readability
    plt.tight_layout()  # Adjust spacing between elements
    plt.show()
