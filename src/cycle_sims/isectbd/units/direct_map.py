def direct_mapped_intersection_unit(v1, v2):
    """
    Computes the ideal set intersection of the two input queues in a single cycle.
    It also compares the tails of the two queues and sets the empty flags accordingly.
    """
    # Compute the intersection
    intersection = sorted(list(set(v1).intersection(v2)))

    # Determine the empty flags based on the tails of the queues
    v1_empty = v2_empty = False
    if v1 and v2:  # Check if both lists are non-empty
        if v1[-1] == v2[-1]:  # If tails are equal, mark both as empty
            v1_empty = v2_empty = True
        elif v1[-1] < v2[-1]:  # If tail of v1 is lesser, mark v1 as empty
            v1_empty = True
        else:  # If tail of v2 is lesser, mark v2 as empty
            v2_empty = True
    else:
        v1_empty = not v1  # v1 is empty if it's actually empty
        v2_empty = not v2  # v2 is empty if it's actually empty

    return intersection, 1, v1_empty, v2_empty