// Bug: Swapped min and max values
public int clamp(int value, int min, int max) {
    if (value < min) return max;
    if (value > max) return min;
    return value;
}
