public int product(int[] numbers) {
    int result = 1;
    for (int i = 0; i < numbers.length; i++) {
        result *= numbers[i];
    }
    return result;
}
