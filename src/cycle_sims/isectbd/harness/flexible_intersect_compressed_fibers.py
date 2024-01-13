import random, math
from tqdm import tqdm

def test_flexible_intersect_compressed_fibers(numTests, compressedFiberLength0, compressedFiberLength1, fiberLength, vectorLength, intersection_function):
    total_cycles = 0
    total_intersections = 0
    total_result_length = 0
    total_count_full_length_intersections = 0

    for _ in range(numTests):
        compressed_fiber0 = sorted(random.sample(range(fiberLength), compressedFiberLength0))
        compressed_fiber1 = sorted(random.sample(range(fiberLength), compressedFiberLength1))
        result, cycle_count, num_intersections, full_length_result_length, count_full_length_intersections, v0_empty, v1_empty = flexible_intersect_compressed_fibers(
            compressed_fiber0, compressed_fiber1, vectorLength, intersection_function
        )
        ideal_result = sorted(list(set(compressed_fiber0) & set(compressed_fiber1)))
        if result != ideal_result:
            raise ValueError("Incorrect intersection result")

        total_cycles += cycle_count
        total_intersections += num_intersections

        # Consider only intersections where both inputs are of length vectorLength
        #if len(compressed_fiber0) == vectorLength and len(compressed_fiber1) == vectorLength:
        total_result_length += full_length_result_length
        total_count_full_length_intersections += count_full_length_intersections

    average_total_cycles = total_cycles / numTests
    average_num_intersections = total_intersections / numTests
    average_cycles_per_intersection = average_total_cycles / average_num_intersections

    # Calculate the average length of the result vector, if applicable
    average_result_length = total_result_length / total_count_full_length_intersections

    # Calculate the average number of full length intersections
    average_num_full_length_intersections = total_count_full_length_intersections / numTests

    return average_total_cycles, average_num_intersections, average_cycles_per_intersection, average_result_length, average_num_full_length_intersections

def flexible_intersect_compressed_fibers(compressed_fiber0, compressed_fiber1, vectorLength, intersection_function):
    total_cycle_count = 0
    num_intersections = 0
    result_compressed_fiber = []
    i = j = 0

    total_result_length = 0
    total_count_full_length_intersections = 0

    while i < len(compressed_fiber0) and j < len(compressed_fiber1):
        v1 = compressed_fiber0[i:i + vectorLength]
        v2 = compressed_fiber1[j:j + vectorLength]
        intersection, cycle_count, v1_empty, v2_empty = intersection_function(v1, v2)
        result_compressed_fiber.extend(intersection)
        total_cycle_count += cycle_count
        num_intersections += 1

        # Consider only intersections where both inputs are of length vectorLength
        if True or len(v1) == vectorLength and len(v2) == vectorLength:
            #assert(len(intersection) <= vectorLength)
            total_result_length += len(intersection)
            total_count_full_length_intersections += 1

        if v1_empty and not v2_empty:
            i += vectorLength
        elif not v1_empty and v2_empty:
            j += vectorLength
        elif v1_empty and v2_empty:
            i += vectorLength
            j += vectorLength
        if i >= len(compressed_fiber0) or j >= len(compressed_fiber1):
            break
    v0_empty = i >= len(compressed_fiber0)
    v1_empty = j >= len(compressed_fiber1)
    return result_compressed_fiber, total_cycle_count, num_intersections, total_result_length, total_count_full_length_intersections, v0_empty, v1_empty

def run_multiple_test_cases(test_cases, numTests, intersection_function):
    """
    Outermost wrapper function to run test_flexible_intersect_compressed_fibers with different combinations
    of parameter values, accounting for additional return values and with tqdm progress bar.

    Args:
    test_cases (list of dicts): List of dictionaries, each containing a different combination of parameter values.
    numTests (int): Number of test cases to run for each combination.
    intersection_function (function): A reference to the intersection function to be used.

    Returns:
    results (list of dicts): A list of dictionaries with the results for each combination of parameter values.
    """
    results = []

    for case in tqdm(test_cases, desc="Running test cases"):
        compressedFiberLength0 = case['compressedFiberLength0']
        compressedFiberLength1 = case['compressedFiberLength1']
        fiberLength = case['fiberLength']
        vectorLength = case['vectorLength']

        # Run the test function with the current combination of parameters
        average_total_cycles, average_num_intersections, average_cycles_per_intersection, average_result_length, average_num_full_length_intersections = test_flexible_intersect_compressed_fibers(
            numTests, compressedFiberLength0, compressedFiberLength1, fiberLength, vectorLength, intersection_function
        )

        # Add the results along with the parameter values to the results list
        result_dict = {
            'compressedFiberLength0': compressedFiberLength0,
            'compressedFiberLength1': compressedFiberLength1,
            'fiberLength': fiberLength,
            'vectorLength': vectorLength,
            'average_total_cycles': average_total_cycles,
            'average_num_intersections': average_num_intersections,
            'average_cycles_per_intersection': average_cycles_per_intersection,
            'average_result_length': average_result_length,
            'average_num_full_length_intersections': average_num_full_length_intersections
        }
        results.append(result_dict)

    return results

def generate_cartesian_product_test_cases(sparsity_values, fiber_length_values, vector_length_values):
    cartesian_product_cases = []
    for sparsity0 in sparsity_values:
        for sparsity1 in sparsity_values:
            for fiber_length in fiber_length_values:
                for vector_length in vector_length_values:
                    test_case = {
                        'sparsity0': sparsity0,
                        'sparsity1': sparsity1,
                        'fiberLength': fiber_length,
                        'vectorLength': vector_length
                    }
                    cartesian_product_cases.append(test_case)
    return cartesian_product_cases

def generate_random_test_cases(sparsity0_range, sparsity1_range, fiber_length_values, vector_length_values, numTests):
    """
    Generates a specified number of test cases with values randomly and independently drawn from the provided ranges and lists.

    Args:
    sparsity0_range (tuple): Closed range (min, max) for sparsity0.
    sparsity1_range (tuple): Closed range (min, max) for sparsity1.
    fiber_length_values (list): List of possible values for fiber length.
    vector_length_values (list): List of possible values for vector length.
    numTests (int): Number of test cases to generate.

    Returns:
    random_test_cases (list of dicts): List of test case dictionaries with randomly selected parameters.
    """
    random_test_cases = []
    for _ in range(numTests):
        test_case = {
            'sparsity0': random.uniform(*sparsity0_range),
            'sparsity1': random.uniform(*sparsity1_range),
            'fiberLength': random.choice(fiber_length_values),
            'vectorLength': random.choice(vector_length_values)
        }
        random_test_cases.append(test_case)

    return random_test_cases

# Example usage
##sparsity0_range = (0.4, 0.6)  # Example range for sparsity0
#sparsity1_range = (0.5, 0.75) # Example range for sparsity1
#fiber_length_values = [20, 30, 40]
#vector_length_values = [5, 10, 15]
#numTests = 10
#generate_random_test_cases(sparsity0_range, sparsity1_range, fiber_length_values, vector_length_values, numTests)



def convert_sparsity_to_compressed_length(test_cases):
    converted_cases = []
    for case in test_cases:
        sparsity0 = case['sparsity0']
        sparsity1 = case['sparsity1']
        fiberLength = case['fiberLength']
        compressedFiberLength0 = math.ceil((1-sparsity0) * fiberLength)
        compressedFiberLength1 = math.ceil((1-sparsity1) * fiberLength)
        new_case = {
            'compressedFiberLength0': compressedFiberLength0,
            'compressedFiberLength1': compressedFiberLength1,
            'fiberLength': fiberLength,
            'vectorLength': case['vectorLength']
        }
        converted_cases.append(new_case)
    return converted_cases