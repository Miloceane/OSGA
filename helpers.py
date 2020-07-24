#########################################################
# Based on: https://stackabuse.com/quicksort-in-python/ #
#########################################################
def partition_flowers(array, start, end):
    pivot_value = array[start].pos_y
    low = start + 1
    high = end

    while True:
        # If the current value we're looking at is larger than the pivot
        # it's in the right place (right side of pivot) and we can move left,
        # to the next element.
        # We also need to make sure we haven't surpassed the low pointer, since that
        # indicates we have already moved all the elements to their correct side of the pivot
        while low <= high and array[high].pos_y >= pivot_value:
            high = high - 1

        # Opposite process of the one above
        while low <= high and array[low].pos_y <= pivot_value:
            low = low + 1

        # We either found a value for both high and low that is out of order
        # or low is higher than high, in which case we exit the loop
        if low <= high:
            array[low], array[high] = array[high], array[low]
            # The loop continues
        else:
            # We exit out of the loop
            break

    array[start], array[high] = array[high], array[start]

    return high


def quick_sort_flowers(array, start, end):
    if start >= end:
        return

    p = partition_flowers(array, start, end)
    quick_sort_flowers(array, start, p-1)
    quick_sort_flowers(array, p+1, end)
