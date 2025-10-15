"""K-means clustering using pure Python.

This program is intended to group multidimensional data using the k-means
clustering algorithm. The data should be supplied as a CSV file. The clusters
are determined based on the normalized data. The program reports cluster sizes,
the number of algorithm iterations, and the final within-cluster sum of
squares.
"""

import csv
import random


def distance(point, center):
    """Returns distance**2"""
    temp = 0.0
    for i in range(len(point)):
        temp += (point[i] - center[i])**2
    return temp


def normalize(data):
    normalized = []
    min_val = []
    max_val = []
    for coord in range(len(data[0])):
        column = []
        for point in data:
            column.append(point[coord])
        min_val.append(min(column))
        max_val.append(max(column))

    for point in data:
        normalized.append([(point[col] - min_val[col]) / (max_val[col] - min_val[col]) for col in range(len(point))])
    return normalized


def initialize_centers(n_centers, data):
    return random.sample(data, n_centers)


def assign_clusters(centers, data):
    labels = []
    wcss = 0.0
    for point in data:
        dists = []
        for center in centers:
            dists.append(distance(point, center))
        min_dist = min(dists)
        labels.append(dists.index(min_dist))
        wcss += min_dist
    return labels, wcss


def update_centers(centers, labels, data):
    for c in range(len(centers)):
        cluster = []
        l = 0
        for point in data:
            if labels[l] == c:
                cluster.append(point)
            l += 1
        if len(cluster) > 0:
            center = []
            for i in range(len(cluster[0])):
                temp = 0.0
                for j in range(len(cluster)):
                    temp += cluster[j][i]
                center.append(temp / len(cluster))
            centers[c] = center


def kmeans(n_clusters, data):
    centers = initialize_centers(n_clusters, data)
    old_labels = None
    n_iters = 0
    while True:
        n_iters += 1
        labels, wcss = assign_clusters(centers, data)
        if labels == old_labels:
            break
        update_centers(centers, labels, data)
        old_labels = labels
    return labels, wcss, n_iters


def load_data():
    data = []

    with open("data.csv", newline="") as file:
        data_reader = csv.reader(file)
        for row in data_reader:
            data.append([float(i) for i in row])

    labels, wcss, n_iters = kmeans(3, normalize(data))
    print("Cluster sizes:")
    for c in range(3):
        print(f"{c + 1} -", labels.count(c))
    print("Iterations:", n_iters)
    print("WCSS:", wcss)


load_data()
