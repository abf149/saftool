import numpy as np
import matplotlib.pyplot as plt

# Plotting function
def plot_residuals(true_values, residuals):
    plt.figure(figsize=(10, 6))
    plt.scatter(true_values, residuals, color='blue', edgecolor='k', alpha=0.7)
    plt.axhline(y=0, color='r', linestyle='-')
    plt.xlabel('True Values')
    plt.ylabel('Residuals')
    plt.title('Residual Plot')
    plt.show()

def plot_distribution(test_cases, values, sparsity1_bin_count=10, title="Values vs sparsity0 for different sparsity1 ranges", sparsity0_range=[0, float('inf')], sparsity1_range=[0, float('inf')]):
    # Calculate sparsity0 and sparsity1
    sparsity0 = (1.0-test_cases[:, 0] / test_cases[:, 2])
    sparsity1 = (1.0-test_cases[:, 1] / test_cases[:, 2])

    # Mask out rows outside sparsity ranges
    sparsity0_mask = (sparsity0 >= sparsity0_range[0]) & (sparsity0 <= sparsity0_range[1])
    sparsity1_mask = (sparsity1 >= sparsity1_range[0]) & (sparsity1 <= sparsity1_range[1])
    mask = sparsity0_mask & sparsity1_mask



    # Determine sparsity1 bins before masking
    sparsity1_min = sparsity1.min()
    sparsity1_max = sparsity1.max()
    sparsity1_bins = np.linspace(sparsity1_min, sparsity1_max, sparsity1_bin_count + 1)

    # Plotting
    plt.figure(figsize=(10, 6))
    for i in range(sparsity1_bin_count):
        # Selecting data for each bin, considering the mask
        bin_mask = (sparsity1 >= sparsity1_bins[i]) & (sparsity1 < sparsity1_bins[i+1]) & mask
        if not np.any(bin_mask):
            continue  # Skip if no points in this bin
        bin_label = f'{sparsity1_bins[i]:.2f}-{sparsity1_bins[i+1]:.2f}'  # Label with sparsity1 range
        plt.plot(sparsity0[bin_mask], values[bin_mask],'.', label=bin_label)

    plt.xlabel('Sparsity0')
    plt.ylabel('Value')
    plt.title(title)
    plt.legend()
    plt.show()


def plot_comparison(test_cases, true_values, predicted, sparsity1_bin_count=10, title="Values vs sparsity0 for different sparsity1 ranges", sparsity0_range=[0, float('inf')], sparsity1_range=[0, float('inf')]):
    # Calculate sparsity0 and sparsity1
    sparsity0 = (1.0-test_cases[:, 0] / test_cases[:, 2])
    sparsity1 = (1.0-test_cases[:, 1] / test_cases[:, 2])

    # Sort test_cases, true_values, and predicted_values in order of increasing sparsity0
    sort_indices = np.argsort(sparsity0)
    test_cases = test_cases[sort_indices]
    true_values = true_values[sort_indices]
    predicted = predicted[sort_indices]
    sparsity0 = sparsity0[sort_indices]
    sparsity1 = sparsity1[sort_indices]

    # Mask out rows outside sparsity ranges
    sparsity0_mask = (sparsity0 >= sparsity0_range[0]) & (sparsity0 <= sparsity0_range[1])
    sparsity1_mask = (sparsity1 >= sparsity1_range[0]) & (sparsity1 <= sparsity1_range[1])
    mask = sparsity0_mask & sparsity1_mask

    # Determine sparsity1 bins based on true_values before masking
    sparsity1_min = sparsity1.min()
    sparsity1_max = sparsity1.max()
    sparsity1_bins = np.linspace(sparsity1_min, sparsity1_max, sparsity1_bin_count + 1)

    # Plotting
    plt.figure(figsize=(10, 6))
    colors = plt.cm.jet(np.linspace(0, 1, sparsity1_bin_count))  # Different colors for each bin
    for i in range(sparsity1_bin_count):
        # Selecting data for each bin, considering the mask
        bin_mask = (sparsity1 >= sparsity1_bins[i]) & (sparsity1 < sparsity1_bins[i+1]) & mask
        if not np.any(bin_mask):
            continue  # Skip if no points in this bin
        bin_label = f'{sparsity1_bins[i]:.2f}-{sparsity1_bins[i+1]:.2f}'

        # Plot true values
        plt.scatter(sparsity0[bin_mask], true_values[bin_mask], color=colors[i], label=f'True values: {bin_label}', marker='.')

        # Plot predicted values
        plt.plot(sparsity0[bin_mask], predicted[bin_mask],'--.', color=colors[i], label=f'Predicted: {bin_label}')

    plt.xlabel('Sparsity0')
    plt.ylabel('Value')
    plt.title(title)
    plt.legend()
    plt.show()