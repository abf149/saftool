def naive_radix2_merge_intersection(v1, v2):
    i = j = 0
    intersection = []
    cycle_count = 0
    while i < len(v1) and j < len(v2):
        cycle_count += 1
        if v1[i] == v2[j]:
            intersection.append(v1[i])
            i += 1
            j += 1
        elif v1[i] < v2[j]:
            i += 1
        else:
            j += 1
    v1_empty = i == len(v1)
    v2_empty = j == len(v2)
    return intersection, cycle_count, v1_empty, v2_empty