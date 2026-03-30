public boolean anyLessThan(int[] numbers, int threshold) {
    for (int i = 0; i < numbers.length; i++) {
        if (numbers[i] >= threshold) {
            return true;
        }
    }
    return false;
}
