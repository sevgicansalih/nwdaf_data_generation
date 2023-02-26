import random

def ranks(sample):
    """
    Return the ranks of each element in an integer sample.
    """
    indices = sorted(range(len(sample)), key=lambda i: sample[i])
    return sorted(indices, key=lambda i: indices[i])

def sample_with_minimum_distance(n=40, k=4, d=10):
    """
    Sample of k elements from range(n), with a minimum distance d.
    """
    sample = random.sample(range(n-(k-1)*(d-1)), k)
    return [s + (d-1)*r for s, r in zip(sample, ranks(sample))]