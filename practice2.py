"""K-means clustering using pure Python.

This program is intended to group multidimensional data using the k-means
clustering algorithm. The data should be supplied as a CSV file. The clusters
are determined based on the normalized data. The program reports cluster sizes,
the number of algorithm iterations, and the final within-cluster sum of
squares.
"""

import csv
import math
import random

file = open("data.csv", newline="")
temp = 0.0


def distance(point, center):
    global temp
    temp = 0.0
    for i in range(len(point)):
        point_x = normalize(point[i], i)
        center_x = normalize(center[i], i)
        temp += (point_x - center_x)**2
    return math.sqrt(temp)


def normalize(val, coord):
    column = []
    for point in data:
        column.append(float(point[coord]))
    min_val = min(column)
    max_val = max(column)
    range = max_val - min_val
    return (float(val) - min_val) / range


def initialize_centers(n_centers):
    return random.sample(data, n_centers)


def assign_clusters(centers):
    labels = []
    wcss = 0.0
    for point in data:
        dists = []
        for center in centers:
            dists.append(distance(point, center))
        min_dist = min(dists)
        labels.append(dists.index(min_dist))
        wcss += min_dist**2
    return labels, wcss


def update_centers(centers, labels):
    for c in range(len(centers)):
        cluster = []
        l = 0
        for point in data:
            if labels[l] == c:
                cluster.append(point)
            l += 1
        if len(cluster) > 0:
            center = []
            for i in range(len(point)):
                global temp
                temp = 0.0
                for j in range(len(cluster)):
                    temp += float(cluster[j][i])
                center.append(temp / len(cluster))
            centers[c] = center


def kmeans(n_clusters):
    centers = initialize_centers(n_clusters)
    old_labels = None
    n_iters = 0
    while True:
        n_iters += 1
        labels, wcss = assign_clusters(centers)
        if labels == old_labels:
            break
        update_centers(centers, labels)
        old_labels = labels
    return labels, wcss, n_iters


data = []


def load_data():
    data_reader = csv.reader(file)
    for row in data_reader:
        data.append(row)
    labels, wcss, n_iters = kmeans(3)
    print("Cluster sizes:")
    for c in range(3):
        print(f"{c + 1} -", labels.count(c))
    print("Iterations:", n_iters)
    print("WCSS:", wcss)


load_data()
file.close()
