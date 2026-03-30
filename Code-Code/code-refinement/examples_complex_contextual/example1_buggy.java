public int sumPositive(int[] numbers) {
    int sum = 0;
    for (int i = 0; i < numbers.length; i++) {
        if (numbers[i] < 0) {
            sum += numbers[i];
        }
    }
    return sum;
}
