public int getFirstNegative(int[] numbers) {
    for (int i = 0; i < numbers.length; i++) {
        if (numbers[i] > 0) {
            return numbers[i];
        }
    }
    return -1;
}
