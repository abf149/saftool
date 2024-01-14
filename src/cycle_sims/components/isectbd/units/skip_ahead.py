def find_largest_geq(queue, value):
    """
    Finds the index of the largest value in 'queue' which is >= 'value'.
    If no such value exists, returns the length of the queue.
    """
    for idx, val in enumerate(queue):
        if val >= value:
            return idx
    return len(queue)

def skipahead_radix2_merge_intersection(v1, v2):
    i = j = 0
    intersection = []
    cycle_count = 0

    x = 0
    if v1[0] < v2[0]:
        # Start with queue 0 (v1) if v1[0] < v2[0]
        x = 1  

    while i < len(v1) and j < len(v2):
        cycle_count += 1

        if x == 0:
            candidate_index = find_largest_geq(v2, v1[i])
            if candidate_index < len(v2) and v1[i] == v2[candidate_index]:
                intersection.append(v1[i])
                j = candidate_index + 1  # Incrementing the candidate head of queue !x
            else:
                j = candidate_index  # Updating the head of queue !x
            x = 1  # Toggling to queue !x
        else:
            candidate_index = find_largest_geq(v1, v2[j])
            if candidate_index < len(v1) and v2[j] == v1[candidate_index]:
                intersection.append(v2[j])
                i = candidate_index + 1
            else:
                i = candidate_index
            x = 0

    # Additional check for tails
    v1_empty = i >= len(v1) or (v1 and v2 and v1[-1] == v2[-1])
    v2_empty = j >= len(v2) or (v1 and v2 and v1[-1] == v2[-1])

    return intersection, cycle_count, v1_empty, v2_empty